"""Shared opt-in two-user contract for PostgreSQL and running-HTTP acceptance."""
import secrets
from httpx import Client
from hashlib import sha256
from uuid import UUID, uuid4
from dataclasses import dataclass
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from sqlalchemy import delete, select, text

from app.core.constants import constants

from app.db.postgres import Database

from app.pipeline.auth.password import Password

from app.models.postgres import Base, File, Folder, User


@dataclass(repr=False)
class Actor:
    """Keep synthetic identities and credentials private, including assertion output."""

    id: UUID
    email: str
    password: str


def fingerprint(database: Database) -> str:
    """Compare every canonical row and installed revision without exposing values."""
    digest = sha256()
    with database.engine.connect() as connection:
        for name in sorted(Base.metadata.tables):
            table = Base.metadata.tables[name]
            rows = connection.execute(select(table).order_by(table.c.id)).all()
            digest.update(name.encode())
            digest.update(repr(rows).encode())
        revision = connection.execute(
            text("SELECT version_num FROM alembic_version")).scalars().all()
        assert revision == ["0002_drive"]
        digest.update(repr(revision).encode())

    return digest.hexdigest()


def cleanup(database: Database, identities: list[UUID]) -> None:
    """Remove only explicit synthetic owners, deepest folders first to honor RESTRICT."""
    assert len(identities) == 2 and len(set(identities)) == 2
    assert all(isinstance(value, UUID) for value in identities)
    with database.session() as session:
        session.execute(delete(File).where(File.owner_id.in_(identities)))
        folders = dict(session.execute(select(Folder.id, Folder.parent_id).where(
            Folder.owner_id.in_(identities))).all())
        while folders:
            parents = set(folders.values())
            leaves = [
                identifier for identifier in folders if identifier not in parents]
            assert leaves, "Synthetic hierarchy cleanup found a cycle"
            session.execute(delete(Folder).where(
                Folder.owner_id.in_(identities), Folder.id.in_(leaves)))
            for identifier in leaves:
                del folders[identifier]
        session.execute(delete(User).where(User.id.in_(identities)))
        session.commit()


@contextmanager
def actors(database: Database, private: list[str]) -> Iterator[list[Actor]]:
    """Seed two verified users atomically and clean even failed HTTP acceptance."""
    users = [Actor(uuid4(), "folders-"+uuid4().hex+"@example.com",
                   secrets.token_urlsafe(24)) for _ in range(2)]
    try:
        now = datetime.now(timezone.utc)
        with database.session() as session:
            for user in users:
                password = Password().hash(user.password)
                private.extend([user.password, password])
                session.add(User(id=user.id, name="Synthetic", email=user.email, password=password,
                                 verified_at=now, created_at=now, updated_at=now))
            session.commit()

        yield users
    finally:
        cleanup(database, [user.id for user in users])


