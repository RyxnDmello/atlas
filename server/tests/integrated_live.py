"""Opt-in disposable PostgreSQL/full integrated verification; Stage 2 approval required."""

import os
import sys
import json
import subprocess
from uuid import UUID, uuid4
from contextlib import closing
from unittest.mock import patch
from fastapi.testclient import TestClient

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from app.core.runtime import storage
from app.core.constants import constants

from app.db.postgres import Database, url

from app.main import app

from tests.files_acceptance import vectors
from tests.folders_acceptance import fingerprint
from tests.integrated_acceptance import acceptance


def validate(name: str) -> None:
    """Allow create/drop only in this helper's generated UUID database namespace."""
    assert name.startswith("atlas_integrated_")
    suffix = name.removeprefix("atlas_integrated_")
    assert len(suffix) == 32 and UUID(hex=suffix).hex == suffix
    assert name != constants.postgres.POSTGRES_DB


def main() -> None:
    """Migrate an isolated DB and compare full canonical/vector state after scoped cleanup."""
    name = "atlas_integrated_" + uuid4().hex
    validate(name)
    admin = create_engine(url(constants.postgres).set(database="postgres"),
                          isolation_level="AUTOCOMMIT", hide_parameters=True)
    database = None
    created = False
    clean = True
    try:
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        migration = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                                   env={**os.environ, "POSTGRES_DB": name}, capture_output=True)
        assert migration.returncode == 0, "Disposable integrated migration failed; diagnostics suppressed"
        engine = create_engine(url(constants.postgres).set(
            database=name), hide_parameters=True)
        database = Database(engine, sessionmaker(bind=engine))
        before = fingerprint(database)
        with patch("app.core.lifespan.prepare", return_value=database), TestClient(app) as client:
            services = storage()
            points = vectors(services)

            clean = False
            try:
                with closing(TestClient(app)) as second:
                    result = acceptance(
                        database, (client, second), services, [], generation=True)
                for path in ('/system/health', '/system/health/databases'):
                    response = client.get(path)
                    assert response.status_code == 200
                    if path.endswith('databases'):
                        assert response.json()[
                            'postgres']['status'] == 'PostgreSQL Healthy'
                        assert response.json()[
                            'qdrant']['status'] == 'Qdrant Healthy'
            finally:
                clean = vectors(services) == points and fingerprint(
                    database) == before
                assert clean, 'Integrated cleanup incomplete; preserve recovery database'
        print(json.dumps({**result, "canonical_and_vector_state": "preserved",
              "head": "0002_drive"}, sort_keys=True))
    finally:
        if database is not None:
            database.close()
        try:
            if created and clean:
                validate(name)
                with admin.connect() as connection:
                    connection.execute(
                        text(f'DROP DATABASE "{name}" WITH (FORCE)'))
            elif created:
                print(json.dumps(
                    {'recovery_database': name, 'cleanup': 'incomplete; retained for scoped recovery'}), file=sys.stderr)
        finally:
            admin.dispose()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"integrated_live": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
