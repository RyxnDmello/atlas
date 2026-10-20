from time import perf_counter
from collections.abc import Generator, Iterator

from app.core.logging import get_logger

from app.pipeline.generation.provider import LLMProvider
from app.pipeline.generation.prompt import FALLBACK, build
from app.pipeline.generation.citations import CitationParser

from app.schemas.generation import Citation
from app.schemas.retrieval import RetrievedChunk

from app.errors.generation import GenerationError

logger = get_logger(__name__)


class GroundedStream(Iterator[str]):
    def __init__(self, provider: LLMProvider, question: str, chunks: list[RetrievedChunk]) -> None:
        """Snapshot one file's inputs; yielded text is provisional until successful exhaustion.

        Consume once and close on early exit. Citations become available only after
        exhaustion; any later failure invalidates all previously yielded text.
        """
        if not question.strip():
            raise GenerationError()

        self.provider = provider
        self.question = question
        self.chunks = [chunk.model_copy(deep=True) for chunk in chunks]
        self.parser = CitationParser(self.chunks)
        self._citations: list[Citation] | None = None
        self.iterator = self._run()

    def __iter__(self) -> "GroundedStream":
        """Return this single-use stream."""
        return self

    def __next__(self) -> str:
        """Yield the next clean provisional delta or propagate a sanitized failure."""
        return next(self.iterator)

    def close(self) -> None:
        """Release provider resources on early exit without promoting partial output to success."""
        self.iterator.close()

    @property
    def citations(self) -> list[Citation]:
        """Return final trusted citations only after successful stream exhaustion."""
        if self._citations is None:
            raise GenerationError()

        return list(self._citations)

    def _run(self) -> Generator[str, None, None]:
        """Coordinate prompt, provider, parser, semantic validation, and owned iterator cleanup."""
        started = perf_counter()
        category = "failed"
        citations: list[Citation] = []
        try:
            if not self.chunks:
                yield FALLBACK
            else:
                prompt, contexts = build(self.question, self.chunks)
                stream = self.provider.stream_generate(prompt, contexts)
                position = 0
                matches = True
                substantive = False
                try:
                    for delta in stream:
                        clean = self.parser.feed(delta)
                        if clean:
                            substantive = substantive or bool(clean.strip())
                            matches = matches and clean == FALLBACK[position:position + len(
                                clean)]
                            position += len(clean)

                            yield clean

                    tail = self.parser.finish()
                    if tail:
                        substantive = substantive or bool(tail.strip())
                        matches = matches and tail == FALLBACK[position:position + len(
                            tail)]
                        position += len(tail)

                        yield tail

                    citations = self.parser.citations
                    fallback = matches and position == len(FALLBACK)
                    if not substantive or (fallback and citations) or (not fallback and not citations):
                        raise GenerationError()
                finally:
                    close = getattr(stream, "close", None)
                    if close is not None:
                        close()

            self._citations = citations
            category = "completed"
        except GeneratorExit:
            category = "cancelled"
            raise
        except GenerationError:
            raise
        except Exception:
            raise GenerationError() from None
        finally:
            logger.info(
                "Grounded generation category=%s sources=%d citations=%d indexes=%s elapsed=%.3fs",
                category, len(self.chunks), len(citations),
                [citation.index for citation in citations], perf_counter() -
                started,
            )
