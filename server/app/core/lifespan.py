from time import perf_counter
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.concurrency import run_in_threadpool

from app.core.logging import logger
from app.core.runtime import activate
from app.core.constants import constants

from app.db.postgres import prepare
from app.db.qdrant import create_client, ensure_collection

from app.pipeline.storage import Storage
from app.pipeline.embeddings.bge_m3 import get_bge_m3_embedder


def initialize() -> Storage:
    """Load the cached embedder and validate storage before accepting uploads."""
    started = perf_counter()
    provider = get_bge_m3_embedder()
    loaded = perf_counter()

    client = create_client()

    try:
        ensure_collection(client, constants.qdrant.QDRANT_COLLECTION, provider)
        storage = Storage(provider, client, constants.qdrant.QDRANT_COLLECTION)
    except Exception:
        client.close()
        raise

    logger.info(
        "Upload startup ready: dimension=%d model_seconds=%.3f total_seconds=%.3f",
        provider.dimension, loaded - started, perf_counter() - started,
    )

    return storage


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Prepare required databases off-loop and release all owned resources."""
    postgres = await run_in_threadpool(prepare)

    try:
        storage = await run_in_threadpool(initialize)

        try:
            with activate(storage, postgres):
                yield
        finally:
            await run_in_threadpool(storage.client.close)
    finally:
        await run_in_threadpool(postgres.close)
