"""Opt-in running-server acceptance; execute only after the Stage 2 green flag."""
import sys
import json
from httpx import Client

from app.core.constants import constants

from app.db.postgres import prepare
from app.db.qdrant import create_client

from app.pipeline.storage import Storage
from app.pipeline.embeddings.bge_m3 import get_bge_m3_embedder

from tests.folders_acceptance import fingerprint
from tests.files_acceptance import acceptance, vectors


def main() -> None:
    """Compare every canonical row and vector before/after exact synthetic cleanup."""
    database = prepare()
    qdrant = create_client()
    try:
        services = Storage(get_bge_m3_embedder(), qdrant,
                           constants.qdrant.QDRANT_COLLECTION)
        before, points = fingerprint(database), vectors(services)
        with Client(base_url=f"http://127.0.0.1:{constants.app.PORT}", timeout=180) as client:
            result = acceptance(database, client, services, [])
        assert fingerprint(database) == before
        assert vectors(services) == points
        print(json.dumps({**result, "canonical_and_vector_state": "preserved",
              "head": "0002_drive"}, sort_keys=True))
    finally:
        qdrant.close()
        database.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"files_http": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
