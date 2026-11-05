"""Opt-in real PostgreSQL/Qdrant failure acceptance; no runtime injection controls."""
import os
import sys
import json
import subprocess
from uuid import UUID, uuid4
from unittest.mock import patch
from fastapi.testclient import TestClient

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, event, select, text

from app.core.runtime import storage
from app.core.constants import constants

from app.models.postgres import File
from app.db.postgres import Database, url

from app.pipeline.upload import ready
from app.pipeline.extraction import TextExtractionError

from app.main import app

from tests.folders_acceptance import actors
from tests.uploads_acceptance import acceptance, scope


def validate(name: str) -> None:
    """Restrict database creation/deletion to this helper's generated UUID namespace."""
    assert name.startswith("atlas_uploads_")
    suffix = name.removeprefix("atlas_uploads_")
    assert len(suffix) == 32 and UUID(hex=suffix).hex == suffix
    assert name != constants.postgres.POSTGRES_DB


def faults(database: Database, client: TestClient) -> None:
    """Inject real partial writes and finalization faults through local patched boundaries."""
    services = storage()
    with actors(database, []) as users:
        try:
            response = client.post(
                "/auth/login", json={"email": users[0].email, "password": users[0].password})
            assert response.status_code == 200
            headers = {"Authorization": "Bearer " +
                       response.json()["access_token"]}

            def post():
                return client.post("/files", headers=headers, data={"name": "Fault probe"},
                                   files={"file": ("fault.md", b"# Synthetic\n\nFailure acceptance source.")})

            def rows():
                with database.session() as session:
                    return [(file.id, file.status) for file in session.scalars(
                        select(File).where(File.owner_id == users[0].id))]

            response = client.post(
                "/auth/login", json={"email": users[1].email, "password": users[1].password})
            assert response.status_code == 200
            survivor = client.post("/files", headers={"Authorization": "Bearer " +
                                                      response.json()["access_token"]},
                                   data={"name": "Unrelated survivor"},
                                   files={"file": ("survivor.md", b"# Synthetic\n\nPreserve unrelated vectors.")})
            assert survivor.status_code == 201
            identifier = UUID(survivor.json()["id"])
            preserved, cursor = services.client.scroll(
                services.collection, scroll_filter=scope(identifier), limit=100,
                with_payload=True, with_vectors=True)
            assert preserved and cursor is None
            count = services.client.count(
                services.collection, exact=True).count
            with patch("app.pipeline.ingestion.extract", side_effect=TextExtractionError("injected")):
                assert post().status_code == 400
            assert rows() == []

            with patch.object(services.provider, "embed", side_effect=RuntimeError("injected")):
                assert post().status_code == 500
            assert rows() == [] and services.client.count(
                services.collection, exact=True).count == count

            write = services.client.upsert

            def partial(*args, **kwargs):
                write(*args, **kwargs)
                raise ConnectionError("injected after real write")

            with patch.object(services.client, "upsert", side_effect=partial):
                assert post().status_code == 503
            assert rows() == [] and services.client.count(
                services.collection, exact=True).count == count

            for uncertain in (False, True):
                with patch.object(services.client, "upsert", side_effect=partial):
                    if uncertain:
                        with patch.object(services, "delete", side_effect=ConnectionError("injected")):
                            assert post().status_code == 503
                    else:
                        assert post().status_code == 503
                remaining = rows()
                assert bool(remaining) == uncertain
                for identifier, status in remaining:
                    assert status == "processing"
                    assert services.client.count(
                        services.collection, count_filter=scope(identifier), exact=True).count > 0
                    services.delete(identifier)
                    with database.session() as session:
                        file = session.get(File, identifier)
                        session.delete(file)
                        session.commit()

            for ambiguous in (False, True):
                def finalization(identifier, owner):
                    if ambiguous:
                        ready(identifier, owner)
                    raise SQLAlchemyError("injected commit acknowledgement")

                with patch("app.pipeline.upload.ready", side_effect=finalization):
                    assert post().status_code == 500
                assert rows() == []
                assert services.client.count(
                    services.collection, exact=True).count == count

            for uncertain in (False, True):
                failed = False

                def reject_ready(session):
                    nonlocal failed
                    if not failed and any(isinstance(item, File) and item.status == "ready"
                                          for item in session.identity_map.values()):
                        failed = True
                        raise SQLAlchemyError(
                            "injected ready transaction commit failure")

                event.listen(Session, "before_commit", reject_ready)
                try:
                    if uncertain:
                        with patch.object(services, "delete", side_effect=ConnectionError("injected")):
                            assert post().status_code == 500
                    else:
                        assert post().status_code == 500
                    assert failed
                finally:
                    event.remove(Session, "before_commit", reject_ready)
                remaining = rows()
                assert bool(remaining) == uncertain
                for identifier, status in remaining:
                    assert status == "processing"
                    assert services.client.count(
                        services.collection, count_filter=scope(identifier), exact=True).count > 0
                    services.delete(identifier)
                    with database.session() as session:
                        file = session.get(File, identifier)
                        assert file is not None
                        session.delete(file)
                        session.commit()
                assert services.client.count(
                    services.collection, exact=True).count == count
            remaining, cursor = services.client.scroll(
                services.collection, scroll_filter=scope(UUID(survivor.json()["id"])), limit=100,
                with_payload=True, with_vectors=True)
            assert remaining == preserved and cursor is None
        finally:
            with database.session() as session:
                identifiers = session.scalars(
                    select(File.id).where(File.owner_id.in_([user.id for user in users]))).all()
            for identifier in identifiers:
                services.delete(identifier)


def main() -> None:
    """Migrate only a disposable database, use real configured Qdrant, then remove scoped residue."""
    admin = create_engine(url(constants.postgres).set(database="postgres"),
                          isolation_level="AUTOCOMMIT", hide_parameters=True)
    name = "atlas_uploads_" + uuid4().hex
    validate(name)
    database = None
    created = False
    try:
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                                env={**os.environ, "POSTGRES_DB": name}, capture_output=True)
        assert result.returncode == 0, "Disposable upload migration failed; diagnostics suppressed"
        engine = create_engine(url(constants.postgres).set(
            database=name), hide_parameters=True)
        database = Database(engine, sessionmaker(bind=engine))
        with patch("app.core.lifespan.prepare", return_value=database), TestClient(app) as client:
            result = acceptance(database, client, storage(), [])
            faults(database, client)
        print(json.dumps({**result, "real_failure_compensation": "passed",
              "head": "0002_drive"}, sort_keys=True))
    finally:
        if database is not None:
            database.close()
        try:
            if created:
                validate(name)
                with admin.connect() as connection:
                    connection.execute(
                        text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        finally:
            admin.dispose()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"uploads_live": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
