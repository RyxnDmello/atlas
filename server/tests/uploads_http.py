"""Opt-in real HTTP acceptance; run only during the separately authorized Docker stage."""
import sys
import json
from httpx import Client

from app.core.constants import constants

from app.db.postgres import prepare
from app.db.qdrant import create_client

from app.pipeline.storage import Storage
from app.pipeline.embeddings.bge_m3 import get_bge_m3_embedder

from tests.uploads_acceptance import acceptance
from tests.folders_acceptance import fingerprint


def main() -> None:
    """Verify the running server against real stores and preserve the post-reset baseline."""
    database = prepare()
    qdrant = create_client()
    try:
        before = fingerprint(database)
        count = qdrant.count(
            constants.qdrant.QDRANT_COLLECTION, exact=True).count
        storage = Storage(get_bge_m3_embedder(), qdrant,
                          constants.qdrant.QDRANT_COLLECTION)
        with Client(base_url=f"http://127.0.0.1:{constants.app.PORT}", timeout=180) as client:
            result = acceptance(database, client, storage, [])
        assert fingerprint(database) == before
        assert qdrant.count(storage.collection, exact=True).count == count
        print(json.dumps({**result, "canonical_state": "preserved",
              "head": "0002_drive"}, sort_keys=True))
    finally:
        qdrant.close()
        database.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"uploads_http": "failed", "category": type(error).__name__,
                          "diagnostics": "suppressed to protect credentials"}), file=sys.stderr)
        sys.exit(1)
