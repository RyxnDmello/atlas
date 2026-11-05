from httpx import Response
from uuid import UUID, uuid4
from time import perf_counter
from unittest import TestCase
from unittest.mock import patch
from contextlib import ExitStack
from fastapi.testclient import TestClient

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import ResponseHandlingException
from qdrant_client.http.models import Distance, UpdateResult, UpdateStatus, VectorParams

from app.core.runtime import storage
from app.core.constants import constants

from app.pipeline.chunking import chunk
from app.pipeline.extraction import extract

from app.db.qdrant import ensure_collection
from app.schemas.constants import QdrantConstants

from app.errors.api import ApiError

from app.main import app

from tests.postgres import database
from tests.uploads import environment


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
        self.database, self.user, self.headers = self.scope.enter_context(
            environment())
        self.scope.enter_context(
            patch("app.core.lifespan.prepare", return_value=self.database))

        self.provider = Provider()
        self.client = QdrantClient(
            ":memory:", force_disable_check_same_thread=True)

        self.constructor = self.scope.enter_context(
            patch("app.core.lifespan.get_bge_m3_embedder",
                  return_value=self.provider)
        )
        self.scope.enter_context(
            patch("app.core.lifespan.create_client", return_value=self.client))

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
            "/files", headers=self.headers, data={"name": "policy.md"}, files={"file": ("policy.md", self.content, "text/markdown")}
        )

    def test_payloads_match_chunks_and_preserve_both_texts(self) -> None:
        """Compare upload responses and stored payloads with freshly generated chunks."""
        expected = chunk(extract(self.content, ".md",
                         "policy.md"), str(uuid4()))

        file_id = uuid4()

        with patch("app.pipeline.upload.uuid4", return_value=file_id) as identifier:
            response = self.upload()

        identifier.assert_called_once_with()

        self.assertEqual(response.status_code, 201, response.text)

        body = response.json()

        self.assertEqual(set(body), {"id", "name", "description", "original_name",
                         "extension", "size_bytes", "status", "folder_id", "created_at", "updated_at"})
        total = len(expected)
        self.assertIsInstance(body["id"], str)
        self.assertEqual(UUID(body["id"]), file_id)
        self.assertEqual(body["name"], "policy.md")
        self.assertEqual(body["extension"], ".md")
        self.assertGreater(total, 1)
        self.assertEqual(self.client.count(
            self.collection, exact=True).count, total)

        points, cursor = self.client.scroll(
            self.collection, limit=total, with_vectors=True)

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

        for item, payload in zip(expected, payloads, strict=True):
            UUID(payload["file_id"])
            self.assertEqual(payload["file_id"], body["id"])
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

        self.assertTrue(
            any(payload["text"] != payload["display_text"] for payload in payloads))

    def test_repeated_uploads_are_independent_and_startup_precedes_embedding(self) -> None:
        """Require independent uploads to reuse the provider after startup readiness."""
        ready = storage().ready

        self.assertEqual(self.provider.calls, [])

        entered = perf_counter()
        first = self.upload()
        second = self.upload()

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.constructor.assert_called_once_with()
        self.assertLessEqual(self.provider.loaded, ready)
        self.assertLessEqual(ready, entered)
        self.assertTrue(all(entered <= call for call in self.provider.calls))
        self.assertIs(storage().provider, self.provider)

        total = 2 * \
            len(chunk(extract(self.content, ".md", "policy.md"), str(uuid4())))

        self.assertEqual(self.client.count(
            self.collection, exact=True).count, total)

        points, _ = self.client.scroll(self.collection, limit=total)
        identifiers = set()

        for point in points:
            assert isinstance(point.payload, dict)
            identifiers.add(point.payload["file_id"])

        self.assertEqual(len(identifiers), 2)
        self.assertNotEqual(first.json()["id"], second.json()["id"])
        self.assertEqual(identifiers, {first.json()[
                         "id"], second.json()["id"]})

        for response in (first, second):
            file_id = response.json()["id"]
            UUID(file_id)
            count = sum(point.payload["file_id"] == file_id for point in points
                        if isinstance(point.payload, dict))
            self.assertEqual(count, total // 2)

    def test_returned_ids_query_only_their_uploaded_chunks(self) -> None:
        """Use public upload IDs directly and verify distinct fixtures stay scoped."""
        responses = []

        for name, text in (("retention.md", "Keep records for seven years."),
                           ("support.md", "Acknowledge support requests within two days.")):
            response = self.http.post(
                "/files", headers=self.headers, data={"name": name}, files={"file": (name, text.encode(), "text/markdown")})
            self.assertEqual(response.status_code, 201, response.text)
            responses.append(response.json())

        self.assertNotEqual(responses[0]["id"], responses[1]["id"])

        total = self.client.count(self.collection, exact=True).count
        points, cursor = self.client.scroll(
            self.collection, limit=total, with_vectors=True)
        self.assertIsNone(cursor)
        before = sorted((point.model_dump(mode="json") for point in points),
                        key=lambda point: str(point["id"]))

        for body in responses:
            with self.subTest(file_id=body["id"]):
                response = self.http.post(
                    f"/files/{body['id']}/query", headers=self.headers, json={"question": "What is the policy?", "top_k": 20})
                self.assertEqual(response.status_code, 200, response.text)
                results = response.json()["results"]
                payloads = {}

                for point in points:
                    assert isinstance(point.payload, dict)

                    if point.payload["file_id"] == body["id"]:
                        payloads[point.payload["chunk_index"]] = point.payload

                self.assertEqual(len(results), len(payloads))

                for result in results:
                    payload = payloads[result["index"]]
                    self.assertEqual(payload["file_id"], body["id"])
                    self.assertEqual(result["text"], payload["text"])
                    self.assertEqual({key: value for key, value in result.items() if key != "score"},
                                     {"text": payload["text"], "index": payload["chunk_index"], "count": payload["token_count"], "page": payload["page"], "heading": payload["heading"], "section": payload["section"]})

        after, cursor = self.client.scroll(
            self.collection, limit=total, with_vectors=True)
        self.assertIsNone(cursor)
        self.assertEqual(self.client.count(
            self.collection, exact=True).count, total)
        self.assertEqual(sorted((point.model_dump(mode="json") for point in after),
                                key=lambda point: str(point["id"])), before)

    def test_embedding_failure_returns_error_without_writing(self) -> None:
        """Return an explicit embedding error without attempting a vector write."""
        with (
            patch.object(self.provider, "embed",
                         side_effect=RuntimeError("injected")),
            patch.object(self.client, "upsert") as writer,
        ):
            response = self.upload()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "INTERNAL_SERVER_ERROR")
        self.assertEqual(set(response.json()), {"error", "code"})
        writer.assert_not_called()
        self.assertEqual(self.client.count(
            self.collection, exact=True).count, 0)

    def test_transport_failure_returns_qdrant_connection_error(self) -> None:
        """Map a failed Qdrant transport to the structured connection error."""
        failure = ResponseHandlingException(ConnectionError("injected"))

        with patch.object(self.client, "upsert", side_effect=failure):
            response = self.upload()

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["code"], "QDRANT_CONNECTION_FAILED")
        self.assertEqual(set(response.json()), {"error", "code"})
        self.assertEqual(self.client.count(
            self.collection, exact=True).count, 0)

    def test_write_failure_returns_qdrant_collection_error(self) -> None:
        """Map a failed vector write to the structured collection error."""
        with patch.object(self.client, "upsert", side_effect=ValueError("injected")):
            response = self.upload()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "QDRANT_COLLECTION_ERROR")
        self.assertEqual(set(response.json()), {"error", "code"})

    def test_unconfirmed_write_is_not_success(self) -> None:
        """Reject an unconfirmed write and require synchronous completion."""
        result = UpdateResult(operation_id=0, status=UpdateStatus.ACKNOWLEDGED)

        with patch.object(self.client, "upsert", return_value=result) as writer:
            response = self.upload()

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "QDRANT_COLLECTION_ERROR")
        self.assertEqual(set(response.json()), {"error", "code"})
        self.assertTrue(writer.call_args.kwargs["wait"])

    def test_partial_write_compensation_preserves_another_ready_file(self) -> None:
        """Delete real partial writes by canonical UUID while retaining an earlier upload."""
        first = self.upload()
        self.assertEqual(first.status_code, 201)
        before, _ = self.client.scroll(
            self.collection, limit=100, with_vectors=True)
        fingerprint = sorted((point.model_dump(mode="json")
                             for point in before), key=lambda point: str(point["id"]))
        write = self.client.upsert

        def partial(*args, **kwargs):
            write(*args, **kwargs)
            raise ConnectionError("injected after write")

        with patch.object(self.client, "upsert", side_effect=partial):
            response = self.upload()
        self.assertEqual(response.status_code, 503)
        after, _ = self.client.scroll(
            self.collection, limit=100, with_vectors=True)
        self.assertEqual(sorted((point.model_dump(mode="json")
                         for point in after), key=lambda point: str(point["id"])), fingerprint)

    def test_live_acceptance_helper_with_isolated_local_stores(self) -> None:
        """Validate the prepared HTTP helper without claiming real PostgreSQL acceptance."""
        from hashlib import sha256
        from sqlalchemy import select
        from app.models.postgres import Base
        from tests.uploads_acceptance import acceptance

        def fingerprint():
            digest = sha256()
            with self.database.engine.connect() as connection:
                for table in Base.metadata.sorted_tables:
                    digest.update(repr(connection.execute(
                        select(table).order_by(table.c.id)).all()).encode())
            return digest.hexdigest()

        before = fingerprint()
        result = acceptance(self.database, self.http, storage(), [])
        self.assertEqual(result["upload_http"], "passed")
        self.assertEqual(fingerprint(), before)
        self.assertEqual(self.client.count(
            self.collection, exact=True).count, 0)

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

    def setUp(self) -> None:
        """Isolate existing Qdrant lifecycle tests from external PostgreSQL."""
        scope = patch("app.core.lifespan.prepare", return_value=database())
        scope.start()
        self.addCleanup(scope.stop)

    def test_unreachable_qdrant_aborts_startup_and_closes_client(self) -> None:
        """Abort startup and close the client when Qdrant cannot be reached."""
        client = QdrantClient(":memory:", force_disable_check_same_thread=True)

        with (
            patch("app.core.lifespan.get_bge_m3_embedder",
                  return_value=Provider()),
            patch("app.core.lifespan.create_client", return_value=client),
            patch.object(client, "collection_exists",
                         side_effect=ConnectionError("injected")),
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
            patch("app.core.lifespan.get_bge_m3_embedder",
                  side_effect=RuntimeError("injected")),
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
            patch("app.core.lifespan.get_bge_m3_embedder",
                  return_value=Provider()),
            patch("app.core.lifespan.create_client", return_value=client),
            patch.object(client, "close", wraps=client.close) as closer,
        ):
            with TestClient(app):
                self.assertIs(storage().client, client)

                ensure_collection(
                    client, constants.qdrant.QDRANT_COLLECTION, storage().provider)

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
            patch("app.core.lifespan.get_bge_m3_embedder",
                  return_value=Provider()),
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
        }

        config = QdrantConstants.model_validate(values)

        self.assertTrue(config.QDRANT_COLLECTION)
        self.assertGreater(config.QDRANT_CLIENT_TIMEOUT, 0)

        for name, value in (("QDRANT_COLLECTION", ""), ("QDRANT_CLIENT_TIMEOUT", 0)):
            with self.subTest(name=name), self.assertRaises(ValueError):
                QdrantConstants.model_validate({**values, name: value})
