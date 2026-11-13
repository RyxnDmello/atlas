"""Owner/ready authorization with isolated SQLAlchemy and actual in-memory Qdrant."""
import unittest
from uuid import UUID, uuid4
from collections.abc import Iterator
from unittest.mock import Mock, patch
from qdrant_client import QdrantClient
from fastapi.testclient import TestClient
from contextlib import ExitStack, contextmanager
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.pipeline import files
from app.pipeline.auth.access import Access
from app.pipeline.generation.prompt import FALLBACK

from app.schemas.pipeline import Chunk
from app.models.postgres import Base, User

from app.errors.postgres import PostgresOperationError

from app.main import app

from tests.test_10_ask import events
from tests.rag import retrieved, seed
from tests.uploads import environment
from tests.test_05_upload_storage import Provider


class RagAuthorizationTests(unittest.TestCase):
    """Keep production auth, SQL predicates, retrieval and native SSE under test."""

    def setUp(self):
        self.scope = ExitStack()
        self.addCleanup(self.scope.close)
        self.database, self.user, self.headers = self.scope.enter_context(
            environment())
        self.provider = Provider()
        self.qdrant = QdrantClient(
            ":memory:", force_disable_check_same_thread=True)
        self.scope.enter_context(
            patch("app.core.lifespan.prepare", return_value=self.database))
        self.scope.enter_context(
            patch("app.core.lifespan.create_client", return_value=self.qdrant))
        self.scope.enter_context(
            patch("app.core.lifespan.get_bge_m3_embedder", return_value=self.provider))
        self.http = self.scope.enter_context(TestClient(app))
        now = datetime.now(timezone.utc)
        self.other = uuid4()
        with self.database.session() as session:
            session.add(User(id=self.other, name="Other", email="rag@example.invalid",
                             password="synthetic-placeholder", verified_at=now,
                             created_at=now, updated_at=now))
            session.commit()
        self.tokens = [self.headers, {
            "Authorization": "Bearer " + Access().issue(self.other)}]
        self.ids = {}
        from app.core.runtime import storage
        self.services = storage()
        for owner in (self.user.id, self.other):
            for status in ("ready", "processing", "deleting"):
                identifier = uuid4()
                self.ids[owner, status] = identifier
                seed(self.database, owner, identifier, status)
                self.index(identifier)
        self.empty, self.orphan = uuid4(), uuid4()
        seed(self.database, self.user.id, self.empty)
        self.index(self.orphan)
        self.provider.calls.clear()
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

    def index(self, identifier: UUID) -> None:
        self.services.write([Chunk(id=str(identifier), text="Synthetic " + str(identifier),
                                   display_text="Trusted source", index=0, count=12)])

    def request(self, route, identifier, headers=None, **kwargs):
        return self.http.post(f"/files/{identifier}/{route}",
                              headers=self.headers if headers is None else headers,
                              json=kwargs.pop("body", {"question": "question"}), **kwargs)

    def snapshot(self):
        with self.database.engine.connect() as connection:
            return {name: connection.execute(select(table).order_by(table.c.id)).all()
                    for name, table in Base.metadata.tables.items()}

    def test_missing_invalid_expired_credentials_precede_lookup(self):
        with patch("app.pipeline.auth.access.datetime", wraps=datetime) as clock:
            clock.now.return_value = datetime.now(
                timezone.utc) - timedelta(days=1)
            expired = Access().issue(self.user.id)
        with patch("app.routers.files.ready") as guard, patch("app.routers.files.retrieve") as search:
            for route in ("ask",):
                for headers in ({}, {"Authorization": "Bearer invalid"}, {"Authorization": "Bearer " + expired}):
                    response = self.request(route, self.empty, headers)
                    self.assertEqual(response.status_code, 401)
                    self.assertEqual(
                        response.json()["code"], "INVALID_ACCESS_TOKEN")
                    self.assertTrue(
                        response.headers["content-type"].startswith("application/json"))
            guard.assert_not_called()
            search.assert_not_called()

    def test_privacy_status_and_orphan_denials_never_enter_rag(self):
        cases = [(uuid4(), 404), (self.orphan, 404)]
        cases += [(self.ids[self.other, status], 404)
                  for status in ("ready", "processing", "deleting")]
        cases += [(self.ids[self.user.id, status], 409)
                  for status in ("processing", "deleting")]
        before = self.snapshot()
        from tests.files_acceptance import vectors
        points = vectors(self.services)
        with patch("app.routers.files.retrieve") as search, patch.object(self.provider, "embed") as embed, patch.object(
                self.qdrant, "query_points") as query, patch("app.routers.files.GeminiFlashProvider") as provider, patch(
                "app.routers.files.GroundedStream") as stream:
            for route in ("ask",):
                for identifier, status in cases:
                    response = self.request(route, identifier)
                    self.assertEqual(response.status_code, status)
                    self.assertEqual(response.json(), {"error": "File not found", "code": "FILE_NOT_FOUND"}
                                     if status == 404 else {"error": "File is not ready", "code": "FILE_NOT_READY"})
                    self.assertTrue(
                        response.headers["content-type"].startswith("application/json"))
                    self.assertNotIn("event:", response.text)
            for call in (search, embed, query, provider, stream):
                call.assert_not_called()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(vectors(self.services), points)

    def test_both_owners_query_and_stream_with_closed_read_sessions(self):
        from tests.files_acceptance import vectors
        from tests.test_09_grounded_generation import Provider as Generator
        before, points = self.snapshot(), vectors(self.services)
        original = self.services.provider.embed

        def encode(texts):
            self.assertEqual(self.depth, 0)
            return original(texts)

        def generate(prompt, chunks):
            self.assertEqual(self.depth, 0)
            yield "Supported[[cite:0]]"
            self.assertEqual(self.depth, 0)

        for owner, headers in zip((self.user.id, self.other), self.tokens, strict=True):
            identifier = self.ids[owner, "ready"]
            provider = Generator([])
            with patch.object(self.provider, "embed", side_effect=encode), patch.object(
                    provider, "stream_generate", side_effect=generate), patch(
                    "app.routers.files.GeminiFlashProvider", return_value=provider), patch(
                    "app.routers.files.ready", wraps=files.ready) as guard:
                results = retrieved(
                    self.database, self.services, owner, identifier)
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0].file_id, identifier)
                self.assertEqual(
                    results[0].text, "Synthetic " + str(identifier))
                response = self.request("ask", identifier, headers)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(
                    response.headers["content-type"].startswith("text/event-stream"))
                wire = events(response.iter_lines())
                self.assertEqual([name for name, _ in wire], [
                                 "answer", "citations", "done"])
                self.assertEqual(wire[1][1]["citations"]
                                 [0]["excerpt"], "Trusted source")
                self.assertEqual(guard.call_count, 1)
                guard.assert_called_with(owner, identifier)
            foreign = self.ids[self.other if owner ==
                               self.user.id else self.user.id, "ready"]
            for route in ("ask",):
                self.assertEqual(self.request(
                    route, foreign, headers).status_code, 404)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(vectors(self.services), points)

    def test_owned_ready_unindexed_keeps_empty_query_and_fallback(self):
        with patch("app.routers.files.GeminiFlashProvider") as provider:
            self.assertEqual(
                retrieved(self.database, self.services, self.user.id, self.empty), [])
            response = self.request("ask", self.empty)
            self.assertEqual(events(response.iter_lines()), [("answer", {"text": FALLBACK}),
                             ("citations", {"citations": []}), ("done", {"status": "completed"})])
            provider.assert_not_called()

    def test_guard_is_read_only_scoped_unlocked_and_sanitizes_sql_failures(self):
        session = Mock(spec=Session)
        session.scalar.return_value = Mock(id=self.empty, status="ready")
        with patch.object(self.database, "session") as context:
            context.return_value.__enter__.return_value = session
            self.assertEqual(files.ready(self.user.id, self.empty), self.empty)
        statement = session.scalar.call_args.args[0]
        self.assertEqual(set(statement.compile().params.values()), {
                         self.empty, self.user.id})
        self.assertIn("files.id =", str(statement))
        self.assertIn("files.owner_id =", str(statement))
        self.assertNotIn("FOR UPDATE", str(statement))
        session.commit.assert_not_called()
        session.flush.assert_not_called()
        with patch.object(self.database, "session", side_effect=SQLAlchemyError("private SQL")):
            with self.assertRaises(PostgresOperationError):
                files.ready(self.user.id, self.empty)

    def test_pg_failure_is_json_before_sse_and_never_starts_rag(self):
        with patch("app.routers.files.ready", side_effect=PostgresOperationError()), patch(
                "app.routers.files.retrieve") as search, patch("app.routers.files.GroundedStream") as stream:
            for route in ("ask",):
                response = self.request(route, self.empty)
                self.assertEqual(response.status_code, 500)
                self.assertEqual(
                    response.json()["code"], "POSTGRES_OPERATION_FAILED")
                self.assertTrue(
                    response.headers["content-type"].startswith("application/json"))
            search.assert_not_called()
            stream.assert_not_called()


