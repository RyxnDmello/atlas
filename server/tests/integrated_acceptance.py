"""Opt-in continuous two-owner journey; generation is deterministic only in TestClient."""

import sys
import json
import secrets
from uuid import UUID, uuid4
from unittest.mock import patch
from httpx import Client, Response
from collections.abc import Iterator
from fastapi.testclient import TestClient
from contextlib import ExitStack, contextmanager

from sqlalchemy import delete, select
from sqlalchemy.pool import QueuePool

from app.db.postgres import Database
from app.core.constants import constants

from app.pipeline.storage import Storage
from app.pipeline.auth.refresh import digest
from app.pipeline.generation.prompt import FALLBACK

from app.schemas.pipeline import Chunk
from app.schemas.retrieval import RetrievedChunk

from app.models.postgres import File, Folder, Session, User, Verification

from tests.test_10_ask import events
from tests.rag import retrieved, seed
from tests.uploads_acceptance import scope
from tests.files_acceptance import canonical, vectors
from tests.folders_acceptance import Actor, fingerprint

Http = Client | TestClient

FILE_FIELDS = {"id", "name", "description", "original_name", "extension", "size_bytes",
               "status", "folder_id", "created_at", "updated_at"}
FOLDER_FIELDS = {"id", "name", "description",
                 "parent_id", "created_at", "updated_at"}
QUESTION = {"question": "How long are synthetic records kept?", "top_k": 1}


def released(database: Database) -> None:
    """Assert real PostgreSQL has no checked-out connection at a RAG boundary."""
    if isinstance(database.engine.pool, QueuePool):
        assert database.engine.pool.checkedout() == 0


def credentials(response: Response, private: list[str]) -> tuple[str, str]:
    """Inspect known auth JSON responses without printing credentials or touching SSE."""
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"access_token", "user"}
    assert set(body["user"]) == {"id", "name", "email"}
    cookie = response.cookies.get("atlas_refresh")
    assert cookie
    attributes = response.headers["set-cookie"].lower()
    assert all(value in attributes for value in (
        "httponly", "path=/auth", "samesite=lax"))
    assert ("secure" in attributes) == constants.refresh.AUTH_COOKIE_SECURE
    private.extend([body["access_token"], cookie, digest(cookie)])

    return body["access_token"], cookie


def cleanup(database: Database, storage: Storage, emails: list[str], identifiers: set[UUID]) -> None:
    """Resolve even an ambiguously acknowledged registration; preserve rows if vector cleanup fails."""
    assert len(emails) == 2 and len(set(emails)) == 2
    assert all(email.startswith("integrated-")
               and email.endswith("@example.com") for email in emails)
    for email in emails:
        suffix = email.removeprefix("integrated-").removesuffix("@example.com")
        assert len(suffix) == 32 and UUID(hex=suffix).hex == suffix
    assert all(isinstance(identifier, UUID) for identifier in identifiers)
    with database.session() as session:
        owners = session.scalars(
            select(User.id).where(User.email.in_(emails))).all()
        identifiers.update(session.scalars(
            select(File.id).where(File.owner_id.in_(owners))).all())
    try:
        for identifier in sorted(identifiers, key=str):
            storage.delete(identifier)

        with database.session() as session:
            session.execute(delete(File).where(File.owner_id.in_(owners)))
            folders = dict(session.execute(select(Folder.id, Folder.parent_id).where(
                Folder.owner_id.in_(owners))).all())
            while folders:
                parents = set(folders.values())
                leaves = [
                    identifier for identifier in folders if identifier not in parents]
                assert leaves, "Synthetic cleanup found a hierarchy cycle"
                session.execute(delete(Folder).where(
                    Folder.owner_id.in_(owners), Folder.id.in_(leaves)))
                for identifier in leaves:
                    del folders[identifier]
            session.execute(delete(User).where(User.id.in_(owners)))
            session.commit()
    except Exception:
        print(json.dumps({"integrated_cleanup": "incomplete", "owner_ids": [str(owner) for owner in owners],
                          "retry_file_ids": sorted(str(identifier) for identifier in identifiers)}), file=sys.stderr)
        raise


