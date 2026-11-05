"""Deterministic HTTP/query/transaction checks; SQLite is not PostgreSQL evidence."""
import os
import secrets
import unittest
from typing import cast
from uuid import UUID, uuid4
from pydantic import ValidationError
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone

from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import Table, create_engine, event, select

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.cors import configure_cors
from app.core.constants import constants

from app.db.postgres import Database
from app.models.postgres import File, Folder, User

from app.pipeline.auth.access import Access
from app.pipeline.drive import create, listing, update

from app.routers.drive import router as drive
from app.routers.folders import router as folders

from app.schemas.constants import CorsConstants
from app.schemas.drive.file import FileResponse
from app.schemas.drive.folder import FolderResponse
from app.schemas.drive.listing import DriveResponse
from app.schemas.drive.requests import FolderCreate, FolderPatch

from app.errors.api import ApiError
from app.errors.handlers import cast_handle_api_error
from app.errors.postgres import PostgresOperationError


def application() -> FastAPI:
    """Exercise actual drive routers without initializing unrelated providers."""
    app = FastAPI()
    app.include_router(drive)
    app.include_router(folders)
    app.add_exception_handler(ApiError, cast_handle_api_error())

    return app


class FolderApiTests(unittest.TestCase):
    """Use actual SQLAlchemy predicates and sessions against isolated in-memory rows."""

    def setUp(self) -> None:
        scope = patch.dict(
            os.environ, {"AUTH_ACCESS_TOKEN_SECRET": secrets.token_urlsafe(48)})
        scope.start()
        self.addCleanup(scope.stop)
        engine = create_engine("sqlite://", poolclass=StaticPool,
                               connect_args={"check_same_thread": False}, hide_parameters=True)
        self.addCleanup(engine.dispose)
        for table in (User.__table__, Folder.__table__, File.__table__):
            cast(Table, table).create(engine)
        self.database = Database(engine, sessionmaker(bind=engine))
        for target in ("app.pipeline.drive.postgres", "app.pipeline.auth.current.postgres"):
            scope = patch(target, return_value=self.database)
            scope.start()
            self.addCleanup(scope.stop)
        self.now = datetime.now(timezone.utc)-timedelta(days=1)
        self.owners = [uuid4(), uuid4()]
        self.tokens = [Access().issue(owner) for owner in self.owners]
        with self.database.session() as session:
            for owner in self.owners:
                session.add(User(id=owner, name="Synthetic", email=f"{owner}@example.invalid",
                                 password="synthetic-placeholder", verified_at=self.now,
                                 created_at=self.now, updated_at=self.now))
            session.commit()
        self.root = self.seed_folder(self.owners[0])
        self.child = self.seed_folder(self.owners[0], self.root)
        self.deep = self.seed_folder(self.owners[0], self.child)
        self.sibling = self.seed_folder(self.owners[0])
        self.foreign = self.seed_folder(self.owners[1])
        self.files = []
        for location in (None, self.root, self.child, self.sibling):
            for status in ("processing", "ready", "deleting"):
                self.files.append(
                    (self.seed_file(self.owners[0], location, status), location, status))
        self.foreign_file = self.seed_file(self.owners[1], None, "ready")
        self.client = TestClient(application())
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def seed_folder(self, owner, parent=None):
        identifier = uuid4()
        with self.database.session() as session:
            session.add(Folder(id=identifier, owner_id=owner, parent_id=parent,
                               name="same", description="original", created_at=self.now, updated_at=self.now))
            session.commit()

        return identifier

    def seed_file(self, owner, folder, status):
        identifier = uuid4()
        with self.database.session() as session:
            session.add(File(id=identifier, owner_id=owner, folder_id=folder, name="same", description=None,
                             original_name="synthetic.md", extension=".md", size_bytes=19, status=status,
                             created_at=self.now, updated_at=self.now))
            session.commit()

        return identifier

    def request(self, method, path, owner=0, **kwargs):
        return self.client.request(method, path, headers={"Authorization": "Bearer "+self.tokens[owner]}, **kwargs)

    def not_found(self, response):
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
                         "error": "Folder not found", "code": "FOLDER_NOT_FOUND"})

    def test_root_is_owner_scoped_and_includes_every_status(self):
        for index, expected in ((0, {str(self.root), str(self.sibling)}), (1, {str(self.foreign)})):
            response = self.request("GET", "/drive", owner=index)
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertEqual(set(body), {"folder", "folders", "files"})
            self.assertIsNone(body["folder"])
            self.assertEqual({item["id"]
                             for item in body["folders"]}, expected)
            expected_files = {str(item[0]) for item in self.files if item[1] is None} if index == 0 else {
                str(self.foreign_file)}
            self.assertEqual({item["id"]
                             for item in body["files"]}, expected_files)
            if index == 0:
                self.assertEqual({item["status"] for item in body["files"]}, {
                                 "processing", "ready", "deleting"})

    def test_nested_contains_only_direct_children(self):
        for folder, expected in ((self.root, {str(self.child)}), (self.child, {str(self.deep)}), (self.deep, set())):
            body = self.request(
                "GET", "/drive", params={"folder_id": str(folder)}).json()
            self.assertEqual(body["folder"]["id"], str(folder))
            self.assertEqual({item["id"]
                             for item in body["folders"]}, expected)
            self.assertEqual({item["id"] for item in body["files"]},
                             {str(item[0]) for item in self.files if item[1] == folder})

    def test_exact_response_fields_and_owner_only_models(self):
        folder_fields = {"id", "name", "description",
                         "parent_id", "created_at", "updated_at"}
        file_fields = {"id", "name", "description", "original_name", "extension", "size_bytes",
                       "status", "folder_id", "created_at", "updated_at"}
        body = self.request("GET", "/drive").json()
        self.assertEqual(set(FolderResponse.model_fields), folder_fields)
        self.assertEqual(set(FileResponse.model_fields), file_fields)
        self.assertEqual(set(DriveResponse.model_fields),
                         {"folder", "folders", "files"})
        for item in body["folders"]:
            self.assertEqual(set(item), folder_fields)
        for item in body["files"]:
            self.assertEqual(set(item), file_fields)
        for model in (Folder, File):
            self.assertIn("owner_id", model.__table__.columns)
            self.assertNotIn("user_id", model.__table__.columns)

    def test_missing_foreign_lookup_patch_and_parent_are_identical(self):
        for identifier in (self.foreign, uuid4()):
            self.not_found(self.request("GET", "/drive",
                           params={"folder_id": str(identifier)}))
            self.not_found(self.request(
                "PATCH", f"/folders/{identifier}", json={"name": "attempt"}))
            self.not_found(self.request(
                "POST", "/folders", json={"name": "attempt", "parent_id": str(identifier)}))
        self.not_found(self.request("GET", "/drive", owner=1,
                       params={"folder_id": str(self.root)}))

    def test_authentication_precedes_resource_queries_on_every_route(self):
        paths = (("GET", "/drive", {}), ("GET", f"/drive?folder_id={self.foreign}", {}),
                 ("POST", "/folders", {"json": {"name": "new"}}),
                 ("PATCH", f"/folders/{self.foreign}", {"json": {"name": "new"}}))
        expired = Access().issue(self.owners[0])
        future = datetime.now(timezone.utc)+timedelta(days=3)
        with patch("app.pipeline.drive.postgres") as database:
            for method, path, kwargs in paths:
                for headers in ({}, {"Authorization": "Bearer malformed"}, {"Cookie": "atlas_refresh="+self.tokens[0]}):
                    response = self.client.request(
                        method, path, headers=headers, **kwargs)
                    self.assertEqual(response.status_code, 401)
                    self.assertEqual(response.json(), {
                                     "error": "Invalid access token", "code": "INVALID_ACCESS_TOKEN"})
                with patch("jwt.api_jwt.datetime") as clock:
                    clock.now.return_value = future
                    response = self.client.request(
                        method, path, headers={"Authorization": "Bearer "+expired}, **kwargs)
                self.assertEqual(response.status_code, 401)
            database.assert_not_called()

    def test_create_root_nested_deep_and_duplicate_names(self):
        for parent in (None, self.root, self.child):
            identifiers = set()
            for _ in range(2):
                response = self.request("POST", "/folders", json={"name": "  same  ", "description": "  details  ",
                                                                  "parent_id": str(parent) if parent else None})
                self.assertEqual(response.status_code, 201)
                item = response.json()
                identifiers.add(item["id"])
                self.assertEqual(item["name"], "same")
                self.assertEqual(item["description"], "details")
                self.assertEqual(item["parent_id"], str(
                    parent) if parent else None)
                self.assertEqual(item["created_at"], item["updated_at"])
                with self.database.session() as session:
                    folder = session.get(Folder, UUID(item["id"]))
                    assert folder is not None
                    self.assertEqual(folder.owner_id, self.owners[0])
            self.assertEqual(len(identifiers), 2)

    def test_create_omitted_and_blank_description_normalize_to_null(self):
        for data in ({"name": "new"}, {"name": "new", "description": None}, {"name": "new", "description": " \t "}):
            response = self.request("POST", "/folders", json=data)
            self.assertEqual(response.status_code, 201)
            self.assertIsNone(response.json()["description"])
            self.assertIsNone(response.json()["parent_id"])

    def test_patch_preserves_immutable_fields_and_omitted_metadata(self):
        before = self.request(
            "GET", "/drive", params={"folder_id": str(self.child)}).json()["folder"]
        for payload, name, description in (({"name": " renamed "}, "renamed", "original"),
                                           ({"description": " edited "},
                                            "renamed", "edited"),
                                           ({"description": None},
                                            "renamed", None),
                                           ({"name": "same", "description": "both"},
                                            "same", "both"),
                                           ({"description": "  "}, "same", None)):
            response = self.request(
                "PATCH", f"/folders/{self.child}", json=payload)
            self.assertEqual(response.status_code, 200)
            item = response.json()
            self.assertEqual(
                (item["name"], item["description"]), (name, description))
            for key in ("id", "parent_id", "created_at"):
                self.assertEqual(item[key], before[key])
            self.assertGreater(datetime.fromisoformat(item["updated_at"]).replace(tzinfo=timezone.utc),
                               datetime.fromisoformat(before["updated_at"]).replace(tzinfo=timezone.utc))
            with self.database.session() as session:
                folder = session.get(Folder, self.child)
                assert folder is not None
                self.assertEqual(folder.owner_id, self.owners[0])
        with self.database.session() as session:
            folder = session.get(Folder, self.child)
            assert folder is not None
            self.assertEqual((folder.name, folder.description), ("same", None))

    def test_invalid_mutations_are_sanitized_and_do_not_write(self):
        invalid = [{"name": value}
                   for value in (None, "", " \t ", 17, True, [], {})]
        for method, path, cases in (("POST", "/folders", [{}, *invalid, {"name": "ok", "parent_id": "invalid"}]),
                                    ("PATCH", f"/folders/{self.root}", [{}, *invalid])):
            for data in cases:
                self.assertEqual(self.request(
                    method, path, json=data).status_code, 422)
        for field in ("owner_id", "user_id", "id", "folder_id", "status", "created_at", "updated_at", "unexpected"):
            for method, path in (("POST", "/folders"), ("PATCH", f"/folders/{self.root}")):
                response = self.request(
                    method, path, json={"name": "ok", field: "private-input"})
                self.assertEqual(response.status_code, 422)
                self.assertNotIn("private-input", response.text)
                self.assertEqual(
                    response.json()["code"], "UNPROCESSABLE_ENTITY")
        response = self.request(
            "PATCH", f"/folders/{self.root}", json={"parent_id": str(self.sibling)})
        self.assertEqual(response.status_code, 422)
        for value in (17, [], {}):
            self.assertEqual(self.request(
                "PATCH", f"/folders/{self.root}", json={"description": value}).status_code, 422)
        with self.database.session() as session:
            self.assertEqual(len(session.scalars(select(Folder)).all()), 5)
            folder = session.get(Folder, self.root)
            assert folder is not None
            self.assertEqual(folder.name, "same")

    def test_query_and_path_validation_reject_ownership_and_unknown_input(self):
        for field in ("owner_id", "user_id", "sort", "limit", "access_token"):
            for method, path, data in (("GET", "/drive", None), ("POST", "/folders", {"name": "ok"}),
                                       ("PATCH", f"/folders/{self.root}", {"name": "ok"})):
                response = self.request(method, path, params={
                                        field: "private-query"}, json=data)
                self.assertEqual(response.status_code, 422)
                self.assertNotIn("private-query", response.text)
        for path in ("/drive?folder_id=invalid", "/drive?folder_id="):
            self.assertEqual(self.request("GET", path).status_code, 422)
        self.assertEqual(self.request("PATCH", "/folders/invalid",
                         json={"name": "ok"}).status_code, 422)
        self.assertEqual(self.request("POST", "/folders",
                         content=b'{').status_code, 422)

    def test_owner_lookup_and_listing_queries_have_both_predicates(self):
        statements = []

        def capture(connection, cursor, statement, parameters, context, many):
            statements.append(statement)

        event.listen(self.database.engine, "before_cursor_execute", capture)
        try:
            result = listing(self.owners[0], self.root)
        finally:
            event.remove(self.database.engine,
                         "before_cursor_execute", capture)
        assert result.folder is not None
        self.assertEqual(result.folder.id, self.root)
        self.assertEqual(len(statements), 3)
        for statement, filters in zip(statements, (("folders.id", "folders.owner_id"),
                                                   ("folders.owner_id",
                                                    "folders.parent_id"),
                                                   ("files.owner_id", "files.folder_id"))):
            where = statement.split("WHERE")[1]
            self.assertIn(" AND ", where)
            for field in filters:
                self.assertIn(field+" =", where)
            self.assertNotIn("ORDER BY", statement)

    def test_database_failures_are_sanitized_without_empty_success(self):
        for method, operation in (("scalar", lambda: listing(self.owners[0], self.root)),
                                  ("scalars", lambda: listing(self.owners[0])),
                                  ("flush", lambda: create(
                                      self.owners[0], FolderCreate(name="new"))),
                                  ("flush", lambda: update(self.owners[0], self.root, FolderPatch(name="new")))):
            with patch.object(Session, method, side_effect=SQLAlchemyError("private-driver-sql")), self.assertNoLogs("app", level="DEBUG"):
                with self.assertRaises(PostgresOperationError) as caught:
                    operation()
                self.assertEqual(caught.exception.status, 500)
                self.assertNotIn("private-driver-sql",
                                 str(caught.exception.to_dict()))
        with patch.object(Session, "scalars", side_effect=SQLAlchemyError("private-driver-sql")):
            response = self.request("GET", "/drive")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["code"], "POSTGRES_OPERATION_FAILED")
        self.assertNotIn("private-driver-sql", response.text)

    def test_commit_failure_rolls_back_create_and_update(self):
        rollbacks = []
        event.listen(self.database.engine, "rollback",
                     lambda connection: rollbacks.append(True))
        for operation in (lambda: create(self.owners[0], FolderCreate(name="new")),
                          lambda: update(self.owners[0], self.root, FolderPatch(name="changed"))):
            with patch.object(Session, "commit", side_effect=SQLAlchemyError("private-commit")):
                with self.assertRaises(PostgresOperationError):
                    operation()
            with self.database.session() as session:
                self.assertEqual(len(session.scalars(select(Folder)).all()), 5)
                folder = session.get(Folder, self.root)
                assert folder is not None
                self.assertEqual(folder.name, "same")
        self.assertGreaterEqual(len(rollbacks), 2)

    def test_read_does_not_commit_or_write_and_results_survive_session_close(self):
        with patch.object(Session, "commit") as commit, patch.object(Session, "add") as add:
            result = listing(self.owners[0])
        commit.assert_not_called()
        add.assert_not_called()
        self.assertEqual(len(result.model_dump(mode="json")["folders"]), 2)
        created = create(self.owners[0], FolderCreate(name="new"))
        self.assertEqual(created.name, "new")
        self.assertIsNotNone(created.created_at.tzinfo)
        updated = update(self.owners[0], created.id,
                         FolderPatch(description=None))
        self.assertIsNone(updated.description)
        self.assertIsNotNone(updated.updated_at.tzinfo)

    def test_cors_exact_methods_origins_headers_and_credentials(self):
        app = application()
        with patch.object(constants, "cors", CorsConstants(CORS_ORIGINS=["https://atlas.example"])):
            configure_cors(app)
        with TestClient(app) as client:
            for origin in ("https://atlas.example", "https://denied.example"):
                for method in ("GET", "POST", "PATCH", "PUT", "DELETE"):
                    response = client.options("/folders/"+str(self.root), headers={"Origin": origin,
                                                                                   "Access-Control-Request-Method": method, "Access-Control-Request-Headers": "Authorization, Content-Type"})
                    self.assertEqual(response.status_code, 200 if origin ==
                                     "https://atlas.example" and method in {"GET", "POST", "PATCH", "DELETE"} else 400)
                    self.assertEqual(set(
                        response.headers["access-control-allow-methods"].split(", ")), {"GET", "POST", "PATCH", "DELETE"})
                    self.assertEqual(
                        response.headers["access-control-allow-credentials"], "true")
                    self.assertEqual(response.headers.get(
                        "access-control-allow-origin"), origin if origin == "https://atlas.example" else None)
                    self.assertNotIn("*", str(response.headers))
            response = client.patch(f"/folders/{self.root}", json={"name": "cors"},
                                    headers={"Origin": "https://atlas.example", "Authorization": "Bearer "+self.tokens[0]})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.headers["access-control-allow-origin"], "https://atlas.example")

    def test_patch_input_contract_omission_and_null(self):
        patch_value = FolderPatch(description=None)
        self.assertEqual(patch_value.model_fields_set, {"description"})
        for value in ({}, {"name": None}):
            with self.assertRaises(ValidationError):
                FolderPatch.model_validate(value)

    def test_drive_operations_do_not_access_rag_and_same_value_patch_advances_timestamp(self):
        with patch("app.core.runtime.storage", side_effect=AssertionError("Unexpected RAG access")):
            created = create(self.owners[0], FolderCreate(name="same"))
            updated = update(
                self.owners[0], created.id, FolderPatch(name="same"))
            self.assertGreater(updated.updated_at, created.updated_at)
            self.assertEqual(updated.name, created.name)
            self.assertTrue(listing(self.owners[0]).folders)

    def test_exact_drive_route_inventory(self):
        from app.main import app
        paths = app.openapi()["paths"]
        self.assertEqual(set(paths["/drive"]), {"get"})
        self.assertEqual(set(paths["/folders"]), {"post"})
        self.assertEqual(set(paths["/folders/{folder_id}"]), {"patch"})
        self.assertEqual(set(paths["/files"]), {"post"})
        self.assertEqual(set(paths["/files/{file_id}"]), {"patch", "delete"})

    def test_synthetic_cleanup_removes_deep_rows_and_preserves_other_owners(self):
        from tests.folders_acceptance import cleanup
        outsider = uuid4()
        with self.database.session() as session:
            session.add(User(id=outsider, name="Preserved", email="preserved@example.invalid",
                             password="synthetic-placeholder", created_at=self.now, updated_at=self.now))
            session.commit()
        folder = self.seed_folder(outsider)
        file = self.seed_file(outsider, folder, "ready")
        cleanup(self.database, self.owners)
        with self.database.session() as session:
            self.assertEqual(session.scalars(
                select(User.id)).all(), [outsider])
            self.assertEqual(session.scalars(
                select(Folder.id)).all(), [folder])
            self.assertEqual(session.scalars(select(File.id)).all(), [file])


