import os
import json
import asyncio
from uuid import UUID, uuid4
from unittest import TestCase
from contextlib import ExitStack
from collections.abc import Iterable
from threading import Event, get_ident
from unittest.mock import PropertyMock, patch

import httpx
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

from app.core.constants import constants

from app.db.qdrant import store

from app.pipeline.retrieval import retrieve
from app.pipeline.generation.prompt import FALLBACK
from app.pipeline.generation.grounded import GroundedStream
from app.pipeline.generation.gemini import GeminiFlashProvider

from app.routers.files import ask, prepare

from app.models.qdrant.chunk import Chunk
from app.schemas.generation import AskRequest

from app.errors.api import ApiError
from app.errors.generation import GenerationError

from app.main import app

from tests.smoke_ask import serve
from tests.postgres import database
from tests.test_05_upload_storage import Provider as Embedder
from tests.test_08_generation import completed, delta, start
from tests.test_09_grounded_generation import Provider, source


def events(lines: Iterable[str]) -> list[tuple[str, dict]]:
    """Parse logical SSE events, ignoring comments and HTTP chunk boundaries."""
    result = []
    name = "message"
    data: list[str] = []

    for line in [*lines, ""]:
        if not line:
            if data:
                result.append((name, json.loads("\n".join(data))))

            name, data = "message", []
        elif not line.startswith(":"):
            field, _, value = line.partition(":")
            value = value.removeprefix(" ")
            if field == "event":
                name = value
            elif field == "data":
                data.append(value)

    return result


