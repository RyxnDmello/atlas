"""Opt-in upload acceptance shared by disposable PostgreSQL and real HTTP verification."""
from httpx import Client
from uuid import UUID, uuid4
from sqlalchemy import select
from fastapi.testclient import TestClient
from qdrant_client.http.models import FieldCondition, Filter, MatchValue

from app.db.postgres import Database

from app.models.postgres import File
from app.pipeline.storage import Storage

from tests.rag import retrieved
from tests.folders_acceptance import actors


def scope(identifier: UUID) -> Filter:
    """Use the same exact canonical payload scope for verification reads."""
    return Filter(must=[FieldCondition(key="file_id", match=MatchValue(value=str(identifier)))])


def acceptance(database: Database, client: Client | TestClient, storage: Storage,
               private: list[str]) -> dict[str, str]:
    """Use two synthetic owners and clean every accepted upload by its canonical UUID."""
    with actors(database, private) as users:
        identifiers: set[UUID] = set()
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
                "/folders", headers=headers[0], json={"name": "Upload parent"})
            assert folder.status_code == 201
            child = client.post("/folders", headers=headers[0], json={
                "name": "Upload nested", "parent_id": folder.json()["id"]})
            assert child.status_code == 201
            content = b"# Synthetic retention\n\nKeep synthetic records for seven years."

            def post(data, auth=None):
                return client.post("/files", headers=headers[0] if auth is None else auth, data=data,
                                   files={"file": ("SYNTHETIC.MD", content, "text/markdown")})

            for location in (None, child.json()["id"]):
                data = {
                    "name": "  Résumé + records (2026)  ", "description": "  synthetic  "}
                if location is not None:
                    data["folder_id"] = location
                response = post(data)
                assert response.status_code == 201
                body = response.json()
                identifier = UUID(body["id"])
                identifiers.add(identifier)
                assert body["status"] == "ready" and body["folder_id"] == location
                assert body["name"] == "Résumé + records (2026)" and body["description"] == "synthetic"
                assert body["original_name"] == "SYNTHETIC.MD" and body["extension"] == ".md"
                assert body["size_bytes"] == len(content)
                assert "owner_id" not in body and "chunks" not in body
                with database.session() as session:
                    file = session.get(File, identifier)
                    assert file is not None and file.owner_id == users[0].id and file.status == "ready"
                    assert file.folder_id == (
                        UUID(location) if location else None)
                    assert file.name == body["name"] and file.description == body["description"]
                    assert file.original_name == body["original_name"] and file.size_bytes == len(
                        content)
                points, cursor = storage.client.scroll(storage.collection, scroll_filter=scope(identifier),
                                                       limit=100, with_payload=True, with_vectors=False)
                assert points and cursor is None
                assert all(point.payload is not None and point.payload["file_id"] == str(identifier)
                           and point.payload["text"] and point.payload["display_text"] for point in points)
                assert retrieved(database, storage,
                                 users[0].id, identifier, "What is retention?")

            before = storage.client.count(storage.collection, exact=True).count
            foreign = post(
                {"name": "Foreign", "folder_id": child.json()["id"]}, headers[1])
            missing = post(
                {"name": "Missing", "folder_id": str(uuid4())}, headers[1])
            assert foreign.status_code == missing.status_code == 404 and foreign.json() == missing.json()
            assert foreign.json()["code"] == "FOLDER_NOT_FOUND"
            assert storage.client.count(
                storage.collection, exact=True).count == before
            with database.session() as session:
                assert not session.scalars(select(File.id).where(
                    File.owner_id == users[1].id)).all()

            for name in ("a", "a" * 100, "_-.,()[]&+@'", "中文 ١٢٣"):
                response = post({"name": name, "description": " "})
                assert response.status_code == 201
                identifiers.add(UUID(response.json()["id"]))
                assert response.json()["description"] is None
            response = post({"name": "Description", "description": "a" * 250})
            assert response.status_code == 201
            identifiers.add(UUID(response.json()["id"]))
            for data in ({"name": "a" * 101}, {"name": "bad/name"}, {"name": "bad\\name"},
                         {"name": "bad:name"}, {
                             "name": "bad\tname"}, {"name": "bad😀"},
                         {"name": "valid", "description": "a" * 251},
                         *({"name": "valid", key: "untrusted"} for key in ("owner_id", "id", "status"))):
                assert post(data).status_code == 422
            assert post({"name": "Unauthenticated"}, {}).status_code == 401
            legacy = client.post("/documents/upload",
                                 files={"file": ("old.md", content)})
            assert legacy.status_code == 404
            return {"upload_http": "passed", "two_owner_isolation": "passed",
                    "canonical_uuid": "passed", "validation": "passed", "legacy_absent": "passed"}
        finally:
            with database.session() as session:
                identifiers.update(session.scalars(select(File.id).where(
                    File.owner_id.in_([user.id for user in users]))).all())
            for identifier in identifiers:
                storage.delete(identifier)
