from typing import Protocol


class EmbeddingProvider(Protocol):
    """Define the provider contract used by the embedding pipeline."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one dense vector for each input text."""
        ...

    @property
    def dimension(self) -> int:
        """Return the width of each dense vector."""
        ...