class AskTests(TestCase):
    def setUp(self) -> None:
        """Patch only retrieval/provider construction, keeping native routing and grounding real."""
        self.scope = ExitStack()
        self.addCleanup(self.scope.close)

        self.file = UUID(int=1)
        self.chunks = [source(7), source(2)]
        self.provider = Provider(
            ["First ", "part[[ci", "te:7]]", "\nSecond[[cite:2]]"],
        )

        self.search = self.scope.enter_context(
            patch("app.routers.files.retrieve", return_value=self.chunks),
        )
        self.constructor = self.scope.enter_context(
            patch("app.routers.files.GeminiFlashProvider",
                  return_value=self.provider),
        )

        self.streams: list[GroundedStream] = []
        self.closers = []
        self.factory = self.scope.enter_context(
            patch("app.routers.files.GroundedStream", side_effect=self.ground),
        )

        self.http = TestClient(app)
        self.addCleanup(self.http.close)

    def ground(self, *args) -> GroundedStream:
        """Observe the real request-scoped stream and explicit cleanup owner."""
        stream = GroundedStream(*args)
        self.streams.append(stream)
        self.closers.append(self.scope.enter_context(
            patch.object(stream, "close", wraps=stream.close),
        ))

        return stream

    def request(self, **body):
        """Call the actual POST route without starting unrelated real-model services."""
        return self.http.post(
            f"/files/{self.file}/ask", json={"question": "question", **body},
        )

    def test_success_exact_wire_order_provenance_and_cleanup(self) -> None:
        """Preserve clean incremental deltas and trusted citation values with one terminal."""
        response = self.request(question="  question \n")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.headers["content-type"].startswith("text/event-stream"),
        )
        self.assertEqual(response.headers["cache-control"], "no-cache")
        self.assertEqual(response.headers["x-accel-buffering"], "no")
        self.search.assert_called_once_with("question", self.file, 5)
        self.factory.assert_called_once_with(
            self.provider, "question", self.chunks,
        )

        expected = [
            dict(
                index=chunk.chunk_index, page=chunk.page, heading=chunk.heading,
                section=chunk.section, excerpt=chunk.display_text,
            )
            for chunk in self.chunks
        ]
        self.assertEqual(events(response.iter_lines()), [
            ("answer", {"text": "First "}),
            ("answer", {"text": "part"}),
            ("answer", {"text": "\nSecond"}),
            ("citations", {"citations": expected}),
            ("done", {"status": "completed"}),
        ])
        self.assertNotIn("[[cite:", response.text)
        self.assertTrue(self.provider.closed)
        self.closers[0].assert_called_once_with()

    def test_actual_provider_filters_thought_and_internal_events_before_sse(self) -> None:
        """Keep provider-internal text off the public wire using the existing SDK test seam."""
        self.constructor.side_effect = GeminiFlashProvider

        with (
            patch.dict(
                os.environ, {"GEMINI_API_KEY": "test-only", "GEMINI_MODEL": "test-only"}),
            patch("app.pipeline.generation.gemini.genai.Client") as factory,
        ):
            client = factory.return_value.__enter__.return_value
            stream = client.interactions.create.return_value
            stream.__enter__.return_value = stream
            stream.__iter__.return_value = iter([
                start(1, "thought"), delta("PRIVATE_THOUGHT", 1),
                delta("PRIVATE_UNKNOWN", 9), start(), delta(
                    "Clean[[cite:7]]"), completed(),
            ])

            response = self.request()
            wire = events(response.iter_lines())

            self.assertEqual(wire[0], ("answer", {"text": "Clean"}))
            self.assertEqual([name for name, _ in wire], [
                             "answer", "citations", "done"])
            self.assertNotIn("PRIVATE", response.text)
            stream.__exit__.assert_called_once()
            factory.return_value.__exit__.assert_called_once()
            self.closers[0].assert_called_once_with()

    def test_validation_matches_query_and_rejects_before_work(self) -> None:
        """Reject invalid UUID/questions/top-k without touching retrieval or Gemini."""
        for body in (
            {}, {"question": ""}, {"question": " \t\n"}, {"question": None},
            {"question": 42}, {"question": "q", "top_k": 0},
            {"question": "q", "top_k": 21}, {"question": "q", "top_k": None},
        ):
            with self.subTest(body=body):
                response = self.http.post(f"/files/{self.file}/ask", json=body)
                self.assertEqual(response.status_code, 422)

        response = self.http.post(
            "/files/not-a-uuid/ask", json={"question": "q"})
        self.assertEqual(response.status_code, 422)
        self.search.assert_not_called()
        self.constructor.assert_not_called()

    def test_top_k_boundaries_and_empty_results_without_generation_configuration(self) -> None:
        """Empty retrieval bypasses both valid and unavailable generation settings entirely."""
        self.search.return_value = []
        self.constructor.side_effect = GenerationError()

        for limit in (1, 20):
            with self.subTest(top_k=limit):
                response = self.request(top_k=limit)
                self.assertEqual(response.status_code, 200)
                self.search.assert_called_with("question", self.file, limit)
                self.assertEqual(events(response.iter_lines()), [
                    ("answer", {"text": FALLBACK}),
                    ("citations", {"citations": []}),
                    ("done", {"status": "completed"}),
                ])

        self.constructor.assert_not_called()
        self.factory.assert_not_called()
        self.assertEqual(self.provider.calls, [])

    def test_retrieval_failures_preserve_http_contract(self) -> None:
        """Keep existing retrieval error codes, status, and body before SSE commitment."""
        for error in (
            ApiError("Embedding failed", "INTERNAL_SERVER_ERROR"),
            ApiError("Invalid payload", "UNPROCESSABLE_ENTITY"),
            ApiError("Qdrant unavailable", "QDRANT_CONNECTION_FAILED"),
            ApiError("Collection invalid", "QDRANT_COLLECTION_ERROR"),
        ):
            with self.subTest(code=error.code):
                self.search.side_effect = error
                response = self.request()

                self.assertEqual(response.status_code, error.status)
                self.assertEqual(response.json(), error.to_dict())
                self.assertTrue(
                    response.headers["content-type"].startswith(
                        "application/json"),
                )

        self.constructor.assert_not_called()

    def test_provider_preparation_failure_is_http_generation_error(self) -> None:
        """Lazy deterministic configuration validation fails before the SSE response starts."""
        self.constructor.side_effect = GenerationError()
        response = self.request()

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), GenerationError().to_dict())
        self.factory.assert_not_called()

    def test_actual_missing_and_invalid_settings_fail_only_for_nonempty_retrieval(self) -> None:
        """Exercise real lazy config validation without permitting any SDK connection."""
        self.constructor.side_effect = GeminiFlashProvider

        for values in (
            {"GEMINI_API_KEY": "", "GEMINI_MODEL": ""},
            {"GEMINI_API_KEY": "fake", "GEMINI_MODEL": "fake",
                "GEMINI_MAX_OUTPUT_TOKENS": "invalid"},
        ):
            with (
                self.subTest(settings=list(values)),
                patch.dict(os.environ, values),
                patch("app.pipeline.generation.gemini.genai.Client") as sdk,
            ):
                self.search.return_value = self.chunks
                response = self.request()
                self.assertEqual(response.status_code, 502)
                self.assertEqual(response.json(), GenerationError().to_dict())

                self.search.return_value = []
                response = self.request()
                self.assertEqual(
                    [name for name, _ in events(response.iter_lines())],
                    ["answer", "citations", "done"],
                )
                sdk.assert_not_called()

    def test_nonempty_unsupported_is_success(self) -> None:
        """Keep the grounded canonical fallback and empty citations on successful exhaustion."""
        self.provider.deltas = [FALLBACK]
        response = self.request()

        self.assertEqual(events(response.iter_lines()), [
            ("answer", {"text": FALLBACK}),
            ("citations", {"citations": []}),
            ("done", {"status": "completed"}),
        ])
        self.assertTrue(self.provider.closed)
        self.closers[0].assert_called_once_with()

    def test_postcommit_failures_are_one_safe_terminal_and_cleanup(self) -> None:
        """Preserve provisional deltas but never expose citations/done or raw error content."""
        for deltas, error, count in (
            ([], GenerationError(), 0),
            (["One", "Two"], RuntimeError("PRIVATE_SOURCE_SECRET"), 2),
            (["One", "[[cite:99]]"], None, 1),
            (["Uncited answer"], None, 1),
        ):
            with self.subTest(deltas=deltas):
                self.provider = Provider(deltas, error)
                self.constructor.return_value = self.provider
                response = self.request()

                self.assertEqual(response.status_code, 200)
                wire = events(response.iter_lines())
                self.assertEqual([name for name, _ in wire], [
                                 "answer"] * count + ["error"])
                self.assertEqual(
                    wire[-1],
                    ("error", {"error": "Generation failed.",
                     "code": "GENERATION_FAILED"}),
                )
                self.assertNotIn("PRIVATE_SOURCE_SECRET", response.text)
                self.assertNotIn("[[cite:", response.text)
                self.assertTrue(self.provider.closed)
                self.closers[-1].assert_called_once_with()
                with self.assertRaises(GenerationError):
                    _ = self.streams[-1].citations

    def test_unexpected_stream_exception_is_sanitized_in_wire_and_logs(self) -> None:
        """Protect the router's unexpected-error boundary without logging exception bodies."""
        with (
            patch(
                "app.pipeline.generation.grounded.GroundedStream.citations",
                new_callable=PropertyMock, side_effect=RuntimeError(
                    "PRIVATE_ERROR_CONTENT"),
            ),
            self.assertLogs("app.routers.files", level="ERROR") as logs,
        ):
            response = self.request()

        self.assertEqual(
            [name for name, _ in events(response.iter_lines())], [
                "answer"] * 3 + ["error"],
        )
        self.assertIn("type=RuntimeError", "".join(logs.output))
        self.assertNotIn("PRIVATE_ERROR_CONTENT",
                         "".join(logs.output) + response.text)
        self.closers[0].assert_called_once_with()

    def test_early_consumer_close_reaches_dependency_owner(self) -> None:
        """Closing a consumer releases resources through the request owner, without final citations."""
        owner = prepare(self.file, AskRequest(question="question"))
        stream = next(owner)
        consumer = ask(stream)

        self.assertEqual(next(consumer).event, "answer")
        consumer.close()
        owner.close()

        self.assertTrue(self.provider.closed)
        self.closers[0].assert_called_once_with()
        with self.assertRaises(GenerationError):
            _ = self.streams[0].citations

    def test_disconnect_closes_stream_and_runs_blocking_work_offloop(self) -> None:
        """Drive real ASGI disconnect after one event; teardown waits for sync iteration then closes."""
        self.provider.deltas = ["delta"] * 1000
        asyncio.run(self.disconnect())

        self.assertTrue(self.provider.closed)
        self.closers[0].assert_called_once_with()
        with self.assertRaises(GenerationError):
            _ = self.streams[0].citations

    def test_real_http_first_answer_arrives_before_provider_completion(self) -> None:
        """Gate generation on the HTTP client's receipt to prove actual incremental delivery."""
        received = Event()

        def generate():
            """Only release the remaining answer after the client receives the first event."""
            try:
                yield "first"

                if not received.wait(timeout=5):
                    raise RuntimeError("First event was buffered")

                yield "second[[cite:7]]"
            finally:
                self.provider.closed = True

        with patch.object(self.provider, "generate", side_effect=generate), serve(lifespan="off") as base:
            try:
                with (
                    httpx.Client(base_url=base, timeout=10, trust_env=False) as http,
                    http.stream(
                        "POST", f"/files/{self.file}/ask", json={"question": "question"},
                    ) as response,
                ):
                    lines = response.iter_lines()
                    first = []
                    for line in lines:
                        first.append(line)
                        if not line:
                            break

                    self.assertEqual(
                        events(first), [("answer", {"text": "first"})])
                    self.assertFalse(self.provider.closed)

                    received.set()
                    wire = events(lines)

                    self.assertEqual([name for name, _ in wire], [
                                     "answer", "citations", "done"])
            finally:
                received.set()

        self.assertTrue(self.provider.closed)
        self.closers[0].assert_called_once_with()

    def test_real_http_disconnect_closes_inflight_provider_without_second_error(self) -> None:
        """Close an actual socket while a worker awaits its next delta and verify quiet teardown."""
        release, closed = Event(), Event()

        def generate():
            """Keep one synchronous next call in flight until the client has disconnected."""
            try:
                yield "first"

                if not release.wait(timeout=5):
                    raise RuntimeError(
                        "Disconnect test did not release worker")

                yield from ["next"] * 1000
            finally:
                self.provider.closed = True
                closed.set()

        with (
            patch.object(self.provider, "generate", side_effect=generate),
            self.assertLogs("app", level="INFO") as logs,
            serve(lifespan="off") as base,
        ):
            try:
                with httpx.Client(base_url=base, timeout=10, trust_env=False) as http:
                    with http.stream(
                        "POST", f"/files/{self.file}/ask", json={"question": "question"},
                    ) as response:
                        first = []
                        for line in response.iter_lines():
                            first.append(line)
                            if not line:
                                break

                        self.assertEqual(
                            events(first), [("answer", {"text": "first"})],
                        )

                    release.set()
                    self.assertTrue(closed.wait(timeout=5))
            finally:
                release.set()

        self.assertNotIn("Unhandled exception", "".join(logs.output))
        self.assertNotIn("Ask stream category=", "".join(logs.output))
        self.closers[0].assert_called_once_with()
        with self.assertRaises(GenerationError):
            _ = self.streams[0].citations

    async def disconnect(self) -> None:
        """Use ASGI receive disconnect without relying on buffering TestClient behavior."""
        loop = get_ident()
        workers: list[int] = []
        started = False
        disconnected = asyncio.Event()
        body = json.dumps({"question": "question"}).encode()
        sent = False

        def search(*args):
            """Require retrieval to finish before response-start on a worker thread."""
            self.assertFalse(started)
            workers.append(get_ident())

            return self.chunks

        def generate(prompt, contexts):
            """Record provider iteration thread without replacing its real generator cleanup."""
            workers.append(get_ident())

            return self.provider.generate()

        async def receive():
            """Send one POST body, then wait until a response event triggers disconnect."""
            nonlocal sent
            if not sent:
                sent = True

                return {"type": "http.request", "body": body, "more_body": False}

            await disconnected.wait()

            return {"type": "http.disconnect"}

        async def send(message):
            """Disconnect once the first actual answer has crossed the response boundary."""
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
                self.assertEqual(message["status"], 200)
            elif b"event: answer" in message.get("body", b""):
                disconnected.set()

        scope = dict(
            type="http", asgi={"version": "3.0", "spec_version": "2.3"},
            http_version="1.1", method="POST", scheme="http", path=f"/files/{self.file}/ask",
            raw_path=f"/files/{self.file}/ask".encode(), query_string=b"", root_path="",
            headers=[(b"content-type", b"application/json")],
            client=("127.0.0.1", 1234), server=("127.0.0.1", 80),
        )

        with (
            patch("app.routers.files.retrieve", side_effect=search),
            patch.object(self.provider, "stream_generate",
                         side_effect=generate),
        ):
            await asyncio.wait_for(app(scope, receive, send), timeout=5)

        self.assertTrue(disconnected.is_set())
        self.assertEqual(len(workers), 2)
        self.assertTrue(all(thread != loop for thread in workers))


