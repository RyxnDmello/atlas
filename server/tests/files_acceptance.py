"""Opt-in real-store contracts, shared by disposable PostgreSQL and live HTTP."""

import json
from httpx import Client
from hashlib import sha256
from uuid import UUID, uuid4
from sqlalchemy import select
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from qdrant_client.http.models import Filter

from app.db.postgres import Database
from app.core.constants import constants

from app.models.postgres import File
from app.pipeline.storage import Storage

from tests.rag import retrieved
from tests.uploads_acceptance import scope
from tests.folders_acceptance import actors


def vectors(storage: Storage, where: Filter | None = None) -> str:
    """Hash every paginated point ID, full payload and vector without exposing content."""
    records = []
    offset = None
    while True:
        points, offset = storage.client.scroll(storage.collection, scroll_filter=where,
                                               offset=offset, limit=100, with_payload=True, with_vectors=True)
        records.extend(point.model_dump(mode="json") for point in points)
        if offset is None:
            break

    records.sort(key=lambda item: str(item["id"]))

    return sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def canonical(database: Database, identifier: UUID) -> tuple[object, ...]:
    """Snapshot every persisted file field privately for exact survivor comparisons."""
    with database.session() as session:
        file = session.get(File, identifier)
        assert file is not None

        return tuple(getattr(file, column.name) for column in File.__table__.columns)


def acceptance(database: Database, client: Client | TestClient, storage: Storage,
               private: list[str]) -> dict[str, str]:
    """Verify metadata immutability, deletion isolation, guards and CORS on synthetic owners."""
    with actors(database, private) as users:
        try:
            headers = []
            for user in users:
                response = client.post(
                    "/auth/login", json={"email": user.email, "password": user.password})
                assert response.status_code == 200
                token = response.json()["access_token"]
                private.append(token)
                headers.append({"Authorization": "Bearer " + token})
            folder = client.post(
                "/folders", headers=headers[0], json={"name": "Mutation parent"})
            assert folder.status_code == 201
            content = b"# Synthetic policy\n\nKeep synthetic records for seven years."
            files = []
            for auth in headers:
                response = client.post("/files", headers=auth, data={"name": "Synthetic", **(
                    {"folder_id": folder.json()["id"]} if auth is headers[0] else {})},
                    files={"file": ("SOURCE.MD", content, "text/markdown")})
                assert response.status_code == 201
                files.append(response.json())
            target, survivor = [UUID(file["id"]) for file in files]
            before = vectors(storage)
            immutable = files[0].keys() - {"name", "description", "updated_at"}
            with database.session() as session:
                original = session.get(File, target)
                assert original is not None and original.owner_id == users[0].id
                created, location = original.created_at, original.folder_id
            for payload in ({"name": "  Résumé 中文 + records  ", "description": "  details  "},
                            {"description": None}, {
                                "name": "a"}, {"name": "a" * 100},
                            {"name": "_-.,()[]&+@'"}, {"description": "d" * 250}, {"description": "  "}):
                response = client.patch(
                    "/files/" + str(target), headers=headers[0], json=payload)
                assert response.status_code == 200
                body = response.json()
                assert set(body) == set(files[0])
                assert all(body[key] == files[0][key] for key in immutable)
                assert body["updated_at"] > files[0]["updated_at"]
                for key, value in payload.items():
                    assert body[key] == (
                        value.strip() or None if isinstance(value, str) else value)
                assert vectors(storage) == before
            with database.session() as session:
                file = session.get(File, target)
                assert file is not None and file.owner_id == users[0].id
                assert file.created_at == created and file.folder_id == location
            listing = client.get(
                "/folders/" + str(folder.json()["id"]), headers=headers[0])
            assert listing.status_code == 200 and listing.json(
            )["files"][0]["name"] == "_-.,()[]&+@'"
            for payload in ({}, {"name": None}, {"name": "a" * 101}, {"description": "d" * 251},
                            {"name": "bad/name"}, {"name": "a\nb"}, {"name": "😀"}, {"name": "e\u0301"},
                            {"folder_id": None}, {"owner_id": str(users[1].id)}, {"status": "deleting"}):
                assert client.patch(
                    "/files/" + str(target), headers=headers[0], json=payload).status_code == 422
            missing = {"error": "File not found", "code": "FILE_NOT_FOUND"}
            for method in ("PATCH", "DELETE"):
                for identifier in (survivor, uuid4()):
                    path = "/files/" + str(identifier)
                    response = client.patch(path, headers=headers[0], json={
                                            "name": "attempt"}) if method == "PATCH" else client.delete(path, headers=headers[0])
                    assert response.status_code == 404 and response.json() == missing
                assert client.request(
                    method, "/files/invalid", content="{").status_code == 401
            marker = uuid4()
            now = datetime.now(timezone.utc)
            with database.session() as session:
                session.add(File(id=marker, owner_id=users[0].id, name="Marker", original_name="marker.md",
                                 extension=".md", size_bytes=0, status="processing", created_at=now, updated_at=now))
                session.commit()
            for method in ("PATCH", "DELETE"):
                path = "/files/" + str(marker)
                response = client.patch(path, headers=headers[0], json={
                                        "name": "attempt"}) if method == "PATCH" else client.delete(path, headers=headers[0])
                assert response.status_code == 409
                assert response.json() == {
                    "error": "File is not ready", "code": "FILE_NOT_READY"}
            assert vectors(storage) == before
            preserved = vectors(storage, scope(survivor))
            survivor_row = canonical(database, survivor)
            response = client.delete(
                "/files/" + str(target), headers=headers[0])
            assert response.status_code == 204 and response.content == b""
            assert storage.client.count(
                storage.collection, count_filter=scope(target), exact=True).count == 0
            with database.session() as session:
                assert session.get(File, target) is None
            assert canonical(database, survivor) == survivor_row
            assert vectors(storage, scope(survivor)) == preserved
            listing = client.get(
                "/folders/" + str(folder.json()["id"]), headers=headers[0])
            assert listing.status_code == 200 and listing.json()["files"] == []
            assert retrieved(
                database, storage, users[1].id, survivor, "How long are records kept?")
            assert vectors(storage, scope(survivor)) == preserved
            for origin in [*constants.cors.CORS_ORIGINS, "https://denied-" + uuid4().hex + ".example"]:
                for method in ("DELETE", "PUT"):
                    response = client.options("/files/" + str(survivor), headers={"Origin": origin,
                                                                                  "Access-Control-Request-Method": method, "Access-Control-Request-Headers": "Authorization, Content-Type"})
                    assert response.status_code == (
                        200 if origin in constants.cors.CORS_ORIGINS and method == "DELETE" else 400)
                    assert set(response.headers["access-control-allow-methods"].split(", ")) == {
                        "GET", "POST", "PATCH", "DELETE"}
                    assert response.headers.get("access-control-allow-origin") == (
                        origin if origin in constants.cors.CORS_ORIGINS else None)
                    assert response.headers["access-control-allow-credentials"] == "true"
                    assert "*" not in str(response.headers)
        finally:
            with database.session() as session:
                identifiers = session.scalars(select(File.id).where(
                    File.owner_id.in_([user.id for user in users]))).all()
            for identifier in identifiers:
                storage.delete(identifier)

    return {"metadata_vectors": "unchanged", "delete_isolation": "passed", "privacy_guards_cors": "passed"}
