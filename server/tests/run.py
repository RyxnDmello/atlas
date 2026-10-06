import sys
import unittest
from time import perf_counter
from unittest.mock import patch

from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

from app.core.runtime import storage

from app.pipeline.embeddings.bge_m3 import get_bge_m3_embedder

from app.main import app


def run() -> bool:
    """Run unchanged upload tests inside a real-model, in-memory lifespan."""
    client = QdrantClient(":memory:", force_disable_check_same_thread=True)
    started = perf_counter()
    with patch("app.core.lifespan.create_client", return_value=client), patch(
        "app.core.lifespan.get_bge_m3_embedder", wraps=get_bge_m3_embedder
    ) as constructor:
        with TestClient(app) as http:
            startup = perf_counter() - started
            services = storage()
            provider = services.provider
            calls: list[float] = []
            encode = provider.embed

            def embed(texts: list[str]) -> list[list[float]]:
                """Record first-request timing while exercising the real provider."""
                calls.append(perf_counter())
                return encode(texts)

            with patch.object(provider, "embed", side_effect=embed):
                for index in range(2):
                    before = client.count(services.collection, exact=True).count
                    entered = perf_counter()
                    response = http.post(
                        "/documents/upload",
                        files={
                            "file": (
                                "policy.md",
                                b"# Atlas Policy\n\nKeep records for seven years.",
                                "text/markdown",
                            ),
                        },
                    )
                    elapsed = perf_counter() - entered
                    assert response.status_code == 200, response.text
                    total = response.json()["total"]
                    assert client.count(services.collection, exact=True).count == before + total
                    assert services.ready <= entered <= calls[-1]
                    print(
                        f"Real upload {index + 1}: startup={startup:.3f}s upload={elapsed:.3f}s "
                        f"ready_before_embed={calls[-1] - services.ready:.3f}s points={total}",
                        file=sys.stderr,
                    )
            constructor.assert_called_once_with()
            assert services.provider is provider
            suite = unittest.defaultTestLoader.discover("tests")
            result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
