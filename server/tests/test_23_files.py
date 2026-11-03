"""Isolated metadata/deletion contracts; never connect to configured datastores."""
import io
import unittest
from uuid import uuid4
from pydantic import ValidationError
from collections.abc import Iterator
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
from contextlib import ExitStack, closing, contextmanager

from fastapi import FastAPI, UploadFile
from fastapi.testclient import TestClient

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from sqlalchemy.orm import Session
from sqlalchemy import event, select
from sqlalchemy.exc import SQLAlchemyError

from app.core.runtime import activate
from app.core.cors import configure_cors

from app.pipeline.storage import Storage
from app.pipeline.files import finish, owned

from app.routers.file_mutations import router
from app.routers.drive import router as drive

from app.schemas.pipeline import Chunk
from app.schemas.drive.upload import FileUpload
from app.schemas.drive.metadata import FilePatch

from app.models.postgres import File, Folder, User

from app.errors.api import ApiError
from app.errors.handlers import cast_handle_api_error

from tests.uploads import environment
from tests.test_05_upload_storage import Provider


class FileValidationTests(unittest.TestCase):
    """Upload and PATCH share normalization and exact validation boundaries."""

    def test_shared_metadata_contract(self):
        for value in ("a", "a" * 100, "  Résumé 中文 ١²Ⅳ  ", "_-.,()[]&+@'"):
            with self.subTest(value=value):
                upload = FileUpload(file=UploadFile(
                    file=io.BytesIO()), name=value)
                self.assertEqual(FilePatch(name=value).name, upload.name)
        for value in (None, "", " \n\t ", "d" * 250, "  details 😀\nbody  "):
            upload = FileUpload(file=UploadFile(
                file=io.BytesIO()), name="a", description=value)
            self.assertEqual(
                FilePatch(description=value).description, upload.description)
        for value in ("", " ", "a" * 101, "a/b", "a\\b", "a:b", "a\tb", "a\nb",
                      "a\u00a0b", "a\u200bb", "e\u0301", "😀", "a\x00b"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                FilePatch(name=value)
        for payload in ({}, {"name": None}, {"name": 1}, {"description": 1},
                        {"description": "x" * 251}, {"name": "ok", "extra": "x"}):
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                FilePatch.model_validate(payload)
        self.assertEqual(
            FilePatch(description=None).model_fields_set, {"description"})

    def test_disposable_helper_namespace_guards(self):
        from tests.files_live import validate
        validate("atlas_files_" + uuid4().hex)
        for value in ("postgres", "atlas_files_", "atlas_files_not-a-uuid", "atlas_uploads_" + uuid4().hex):
            with self.assertRaises(AssertionError):
                validate(value)


class FileAcceptanceHelperTests(unittest.TestCase):
    """Dry-run opt-in helper logic with isolated stores and deterministic ingestion."""

    def test_shared_acceptance_and_fault_cleanup_locally(self):
        from app.main import app
        from tests.files_acceptance import acceptance
        from tests.files_live import faults
        with environment() as (database, user, headers), closing(QdrantClient(
                ":memory:", force_disable_check_same_thread=True)) as qdrant:
            provider = Provider()
            qdrant.create_collection("acceptance-test", vectors_config=VectorParams(
                size=provider.dimension, distance=Distance.COSINE))
            services = Storage(provider, qdrant, "acceptance-test")

            def index(content, filename, extension, identifier):
                chunks = [Chunk(id=str(identifier), text=content.decode(
                ), display_text=content.decode(), index=0, count=12)]
                services.write(chunks)

                return chunks

            with activate(services, database), patch("app.pipeline.upload.ingest", side_effect=index), closing(TestClient(app)) as client:
                result = acceptance(database, client, services, [])
                faults(database, client)
            self.assertEqual(result["metadata_vectors"], "unchanged")
            self.assertEqual(qdrant.count(
                "acceptance-test", exact=True).count, 0)
            with database.session() as session:
                self.assertIsNone(session.scalar(select(File)))


class FileMutationTests(unittest.TestCase):
    """Exercise real local transactions and exact-file Qdrant through HTTP boundaries."""

    def setUp(self):
        self.scope = ExitStack()
        self.addCleanup(self.scope.close)
        self.database, self.user, self.headers = self.scope.enter_context(
            environment())
        for target in ("app.pipeline.files.postgres", "app.pipeline.drive.postgres"):
            self.scope.enter_context(patch(target, return_value=self.database))
        self.depth = 0
        original = self.database.session

        @contextmanager
        def operation() -> Iterator[Session]:
            self.depth += 1
            try:
                with original() as session:
                    yield session
            finally:
                self.depth -= 1

        self.scope.enter_context(patch.object(
            self.database, "session", side_effect=operation))
        self.qdrant = QdrantClient(
            ":memory:", force_disable_check_same_thread=True)
        self.scope.callback(self.qdrant.close)
        self.qdrant.create_collection(
            "files-test", vectors_config=VectorParams(size=3, distance=Distance.COSINE))
        self.services = Storage(Provider(), self.qdrant, "files-test")
        self.runtime = self.scope.enter_context(
            patch("app.pipeline.files.storage", return_value=self.services))
        application = FastAPI()
        with patch("app.core.cors.constants.cors.CORS_ORIGINS", ["https://atlas.example"]):
            configure_cors(application)
        application.include_router(router)
        application.include_router(drive)
        application.add_exception_handler(ApiError, cast_handle_api_error())
        self.client = self.scope.enter_context(TestClient(application))
        self.target, self.survivor, self.processing, self.deleting = [
            uuid4() for _ in range(4)]
        self.foreign, self.folder, outsider = uuid4(), uuid4(), uuid4()
        now = datetime.now(timezone.utc) - timedelta(days=1)
        with self.database.session() as session:
            session.add(User(id=outsider, name="Other", email="other@example.invalid",
                             password="synthetic-placeholder", created_at=now, updated_at=now))
            session.flush()
            session.add(Folder(id=self.folder, owner_id=self.user.id,
                        name="nested", created_at=now, updated_at=now))
            session.flush()
            for identifier, status, owner in ((self.target, "ready", self.user.id),
                                              (self.survivor, "ready", self.user.id), (
                                                  self.processing, "processing", self.user.id),
                                              (self.deleting, "deleting", self.user.id), (self.foreign, "ready", outsider)):
                session.add(File(id=identifier, owner_id=owner, folder_id=self.folder if identifier == self.target else None,
                                 name="Original", description="Description", original_name="SOURCE.MD", extension=".md",
                                 size_bytes=42, status=status, created_at=now, updated_at=now))
            session.commit()
        self.qdrant.upsert("files-test", [PointStruct(id=str(uuid4()), vector=[1.0, 0.5, 0.25],
                           payload={"file_id": str(identifier), "text": "Synthetic", "index": index})
            for identifier in (self.target, self.survivor, self.deleting, self.foreign) for index in range(2)])

    def request(self, method, identifier=None, **kwargs):
        return self.client.request(method, "/files/" + str(identifier or self.target),
                                   headers=kwargs.pop("headers", self.headers), **kwargs)

    def row(self, identifier=None):
        with self.database.session() as session:
            file = session.get(File, identifier or self.target)
            return {column.name: getattr(file, column.name) for column in File.__table__.columns} if file else None

    def points(self):
        points, cursor = self.qdrant.scroll(
            "files-test", limit=100, with_payload=True, with_vectors=True)
        self.assertIsNone(cursor)
        return sorted(points, key=lambda point: str(point.id))

    def test_patch_preserves_source_and_index_and_updates_listing(self):
        before, points = self.row(), self.points()
        assert before is not None
        for payload, expected in (({"name": "  Renamed 中文  "}, ("Renamed 中文", "Description")),
                                  ({"description": "  details  "},
                                   ("Renamed 中文", "details")),
                                  ({"description": None}, ("Renamed 中文", None)),
                                  ({"name": "Both", "description": "  "}, ("Both", None))):
            response = self.request("PATCH", json=payload)
            self.assertEqual(response.status_code, 200, response.text)
            body = response.json()
            self.assertEqual((body["name"], body["description"]), expected)
            self.assertEqual(set(body), set(before) - {"owner_id"})
            after = self.row()
            assert after is not None
            for key in before.keys() - {"name", "description", "updated_at"}:
                self.assertEqual(after[key], before[key])
            self.assertGreater(after["updated_at"], before["updated_at"])
        self.runtime.assert_not_called()
        self.assertEqual(self.points(), points)
        listing = self.client.get(
            "/drive", params={"folder_id": str(self.folder)}, headers=self.headers)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()["files"][0]["name"], "Both")

    def test_patch_rejects_immutable_fields_and_malformed_input(self):
        before = self.row()
        for key in ("id", "owner_id", "folder_id", "original_name", "extension", "size_bytes", "status", "created_at", "updated_at", "content"):
            self.assertEqual(self.request(
                "PATCH", json={key: "attempt", "name": "ok"}).status_code, 422)
        for payload in ({}, {"name": None}, {"name": "a" * 101}, {"description": "d" * 251}, []):
            self.assertEqual(self.request(
                "PATCH", json=payload).status_code, 422)
        self.assertEqual(self.request("PATCH", content="{", headers={
                         **self.headers, "Content-Type": "application/json"}).status_code, 422)
        self.assertEqual(self.request("PATCH", "invalid",
                         json={"name": "ok"}).status_code, 422)
        self.assertEqual(self.row(), before)
        self.runtime.assert_not_called()

    def test_authentication_precedes_input_and_lookup(self):
        with patch("app.pipeline.files.owned") as lookup:
            for method in ("PATCH", "DELETE"):
                for headers in ({}, {"Authorization": "Bearer invalid"}):
                    response = self.request(method, "invalid", headers=headers,
                                            content="{", extensions={})
                    self.assertEqual(response.status_code, 401)
            lookup.assert_not_called()
        self.runtime.assert_not_called()

    def test_owner_scope_and_privacy(self):
        before = self.points()
        for method in ("PATCH", "DELETE"):
            responses = [self.request(method, identifier, **({"json": {"name": "attempt"}} if method == "PATCH" else {}))
                         for identifier in (self.foreign, uuid4())]
            for response in responses:
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json(), {
                                 "error": "File not found", "code": "FILE_NOT_FOUND"})
        self.runtime.assert_not_called()
        self.assertEqual(self.points(), before)
        session = Mock(spec=Session)
        owned(session, self.target, self.user.id)
        statement = session.scalar.call_args.args[0]
        self.assertIn("files.owner_id", str(statement))
        self.assertIn("FOR UPDATE", str(statement))

    def test_processing_and_deleting_guards(self):
        for method, identifier in (("PATCH", self.processing), ("PATCH", self.deleting), ("DELETE", self.processing)):
            before = self.row(identifier)
            response = self.request(
                method, identifier, **({"json": {"name": "attempt"}} if method == "PATCH" else {}))
            self.assertEqual(response.status_code, 409)
            self.assertEqual(response.json(), {
                             "error": "File is not ready", "code": "FILE_NOT_READY"})
            self.assertEqual(self.row(identifier), before)
        self.runtime.assert_not_called()

    def test_delete_commits_marker_and_closes_session_before_exact_cleanup(self):
        points = self.points()
        survivor = self.row(self.survivor)
        original = self.services.delete

        def cleanup(identifier):
            self.assertEqual(self.depth, 0)
            row = self.row(identifier)
            assert row is not None
            self.assertEqual(row["status"], "deleting")
            original(identifier)
            self.assertIsNotNone(self.row(identifier))

        with patch.object(self.services, "delete", side_effect=cleanup) as call:
            response = self.request("DELETE")
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(response.content, b"")
        call.assert_called_once_with(self.target)
        self.assertIsNone(self.row())
        self.assertEqual(self.row(self.survivor), survivor)
        self.assertEqual(self.points(), [
                         point for point in points if point.payload is not None and point.payload["file_id"] != str(self.target)])
        self.assertEqual(self.request("DELETE").status_code, 404)
        listing = self.client.get(
            "/drive", params={"folder_id": str(self.folder)}, headers=self.headers)
        self.assertEqual(listing.json()["files"], [])

    def test_qdrant_failure_retains_deleting_and_retry_removes_existing_vectors(self):
        before = self.points()
        with patch.object(self.qdrant, "delete", side_effect=ConnectionError("private backend diagnostics")):
            response = self.request("DELETE")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", response.text)
        row = self.row()
        assert row is not None
        self.assertEqual(row["status"], "deleting")
        self.assertEqual(self.points(), before)
        listing = self.client.get(
            "/drive", params={"folder_id": str(self.folder)}, headers=self.headers)
        self.assertEqual(listing.json()["files"][0]["status"], "deleting")
        self.assertEqual(self.request("DELETE").status_code, 204)
        self.assertIsNone(self.row())

    def test_final_commit_failure_retains_deleting_and_zero_vector_retry(self):
        before = [point for point in self.points(
        ) if point.payload is not None and point.payload["file_id"] != str(self.target)]

        def reject(session):
            if any(isinstance(item, File) and item.id == self.target for item in session.deleted):
                raise SQLAlchemyError("private SQL parameters")

        event.listen(Session, "before_commit", reject)
        try:
            response = self.request("DELETE")
            self.assertEqual(response.status_code, 500)
            self.assertEqual(
                response.json()["code"], "POSTGRES_OPERATION_FAILED")
            self.assertNotIn("private", response.text)
        finally:
            event.remove(Session, "before_commit", reject)
        row = self.row()
        assert row is not None
        self.assertEqual(row["status"], "deleting")
        self.assertEqual(self.points(), before)
        self.assertEqual(self.request("DELETE").status_code, 204)
        self.assertIsNone(self.row())
        self.assertEqual(self.points(), before)

    def test_initial_commit_failure_does_not_touch_index(self):
        before, points = self.row(), self.points()

        def reject(session):
            raise SQLAlchemyError("private SQL parameters")

        event.listen(Session, "before_commit", reject)
        try:
            self.assertEqual(self.request("DELETE").status_code, 500)
            self.assertEqual(self.request(
                "PATCH", json={"name": "attempt"}).status_code, 500)
        finally:
            event.remove(Session, "before_commit", reject)
        self.assertEqual(self.row(), before)
        self.assertEqual(self.points(), points)
        self.runtime.assert_not_called()

    def test_deleting_retry_and_concurrent_finalizer(self):
        self.assertEqual(self.request(
            "DELETE", self.deleting).status_code, 204)
        original = self.services.delete

        def concurrent(identifier):
            original(identifier)
            finish(self.user.id, identifier)

        with patch.object(self.services, "delete", side_effect=concurrent):
            self.assertEqual(self.request("DELETE").status_code, 204)
        self.assertIsNone(self.row())

    def test_finish_requires_deleting(self):
        with self.assertRaises(ApiError) as error:
            finish(self.user.id, self.target)
        self.assertEqual(error.exception.code, "FILE_NOT_READY")
        self.assertIsNotNone(self.row())

    def test_delete_cors_exact_policy_on_preflight_and_errors(self):
        for origin in ("https://atlas.example", "https://foreign.example"):
            for method in ("GET", "POST", "PATCH", "DELETE", "PUT"):
                response = self.client.options("/files/" + str(self.target), headers={"Origin": origin,
                                                                                      "Access-Control-Request-Method": method, "Access-Control-Request-Headers": "Authorization, Content-Type"})
                self.assertEqual(response.status_code, 200 if origin ==
                                 "https://atlas.example" and method != "PUT" else 400)
                self.assertEqual(set(response.headers["access-control-allow-methods"].split(
                    ", ")), {"GET", "POST", "PATCH", "DELETE"})
                self.assertEqual(response.headers.get(
                    "access-control-allow-origin"), origin if origin == "https://atlas.example" else None)
                self.assertEqual(
                    response.headers["access-control-allow-credentials"], "true")
        response = self.request(
            "DELETE", headers={"Origin": "https://atlas.example"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.headers["access-control-allow-origin"], "https://atlas.example")


if __name__ == "__main__":
    unittest.main()