@contextmanager
def actors(database: Database, clients: tuple[Http, Http], storage: Storage,
           private: list[str], identifiers: set[UUID]) -> Iterator[tuple[list[Actor], list[dict[str, str]]]]:
    """Register/verify/login/rotate two independent public identities and clean partial setup."""
    emails = ["integrated-" + uuid4().hex + "@example.com" for _ in clients]
    users, headers = [], []
    try:
        for client, email in zip(clients, emails):
            password = secrets.token_urlsafe(24)
            private.append(password)
            response = client.post("/auth/register", json={
                "name": "Synthetic", "email": email, "password": password})
            assert response.status_code == 201 and response.json() == {
                "status": "verification_required"}
            with database.session() as session:
                user = session.scalar(select(User).where(User.email == email))
                assert user is not None and user.verified_at is None
                identifier = user.id
                otp = session.scalar(select(Verification.otp).where(
                    Verification.user_id == identifier, Verification.type == "auth"))
                assert otp is not None
                private.extend([otp, user.password])
            credentials(client.post("/auth/verify",
                        json={"email": email, "otp": otp}), private)
            token, refresh = credentials(client.post("/auth/login", json={
                "email": email, "password": password}), private)
            token, replacement = credentials(client.post("/auth/refresh", headers={
                "Cookie": "atlas_refresh=" + refresh}), private)
            assert replacement != refresh
            auth = {"Authorization": "Bearer " + token}
            profile = client.get("/auth", headers=auth)
            assert profile.status_code == 200 and profile.json() == {
                "id": str(identifier), "name": "Synthetic", "email": email}
            with database.session() as session:
                assert session.scalar(select(Verification.id).where(
                    Verification.user_id == identifier)) is None
                rows = session.scalars(select(Session.token_hash).where(
                    Session.user_id == identifier)).all()
                assert len(
                    rows) == 2 and refresh not in rows and replacement not in rows
                private.extend(rows)
            users.append(Actor(identifier, email, password))
            headers.append(auth)

        yield users, headers
    finally:
        cleanup(database, storage, emails, identifiers)


def folder(client: Http, auth: dict[str, str], parent: str | None = None) -> str:
    """Create duplicate-friendly metadata through the public folder boundary."""
    response = client.post("/folders", headers=auth, json={
        "name": " Shared ", "description": " details ", "parent_id": parent})
    assert response.status_code == 201
    body = response.json()
    assert set(body) == FOLDER_FIELDS
    assert (body["name"], body["description"], body["parent_id"]) == (
        "Shared", "details", parent)

    return body["id"]


def listing(client: Http, auth: dict[str, str], parent: str | None = None) -> dict:
    """Assert the unchanged listing envelope and return direct children."""
    response = client.get(
        "/folders" if parent is None else "/folders/" + parent, headers=auth)
    assert response.status_code == 200 and set(response.json()) == {
        "folder", "folders", "files"}
    body = response.json()
    assert (body["folder"]
            is None) if parent is None else body["folder"]["id"] == parent

    return body


def denied(response: Response, status: int, code: str, message: str) -> None:
    """Require ordinary privacy-safe JSON, including before any ask stream commitment."""
    assert response.status_code == status
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"error": message, "code": code}
    assert "event:" not in response.text


def query(database: Database, storage: Storage, owner_id: UUID, identifier: UUID, owner: str) -> list[RetrievedChunk]:
    """Keep actual internal raw scores and exact-file context in the lifecycle journey."""
    results = retrieved(database, storage, owner_id, identifier, **QUESTION)
    assert len(results) == 1
    assert results[0].file_id == identifier
    assert isinstance(results[0].score, (int, float)
                      ) and owner in results[0].text

    return results


