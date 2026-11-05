"""Deterministic canonical upload checks; no configured datastore or model is mutated."""
import io
import unittest
from uuid import UUID, uuid4
from collections.abc import Iterator
from pydantic import ValidationError
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch
from contextlib import ExitStack, closing, contextmanager
from starlette.datastructures import UploadFile as Uploaded

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, UpdateResult, UpdateStatus, VectorParams

from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.qdrant import remove
from app.routers.uploads import router

from app.pipeline.upload import ready
from app.pipeline.storage import Storage

from app.schemas.drive.upload import FileUpload
from app.models.postgres import File, Folder, User

from app.errors.api import ApiError
from app.errors.handlers import cast_handle_api_error

from tests.uploads import environment


class UploadValidationTests(unittest.TestCase):
    """Check the exact metadata alphabet independently of HTTP multipart encoding."""

    def form(self, **values):
        return FileUpload(file=UploadFile(filename="source.md", file=io.BytesIO(b"source")), **values)

    def test_name_boundaries_and_normalization(self):
        for name in ("a", "a" * 100, "Résumé 中文 ١²Ⅳ", "_-.,()[]&+@'", "  Good name  "):
            with self.subTest(name=name):
                self.assertEqual(self.form(name=name).name, name.strip())
        for name in ("", "   ", "a" * 101, "a/b", "a\\b", "a:b", "a*b", "a?b", 'a"b',
                     "a<b", "a>b", "a|b", "a\tb", "a\nb", "a\rb", "a\x00b", "a\x7fb",
                     "a😀b", "a$b", "a#b", "a\u00a0b", "e\u0301", "a\u200bb"):
            with self.subTest(name=repr(name)), self.assertRaises(ValidationError):
                self.form(name=name)
        with self.assertRaises(ValidationError):
            self.form()

    def test_description(self):
        for value, expected in ((None, None), ("", None), (" \t\n ", None), ("  detail  ", "detail"),
                                ("a" * 250, "a" * 250), ("中文😀 /:?!\nnotes", "中文😀 /:?!\nnotes")):
            self.assertEqual(
                self.form(name="valid", description=value).description, expected)
        self.assertIsNone(self.form(name="valid").description)
        with self.assertRaises(ValidationError):
            self.form(name="valid", description="a" * 251)