def acceptance(database: Database, client: Client, private: list[str]) -> dict[str, str]:
    """Exercise actual HTTP auth, CRUD, visibility, privacy, validation and narrow CORS."""
    folder_fields = {"id", "name", "description",
                     "parent_id", "created_at", "updated_at"}
    file_fields = {"id", "name", "description", "original_name", "extension", "size_bytes",
                   "status", "folder_id", "created_at", "updated_at"}
    with actors(database, private) as users:
        headers = []
        for user in users:
            response = client.post(
                "/auth/login", json={"email": user.email, "password": user.password})
            assert response.status_code == 200
            token = response.json()["access_token"]
            private.append(token)
            private.extend(response.cookies.values())
            headers.append({"Authorization": "Bearer "+token})
        own, other = headers

        def folder(parent=None, actor=own):
            response = client.post("/folders", headers=actor, json={
                                   "name": " same ", "description": " details ", "parent_id": parent})
            assert response.status_code == 201
            result = response.json()
            assert set(result) == folder_fields
            assert (result["name"], result["description"],
                    result["parent_id"]) == ("same", "details", parent)
            assert result["created_at"] == result["updated_at"]
            return result

        root, sibling, foreign = folder(), folder(), folder(actor=other)
        child = folder(root["id"])
        deep = folder(child["id"])
        duplicate = folder(root["id"])
        assert len({root["id"], sibling["id"], child["id"],
                   deep["id"], duplicate["id"], foreign["id"]}) == 6
        expected_files = {}
        now = datetime.now(timezone.utc)
        with database.session() as session:
            for owner, location in ((users[0].id, None), (users[0].id, UUID(root["id"])),
                                    (users[0].id, UUID(child["id"])
                                     ), (users[0].id, UUID(sibling["id"])),
                                    (users[1].id, None), (users[1].id, UUID(foreign["id"]))):
                identifiers = set()
                for status in ("processing", "ready", "deleting"):
                    identifier = uuid4()
                    identifiers.add(str(identifier))
                    session.add(File(id=identifier, owner_id=owner, folder_id=location, name="same", description=None,
                                     original_name="synthetic.md", extension=".md", size_bytes=19, status=status,
                                     created_at=now, updated_at=now))
                expected_files[(owner, str(location)
                                if location else None)] = identifiers
            session.commit()

        for user, actor, location, expected in ((users[0], own, None, {root["id"], sibling["id"]}),
                                                (users[1], other, None,
                                                 {foreign["id"]}),
                                                (users[0], own, root["id"], {
                                                 child["id"], duplicate["id"]}),
                                                (users[0], own, child["id"], {
                                                 deep["id"]}),
                                                (users[0], own,
                                                 deep["id"], set()),
                                                (users[1], other, foreign["id"], set())):
            response = client.get("/drive", headers=actor, params={}
                                  if location is None else {"folder_id": location})
            assert response.status_code == 200
            body = response.json()
            assert set(body) == {"folder", "folders", "files"}
            assert body["folder"] is None if location is None else body["folder"]["id"] == location
            assert {item["id"] for item in body["folders"]} == expected
            assert {item["id"] for item in body["files"]
                    } == expected_files.get((user.id, location), set())
            assert all(set(item) == folder_fields for item in body["folders"])
            assert all(set(item) == file_fields for item in body["files"])
            if body["files"]:
                assert {item["status"] for item in body["files"]} == {
                    "processing", "ready", "deleting"}

        for identifier in (foreign["id"], str(uuid4())):
            responses = [client.get("/drive", headers=own, params={"folder_id": identifier}),
                         client.patch("/folders/"+identifier,
                                      headers=own, json={"name": "attempt"}),
                         client.post("/folders", headers=own, json={"name": "attempt", "parent_id": identifier})]
            assert all(response.status_code == 404 and response.json() == {
                "error": "Folder not found", "code": "FOLDER_NOT_FOUND"} for response in responses)
        for method, path, data in (("GET", "/drive?folder_id="+root["id"], None),
                                   ("PATCH", "/folders/" +
                                    root["id"], {"name": "attempt"}),
                                   ("POST", "/folders", {"name": "attempt", "parent_id": root["id"]})):
            response = client.request(method, path, headers=other, json=data)
            assert response.status_code == 404 and response.json(
            ) == {"error": "Folder not found", "code": "FOLDER_NOT_FOUND"}

        for payload, name, description in (({"name": " renamed "}, "renamed", "details"),
                                           ({"description": " updated "},
                                            "renamed", "updated"),
                                           ({"description": None},
                                            "renamed", None),
                                           ({"name": "same", "description": "both"},
                                            "same", "both"),
                                           ({"description": "  "}, "same", None)):
            response = client.patch(
                "/folders/"+child["id"], headers=own, json=payload)
            assert response.status_code == 200
            body = response.json()
            assert set(body) == folder_fields
            assert (body["name"], body["description"]) == (name, description)
            assert all(body[key] == child[key]
                       for key in ("id", "parent_id", "created_at"))
            assert datetime.fromisoformat(
                body["updated_at"]) > datetime.fromisoformat(child["updated_at"])
        with database.session() as session:
            persisted = session.get(Folder, UUID(child["id"]))
            assert persisted is not None
            assert (persisted.owner_id, persisted.parent_id, persisted.name, persisted.description) == (
                users[0].id, UUID(root["id"]), "same", None)

        for method, path, payload in (("POST", "/folders", {"name": " "}),
                                      ("PATCH", "/folders/"+root["id"], {}),
                                      ("PATCH", "/folders/" +
                                       root["id"], {"name": None}),
                                      ("PATCH", "/folders/"+root["id"], {"parent_id": foreign["id"]})):
            assert client.request(method, path, headers=own,
                                  json=payload).status_code == 422
        for field in ("owner_id", "user_id"):
            for method, path in (("GET", "/drive"), ("POST", "/folders"), ("PATCH", "/folders/"+root["id"])):
                data = {"name": "ok"} if method != "GET" else None
                assert client.request(method, path, headers=own, params={
                                      field: str(users[1].id)}, json=data).status_code == 422
                if data is not None:
                    assert client.request(method, path, headers=own, json={
                                          "name": "ok", field: str(users[1].id)}).status_code == 422
        for method, path, data in (("GET", "/drive", None), ("POST", "/folders", {"name": "ok"}),
                                   ("PATCH", "/folders/"+root["id"], {"name": "ok"})):
            for actor in ({}, {"Authorization": "Bearer malformed"}):
                response = client.request(
                    method, path, headers=actor, json=data)
                assert response.status_code == 401 and response.json()[
                    "code"] == "INVALID_ACCESS_TOKEN"

        for origin in [*constants.cors.CORS_ORIGINS, "https://unapproved-"+uuid4().hex+".example"]:
            approved = origin in constants.cors.CORS_ORIGINS
            for method in ("GET", "POST", "PATCH", "PUT", "DELETE"):
                response = client.options("/folders/"+root["id"], headers={"Origin": origin,
                                                                           "Access-Control-Request-Method": method, "Access-Control-Request-Headers": "Authorization, Content-Type"})
                assert response.status_code == (200 if approved and method in {
                                                "GET", "POST", "PATCH"} else 400)
                assert set(
                    response.headers["access-control-allow-methods"].split(", ")) == {"GET", "POST", "PATCH"}
                assert response.headers.get(
                    "access-control-allow-origin") == (origin if approved else None)
                assert response.headers["access-control-allow-credentials"] == "true"
                assert "*" not in str(response.headers)
            for method, path, data in (("GET", "/drive", None), ("POST", "/folders", {"name": "cors"}),
                                       ("PATCH", "/folders/"+root["id"], {"name": "cors"})):
                response = client.request(method, path, headers={
                                          **own, "Origin": origin}, json=data)
                assert response.status_code in {200, 201}
                assert response.headers.get(
                    "access-control-allow-origin") == (origin if approved else None)

    return {"two_user_isolation": "passed", "direct_children_all_statuses": "passed",
            "duplicates_and_metadata": "passed", "foreign_missing_privacy": "passed",
            "validation_and_cors": "passed", "synthetic_cleanup": "passed"}
