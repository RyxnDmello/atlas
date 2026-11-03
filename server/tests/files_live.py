"""Opt-in disposable PostgreSQL and real Qdrant acceptance; Stage 2 approval required."""
import os
import sys
import json
import subprocess
from uuid import UUID, uuid4
from unittest.mock import patch
from time import monotonic, sleep
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, event, select, text

from app.core.runtime import storage
from app.core.constants import constants

from app.models.postgres import File
from app.schemas.drive.metadata import FilePatch

from app.pipeline import files
from app.db.postgres import Database, url

from app.errors.file import FileNotReadyError

from app.main import app

from tests.uploads_acceptance import scope
from tests.folders_acceptance import actors, fingerprint
from tests.files_acceptance import acceptance, canonical, vectors


def validate(name: str) -> None:
    """Permit CREATE/DROP only for this helper's generated database namespace."""
    assert name.startswith("atlas_files_")
    suffix = name.removeprefix("atlas_files_")
    assert len(suffix) == 32 and UUID(hex=suffix).hex == suffix
    assert name != constants.postgres.POSTGRES_DB


def faults(database: Database, client: TestClient) -> None:
    """Prove durable deleting and both retries with actual Qdrant and commit rejection."""
    services = storage()
    with actors(database, []) as users:
        try:
            headers = []
            for user in users:
                response = client.post(
                    "/auth/login", json={"email": user.email, "password": user.password})
                assert response.status_code == 200
                headers.append({"Authorization": "Bearer " +
                               response.json()["access_token"]})

            def upload(auth):
                response = client.post("/files", headers=auth, data={"name": "Deletion fault probe"},
                                       files={"file": ("fault.md", b"# Synthetic\n\nPreserve unrelated records for seven years.")})
                assert response.status_code == 201

                return UUID(response.json()["id"])

            survivor = upload(headers[1])
            preserved = vectors(services, scope(survivor))
            survivor_row = canonical(database, survivor)
            for fault in ("qdrant", "commit"):
                identifier = upload(headers[0])
                before = vectors(services, scope(identifier))
                cleanup = services.client.delete

                def separated() -> None:
                    if database.engine.dialect.name == "postgresql":
                        pool = database.engine.pool
                        assert isinstance(
                            pool, QueuePool) and pool.checkedout() == 0
                    with database.session() as session:
                        marker = session.get(File, identifier)
                        assert marker is not None and marker.status == "deleting"

                def unavailable(*args, **kwargs):
                    separated()
                    raise ConnectionError("injected")

                def confirmed(*args, **kwargs):
                    separated()

                    return cleanup(*args, **kwargs)

                if fault == "qdrant":
                    with patch.object(services.client, "delete", side_effect=unavailable):
                        response = client.delete(
                            "/files/" + str(identifier), headers=headers[0])
                    assert response.status_code == 503
                    assert vectors(services, scope(identifier)) == before
                else:
                    rejected = False

                    def reject(session: Session) -> None:
                        nonlocal rejected
                        if any(isinstance(item, File) and item.id == identifier for item in session.deleted):
                            rejected = True
                            raise SQLAlchemyError(
                                "injected final delete commit failure")

                    event.listen(Session, "before_commit", reject)
                    try:
                        with patch.object(services.client, "delete", side_effect=confirmed):
                            response = client.delete(
                                "/files/" + str(identifier), headers=headers[0])
                        assert response.status_code == 500 and rejected
                    finally:
                        event.remove(Session, "before_commit", reject)
                    assert services.client.count(
                        services.collection, count_filter=scope(identifier), exact=True).count == 0
                with database.session() as session:
                    file = session.get(File, identifier)
                    assert file is not None and file.status == "deleting"
                listing = client.get("/drive", headers=headers[0])
                assert listing.status_code == 200
                assert any(item["id"] == str(identifier) and item["status"]
                           == "deleting" for item in listing.json()["files"])
                assert client.patch(
                    "/files/" + str(identifier), headers=headers[0], json={"name": "attempt"}).status_code == 409
                assert vectors(services, scope(survivor)) == preserved
                assert canonical(database, survivor) == survivor_row
                response = client.delete(
                    "/files/" + str(identifier), headers=headers[0])
                assert response.status_code == 204 and response.content == b""
                with database.session() as session:
                    assert session.get(File, identifier) is None
                assert services.client.count(
                    services.collection, count_filter=scope(identifier), exact=True).count == 0
                assert vectors(services, scope(survivor)) == preserved
                assert canonical(database, survivor) == survivor_row
        finally:
            with database.session() as session:
                identifiers = session.scalars(select(File.id).where(
                    File.owner_id.in_([user.id for user in users]))).all()
            for identifier in identifiers:
                services.delete(identifier)


