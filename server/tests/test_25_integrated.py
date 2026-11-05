"""Isolated acceptance dry runs prove helper safety, not real PostgreSQL or deployment."""
import unittest
from uuid import uuid4
from datetime import timezone
from unittest.mock import patch
from contextlib import ExitStack, closing
from fastapi.testclient import TestClient
from sqlalchemy import event, select, text

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.runtime import activate
from app.pipeline.storage import Storage

from app.schemas.pipeline import Chunk
from app.models.postgres import File, Folder, User, Verification

from app.main import app

from tests.uploads import environment
from tests.files_acceptance import vectors
from tests.folders_acceptance import fingerprint
from tests.test_05_upload_storage import Provider
from tests.integrated_acceptance import acceptance, cleanup


class IntegratedAcceptanceTests(unittest.TestCase):
    """Exercise actual auth and drive APIs while keeping every store/model isolated."""

    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.database, self.original, _ = self.stack.enter_context(
            environment())
        with self.database.engine.begin() as connection:
            connection.execute(
                text('CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)'))
            connection.execute(
                text("INSERT INTO alembic_version VALUES ('0002_drive')"))
        qdrant = self.stack.enter_context(closing(QdrantClient(
            ":memory:", force_disable_check_same_thread=True)))
        provider = Provider()
        qdrant.create_collection("integrated-helper", vectors_config=VectorParams(
            size=provider.dimension, distance=Distance.COSINE))
        self.storage = Storage(provider, qdrant, "integrated-helper")
        self.stack.enter_context(activate(self.storage, self.database))
        self.clients = (self.stack.enter_context(closing(TestClient(app))),
                        self.stack.enter_context(closing(TestClient(app))))

        def aware(verification, context):
            verification.expires_at = verification.expires_at.replace(
                tzinfo=timezone.utc)

        event.listen(Verification, "load", aware)
        self.stack.callback(event.remove, Verification, "load", aware)

        def index(content, filename, extension, identifier):
            chunks = [Chunk(id=str(identifier), text=content.decode(), display_text=content.decode(),
                            index=0, count=16, page=None, heading=f"Owner {0 if 'Owner 0' in content.decode() else 1}", section=None)]
            self.storage.write(chunks)

            return chunks

        self.index = self.stack.enter_context(
            patch("app.pipeline.ingestion.ingest", side_effect=index))
        self.baseline = fingerprint(self.database), vectors(self.storage)

    def preserved(self):
        self.assertEqual((fingerprint(self.database),
                         vectors(self.storage)), self.baseline)
        with self.database.session() as session:
            self.assertEqual(session.scalars(
                select(User.id)).all(), [self.original.id])
            self.assertIsNone(session.scalar(select(File)))
            self.assertIsNone(session.scalar(select(Folder)))

    def test_continuous_journey_and_exact_cleanup(self):
        result = acceptance(self.database, self.clients,
                            self.storage, [], generation=True)
        self.assertEqual(result["integrated_journey"], "passed")
        self.assertEqual(result["ask_generation"], "deterministic")
        self.assertEqual(self.index.call_count, 3)
        self.preserved()

    def test_http_mode_never_constructs_live_provider(self):
        with patch("app.routers.files.GeminiFlashProvider", side_effect=AssertionError("Live provider forbidden")) as provider:
            result = acceptance(self.database, self.clients, self.storage, [])
            provider.assert_not_called()
        self.assertEqual(result["ask_generation"], "empty_fallback_only")
        self.preserved()

    def test_partial_registration_acknowledgement_failure_cleanup(self):
        original = self.clients[0].post

        def interrupted(path, *args, **kwargs):
            response = original(path, *args, **kwargs)
            if path == "/auth/register":
                self.assertEqual(response.status_code, 201)
                raise RuntimeError(
                    "Synthetic registration acknowledgement lost")

            return response

        with patch.object(self.clients[0], "post", side_effect=interrupted), self.assertRaises(RuntimeError):
            acceptance(self.database, self.clients,
                       self.storage, [], generation=True)
        self.preserved()

    def test_nested_upload_acknowledgement_failure_cleanup(self):
        original = self.clients[0].post
        uploads = 0

        def interrupted(path, *args, **kwargs):
            nonlocal uploads
            response = original(path, *args, **kwargs)
            if path == "/files" and response.status_code == 201:
                uploads += 1
                if uploads == 2:
                    raise RuntimeError(
                        "Synthetic nested upload acknowledgement lost")

            return response

        with patch.object(self.clients[0], "post", side_effect=interrupted), self.assertRaises(RuntimeError):
            acceptance(self.database, self.clients,
                       self.storage, [], generation=True)
        self.assertEqual(uploads, 2)
        self.preserved()

    def test_cleanup_rejects_non_synthetic_identity_scope(self):
        for emails in ([], [self.original.email], [self.original.email, "integrated-foreign@example.com"]):
            with self.assertRaises(AssertionError):
                cleanup(self.database, self.storage, emails, set())
        self.preserved()

    def test_vector_cleanup_failure_retains_canonical_recovery_state(self):
        original = self.clients[0].post

        def interrupted(path, *args, **kwargs):
            response = original(path, *args, **kwargs)
            if path == "/files" and response.status_code == 201:
                raise RuntimeError("Synthetic upload acknowledgement lost")

            return response

        with patch.object(self.clients[0], "post", side_effect=interrupted), patch.object(
                self.storage, "delete", side_effect=RuntimeError("Synthetic cleanup unavailable")), self.assertRaises(RuntimeError):
            acceptance(self.database, self.clients,
                       self.storage, [], generation=True)
        with self.database.session() as session:
            emails = session.scalars(select(User.email).where(
                User.id != self.original.id)).all()
            self.assertEqual(len(emails), 2)
            self.assertIsNotNone(session.scalar(select(File)))
            self.assertIsNotNone(session.scalar(select(Folder)))
        self.assertNotEqual(vectors(self.storage), self.baseline[1])
        cleanup(self.database, self.storage, list(emails), set())
        self.preserved()

    def test_generation_preparation_failure_cleanup(self):
        with patch("app.routers.files.GroundedStream", side_effect=ValueError("Synthetic preparation failure")), self.assertRaises(AssertionError):
            acceptance(self.database, self.clients,
                       self.storage, [], generation=True)
        self.assertEqual(self.index.call_count, 3)
        self.preserved()

    def test_disposable_namespace_guard(self):
        from tests.integrated_live import validate
        validate("atlas_integrated_" + uuid4().hex)
        for name in ("postgres", "atlas_integrated_", "atlas_integrated_invalid", "atlas_rag_" + uuid4().hex):
            with self.assertRaises((AssertionError, ValueError)):
                validate(name)


if __name__ == "__main__":
    unittest.main()