class RagAcceptanceHelperTests(unittest.TestCase):
    """Dry-run live helper behavior and cleanup with isolated stores only."""

    def test_disposable_namespace_guards(self):
        from tests.rag_live import validate
        validate("atlas_rag_" + uuid4().hex)
        for name in ("postgres", "atlas_rag_", "atlas_rag_invalid", "atlas_files_" + uuid4().hex):
            with self.assertRaises((AssertionError, ValueError)):
                validate(name)

    def test_acceptance_and_failure_cleanup_locally(self):
        from contextlib import closing
        from qdrant_client.http.models import Distance, VectorParams
        from app.core.runtime import activate
        from app.pipeline.storage import Storage
        from app.models.postgres import File
        from tests.rag_acceptance import acceptance
        from tests.files_acceptance import vectors
        with environment() as (database, user, headers), closing(QdrantClient(
                ":memory:", force_disable_check_same_thread=True)) as qdrant:
            provider = Provider()
            qdrant.create_collection("rag-helper", vectors_config=VectorParams(
                size=provider.dimension, distance=Distance.COSINE))
            services = Storage(provider, qdrant, "rag-helper")

            def index(content, filename, extension, identifier):
                chunks = [Chunk(id=str(identifier), text=content.decode(),
                                display_text=content.decode(), index=0, count=12)]
                services.write(chunks)
                return chunks

            with activate(services, database), patch("app.pipeline.upload.ingest", side_effect=index), closing(TestClient(app)) as client:
                baseline = vectors(services)
                result = acceptance(
                    database, client, services, [], generation=True)
                self.assertEqual(result["ask_generation"], "deterministic")
                self.assertEqual(vectors(services), baseline)
                with database.session() as session:
                    self.assertEqual(session.scalars(
                        select(User.id)).all(), [user.id])
                    self.assertIsNone(session.scalar(select(File)))
                with patch("app.routers.files.retrieve", side_effect=PostgresOperationError()), self.assertRaises(AssertionError):
                    acceptance(database, client, services, [], generation=True)
                self.assertEqual(vectors(services), baseline)
                with database.session() as session:
                    self.assertEqual(session.scalars(
                        select(User.id)).all(), [user.id])
                    self.assertIsNone(session.scalar(select(File)))


if __name__ == "__main__":
    unittest.main()
