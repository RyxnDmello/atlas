"""Opt-in disposable PostgreSQL/actual Qdrant verification; Stage 2 approval required."""

import os
import sys
import json
import subprocess
from uuid import UUID, uuid4
from unittest.mock import patch
from fastapi.testclient import TestClient

from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from app.core.runtime import storage
from app.core.constants import constants

from app.db.postgres import Database, url
from app.pipeline.retrieval import retrieve

from app.main import app

from tests.files_acceptance import vectors
from tests.rag_acceptance import acceptance
from tests.folders_acceptance import fingerprint


def validate(name: str) -> None:
    """Allow create/drop only in this helper's generated UUID database namespace."""
    assert name.startswith("atlas_rag_")
    suffix = name.removeprefix("atlas_rag_")
    assert len(suffix) == 32 and UUID(hex=suffix).hex == suffix
    assert name != constants.postgres.POSTGRES_DB


def main() -> None:
    """Migrate an isolated DB and compare full canonical/vector state after scoped cleanup."""
    name = "atlas_rag_" + uuid4().hex
    validate(name)
    admin = create_engine(url(constants.postgres).set(database="postgres"),
                          isolation_level="AUTOCOMMIT", hide_parameters=True)
    database = None
    created = False
    try:
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        migration = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                                   env={**os.environ, "POSTGRES_DB": name}, capture_output=True)
        assert migration.returncode == 0, "Disposable RAG migration failed; diagnostics suppressed"
        engine = create_engine(url(constants.postgres).set(
            database=name), hide_parameters=True)
        database = Database(engine, sessionmaker(bind=engine))
        before = fingerprint(database)
        with patch("app.core.lifespan.prepare", return_value=database), TestClient(app) as client:
            services = storage()
            points = vectors(services)

            def separated(*args):
                assert isinstance(
                    engine.pool, QueuePool) and engine.pool.checkedout() == 0

                return retrieve(*args)

            with patch("app.routers.files.retrieve", side_effect=separated):
                result = acceptance(
                    database, client, services, [], generation=True)
            assert vectors(services) == points
            assert fingerprint(database) == before
        print(json.dumps({**result, "canonical_and_vector_state": "preserved",
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
        print(json.dumps({"rag_live": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
