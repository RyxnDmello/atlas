"""Opt-in two-owner authorization acceptance; no live provider calls are required."""

from httpx import Client
from uuid import UUID, uuid4
from unittest.mock import patch
from contextlib import ExitStack
from fastapi.testclient import TestClient

from sqlalchemy import select
from sqlalchemy.pool import QueuePool

from app.db.postgres import Database

from app.pipeline.storage import Storage
from app.pipeline.generation.prompt import FALLBACK

from app.models.postgres import File
from app.schemas.pipeline import Chunk

from tests.test_10_ask import events
from tests.rag import retrieved, seed
from tests.uploads_acceptance import scope
from tests.folders_acceptance import actors
from tests.files_acceptance import canonical, vectors


def acceptance(database: Database, client: Client | TestClient, storage: Storage,
               private: list[str], generation: bool = False) -> dict[str, str]:
    """Exercise real HTTP contracts; fake generation only inside an explicit TestClient harness."""
    assert not generation or isinstance(client, TestClient)
    before = vectors(storage)
    with actors(database, private) as users:
        identifiers: set[UUID] = set()
        try:
            headers = []
            for user in users:
                response = client.post(
                    "/auth/login", json={"email": user.email, "password": user.password})
                assert response.status_code == 200
                token = response.json()["access_token"]
                private.extend([token, *response.cookies.values()])
                headers.append({"Authorization": "Bearer " + token})
            files = []
            for index, auth in enumerate(headers):
                content = f"# Synthetic owner {index}\n\nOwner {index} keeps synthetic records for {index + 7} years."
                private.append(content)
                response = client.post("/files", headers=auth, data={"name": "RAG owner probe"},
                                       files={"file": ("probe.md", content.encode(), "text/markdown")})
                assert response.status_code == 201
                identifier = UUID(response.json()["id"])
                identifiers.add(identifier)
                files.append(identifier)
            survivor = canonical(database, files[1])
            preserved = vectors(storage)

            for owner, identifier in enumerate(files):
                results = retrieved(database, storage, users[owner].id, identifier,
                                    "How long are records kept?")
                assert results and all(
                    item.file_id == identifier for item in results)
                assert all(f"Owner {owner}" in item.text for item in results)
                if generation:
                    citation = results[0].chunk_index

                    class Provider:
                        """Deterministic test-only provider with actual retrieval and trusted citations."""

                        def stream_generate(self, prompt, chunks):
                            if isinstance(database.engine.pool, QueuePool):
                                assert database.engine.pool.checkedout() == 0
                            yield f"Synthetic answer[[cite:{citation}]]"
                            if isinstance(database.engine.pool, QueuePool):
                                assert database.engine.pool.checkedout() == 0

                    with patch("app.routers.files.GeminiFlashProvider", return_value=Provider()):
                        response = client.post(f"/files/{identifier}/ask", headers=headers[owner],
                                               json={"question": "How long are records kept?"})
                    assert response.status_code == 200
                    wire = events(response.iter_lines())
                    assert [name for name, _ in wire] == [
                        "answer", "citations", "done"]
                    assert wire[1][1]["citations"][0]["index"] == citation
                    assert wire[1][1]["citations"][0]["excerpt"]
            assert vectors(storage) == preserved
            assert canonical(database, files[1]) == survivor

            orphan, empty, missing = uuid4(), uuid4(), uuid4()
            identifiers.update([orphan, empty])
            storage.write([Chunk(id=str(orphan), text="Synthetic orphan",
                          display_text="Synthetic orphan", index=0, count=2)])
            seed(database, users[0].id, empty)
            for route in ("ask",):
                for auth in ({}, {"Authorization": "Bearer invalid"}):
                    response = client.post(
                        f"/files/{files[0]}/{route}", headers=auth, json={"question": "question"})
                    assert response.status_code == 401 and response.json()[
                        "code"] == "INVALID_ACCESS_TOKEN"
                    assert response.headers["content-type"].startswith(
                        "application/json")

            for status in ("ready", "processing", "deleting"):
                with database.session() as session:
                    for identifier in files:
                        file = session.get(File, identifier)
                        assert file is not None
                        file.status = status
                    session.commit()
                with ExitStack() as stack:
                    calls = []
                    if isinstance(client, TestClient):
                        for target in ("app.routers.files.retrieve", "app.routers.files.GeminiFlashProvider",
                                       "app.routers.files.GroundedStream"):
                            calls.append(stack.enter_context(patch(target)))
                        calls.append(stack.enter_context(
                            patch.object(storage.provider, "embed")))
                        calls.append(stack.enter_context(
                            patch.object(storage.client, "query_points")))
                    for owner, identifier in enumerate(files):
                        for route in ("ask",):
                            cases = [(identifier, headers[1 - owner], 404), (orphan, headers[owner], 404),
                                     (missing, headers[owner], 404)]
                            if status != "ready":
                                cases.append((identifier, headers[owner], 409))
                            for target, auth, expected in cases:
                                response = client.post(
                                    f"/files/{target}/{route}", headers=auth, json={"question": "question"})
                                assert response.status_code == expected
                                assert response.json() == ({"error": "File not found", "code": "FILE_NOT_FOUND"}
                                                           if expected == 404 else {"error": "File is not ready", "code": "FILE_NOT_READY"})
                                assert response.headers["content-type"].startswith(
                                    "application/json")
                                assert "event:" not in response.text
                    for call in calls:
                        call.assert_not_called()

            assert retrieved(database, storage, users[0].id, empty) == []
            response = client.post(
                f"/files/{empty}/ask", headers=headers[0], json={"question": "question"})
            assert response.status_code == 200
            assert events(response.iter_lines()) == [("answer", {"text": FALLBACK}),
                                                     ("citations", {"citations": []}), ("done", {"status": "completed"})]
            survivor = canonical(database, files[1])
            survivor_points = vectors(storage, scope(files[1]))
            response = client.delete(f"/files/{files[0]}", headers=headers[0])
            assert response.status_code == 204
            assert canonical(database, files[1]) == survivor
            assert vectors(storage, scope(files[1])) == survivor_points
            for route in ("ask",):
                response = client.post(
                    f"/files/{files[0]}/{route}", headers=headers[0], json={"question": "question"})
                assert response.status_code == 404 and response.json()[
                    "code"] == "FILE_NOT_FOUND"
            result = {"rag_authorization": "passed", "orphan_and_foreign": "denied",
                      "ask_generation": "deterministic" if generation else "empty_fallback_only"}
        finally:
            with database.session() as session:
                identifiers.update(session.scalars(select(File.id).where(
                    File.owner_id.in_([user.id for user in users]))).all())
            for identifier in identifiers:
                storage.delete(identifier)
    assert vectors(storage) == before

    return result
