from contextlib import ExitStack
from time import perf_counter
from unittest import TestCase
from unittest.mock import patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from httpx import Response
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.http.models import Distance, UpdateResult, UpdateStatus, VectorParams

from app.core.constants import constants
from app.core.runtime import storage

from app.db.qdrant import ensure_collection

from app.pipeline.chunking import chunk
from app.pipeline.extraction import extract

from app.schemas.constants import QdrantConstants

from app.errors.api import ApiError

from app.main import app


class Provider:
    """Record timing and input text while providing deterministic test vectors."""

    def __init__(self) -> None:
        """Record when the test provider becomes ready."""
        self.loaded = perf_counter()
        self.calls: list[float] = []
        self.texts: list[str] = []

    @property
    def dimension(self) -> int:
        """Return the active dense dimension."""
        return constants.embedding.EMBEDDING_DIMENSION

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Record the encode boundary and return one vector per input."""
        self.calls.append(perf_counter())
        self.texts = texts
        return [[1.0] + [0.0] * (self.dimension - 1) for _ in texts]


class UploadStorageTests(TestCase):
    """Exercise real multipart parsing/chunking with initialized local storage."""

    def setUp(self) -> None:
        """Prepare an injected provider, in-memory Qdrant, and a real upload client."""
        self.scope = ExitStack()
        self.addCleanup(self.scope.close)
        self.provider = Provider()
        self.client = QdrantClient(":memory:", force_disable_check_same_thread=True)
        self.constructor = self.scope.enter_context(
            patch("app.core.lifespan.get_bge_m3_embedder", return_value=self.provider)
        )
        self.scope.enter_context(patch("app.core.lifespan.create_client", return_value=self.client))
        self.http = self.scope.enter_context(TestClient(app))
        self.collection = constants.qdrant.QDRANT_COLLECTION
        self.content = (
            "# Atlas Policy\n\n## Retention\n\n"
            + "Keep records for seven years. " * 150
            + "\n\n## Review\n\nReview access every month."
        ).encode()

    def upload(self) -> Response:
        """Upload the same realistic Markdown fixture through HTTP."""
        return self.http.post(
            "/documents/upload", files={"file": ("policy.md", self.content, "text/markdown")}
        )

    def test_payloads_match_chunks_and_preserve_both_texts(self) -> None:
        """Compare upload responses and stored payloads with freshly generated chunks."""
        expected = chunk(extract(self.content, ".md", "policy.md"), str(uuid4()))
        response = self.upload()
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(set(body), {"name", "type", "total", "chunks"})
        self.assertEqual(body["name"], "policy.md")
        self.assertEqual(body["type"], ".md")
        self.assertGreater(body["total"], 1)
        self.assertEqual(body["total"], len(expected))
        self.assertEqual(self.client.count(self.collection, exact=True).count, body["total"])
        points, cursor = self.client.scroll(self.collection, limit=body["total"], with_vectors=True)
        self.assertIsNone(cursor)
        payloads = []
        for point in points:
            UUID(str(point.id))
            assert isinstance(point.vector, list)
            self.assertEqual(len(point.vector), self.provider.dimension)
            assert isinstance(point.payload, dict)
            payloads.append(point.payload)
        payloads.sort(key=lambda payload: payload["chunk_index"])
        self.assertEqual(len({payload["file_id"] for payload in payloads}), 1)
        self.assertEqual(self.provider.texts, [item.text for item in expected])
        for item, payload, returned in zip(expected, payloads, body["chunks"], strict=True):
            UUID(payload["file_id"])
            self.assertEqual(
                set(payload),
                {
                    "file_id", "chunk_index", "token_count", "page", "heading",
                    "section", "text", "display_text",
                },
            )
            self.assertEqual(payload["chunk_index"], item.index)
            self.assertEqual(payload["token_count"], item.count)
            self.assertEqual(payload["page"], item.page)
            self.assertEqual(payload["heading"], item.heading)
            self.assertEqual(payload["section"], item.section)
            self.assertEqual(payload["text"], item.text)
            self.assertEqual(payload["display_text"], item.display_text)
            self.assertEqual(
                returned,
                {
                    "text": item.text, "index": item.index, "count": item.count,
                    "page": item.page, "heading": item.heading, "section": item.section,
                },
            )
        self.assertTrue(any(payload["text"] != payload["display_text"] for payload in payloads))

    def test_repeated_uploads_are_independent_and_startup_precedes_embedding(self) -> None:
        """Require independent uploads to reuse the provider after startup readiness."""
        ready = storage().ready
        self.assertEqual(self.provider.calls, [])
        entered = perf_counter()
        first = self.upload()
        second = self.upload()
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.constructor.assert_called_once_with()
        self.assertLessEqual(self.provider.loaded, ready)
        self.assertLessEqual(ready, entered)
        self.assertTrue(all(entered <= call for call in self.provider.calls))
        self.assertIs(storage().provider, self.provider)
        total = first.json()["total"] + second.json()["total"]
        self.assertEqual(self.client.count(self.collection, exact=True).count, total)
        points, _ = self.client.scroll(self.collection, limit=total)
        identifiers = set()
        for point in points:
            assert isinstance(point.payload, dict)
            identifiers.add(point.payload["file_id"])
        self.assertEqual(len(identifiers), 2)

    def test_embedding_failure_returns_error_without_writing(self) -> None:
        """Return an explicit embedding error without attempting a vector write."""
        with (
            patch.object(self.provider, "embed", side_effect=RuntimeError("injected")),
            patch.object(self.client, "upsert") as writer,
        ):
            response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "INTERNAL_SERVER_ERROR")
        self.assertEqual(set(response.json()), {"error", "code"})
        writer.assert_not_called()
        self.assertEqual(self.client.count(self.collection, exact=True).count, 0)

    def test_transport_failure_returns_qdrant_connection_error(self) -> None:
        """Map a failed Qdrant transport to the structured connection error."""
        failure = ResponseHandlingException(ConnectionError("injected"))
        with patch.object(self.client, "upsert", side_effect=failure):
            response = self.upload()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["code"], "QDRANT_CONNECTION_FAILED")
        self.assertEqual(set(response.json()), {"error", "code"})
        self.assertEqual(self.client.count(self.collection, exact=True).count, 0)

    def test_write_failure_returns_qdrant_collection_error(self) -> None:
        """Map a failed vector write to the structured collection error."""
        with patch.object(self.client, "upsert", side_effect=ValueError("injected")):
            response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "QDRANT_COLLECTION_ERROR")

    def test_unconfirmed_write_is_not_success(self) -> None:
        """Reject an unconfirmed write and require synchronous completion."""
        result = UpdateResult(operation_id=0, status=UpdateStatus.ACKNOWLEDGED)
        with patch.object(self.client, "upsert", return_value=result) as writer:
            response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "QDRANT_COLLECTION_ERROR")
        self.assertTrue(writer.call_args.kwargs["wait"])

    def test_invalid_embeddings_do_not_reach_storage(self) -> None:
        """Reject missing or incorrectly sized vectors before storage."""
        for vectors in ([], [[1.0]]):
            with (
                self.subTest(vectors=vectors),
                patch.object(self.provider, "embed", return_value=vectors),
                patch.object(self.client, "upsert") as writer,
            ):
                response = self.upload()
                self.assertEqual(response.status_code, 500)
                writer.assert_not_called()


class StartupTests(TestCase):
    """Verify startup failure, shutdown cleanup, and idempotent restart."""

    def test_unreachable_qdrant_aborts_startup_and_closes_client(self) -> None:
        """Abort startup and close the client when Qdrant cannot be reached."""
        client = QdrantClient(":memory:", force_disable_check_same_thread=True)
        with (
            patch("app.core.lifespan.get_bge_m3_embedder", return_value=Provider()),
            patch("app.core.lifespan.create_client", return_value=client),
            patch.object(client, "collection_exists", side_effect=ConnectionError("injected")),
            patch.object(client, "close", wraps=client.close) as closer,
        ):
            with self.assertRaises(ApiError) as caught:
                with TestClient(app):
                    self.fail("Failed startup must not accept requests")
            self.assertEqual(caught.exception.code, "QDRANT_CONNECTION_FAILED")
            closer.assert_called_once()

    def test_model_failure_aborts_before_client_creation(self) -> None:
        """Abort startup before constructing Qdrant when model loading fails."""
        with (
            patch("app.core.lifespan.get_bge_m3_embedder", side_effect=RuntimeError("injected")),
            patch("app.core.lifespan.create_client") as factory,
        ):
            with self.assertRaises(RuntimeError):
                with TestClient(app):
                    self.fail("Failed startup must not accept requests")
            factory.assert_not_called()

    def test_lifespan_restores_readiness_and_closes_client(self) -> None:
        """Restore the prior runtime state and close the lifespan-owned client."""
        try:
            previous = storage()
        except ApiError:
            previous = None
        client = QdrantClient(":memory:", force_disable_check_same_thread=True)
        with (
            patch("app.core.lifespan.get_bge_m3_embedder", return_value=Provider()),
            patch("app.core.lifespan.create_client", return_value=client),
            patch.object(client, "close", wraps=client.close) as closer,
        ):
            with TestClient(app):
                self.assertIs(storage().client, client)
                ensure_collection(client, constants.qdrant.QDRANT_COLLECTION, storage().provider)
            closer.assert_called_once()
        if previous is None:
            with self.assertRaises(ApiError):
                storage()
        else:
            self.assertIs(storage(), previous)

    def test_wrong_collection_dimension_aborts_startup(self) -> None:
        """Reject an existing collection with an incompatible vector dimension."""
        client = QdrantClient(":memory:", force_disable_check_same_thread=True)
        client.create_collection(
            constants.qdrant.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=1, distance=Distance(constants.qdrant.QDRANT_DISTANCE)
            ),
        )
        with (
            patch("app.core.lifespan.get_bge_m3_embedder", return_value=Provider()),
            patch("app.core.lifespan.create_client", return_value=client),
        ):
            with self.assertRaises(ApiError) as caught:
                with TestClient(app):
                    self.fail("Incompatible vectors must abort startup")
            self.assertEqual(caught.exception.code, "QDRANT_COLLECTION_ERROR")

    def test_optional_configuration_defaults_are_validated(self) -> None:
        """Verify optional collection defaults and reject invalid overrides."""
        values = {
            "QDRANT_URL": "http://localhost:6333",
            "QDRANT_HEALTHCHECK_RETRIES": 1,
            "QDRANT_HEALTHCHECK_TIMEOUT": 1,
            "QDRANT_HEALTHCHECK_INTERVAL": 1,
            "QDRANT_HEALTHCHECK_START_PERIOD": 0,
        }
        config = QdrantConstants.model_validate(values)
        self.assertTrue(config.QDRANT_COLLECTION)
        self.assertGreater(config.QDRANT_CLIENT_TIMEOUT, 0)
        for name, value in (("QDRANT_COLLECTION", ""), ("QDRANT_CLIENT_TIMEOUT", 0)):
            with self.subTest(name=name), self.assertRaises(ValueError):
                QdrantConstants.model_validate({**values, name: value})