class UploadLifecycleTests(unittest.TestCase):
    """Exercise actual auth, multipart parsing, SQL predicates and independent transactions."""

    def setUp(self):
        self.scope = ExitStack()
        self.addCleanup(self.scope.close)
        self.database, self.user, self.headers = self.scope.enter_context(
            environment())
        self.depth = 0
        original = self.database.session

        @contextmanager
        def operation() -> Iterator[Session]:
            self.depth += 1
            try:
                with original() as value:
                    yield value
            finally:
                self.depth -= 1

        self.scope.enter_context(patch.object(
            self.database, "session", side_effect=operation))
        self.storage = Mock(spec=Storage)
        self.scope.enter_context(
            patch("app.pipeline.upload.storage", return_value=self.storage))
        self.ingest = self.scope.enter_context(
            patch("app.pipeline.upload.ingest", side_effect=self.index))
        app = FastAPI()
        app.include_router(router)
        app.add_exception_handler(ApiError, cast_handle_api_error())
        self.client = self.scope.enter_context(TestClient(app))
        self.folder = uuid4()
        self.foreign = uuid4()
        outsider = uuid4()
        now = datetime.now(timezone.utc)
        with self.database.session() as session:
            session.add(User(id=outsider, name="Other", email="other@example.invalid",
                             password="synthetic-placeholder", created_at=now, updated_at=now))
            session.flush()
            session.add_all([Folder(id=identifier, owner_id=owner, name="folder",
                                    created_at=now, updated_at=now)
                             for identifier, owner in ((self.folder, self.user.id), (self.foreign, outsider))])
            session.commit()

    def index(self, content, filename, extension, identifier):
        self.assertEqual(self.depth, 0, "A PostgreSQL session spans ingestion")
        with self.database.session() as session:
            file = session.get(File, identifier)
            assert file is not None
            self.assertEqual(file.status, "processing")
            self.assertEqual(file.owner_id, self.user.id)
            self.assertEqual(file.size_bytes, len(content))
        return []

    def post(self, data=None, headers=None, content=b"# Policy\n\nSynthetic content.", filename="SOURCE.MD"):
        return self.client.post("/files", headers=self.headers if headers is None else headers,
                                data={"name": "  Valid  ", **(data or {})},
                                files={"file": (filename, content, "text/markdown")})

    def rows(self):
        with self.database.session() as session:
            return [(file.id, file.status) for file in session.scalars(select(File))]

    def test_root_nested_duplicate_success_and_canonical_identity(self):
        for folder in (None, self.folder, self.folder):
            response = self.post({"folder_id": str(folder)} if folder else {})
            self.assertEqual(response.status_code, 201, response.text)
            body = response.json()
            identifier = UUID(body["id"])
            self.assertEqual(self.ingest.call_args.args[-1], identifier)
            self.assertEqual(body["status"], "ready")
            self.assertEqual(body["name"], "Valid")
            self.assertEqual(body["original_name"], "SOURCE.MD")
            self.assertEqual(body["extension"], ".md")
            self.assertEqual(body["folder_id"], str(
                folder) if folder else None)
            self.assertEqual(set(body), {"id", "name", "description", "original_name", "extension",
                                         "size_bytes", "status", "folder_id", "created_at", "updated_at"})
            with self.database.session() as session:
                file = session.get(File, identifier)
                assert file is not None
                self.assertEqual(file.status, "ready")
                self.assertEqual(file.owner_id, self.user.id)
        self.assertEqual(len(self.rows()), 3)
        self.storage.delete.assert_not_called()

    def test_auth_before_malformed_multipart_and_zero_mutation(self):
        for headers in ({}, {"Authorization": "Bearer invalid"}):
            response = self.client.post("/files", headers=headers,
                                        content=b"invalid", json=None)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json()["code"], "INVALID_ACCESS_TOKEN")
        self.assertEqual(self.rows(), [])
        self.ingest.assert_not_called()

    def test_folder_privacy_before_row_or_ingestion(self):
        results = [self.post({"folder_id": str(folder)})
                   for folder in (self.foreign, uuid4())]
        self.assertEqual(
            [response.status_code for response in results], [404, 404])
        self.assertEqual(results[0].json(), results[1].json())
        self.assertEqual(results[0].json()["code"], "FOLDER_NOT_FOUND")
        self.assertEqual(self.rows(), [])
        self.ingest.assert_not_called()

    def test_forbidden_and_invalid_fields_do_not_ingest(self):
        for field in ("owner_id", "user_id", "id", "file_id", "status", "size_bytes", "extension",
                      "original_name", "created_at", "updated_at"):
            with self.subTest(field=field):
                response = self.post({field: "untrusted"})
                self.assertEqual(response.status_code, 422, response.text)
                self.assertEqual(response.json(), {
                                 "error": "Invalid drive input", "code": "UNPROCESSABLE_ENTITY"})
        for data in ({"folder_id": "invalid"}, {"name": "bad/name"}, {"description": "a" * 251}):
            self.assertEqual(self.post(data).status_code, 422)
        self.assertEqual(self.rows(), [])
        self.ingest.assert_not_called()

    def test_source_validation_before_row(self):
        self.assertEqual(self.post(content=b"").json()
                         ["code"], "INVALID_FILE_SIZE")
        self.assertEqual(self.post(filename="archive.zip").json()[
                         "code"], "INVALID_FILE_TYPE")
        self.assertEqual(self.rows(), [])
        self.ingest.assert_not_called()

    def test_upload_read_error_is_safe_and_does_not_create_state(self):
        with patch.object(Uploaded, "read", new=AsyncMock(side_effect=OSError("private temp path"))):
            response = self.post()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "FILE_UPLOAD_FAILED")
        self.assertNotIn("private", response.text)
        self.assertEqual(self.rows(), [])
        self.ingest.assert_not_called()

    def test_processing_commit_failure_prevents_ingestion(self):
        with patch("sqlalchemy.orm.Session.commit", side_effect=SQLAlchemyError("private SQL")):
            response = self.post()
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("private", response.text)
        self.assertEqual(self.rows(), [])
        self.ingest.assert_not_called()
        self.storage.delete.assert_not_called()

    def test_known_failure_confirmed_cleanup_removes_row(self):
        self.ingest.side_effect = ApiError(
            "Unable to extract uploaded file", "FILE_UPLOAD_FAILED")
        self.storage.delete.side_effect = lambda identifier: self.assertEqual(
            self.depth, 0)
        response = self.post()
        self.assertEqual(response.status_code, 400)
        self.storage.delete.assert_called_once_with(
            self.ingest.call_args.args[-1])
        self.assertEqual(self.rows(), [])

    def test_ingestion_failure_cleans_vectors_even_when_postgres_is_unavailable(self):
        def failed(*args):
            self.scope.enter_context(
                patch("app.pipeline.upload.postgres", side_effect=SQLAlchemyError()))
            raise RuntimeError("injected ingestion failure")

        self.ingest.side_effect = failed
        response = self.post()
        self.assertEqual(response.status_code, 500)
        self.storage.delete.assert_called_once_with(
            self.ingest.call_args.args[-1])
        self.assertEqual(
            self.rows(), [(self.ingest.call_args.args[-1], "processing")])

    def test_cleanup_uncertainty_retains_processing_and_sanitizes_unknown_error(self):
        self.ingest.side_effect = RuntimeError("PRIVATE SOURCE AND SECRET")
        self.storage.delete.side_effect = ConnectionError("PRIVATE PROVIDER")
        with self.assertLogs("app", level="ERROR") as logs:
            response = self.post()
        self.assertEqual(response.status_code, 500)
        self.assertNotIn("PRIVATE", response.text + " ".join(logs.output))
        self.assertEqual(
            self.rows(), [(self.ingest.call_args.args[-1], "processing")])

    def test_finalization_failure_compensates(self):
        for cleanup_fails in (False, True):
            with self.subTest(cleanup_fails=cleanup_fails):
                self.storage.delete.side_effect = ConnectionError() if cleanup_fails else None
                with patch("app.pipeline.upload.ready", side_effect=SQLAlchemyError("private")):
                    response = self.post()
                self.assertEqual(response.status_code, 500)
                identifier = self.ingest.call_args.args[-1]
                self.assertEqual((identifier, "processing")
                                 in self.rows(), cleanup_fails)

    def test_real_finalization_commit_failure_rolls_back_then_compensates(self):
        commit = Session.commit
        calls = 0

        def failing(session):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise SQLAlchemyError("private commit details")
            return commit(session)

        with patch.object(Session, "commit", new=failing):
            response = self.post()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "POSTGRES_OPERATION_FAILED")
        self.assertEqual(self.rows(), [])
        self.storage.delete.assert_called_once()

    def test_request_upload_resources_close_on_all_paths(self):
        closed = []
        close = Uploaded.close

        async def closing(file):
            await close(file)
            closed.append(file.file.closed)

        with patch.object(Uploaded, "close", new=closing):
            self.assertEqual(self.post().status_code, 201)
            self.assertTrue(closed and all(closed))
            closed.clear()
            self.assertEqual(self.post({"name": "bad/name"}).status_code, 422)
            self.assertTrue(closed and all(closed))
            closed.clear()
            self.ingest.side_effect = RuntimeError("injected")
            self.assertEqual(self.post().status_code, 500)
            self.assertTrue(closed and all(closed))

    def test_ambiguous_ready_commit_reverts_before_vector_cleanup(self):
        def uncertain(identifier, owner):
            ready(identifier, owner)
            raise SQLAlchemyError("lost acknowledgement")

        def deleted(identifier):
            self.assertEqual(self.depth, 0)
            self.assertIn((identifier, "processing"), self.rows())

        self.storage.delete.side_effect = deleted
        with patch("app.pipeline.upload.ready", side_effect=uncertain):
            response = self.post()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.rows(), [])

    def test_canonical_cleanup_failure_retains_processing(self):
        def fail_delete(identifier):
            self.scope.enter_context(
                patch("sqlalchemy.orm.Session.commit", side_effect=SQLAlchemyError()))

        self.storage.delete.side_effect = fail_delete
        self.ingest.side_effect = RuntimeError()
        response = self.post()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            self.rows(), [(self.ingest.call_args.args[-1], "processing")])

    def test_legacy_route_absent(self):
        from app.main import app
        paths = app.openapi()["paths"]
        self.assertNotIn("/documents/upload", paths)
        self.assertEqual(
            set(paths["/files"]["post"]["requestBody"]["content"]), {"multipart/form-data"})
        response = self.client.post(
            "/documents/upload", files={"file": ("old.md", b"legacy")})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.rows(), [])
        self.ingest.assert_not_called()


