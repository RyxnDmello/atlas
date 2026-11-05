"""Opt-in real PostgreSQL API acceptance; only a generated disposable DB is written."""
import os
import sys
import json
import subprocess
from uuid import UUID, uuid4
from unittest.mock import patch
from fastapi.testclient import TestClient

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from app.core.cors import configure_cors
from app.core.constants import constants

from app.db.postgres import Database, url
from app.routers.auth import router as auth

from tests.drive_live import constraints, schema
from tests.test_21_folders import application
from tests.folders_acceptance import acceptance


def validate(name: str) -> None:
    """Never migrate or drop a configured or externally supplied database name."""
    assert name.startswith("atlas_folders_")
    suffix = name.removeprefix("atlas_folders_")
    assert len(suffix) == 32 and UUID(hex=suffix).hex == suffix
    assert name != constants.postgres.POSTGRES_DB


def migrate(name: str) -> None:
    validate(name)
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                            env={**os.environ, "POSTGRES_DB": name}, capture_output=True)
    assert result.returncode == 0, "Disposable folder migration failed; diagnostics suppressed"


def main() -> None:
    """Check catalog/backstops plus real transactions/HTTP and always drop the disposable DB."""
    admin = create_engine(url(constants.postgres).set(database="postgres"), isolation_level="AUTOCOMMIT",
                          hide_parameters=True, connect_args={"connect_timeout": 5})
    name = "atlas_folders_"+uuid4().hex
    validate(name)
    database = None
    created = False
    try:
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        migrate(name)
        engine = create_engine(url(constants.postgres).set(
            database=name), hide_parameters=True)
        database = Database(engine, sessionmaker(bind=engine))
        schema(database)
        app = application()
        app.include_router(auth)
        configure_cors(app)
        with patch("app.pipeline.drive.postgres", return_value=database), patch(
                "app.pipeline.auth.current.postgres", return_value=database), patch(
                "app.pipeline.auth.login.postgres", return_value=database), TestClient(app) as client:
            result = acceptance(database, client, [])
        constraints(database)
        schema(database)
        print(json.dumps({**result, "postgres_constraints": "passed",
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
        print(json.dumps({"folders_live": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
