from functools import lru_cache
from typing import Any

from FlagEmbedding import BGEM3FlagModel

from app.core.constants import constants


class BGEM3Embedder:
    """Generate dense BGE-M3 embeddings through FlagEmbedding."""

    def __init__(self, model: Any | None = None) -> None:
        """Load or accept the BGE-M3 model used for dense embeddings.

        Args:
            model: An optional compatible model instance for isolated tests.
        """
        self._model = (
            model
            if model is not None
            else BGEM3FlagModel(
                constants.embedding.EMBEDDING_MODEL,
                use_fp16=constants.embedding.EMBEDDING_USE_FP16,
            )
        )

    @property
    def dimension(self) -> int:
        """Return BGE-M3's dense vector dimension."""
        return constants.embedding.EMBEDDING_DIMENSION

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Encode texts as dense-only BGE-M3 vectors.

        Args:
            texts: Text values to encode in one batch.

        Returns:
            One configured-dimension dense vector per input text.

        Raises:
            ValueError: If the model returns an unexpected number or size of
                vectors.
        """
        if not texts:
            return []

        output = self._model.encode(
            texts,
            return_dense=constants.embedding.EMBEDDING_RETURN_DENSE,
            return_sparse=constants.embedding.EMBEDDING_RETURN_SPARSE,
            return_colbert_vecs=constants.embedding.EMBEDDING_RETURN_COLBERT_VECS,
        )
        dense = output[constants.embedding.EMBEDDING_DENSE_KEY]

        if len(dense) != len(texts):
            raise ValueError(
                "BGE-M3 returned a vector count different from the input")

        vectors = [self._to_vector(vector) for vector in dense]
        if any(len(vector) != self.dimension for vector in vectors):
            raise ValueError(
                "BGE-M3 returned a vector with an unexpected dimension")

        return vectors

    @staticmethod
    def _to_vector(vector: Any) -> list[float]:
        """Convert a model tensor or array row into plain Python floats."""
        values = vector.tolist() if hasattr(vector, "tolist") else vector
        return [float(value) for value in values]


@lru_cache(maxsize=1)
def get_bge_m3_embedder() -> BGEM3Embedder:
    """Return the process-wide BGE-M3 embedder singleton."""
    return BGEM3Embedder()
