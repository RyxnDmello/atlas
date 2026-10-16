from app.schemas.generation import Citation
from app.schemas.retrieval import RetrievedChunk

from app.errors.generation import GenerationError


PREFIX = "[[cite:"


class CitationParser:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        """Snapshot trusted provenance, rejecting ambiguous or mixed-file inputs."""
        self.sources: dict[int, Citation] = {}
        files = {chunk.file_id for chunk in chunks}
        if len(files) > 1:
            raise GenerationError()

        for chunk in chunks:
            if chunk.chunk_index in self.sources:
                raise GenerationError()

            self.sources[chunk.chunk_index] = Citation(
                index=chunk.chunk_index, page=chunk.page, heading=chunk.heading,
                section=chunk.section, excerpt=chunk.display_text,
            )

        self.limit = max(self.sources, default=-1) + 1
        self.pending = ""
        self.state = "text"
        self.number = 0
        self.digits = False
        self.indexes: dict[int, None] = {}
        self.finished = False
        self.failed = False

    def feed(self, text: str) -> str:
        """Remove reserved markers with constant suffix/numeric state across arbitrary deltas."""
        if self.finished or self.failed:
            raise GenerationError()

        output: list[str] = []
        for character in text:
            if self.state == "text":
                self.pending += character
                while self.pending and not PREFIX.startswith(self.pending):
                    output.append(self.pending[0])
                    self.pending = self.pending[1:]

                if self.pending == PREFIX:
                    self.pending = ""
                    self.state = "digits"
                    self.number = 0
                    self.digits = False
            elif self.state == "digits":
                if "0" <= character <= "9":
                    self.digits = True
                    self.number = min(self.limit, self.number *
                                      10 + ord(character) - ord("0"))
                elif character == "]" and self.digits:
                    self.state = "closing"
                else:
                    self.failed = True
                    raise GenerationError()
            elif character == "]" and self.number in self.sources:
                self.indexes[self.number] = None
                self.state = "text"
            else:
                self.failed = True
                raise GenerationError()

        return "".join(output)

    def finish(self) -> str:
        """Reject unfinished reserved markers; release a literal non-reserved suffix."""
        if self.finished or self.failed or self.state != "text":
            self.failed = True
            raise GenerationError()

        self.finished = True
        tail = self.pending
        self.pending = ""

        return tail

    @property
    def citations(self) -> list[Citation]:
        """Expose trusted provenance in first-reference order only after parser completion."""
        if not self.finished or self.failed:
            raise GenerationError()

        return [self.sources[index] for index in self.indexes]
