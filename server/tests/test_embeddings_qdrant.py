import logging
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance

from app.core.constants import constants
from app.db.qdrant import ensure_collection
from app.pipeline.embeddings.bge_m3 import (
    BGEM3Embedder,
    get_bge_m3_embedder,
)


class FakeProvider:
    """Provide deterministic vectors for collection-only tests."""

    @property
    def dimension(self) -> int:
        """Return the configured embedding dimension."""
        return constants.embedding.EMBEDDING_DIMENSION

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one deterministic vector for each test input."""
        return [[0.0] * self.dimension for _ in texts]


class EmbeddingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.embedder = BGEM3Embedder()
        first_start = time.perf_counter()
        cls.first = cls.embedder.embed(["Atlas stores semantic policy knowledge."])
        cls.first_latency = time.perf_counter() - first_start
        second_start = time.perf_counter()
        cls.second = cls.embedder.embed(["Atlas retrieves semantic policy knowledge."])
        cls.second_latency = time.perf_counter() - second_start
        logging.getLogger(__name__).info(
            "BGE-M3 embedding latency first=%.3fs subsequent=%.3fs",
            cls.first_latency,
            cls.second_latency,
        )

    def test_embed_returns_configured_dimensional_vectors(self) -> None:
        self.assertEqual(
            self.embedder.dimension,
            constants.embedding.EMBEDDING_DIMENSION,
        )
        self.assertEqual(len(self.first), 1)
        self.assertEqual(
            len(self.first[0]),
            constants.embedding.EMBEDDING_DIMENSION,
        )
        self.assertTrue(all(isinstance(value, float) for value in self.first[0]))

    def test_sequential_embedding_reuses_loaded_model(self) -> None:
        self.assertIsNotNone(self.embedder._model)
        self.assertEqual(len(self.second), 1)

    def test_cached_accessor_constructs_model_once(self) -> None:
        class FakeModel:
            def encode(self, texts, **kwargs):
                return {
                    constants.embedding.EMBEDDING_DENSE_KEY: [
                        [0.0] * constants.embedding.EMBEDDING_DIMENSION for _ in texts
                    ]
                }

        fake_model = FakeModel()
        get_bge_m3_embedder.cache_clear()
        with patch(
            "app.pipeline.embeddings.bge_m3.BGEM3FlagModel",
            return_value=fake_model,
        ) as constructor:
            first = get_bge_m3_embedder()
            second = get_bge_m3_embedder()

        self.assertIs(first, second)
        self.assertIs(first._model, fake_model)
        first.embed(["first"])
        second.embed(["second"])
        constructor.assert_called_once_with(
            constants.embedding.EMBEDDING_MODEL,
            use_fp16=constants.embedding.EMBEDDING_USE_FP16,
        )
        get_bge_m3_embedder.cache_clear()


class QdrantCollectionTests(unittest.TestCase):
    def test_collection_creation_is_idempotent_and_configured(self) -> None:
        client = QdrantClient(":memory:")
        provider = FakeProvider()

        ensure_collection(client, "atlas-test", provider)
        ensure_collection(client, "atlas-test", provider)

        info = client.get_collection("atlas-test")
        vectors = info.config.params.vectors
        self.assertEqual(vectors.size, constants.embedding.EMBEDDING_DIMENSION)
        self.assertEqual(vectors.distance, Distance(constants.qdrant.QDRANT_DISTANCE))


if __name__ == "__main__":
    unittest.main()