class ExactCleanupTests(unittest.TestCase):
    """Prove completed, idempotent payload-scoped deletion using real in-memory Qdrant."""

    def test_exact_scope_and_idempotence(self):
        with closing(QdrantClient(":memory:")) as client:
            client.create_collection("test", vectors_config=VectorParams(
                size=2, distance=Distance.COSINE))
            target, other = uuid4(), uuid4()
            client.upsert("test", [PointStruct(id=str(uuid4()), vector=[1., 0.], payload={"file_id": str(file)})
                                   for file in (target, target, other)], wait=True)
            for _ in range(2):
                remove(client, "test", target)
                points, _ = client.scroll("test", with_vectors=True)
                self.assertEqual(len(points), 1)
                self.assertEqual(points[0].payload, {"file_id": str(other)})
            with patch.object(client, "delete", return_value=UpdateResult(status=UpdateStatus.ACKNOWLEDGED)):
                with self.assertRaises(ApiError):
                    remove(client, "test", target)

    def test_safe_cleanup_errors(self):
        client = Mock(spec=QdrantClient)
        for error, code in ((ConnectionError("private"), "QDRANT_CONNECTION_FAILED"),
                            (ValueError("private"), "QDRANT_COLLECTION_ERROR")):
            client.delete.side_effect = error
            with self.assertRaises(ApiError) as caught:
                remove(client, "test", uuid4())
            self.assertEqual(caught.exception.code, code)
            self.assertNotIn("private", caught.exception.message)

    def test_disposable_database_guard(self):
        from tests.uploads_live import validate
        validate("atlas_uploads_" + uuid4().hex)
        for name in ("postgres", "atlas", "atlas_uploads_", "atlas_uploads_bad", "atlas_uploads_" + "g" * 32):
            with self.subTest(name=name), self.assertRaises((AssertionError, ValueError)):
                validate(name)
