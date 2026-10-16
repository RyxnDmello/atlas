import os
import json
import httpx
import inspect
from google import genai
from unittest import TestCase
from contextlib import ExitStack
from types import SimpleNamespace
from collections.abc import Generator
from unittest.mock import MagicMock, patch

from app.core.constants import Constants

from app.pipeline.generation.provider import LLMProvider
from app.pipeline.generation.gemini import GeminiFlashProvider

from app.errors.generation import GenerationError


def event(kind: str, **values) -> SimpleNamespace:
    """Build a minimal SDK-shaped event without spending provider quota."""
    return SimpleNamespace(event_type=kind, **values)


def start(index: int = 0, kind: str = "model_output") -> SimpleNamespace:
    """Start one typed step in a fake stream."""
    return event("step.start", index=index, step=SimpleNamespace(type=kind))


def delta(text: str, index: int = 0, kind: str = "text") -> SimpleNamespace:
    """Build a typed incremental event."""
    return event("step.delta", index=index, delta=SimpleNamespace(type=kind, text=text))


def completed(status: str | None = "completed", usage=None) -> SimpleNamespace:
    """Build a terminal interaction with optional usage metadata."""
    return event("interaction.completed", interaction=SimpleNamespace(status=status, usage=usage))


class GenerationTests(TestCase):
    """Verify provider transport, provisional output, cleanup, and safe failures."""

    def setUp(self) -> None:
        """Prepare isolated credentials and an SDK context-manager boundary."""
        self.scope = ExitStack()
        self.addCleanup(self.scope.close)
        self.scope.enter_context(patch.dict(os.environ, {
            "GEMINI_API_KEY": "secret-key-sentinel",
            "GEMINI_MODEL": "configured-model",
            "GEMINI_MAX_OUTPUT_TOKENS": "73",
        }))
        self.factory = self.scope.enter_context(
            patch("app.pipeline.generation.gemini.genai.Client"))
        self.client = self.factory.return_value.__enter__.return_value
        self.stream = self.client.interactions.create.return_value
        self.stream.__enter__.return_value = self.stream
        self.events = [start(), delta("answer-sentinel"), completed()]
        self.stream.__iter__.side_effect = lambda: iter(self.events)
        self.provider = GeminiFlashProvider()

    def output(self, prompt="prompt-sentinel", chunks=None):
        """Exhaust the provider using private content sentinels."""
        return list(self.provider.stream_generate(prompt, ["context-sentinel"] if chunks is None else chunks))

    def closed(self) -> None:
        """Require both stream and client context managers to exit exactly once."""
        self.stream.__exit__.assert_called_once()
        self.factory.return_value.__exit__.assert_called_once()

    def test_signature_and_exact_request(self) -> None:
        """Lock the protocol and request while preserving content, order, and caller lists."""
        self.assertEqual(inspect.signature(LLMProvider.stream_generate),
                         inspect.signature(GeminiFlashProvider.stream_generate))
        chunks = ["  first\nsource ", "second\n\nsource"]
        original = chunks.copy()
        self.assertEqual(self.output(" question \n", chunks),
                         ["answer-sentinel"])
        self.assertEqual(chunks, original)
        self.client.interactions.create.assert_called_once_with(
            model="configured-model", input="  first\nsource \n\nsecond\n\nsource\n\n question \n",
            stream=True, store=False, generation_config={"max_output_tokens": 73},
        )
        self.assertEqual(
            self.factory.call_args.kwargs["http_options"].retry_options.attempts, 0)
        self.assertFalse(self.factory.call_args.kwargs["vertexai"])
        self.closed()

    def test_interleaved_steps_and_safe_usage(self) -> None:
        """Emit only active model text, preserving repeated deltas and all usage counters."""
        usage = SimpleNamespace(
            total_input_tokens=11, total_output_tokens=12, total_thought_tokens=13, total_tokens=36)
        self.events = [
            start(1, "thought"), delta("private-thought", 1),
            delta("signature-sentinel", 1, "thought_signature"),
            start(2), delta("answer-sentinel", 2), delta("answer-sentinel", 2),
            delta("image-sentinel", 2, "image"), event("step.stop", index=2),
            delta("stopped-sentinel", 2), delta("orphan-sentinel", 99),
            start(3, "function_call"), delta("tool-sentinel", 3),
            completed(usage=usage),
        ]

        with self.assertLogs("app.pipeline.generation.gemini", level="INFO") as logs:
            self.assertEqual(
                self.output(), ["answer-sentinel", "answer-sentinel"])

        text = "\n".join(logs.output)
        for value in ("input_tokens=11", "output_tokens=12", "thought_tokens=13", "total_tokens=36", "deltas=2"):
            self.assertIn(value, text)
        for value in ("secret-key-sentinel", "prompt-sentinel", "context-sentinel", "answer-sentinel", "private-thought"):
            self.assertNotIn(value, text)

        self.closed()

    def test_empty_context_is_valid(self) -> None:
        """Allow independent provider use without retrieved chunks."""
        self.output(chunks=[])
        self.assertEqual(
            self.client.interactions.create.call_args.kwargs["input"], "prompt-sentinel")

    def test_blank_prompt_precedes_client_creation(self) -> None:
        """Reject blank prompts before opening SDK resources."""
        for prompt in ("", " \n\t"):
            with self.subTest(prompt=prompt), self.assertRaises(ValueError):
                self.output(prompt)

        self.factory.assert_not_called()

    def test_config_validation_is_lazy_and_safe(self) -> None:
        """Reject absent, blank, and invalid generation settings only on provider construction."""
        for name, values in {
            "GEMINI_API_KEY": (None, "", " \n"),
            "GEMINI_MODEL": (None, "", " \t"),
            "GEMINI_MAX_OUTPUT_TOKENS": ("0", "-1", "bad-secret-sentinel"),
        }.items():
            for value in values:
                with self.subTest(name=name, value=value), patch.dict(os.environ):
                    if value is None:
                        os.environ.pop(name, None)
                    else:
                        os.environ[name] = value

                    Constants()
                    with self.assertRaises(ValueError) as caught:
                        GeminiFlashProvider()

                    self.assertNotIn("sentinel", str(caught.exception))

        self.factory.assert_not_called()
        with patch.dict(os.environ):
            os.environ.pop("GEMINI_MAX_OUTPUT_TOKENS", None)
            self.assertEqual(GeminiFlashProvider(
            ).config.GEMINI_MAX_OUTPUT_TOKENS, 2048)

        self.assertNotIn("secret-key-sentinel",
                         repr(self.provider.config.GEMINI_API_KEY))

    def test_unsuccessful_and_empty_streams(self) -> None:
        """Reject token cutoff, blocked/failed/action states, missing completion, and whitespace output."""
        cases = [[start(), delta("partial")], [completed()],
                 [start(), delta(" \n"), completed()]]
        cases += [[start(), delta("partial"), completed(status)]
                  for status in ("incomplete", "failed", "cancelled", "requires_action", None)]
        cases += [[event("error", error=SimpleNamespace(message="sensitive-error-sentinel"))]]

        for events in cases:
            with self.subTest(events=events):
                self.events = events
                with self.assertRaises(GenerationError) as caught:
                    self.output()

                self.assertEqual(caught.exception.to_dict(), {
                                 "error": "Generation failed", "code": "GENERATION_FAILED"})
                self.assertEqual(caught.exception.status, 502)

    def test_exception_and_timeout_cleanup_are_sanitized(self) -> None:
        """Suppress raw SDK exceptions, including errors after partial answer output."""
        for failure in (RuntimeError("sensitive-error-sentinel"), httpx.ReadTimeout("sensitive-error-sentinel")):
            with self.subTest(failure=type(failure).__name__):
                self.stream.__iter__.side_effect = failure
                with self.assertLogs("app.pipeline.generation.gemini", level="INFO") as logs:
                    with self.assertRaises(GenerationError) as caught:
                        self.output()

                self.assertNotIn("sensitive-error-sentinel",
                                 str(caught.exception) + str(logs.output))
                self.assertTrue(caught.exception.__suppress_context__)

        self.assertEqual(self.stream.__exit__.call_count, 2)
        self.assertEqual(self.factory.return_value.__exit__.call_count, 2)

    def test_request_failure_closes_client(self) -> None:
        """Release the client if obtaining a stream fails."""
        self.client.interactions.create.side_effect = RuntimeError(
            "sensitive-error-sentinel")
        with self.assertRaises(GenerationError):
            self.output()

        self.factory.return_value.__exit__.assert_called_once()

    def test_failure_after_partial_text_is_not_success(self) -> None:
        """Keep an already-yielded prefix provisional when the remote stream fails."""
        def events():
            """Emit a prefix and then simulate an upstream timeout."""
            yield start()
            yield delta("partial")
            raise httpx.ReadTimeout("sensitive-error-sentinel")

        self.stream.__iter__.side_effect = events
        iterator = self.provider.stream_generate("question", [])
        self.assertEqual(next(iterator), "partial")
        with self.assertRaises(GenerationError):
            next(iterator)

        self.closed()

    def test_early_close_releases_stream_and_client(self) -> None:
        """Support consumer cancellation without draining the remote response."""
        iterator = self.provider.stream_generate("question", [])
        self.assertEqual(next(iterator), "answer-sentinel")
        assert isinstance(iterator, Generator)
        iterator.close()
        self.closed()