def locking(database: Database) -> None:
    """Observe actual PostgreSQL row-lock waits in both metadata/deletion orders."""
    def waiting(blocker: int) -> None:
        deadline = monotonic() + 10
        while monotonic() < deadline:
            with database.engine.connect() as connection:
                blocked = connection.scalar(text(
                    "SELECT EXISTS (SELECT 1 FROM pg_stat_activity "
                    "WHERE :blocker = ANY(pg_blocking_pids(pid)))"), {"blocker": blocker})
            if blocked:
                return
            sleep(0.02)
        raise AssertionError(
            "Expected PostgreSQL row-lock wait was not observed")

    with actors(database, []) as users:
        owner = users[0].id
        for first in ("delete", "patch"):
            identifier = uuid4()
            now = datetime.now(timezone.utc)
            with database.session() as session:
                session.add(File(id=identifier, owner_id=owner, name="Lock probe",
                                 original_name="probe.md", extension="md", size_bytes=1,
                                 status="ready", created_at=now, updated_at=now))
                session.commit()
            with ThreadPoolExecutor(max_workers=1) as pool:
                with database.session() as session:
                    blocker = session.scalar(text("SELECT pg_backend_pid()"))
                    assert isinstance(blocker, int)
                    file = files.owned(session, identifier, owner)
                    assert file is not None
                    if first == "delete":
                        file.status = "deleting"
                        pending = pool.submit(
                            files.update, owner, identifier, FilePatch(name="Blocked patch"))
                    else:
                        file.name = "Committed patch"
                        pending = pool.submit(
                            files.deleting, owner, identifier)
                    try:
                        session.flush()
                        waiting(blocker)
                        assert not pending.done()
                        session.commit()
                    finally:
                        session.rollback()
                if first == "delete":
                    try:
                        pending.result(timeout=10)
                    except FileNotReadyError:
                        pass
                    else:
                        raise AssertionError(
                            "Blocked PATCH ignored committed deleting state")
                else:
                    pending.result(timeout=10)
            with database.session() as session:
                file = session.get(File, identifier)
                assert file is not None and file.status == "deleting"
                assert file.name == (
                    "Lock probe" if first == "delete" else "Committed patch")


def main() -> None:
    """Migrate a guarded disposable DB; clean exact vectors before dropping canonical state."""
    admin = create_engine(url(constants.postgres).set(
        database="postgres"), isolation_level="AUTOCOMMIT", hide_parameters=True)
    name = "atlas_files_" + uuid4().hex
    validate(name)
    database = None
    created = False
    try:
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                                env={**os.environ, "POSTGRES_DB": name}, capture_output=True)
        assert result.returncode == 0, "Disposable file migration failed; diagnostics suppressed"
        engine = create_engine(url(constants.postgres).set(
            database=name), hide_parameters=True)
        database = Database(engine, sessionmaker(bind=engine))
        canonical_before = fingerprint(database)
        with patch("app.core.lifespan.prepare", return_value=database), TestClient(app) as client:
            services = storage()
            before = vectors(services)
            result = acceptance(database, client, services, [])
            faults(database, client)
            locking(database)
            assert vectors(services) == before
            assert fingerprint(database) == canonical_before
        print(json.dumps({**result, "delete_fault_retries": "passed",
              "postgres_row_lock_orders": "passed", "head": "0002_drive"}, sort_keys=True))
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
        print(json.dumps({"files_live": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