def acceptance(database: Database, clients: tuple[Http, Http], storage: Storage,
               private: list[str], generation: bool = False) -> dict[str, str]:
    """Run one continuous journey; all verification-only patches stay out of the deployed API."""
    assert clients[0] is not clients[1]
    assert not generation or all(isinstance(
        client, TestClient) for client in clients)
    instrument = all(isinstance(client, TestClient) for client in clients)
    before, points = fingerprint(database), vectors(storage)
    private.append(QUESTION["question"])
    identifiers: set[UUID] = set()
    with actors(database, clients, storage, private, identifiers) as (users, headers):
        a, b = clients
        own, other = headers
        for client, auth in ((a, own), (b, other)):
            body = listing(client, auth)
            assert not body["files"] and not body["folders"]
        root, foreign = folder(a, own), folder(b, other)
        nested, duplicate = folder(a, own, root), folder(a, own, root)
        deep, foreign_child = folder(a, own, nested), folder(b, other, foreign)
        assert {item["id"] for item in listing(a, own)["folders"]} == {root}
        assert {item["id"] for item in listing(a, own, root)["folders"]} == {
            nested, duplicate}
        assert {item["id"]
                for item in listing(a, own, nested)["folders"]} == {deep}
        assert {item["id"]
                for item in listing(b, other)["folders"]} == {foreign}
        assert {item["id"] for item in listing(b, other, foreign)["folders"]} == {
            foreign_child}
        for client, auth, foreign_folder in ((a, own, foreign), (b, other, root)):
            for target in (foreign_folder, str(uuid4())):
                denied(client.get("/folders/" + str(target), headers=auth),
                       404, "FOLDER_NOT_FOUND", "Folder not found")
                denied(client.post("/folders", headers=auth, json={"name": "attempt", "parent_id": target}),
                       404, "FOLDER_NOT_FOUND", "Folder not found")
                denied(client.patch(f"/folders/{target}", headers=auth, json={"name": "attempt"}),
                       404, "FOLDER_NOT_FOUND", "Folder not found")
                denied(client.post("/files", headers=auth, data={"name": "attempt", "folder_id": target},
                                   files={"file": ("probe.md", b"Synthetic forbidden upload", "text/markdown")}),
                       404, "FOLDER_NOT_FOUND", "Folder not found")

        uploaded = []
        with ExitStack() as stack:
            if instrument:
                from app.pipeline.ingestion import ingest

                def indexing(content, filename, extension, identifier):
                    released(database)
                    with database.session() as session:
                        file = session.get(File, identifier)
                        assert file is not None and file.status == "processing"
                    result = ingest(content, filename, extension, identifier)
                    assert storage.client.count(
                        storage.collection, count_filter=scope(identifier), exact=True).count > 0
                    return result

                stack.enter_context(
                    patch("app.pipeline.upload.ingest", side_effect=indexing))
            for client, auth, owner, parent in ((a, own, 0, None), (a, own, 0, nested), (b, other, 1, foreign_child)):
                content = f"# Owner {owner}\n\nOwner {owner} keeps synthetic records for {owner + 7} years."
                private.append(content)
                response = client.post("/files", headers=auth, data={
                    "name": " Shared ", "description": " source ", **({"folder_id": parent} if parent else {})},
                    files={"file": ("SOURCE.MD", content.encode(), "text/markdown")})
                assert response.status_code == 201
                body = response.json()
                assert set(body) == FILE_FIELDS
                assert (body["name"], body["description"], body["status"], body["folder_id"]) == (
                    "Shared", "source", "ready", parent)
                assert (body["original_name"], body["extension"], body["size_bytes"]) == (
                    "SOURCE.MD", ".md", len(content.encode()))
                identifier = UUID(body["id"])
                identifiers.add(identifier)
                with database.session() as session:
                    file = session.get(File, identifier)
                    assert file is not None and file.owner_id == users[
                        owner].id and file.status == "ready"
                stored, cursor = storage.client.scroll(storage.collection, scroll_filter=scope(identifier),
                                                       limit=100, with_payload=True, with_vectors=True)
                assert stored and cursor is None
                for point in stored:
                    payload = point.payload
                    assert payload is not None and payload["file_id"] == str(
                        identifier)
                    assert all(key in payload for key in (
                        "text", "display_text", "chunk_index", "token_count", "page", "heading", "section"))
                    assert point.vector and f"Owner {owner}" in payload["text"]
                uploaded.append(body)
        root_file, target, survivor = [UUID(body["id"]) for body in uploaded]
        assert {item["id"] for item in listing(a, own)["files"]} == {
            str(root_file)}
        assert {item["id"] for item in listing(a, own, nested)["files"]} == {
            str(target)}
        assert {item["id"] for item in listing(b, other, foreign_child)[
            "files"]} == {str(survivor)}
        query(database, storage, users[0].id, target, "Owner 0")
        preserved = vectors(storage)
        immutable = canonical(database, target)
        with ExitStack() as stack:
            calls = []
            if instrument:
                calls = [stack.enter_context(patch("app.pipeline.upload.ingest")),
                         stack.enter_context(patch.object(
                             storage.provider, "embed")),
                         stack.enter_context(patch.object(
                             storage.client, "upsert")),
                         stack.enter_context(patch.object(storage.client, "delete"))]
            response = a.patch(f"/folders/{nested}", headers=own,
                               json={"name": "Renamed", "description": " details "})
            assert response.status_code == 200 and response.json()[
                "parent_id"] == root
            assert response.json()["name"] == "Renamed" and response.json()[
                "description"] == "details"
            for body in ({"name": " Résumé 中文 + records ", "description": " revised "}, {"description": None}):
                response = a.patch(f"/files/{target}", headers=own, json=body)
                assert response.status_code == 200 and set(
                    response.json()) == FILE_FIELDS
                assert all(response.json()[key] == uploaded[1][key]
                           for key in FILE_FIELDS - {"name", "description", "updated_at"})
                assert response.json()[
                    "updated_at"] > uploaded[1]["updated_at"]
                assert vectors(storage) == preserved
            for call in calls:
                call.assert_not_called()
        updated = canonical(database, target)
        assert all(updated[index] == immutable[index] for index, column in enumerate(File.__table__.columns)
                   if column.name not in {"name", "description", "updated_at"})
        visible = listing(a, own, nested)["files"][0]
        assert visible["name"] == "Résumé 中文 + records" and visible["description"] is None

        with ExitStack() as stack:
            if instrument:
                from app.pipeline.retrieval import retrieve

                def retrieval(*args):
                    released(database)
                    return retrieve(*args)

                stack.enter_context(
                    patch("app.routers.files.retrieve", side_effect=retrieval))
            for client, auth, identifier, owner in ((a, own, root_file, 0), (a, own, target, 0), (b, other, survivor, 1)):
                results = query(database, storage,
                                users[owner].id, identifier, f"Owner {owner}")
                if generation:
                    citation = results[0].chunk_index

                    class Provider:
                        """No external provider access; actual grounding/citation/SSE layers remain intact."""

                        def stream_generate(self, prompt, chunks):
                            released(database)
                            assert chunks and all(
                                f"Owner {owner}" in chunk for chunk in chunks)
                            yield f"Synthetic integrated answer[[cite:{citation}]]"
                            released(database)

                    with patch("app.routers.files.GeminiFlashProvider", return_value=Provider()):
                        response = client.post(
                            f"/files/{identifier}/ask", headers=auth, json=QUESTION)
                    assert response.status_code == 200 and response.headers["content-type"].startswith(
                        "text/event-stream")
                    wire = events(response.iter_lines())
                    assert [name for name, _ in wire] == [
                        "answer", "citations", "done"]
                    stored, _ = storage.client.scroll(
                        storage.collection, scroll_filter=scope(identifier), limit=100)
                    payload = next(
                        point.payload for point in stored if point.payload and point.payload["chunk_index"] == citation)
                    assert payload is not None
                    assert wire[1][1]["citations"] == [{"index": citation, "page": payload["page"],
                                                        "heading": payload["heading"], "section": payload["section"], "excerpt": payload["display_text"]}]
                    assert wire[-1] == ("done", {"status": "completed"})
        assert vectors(storage) == preserved and canonical(
            database, target) == updated

        empty, orphan, missing = uuid4(), uuid4(), uuid4()
        identifiers.update([empty, orphan])
        seed(database, users[0].id, empty)
        storage.write([Chunk(id=str(orphan), text="Synthetic orphan",
                      display_text="Synthetic orphan", index=0, count=2)])
        markers = []
        for user in users:
            for status in ("processing", "deleting"):
                marker = uuid4()
                identifiers.add(marker)
                seed(database, user.id, marker, status)
                storage.write([Chunk(id=str(marker), text="Synthetic blocked",
                              display_text="Synthetic blocked", index=0, count=2)])
                markers.append((user.id, marker))
        with ExitStack() as stack:
            calls = []
            if instrument:
                calls = [stack.enter_context(patch(path)) for path in (
                    "app.routers.files.retrieve", "app.routers.files.GeminiFlashProvider", "app.routers.files.GroundedStream")]
                calls.extend([stack.enter_context(patch.object(storage.provider, "embed")),
                              stack.enter_context(patch.object(
                                  storage.client, "query_points")),
                              stack.enter_context(patch.object(storage, "delete"))])
            for client, auth, foreign_file in ((a, own, survivor), (b, other, target)):
                for identifier in (foreign_file, missing):
                    denied(client.patch(f"/files/{identifier}", headers=auth, json={"name": "attempt"}),
                           404, "FILE_NOT_FOUND", "File not found")
                    denied(client.delete(f"/files/{identifier}", headers=auth),
                           404, "FILE_NOT_FOUND", "File not found")
            for route in ("ask",):
                for client, auth, foreign_file in ((a, own, survivor), (b, other, target)):
                    for identifier in (foreign_file, orphan, missing):
                        denied(client.post(f"/files/{identifier}/{route}", headers=auth, json=QUESTION),
                               404, "FILE_NOT_FOUND", "File not found")
                    for owner, marker in markers:
                        owned = owner == (
                            users[0].id if client is a else users[1].id)
                        denied(client.post(f"/files/{marker}/{route}", headers=auth, json=QUESTION),
                               409 if owned else 404, "FILE_NOT_READY" if owned else "FILE_NOT_FOUND",
                               "File is not ready" if owned else "File not found")
                for auth in ({}, {"Authorization": "Bearer invalid"}):
                    response = a.post(
                        f"/files/{target}/{route}", headers=auth, json=QUESTION)
                    assert response.status_code == 401 and response.json()[
                        "code"] == "INVALID_ACCESS_TOKEN"
                    assert response.headers["content-type"].startswith(
                        "application/json")
            for call in calls:
                call.assert_not_called()
        assert retrieved(database, storage,
                         users[0].id, empty, **QUESTION) == []
        with ExitStack() as stack:
            provider = stack.enter_context(
                patch("app.routers.files.GeminiFlashProvider")) if instrument else None
            response = a.post(f"/files/{empty}/ask",
                              headers=own, json=QUESTION)
            assert response.status_code == 200 and response.headers["content-type"].startswith(
                "text/event-stream")
            assert events(response.iter_lines()) == [("answer", {"text": FALLBACK}),
                                                     ("citations", {"citations": []}), ("done", {"status": "completed"})]
            if provider is not None:
                provider.assert_not_called()

        survivor_row, survivor_points = canonical(
            database, survivor), vectors(storage, scope(survivor))
        with ExitStack() as stack:
            if instrument:
                erase = storage.delete

                def deleting(identifier):
                    released(database)
                    with database.session() as session:
                        file = session.get(File, identifier)
                        assert file is not None and file.status == "deleting"
                    return erase(identifier)

                stack.enter_context(patch.object(
                    storage, "delete", side_effect=deleting))
            response = a.delete(f"/files/{target}", headers=own)
            assert response.status_code == 204 and not response.content
        with database.session() as session:
            assert session.get(File, target) is None
        assert storage.client.count(
            storage.collection, count_filter=scope(target), exact=True).count == 0
        assert not listing(a, own, nested)["files"]
        for route in ("ask",):
            denied(a.post(f"/files/{target}/{route}", headers=own, json=QUESTION),
                   404, "FILE_NOT_FOUND", "File not found")
        assert canonical(database, survivor) == survivor_row and vectors(
            storage, scope(survivor)) == survivor_points
        query(database, storage, users[1].id, survivor, "Owner 1")
        origin = constants.cors.CORS_ORIGINS[0]
        for method in ("GET", "POST", "PATCH", "DELETE"):
            response = a.options("/files", headers={"Origin": origin, "Access-Control-Request-Method": method,
                                                    "Access-Control-Request-Headers": "Authorization, Content-Type"})
            assert response.status_code == 200 and response.headers[
                "access-control-allow-origin"] == origin
            assert response.headers["access-control-allow-credentials"] == "true"
            assert set(response.headers["access-control-allow-methods"].replace(
                " ", "").split(",")) == {"GET", "POST", "PATCH", "DELETE"}
        for origin, method in ((origin, "PUT"), ("https://" + uuid4().hex + ".invalid", "POST")):
            assert a.options(
                "/files", headers={"Origin": origin, "Access-Control-Request-Method": method}).status_code == 400
        assert "/documents/upload" not in a.get(
            "/openapi.json").json()["paths"]
        for client in clients:
            refresh = client.cookies.get("atlas_refresh")
            assert refresh
            response = client.post(
                "/auth/logout", headers={"Cookie": "atlas_refresh=" + refresh})
            assert response.status_code == 204 and not response.content

    assert fingerprint(database) == before and vectors(storage) == points

    return {"integrated_journey": "passed", "two_owner_isolation": "passed", "canonical_and_vector_state": "preserved",
            "ask_generation": "deterministic" if generation else "empty_fallback_only"}