class AskIsolationTests(TestCase):
    def test_real_retrieval_excludes_competitive_foreign_source_and_preserves_query(self) -> None:
        """Use actual file-filtered Qdrant retrieval before real grounding through HTTP."""
        embedder = Embedder()
        client = QdrantClient(":memory:", force_disable_check_same_thread=True)
        file, other = uuid4(), uuid4()
        collection = constants.qdrant.QDRANT_COLLECTION

        with (
            patch("app.core.lifespan.get_bge_m3_embedder", return_value=embedder),
            patch("app.core.lifespan.create_client", return_value=client),
            patch("app.core.lifespan.prepare", return_value=database()),
            TestClient(app) as http,
        ):
            payloads = [
                Chunk(**source(7, file_id=file).model_dump(exclude={"score"})),
                Chunk(**source(
                    99, file_id=other, text="FOREIGN_SOURCE", display_text="FOREIGN_EXCERPT",
                ).model_dump(exclude={"score"})),
            ]
            store(client, collection, payloads, [
                [0.8, 0.6] + [0.0] * (embedder.dimension - 2),
                [1.0] + [0.0] * (embedder.dimension - 1),
            ])
            before = client.count(collection, exact=True).count

            provider = Provider(["Supported[[cite:7]]"])
            with (
                patch("app.routers.files.GeminiFlashProvider",
                      return_value=provider),
                patch("app.routers.files.retrieve", wraps=retrieve) as search,
                patch("app.routers.files.GroundedStream", wraps=GroundedStream) as factory,
            ):
                response = http.post(
                    f"/files/{file}/ask", json={"question": "question"},
                )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                [chunk.file_id for chunk in factory.call_args.args[2]], [file],
            )
            search.assert_called_once_with("question", file, 5)
            self.assertNotIn("FOREIGN", response.text)
            self.assertNotIn("FOREIGN", str(provider.calls))
            self.assertEqual(events(response.iter_lines())[1], ("citations", {"citations": [
                dict(
                    index=7, page=3, heading="Trusted heading",
                    section="Trusted section", excerpt="Raw source body",
                ),
            ]}))

            query = http.post(f"/files/{file}/query",
                              json={"question": "question"})
            self.assertEqual(set(query.json()["results"][0]), {
                "score", "text", "index", "count", "page", "heading", "section",
            })
            self.assertEqual(client.count(
                collection, exact=True).count, before)
