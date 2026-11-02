"""Opt-in running-server acceptance; capture a fresh PG/Qdrant baseline before invocation."""
import sys
import json
import subprocess

from httpx import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.constants import constants

from app.db.postgres import Database, url

from tests.folders_acceptance import acceptance, fingerprint


def main() -> None:
    """Exercise the running API, remove only synthetic state and check all canonical rows."""
    engine = create_engine(url(
        constants.postgres), hide_parameters=True, connect_args={"connect_timeout": 5})
    database = Database(engine, sessionmaker(bind=engine))
    try:
        private = [constants.postgres.POSTGRES_PASSWORD.get_secret_value(),
                   constants.auth.AUTH_ACCESS_TOKEN_SECRET.get_secret_value()]
        before = fingerprint(database)
        with Client(base_url=f"http://127.0.0.1:{constants.app.PORT}", timeout=30) as client:
            result = acceptance(database, client, private)
        assert fingerprint(
            database) == before, "Canonical state changed after synthetic cleanup"
        logs = subprocess.run(["docker", "compose", "--env-file", ".env", "-f", "docker-compose.yml",
                               "logs", "--no-color", "server"], capture_output=True, check=True)
        assert not any(value.encode() in logs.stdout +
                       logs.stderr for value in private if value)
        print(json.dumps({**result, "canonical_state": "preserved", "credential_log_scan": "passed",
                          "head": "0002_drive"}, sort_keys=True))
    finally:
        database.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"folders_http": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
