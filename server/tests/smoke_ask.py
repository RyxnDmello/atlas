import sys
import json
import socket
import argparse
from uuid import uuid4
from typing import Literal
from threading import Thread
from unittest.mock import patch
from time import monotonic, sleep
from collections.abc import Iterator
from contextlib import closing, contextmanager

import httpx
import uvicorn
from qdrant_client import QdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchValue

from app.core.constants import constants
from app.core.runtime import storage

from app.pipeline.generation.prompt import FALLBACK

from app.main import app


@contextmanager
def serve(lifespan: Literal["on", "off"] = "on") -> Iterator[str]:
    """Own a loopback HTTP server and close its thread/socket even after a failed check."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]

        server = uvicorn.Server(
            uvicorn.Config(app, log_level="warning", lifespan=lifespan),
        )
        thread = Thread(target=server.run, kwargs={"sockets": [listener]})
        thread.start()

        try:
            deadline = monotonic() + 120
            while not server.started:
                if not thread.is_alive() or monotonic() > deadline:
                    raise RuntimeError(
                        "Local verification server did not start")

                sleep(0.05)

            yield f"http://127.0.0.1:{port}"
        finally:
            server.should_exit = True
            thread.join(timeout=120)
            if thread.is_alive():
                raise RuntimeError("Local verification server did not stop")


def stream(http: httpx.Client, file: str, question: str, case: str) -> tuple[str, list[dict]]:
    """Validate logical events over real HTTP, printing only event counts/indexes/timings."""
    started = monotonic()
    wire: list[tuple[str, dict]] = []
    times: list[float] = []

    with http.stream("POST", f"/files/{file}/ask", json={"question": question}) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        name = "message"
        data: list[str] = []
        for line in response.iter_lines():
            if not line:
                if data:
                    wire.append((name, json.loads("\n".join(data))))
                    times.append(monotonic() - started)

                name, data = "message", []
            elif not line.startswith(":"):
                field, _, value = line.partition(":")
                value = value.removeprefix(" ")
                if field == "event":
                    name = value
                elif field == "data":
                    data.append(value)

    names = [name for name, _ in wire]
    assert len(names) >= 3 and names[:-2] == ["answer"] * (len(names) - 2)
    assert names[-2:] == ["citations", "done"]
    assert all(set(data) == {"text"} and data["text"] for _, data in wire[:-2])
    assert set(wire[-2][1]) == {"citations"}
    assert wire[-1][1] == {"status": "completed"}

    answer = "".join(data["text"] for _, data in wire[:-2])
    citations = wire[-2][1]["citations"]
    assert "[[cite:" not in answer and times[0] < times[-1]

    if case in {"unsupported", "unindexed"}:
        assert answer == FALLBACK and citations == []
    else:
        assert answer.strip() and citations
        query = http.post(f"/files/{file}/query", json={"question": question})
        assert query.status_code == 200
        results = {item["index"]: item for item in query.json()["results"]}
        for citation in citations:
            assert set(citation) == {
                "index", "page", "heading", "section", "excerpt",
            }
            chunk = results[citation["index"]]
            assert all(
                citation[field] == chunk[field]
                for field in ("page", "heading", "section")
            )

    print(
        f"Ask HTTP OK case={case} answers={len(names) - 2} citations={len(citations)} "
        f"indexes={[item['index'] for item in citations]} first={times[0]:.3f}s done={times[-1]:.3f}s"
    )

    return answer, citations


def check(base: str, file: str, other: str, unindexed: str) -> dict[str, list[dict]]:
    """Exercise documented synthetic Luma/Vela fixtures without logging generated/source text."""
    with httpx.Client(base_url=base, timeout=90, trust_env=False) as http:
        for path in ("/system/health", "/system/health/databases"):
            assert http.get(path).status_code == 200

        answer, citations = stream(
            http, file, "How many silver trees does the Luma garden have?", "supported",
        )
        observed = {file: citations}
        assert "two" in answer.lower() or "2" in answer
        assert all("two silver trees" in item["excerpt"] for item in citations)
        stream(
            http, file, "What is the Luma garden's annual maintenance budget in dollars?", "unsupported",
        )

        answer, citations = stream(
            http, other, "How many copper trees does the Vela garden have?", "isolation",
        )
        observed[other] = citations
        assert "nine" in answer.lower() or "9" in answer
        assert all(
            "nine copper trees" in item["excerpt"] and "Luma" not in item["excerpt"]
            for item in citations
        )

        stream(
            http, unindexed, "How many silver trees does the Luma garden have?", "unindexed",
        )

        assert http.post("/files/not-a-uuid/ask",
                         json={"question": "q"}).status_code == 422
        assert http.post(f"/files/{file}/ask",
                         json={"question": " "}).status_code == 422

    return observed


def provenance(observed: dict[str, list[dict]]) -> None:
    """Privately compare all five citation fields to actual stored payloads in the owned app."""
    services = storage()

    for file, citations in observed.items():
        points, _ = services.client.scroll(
            services.collection, limit=100, with_vectors=False, with_payload=True,
            scroll_filter=Filter(must=[
                FieldCondition(key="file_id", match=MatchValue(value=file)),
            ]),
        )
        sources = {
            point.payload["chunk_index"]: point.payload
            for point in points if point.payload is not None
        }

        for citation in citations:
            payload = sources[citation["index"]]
            assert citation == dict(
                index=payload["chunk_index"], page=payload["page"],
                heading=payload["heading"], section=payload["section"],
                excerpt=payload["display_text"],
            )

    print("Ask stored provenance OK")


def outage(base: str, file: str) -> None:
    """Prove pre-stream HTTP failure through real refused Qdrant transport without stopping it."""
    services = storage()

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
        with (
            closing(QdrantClient(
                url=f"http://127.0.0.1:{port}", timeout=1, check_compatibility=False,
            )) as client,
            patch.object(services, "client", client),
            patch("app.routers.files.GeminiFlashProvider") as provider,
            httpx.Client(base_url=base, timeout=30, trust_env=False) as http,
        ):
            for route in ("query", "ask"):
                response = http.post(
                    f"/files/{file}/{route}", json={"question": "synthetic outage check"},
                )
                assert response.status_code == 503
                assert response.headers["content-type"].startswith(
                    "application/json")
                assert response.json() == {
                    "error": "Unable to connect to Qdrant while retrieving chunks",
                    "code": "QDRANT_CONNECTION_FAILED",
                }

            provider.assert_not_called()

    print("Ask/query refused Qdrant transport OK status=503 provider_calls=0")


def hosted(file: str, other: str, unindexed: str) -> None:
    """Own the real configured app/HTTP server and verify existing persistent fixtures read-only."""
    with serve() as base:
        services = storage()
        before = services.client.count(services.collection, exact=True).count

        provenance(check(base, file, other, unindexed))
        outage(base, file)

        after = services.client.count(services.collection, exact=True).count
        assert before == after

        print(
            f"Persistent Qdrant points_before={before} points_after={after}; no uploads"
        )


def local() -> None:
    """Run the actual app with real BGE/Gemini and isolated ephemeral Qdrant, without Docker."""
    client = QdrantClient(":memory:", force_disable_check_same_thread=True)

    with patch("app.core.lifespan.create_client", return_value=client), serve() as base:
        files = []
        with httpx.Client(base_url=base, timeout=120, trust_env=False) as http:
            for name, body in (
                ("Luma", "The Luma garden has exactly two silver trees and a blue pond."),
                ("Vela", "The Vela garden has exactly nine copper trees and a red pond."),
            ):
                response = http.post("/documents/upload", files={"file": (
                    f"ask-{name}-{uuid4()}.md", body.encode(), "text/markdown",
                )})
                assert response.status_code == 200
                files.append(response.json()["id"])

        before = client.count(
            constants.qdrant.QDRANT_COLLECTION, exact=True,
        ).count

        provenance(check(base, files[0], files[1], str(uuid4())))

        after = client.count(
            constants.qdrant.QDRANT_COLLECTION, exact=True,
        ).count
        assert before == after

        print(
            f"Local ephemeral Qdrant points_before={before} points_after={after}; persistent storage untouched"
        )


def run() -> int:
    """Explicit live-only entry point; discovery never consumes Gemini quota."""
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--local", action="store_true")
    mode.add_argument("--serve", action="store_true")
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--file", default="765dfcea-a956-4912-aa32-de29c1a7f2bb",
    )
    parser.add_argument(
        "--other", default="c6262bff-76c8-4ad8-8121-bd63273e5ff4",
    )
    parser.add_argument(
        "--unindexed", default="5332bcdd-9192-44af-baa1-04f58342637e",
    )
    args = parser.parse_args()

    try:
        if args.local:
            local()
        elif args.serve:
            hosted(args.file, args.other, args.unindexed)
        else:
            check(args.base, args.file, args.other, args.unindexed)
    except Exception as error:
        print(
            f"Ask HTTP FAILED category={type(error).__name__}", file=sys.stderr,
        )

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(run())