class SDKTransportTests(TestCase):
    """Exercise the installed SDK over mock HTTP rather than a fake event adapter."""

    def test_retryable_failure_is_one_request_and_debug_is_safe(self) -> None:
        """Prove SDK retry suppression and prevent SDK debug payload logging."""
        requests = []

        def respond(request):
            """Return a retryable upstream error containing a sensitive sentinel."""
            requests.append(request)

            return httpx.Response(503, json={"error": {"code": 503, "message": "sensitive-error-sentinel", "status": "UNAVAILABLE"}})

        constructor = genai.Client
        closers = []
        transport = httpx.Client(transport=httpx.MockTransport(respond))
        self.addCleanup(transport.close)

        def client(**kwargs):
            """Keep the provider's real SDK options and replace only its HTTP transport."""
            kwargs["http_options"].httpx_client = transport

            instance = constructor(**kwargs)
            instance.close = MagicMock(wraps=instance.close)
            closers.append(instance.close)

            return instance

        with patch.dict(os.environ, {
            "GEMINI_API_KEY": "secret-key-sentinel", "GEMINI_MODEL": "configured-model",
            "GEMINI_MAX_OUTPUT_TOKENS": "2048", "GOOGLE_GENAI_DEBUG": "1",
        }), patch("app.pipeline.generation.gemini.genai.Client", side_effect=client):
            with self.assertLogs(level="DEBUG") as logs:
                with self.assertRaises(GenerationError):
                    list(GeminiFlashProvider().stream_generate(
                        "prompt-sentinel", ["context-sentinel"]))

        self.assertEqual(len(requests), 1)
        payload = json.loads(requests[0].content)
        self.assertEqual(payload["model"], "configured-model")
        self.assertTrue(payload["stream"])
        self.assertFalse(payload["store"])
        self.assertEqual(payload["generation_config"],
                         {"max_output_tokens": 2048})
        closers[0].assert_called_once()
        for value in ("secret-key-sentinel", "prompt-sentinel", "context-sentinel", "sensitive-error-sentinel"):
            self.assertNotIn(value, "\n".join(logs.output))

    def test_real_sdk_decodes_sse_and_closes_response(self) -> None:
        """Verify native SDK event decoding and stream cleanup over synthetic SSE bytes."""
        events = [
            {"event_type": "step.start", "index": 0, "step": {"type": "thought"}},
            {"event_type": "step.delta", "index": 0, "delta": {
                "type": "thought_signature", "signature": "private-signature"}},
            {"event_type": "step.stop", "index": 0},
            {"event_type": "step.start", "index": 1,
                "step": {"type": "model_output"}},
            {"event_type": "step.delta", "index": 1,
                "delta": {"type": "text", "text": "first"}},
            {"event_type": "step.delta", "index": 1,
                "delta": {"type": "text", "text": "second"}},
            {"event_type": "step.stop", "index": 1},
            {"event_type": "interaction.completed", "interaction": {
                "id": "synthetic-id", "object": "interaction", "status": "completed",
                "model": "configured-model", "created": "2026-10-15T00:00:00Z", "updated": "2026-10-15T00:00:00Z",
                "usage": {"total_input_tokens": 2, "total_output_tokens": 3, "total_thought_tokens": 4, "total_tokens": 9},
            }},
        ]
        body = "".join(
            f"event: {item['event_type']}\ndata: {json.dumps(item)}\n\n" for item in events) + "data: [DONE]\n\n"
        response = httpx.Response(200, headers={
                                  "content-type": "text/event-stream"}, stream=httpx.ByteStream(body.encode()))
        self.assertFalse(response.is_closed)
        transport = httpx.Client(
            transport=httpx.MockTransport(lambda request: response))
        self.addCleanup(transport.close)
        constructor = genai.Client

        def client(**kwargs):
            """Inject mock HTTP while preserving production client options."""
            kwargs["http_options"].httpx_client = transport

            return constructor(**kwargs)

        with patch.dict(os.environ, {
            "GEMINI_API_KEY": "fake-key", "GEMINI_MODEL": "configured-model", "GEMINI_MAX_OUTPUT_TOKENS": "2048",
        }), patch("app.pipeline.generation.gemini.genai.Client", side_effect=client):
            self.assertEqual(list(GeminiFlashProvider().stream_generate(
                "synthetic", [])), ["first", "second"])

        self.assertTrue(response.is_closed)