class FolderAcceptanceSafetyTests(unittest.TestCase):
    """Test real-verification guards without invoking Docker or a PostgreSQL connection."""

    def test_migrations_reject_non_generated_names(self):
        from tests import folders_live
        with patch.object(folders_live.subprocess, "run") as run:
            for name in ("atlas", "postgres", "atlas_folders_", "atlas_folders_"+"z"*32,
                         "atlas_folders_"+"a"*33, 'atlas_folders_";DROP DATABASE atlas'):
                with self.assertRaises((AssertionError, ValueError)):
                    folders_live.migrate(name)
            run.assert_not_called()

    def test_disposable_failure_after_creation_always_drops_generated_database(self):
        from tests import folders_live
        admin = Mock()
        connection = Mock()
        scope = Mock(__enter__=Mock(return_value=connection),
                     __exit__=Mock(return_value=False))
        admin.connect.return_value = scope
        with patch.object(folders_live, "create_engine", return_value=admin), patch.object(
                folders_live, "migrate", side_effect=RuntimeError("injected")) as migrate:
            with self.assertRaisesRegex(RuntimeError, "injected"):
                folders_live.main()
        name = migrate.call_args.args[0]
        folders_live.validate(name)
        self.assertEqual([str(call.args[0]) for call in connection.execute.call_args_list], [
            f'CREATE DATABASE "{name}"', f'DROP DATABASE "{name}" WITH (FORCE)'])
        admin.dispose.assert_called_once_with()

    def test_fixture_failure_attempts_scoped_cleanup(self):
        from tests import folders_acceptance
        database = Mock()
        database.session.return_value.__enter__ = Mock(return_value=Mock())
        database.session.return_value.__exit__ = Mock(return_value=False)
        with patch.object(folders_acceptance.Password, "hash", side_effect=RuntimeError("injected")), patch.object(
                folders_acceptance, "cleanup") as cleanup:
            with self.assertRaisesRegex(RuntimeError, "injected"):
                with folders_acceptance.actors(database, []):
                    self.fail("Failed fixture yielded")
        cleanup.assert_called_once()
        identities = cleanup.call_args.args[1]
        self.assertEqual(len(set(identities)), 2)
        self.assertTrue(all(isinstance(identifier, UUID)
                        for identifier in identities))
