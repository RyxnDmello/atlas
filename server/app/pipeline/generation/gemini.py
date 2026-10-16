import logging
from time import perf_counter
from collections.abc import Iterator

from google import genai
from google.genai import types
from google.genai.interactions import Interaction

from app.core.logging import get_logger
from app.core.constants import constants

from app.errors.generation import GenerationError

logger = get_logger(__name__)


class GeminiFlashProvider:
    """Stream stateless Gemini answer text with per-call resource ownership."""

    def __init__(self) -> None:
        """Require validated generation configuration without opening a connection."""
        self.config = constants.gemini

    def stream_generate(self, prompt: str, context_chunks: list[str]) -> Iterator[str]:
        """Join context then prompt, yield answer deltas, and require successful completion.

        Consumers stopping early must close this iterator to release its resources.
        Previously yielded text remains provisional until iteration finishes successfully.
        SDK 2.31 normalizes zero attempts to one at client construction; reset the
        shared public retry options before the lazy Interactions adapter reads them.
        """
        if not prompt.strip():
            raise ValueError("Generation prompt must be nonblank")

        started = perf_counter()
        count = size = 0
        answered = completed = False
        category = "provider"
        usage = None
        steps: dict[int, str] = {}
        retry = types.HttpRetryOptions(attempts=0)
        logging.getLogger("google.genai").setLevel(logging.WARNING)

        try:
            with genai.Client(
                api_key=self.config.GEMINI_API_KEY.get_secret_value(),
                vertexai=False,
                http_options=types.HttpOptions(retry_options=retry),
            ) as client:
                retry.attempts = 0

                response = client.interactions.create(
                    model=self.config.GEMINI_MODEL,
                    input="\n\n".join([*context_chunks, prompt]),
                    stream=True,
                    store=False,
                    generation_config={
                        "max_output_tokens": self.config.GEMINI_MAX_OUTPUT_TOKENS},
                )
                if isinstance(response, Interaction):
                    raise GenerationError()

                with response as stream:
                    for event in stream:
                        if event.event_type == "error":
                            category = "stream_error"
                            raise GenerationError()

                        if event.event_type == "step.start":
                            steps[event.index] = event.step.type
                        elif event.event_type == "step.stop":
                            steps.pop(event.index, None)
                        elif event.event_type == "step.delta":
                            if steps.get(event.index) == "model_output" and event.delta.type == "text":
                                text = event.delta.text
                                if text:
                                    count += 1
                                    size += len(text)
                                    answered = answered or bool(text.strip())

                                    yield text
                        elif event.event_type == "interaction.completed":
                            usage = event.interaction.usage
                            if event.interaction.status != "completed":
                                category = "incomplete"
                                raise GenerationError()

                            completed = True
                            break

            if not completed or not answered:
                category = "missing_completion" if not completed else "empty_output"
                raise GenerationError()

            category = "completed"
        except GeneratorExit:
            category = "cancelled"
            raise
        except Exception:
            raise GenerationError() from None
        finally:
            logger.info(
                "Generation model=%s category=%s elapsed=%.3fs deltas=%d characters=%d "
                "input_tokens=%s output_tokens=%s thought_tokens=%s total_tokens=%s",
                self.config.GEMINI_MODEL, category, perf_counter() - started, count, size,
                getattr(usage, "total_input_tokens", None),
                getattr(usage, "total_output_tokens", None),
                getattr(usage, "total_thought_tokens", None),
                getattr(usage, "total_tokens", None),
            )
