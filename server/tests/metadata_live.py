"""Opt-in folder/file acceptance; all writes and reversals use a disposable database.

The configured development database is never migrated or written by this helper.
Run only after approval for live PostgreSQL verification. No Qdrant access occurs.
"""
import os
import sys
import json
import subprocess
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session as OrmSession, sessionmaker
from sqlalchemy import create_engine, delete, inspect, select, text

from app.core.constants import constants
from app.db.postgres import Database, url

from app.models.postgres import Base, File, Folder, Session, User, Verification

from tests.postgres_live import reject, schema as identity_schema
from tests.postgres_live import constraints as identity_constraints


def migrate(name: str, action: str, target: str) -> None:
    """Restrict explicit migration execution to this helper's disposable names."""
    assert name.startswith("atlas_metadata_verify_") and len(name) == 54
    assert action in {"upgrade", "downgrade"}
    assert target in {"0001_identity", "head"}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", action, target],
        env={**os.environ, "POSTGRES_DB": name}, capture_output=True, text=True,
    )
    assert result.returncode == 0, "Disposable folder/file migration failed; inspect safely"


def schema(database: Database) -> None:
    """Inspect exact live columns, named constraints, actions, and browse indexes."""
    identity_schema(database.engine)
    inspector = inspect(database.engine)
    for name, location in (("folders", "parent_id"), ("files", "folder_id")):
        table = Base.metadata.tables[name]
        columns = inspector.get_columns(name)
        assert {item["name"] for item in columns} == set(table.columns.keys())
        for item in columns:
            column = table.c[item["name"]]
            assert item["nullable"] == column.nullable
            assert item["default"] is None
            assert item["type"].compile(dialect=database.engine.dialect) == column.type.compile(
                dialect=database.engine.dialect)
        primary = inspector.get_pk_constraint(name)
        assert primary["name"] == f"pk_{name}"
        assert primary["constrained_columns"] == ["id"]
        foreign = {
            item["name"]: (item["constrained_columns"], item["referred_table"],
                           item["referred_columns"], item.get("options", {}).get("ondelete"))
            for item in inspector.get_foreign_keys(name)
        }
        assert foreign == {
            f"fk_{name}_owner_id_users": (["owner_id"], "users", ["id"], "RESTRICT"),
            f"fk_{name}_{location}_owner_id_folders": (
                [location, "owner_id"], "folders", ["id", "owner_id"], "RESTRICT"),
        }
        unique = {item["name"]: item["column_names"]
                  for item in inspector.get_unique_constraints(name)}
        assert unique == ({"uq_folders_id_owner_id": ["id", "owner_id"]}
                          if name == "folders" else {})
        indexes = {item["name"]: (item["column_names"], bool(item["unique"]))
                   for item in inspector.get_indexes(name) if not item.get("duplicates_constraint")}
        assert indexes == {f"ix_{name}_owner_id_{location}": (
            ["owner_id", location], False)}
        checks = {item["name"]: item["sqltext"].replace("(", "").replace(")", "").strip()
                  for item in inspector.get_check_constraints(name)}
        assert checks == ({"ck_files_size_bytes_nonnegative": "size_bytes >= 0"}
                          if name == "files" else {})


def deletion(session: OrmSession, user: User, constraint: str) -> None:
    """Require user deletion to fail without losing canonical owned folder/file rows."""
    try:
        with session.begin_nested():
            session.execute(delete(User).where(User.id == user.id))
    except IntegrityError as error:
        assert getattr(getattr(error.orig, "diag", None),
                       "constraint_name", None) == constraint
    else:
        raise AssertionError(
            "folder/file ownership did not restrict user deletion")
    assert session.get(User, user.id) is user


def constraints(database: Database) -> None:
    """Exercise duplicate names, adjacency, ownership, lifecycle, and restrictions."""
    now = datetime.now(timezone.utc)
    with database.session() as session:
        users = [User(name="Synthetic", email=f"metadata-{index}@example.invalid",
                      password="synthetic-placeholder", created_at=now, updated_at=now)
                 for index in range(3)]
        session.add_all(users)
        session.flush()
        owner, other, fileowner = users
        folder = dict(owner_id=owner.id, name="same",
                      created_at=now, updated_at=now)
        root = Folder(**folder)
        foreign = Folder(**{**folder, "owner_id": other.id})
        session.add_all([root, foreign, Folder(**folder)])
        session.flush()
        child = Folder(**folder, parent_id=root.id)
        session.add_all([child, Folder(**folder, parent_id=root.id),
                         Folder(**folder, parent_id=root.id)])
        session.flush()
        deep = Folder(**folder, parent_id=child.id)
        session.add(deep)
        session.flush()
        assert root.parent_id is None and child.parent_id == root.id and deep.parent_id == child.id
        assert all(item.id is not None for item in (
            root, foreign, child, deep))
        reject(session, Folder(
            **{**folder, "owner_id": uuid4()}), "fk_folders_owner_id_users")
        for parent in (foreign.id, uuid4()):
            reject(session, Folder(**folder, parent_id=parent),
                   "fk_folders_parent_id_owner_id_folders")
        file = dict(owner_id=owner.id, name="same", original_name="synthetic.md",
                    extension=".md", size_bytes=0, status="processing", created_at=now, updated_at=now)
        rootfile = File(**file)
        nested = File(**{**file, "size_bytes": 1,
                      "status": "ready"}, folder_id=root.id)
        deleting = File(**{**file, "status": "deleting"}, folder_id=root.id)
        independent = File(**{**file, "owner_id": fileowner.id})
        session.add_all([rootfile, nested, deleting, independent])
        session.flush()
        assert rootfile.id is not None and rootfile.folder_id is None
        assert nested.folder_id == root.id and nested.name == child.name == deleting.name
        session.expire_all()
        assert set(session.scalars(select(File.status))) == {
            "processing", "ready", "deleting"}
        reject(session, File(
            **{**file, "owner_id": uuid4()}), "fk_files_owner_id_users")
        for target in (foreign.id, uuid4()):
            reject(session, File(**file, folder_id=target),
                   "fk_files_folder_id_owner_id_folders")
        reject(session, File(**{**file, "size_bytes": -1}),
               "ck_files_size_bytes_nonnegative")
        try:
            with session.begin_nested():
                session.execute(text("UPDATE files SET status = 'failed' WHERE id = :id"),
                                {"id": rootfile.id})
        except DBAPIError as error:
            assert getattr(error.orig, "sqlstate", None) == "22P02"
        else:
            raise AssertionError("Unsupported file status was accepted")
        deletion(session, other, "fk_folders_owner_id_users")
        deletion(session, fileowner, "fk_files_owner_id_users")
        assert session.get(Folder, foreign.id) is foreign
        assert session.get(File, independent.id) is independent
        session.commit()


def identity(database: Database) -> dict[str, list[tuple]]:
    """Keep identity rows private in memory to prove migration preservation."""
    with database.engine.connect() as connection:
        return {name: [tuple(row) for row in connection.execute(
            text(f"SELECT * FROM {name} ORDER BY id"))]
            for name in ("users", "verifications", "sessions")}


def main() -> None:
    """Prove upgrade/reversal in isolated synthetic state with guaranteed cleanup."""
    admin = create_engine(url(constants.postgres).set(database="postgres"),
                          isolation_level="AUTOCOMMIT", hide_parameters=True,
                          connect_args={"connect_timeout": 5})
    name = "atlas_metadata_verify_" + uuid4().hex
    database = None
    created = False
    try:
        with admin.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{name}"'))
            created = True
        migrate(name, "upgrade", "0001_identity")
        engine = create_engine(url(constants.postgres).set(
            database=name), hide_parameters=True)
        database = Database(engine, sessionmaker(bind=engine))
        assert database.check().startswith("18.")
        identity_schema(engine, "0001_identity")
        identity_constraints(database)
        now = datetime.now(timezone.utc)
        with database.session() as session:
            user = User(name="Preserved", email="preserved@example.invalid",
                        password="synthetic-placeholder", created_at=now, updated_at=now)
            session.add(user)
            session.flush()
            session.add_all([
                Verification(user_id=user.id, type="auth", otp="000000",
                             expires_at=now + timedelta(minutes=10), created_at=now),
                Session(user_id=user.id, token_hash="a" * 64,
                        expires_at=now + timedelta(minutes=10), created_at=now),
            ])
            session.commit()
        before = identity(database)
        database.close()
        migrate(name, "upgrade", "head")
        schema(database)
        assert identity(database) == before
        constraints(database)
        preserved = identity(database)
        database.close()
        migrate(name, "downgrade", "0001_identity")
        identity_schema(engine, "0001_identity")
        assert identity(database) == preserved
        database.close()
        migrate(name, "upgrade", "head")
        schema(database)
        assert identity(database) == preserved
        with engine.connect() as connection:
            for table in ("folders", "files"):
                assert connection.execute(
                    text(f"SELECT count(*) FROM {table}")).scalar_one() == 0
        print(json.dumps({"canonical_schema": "passed", "ownership_and_names": "passed",
                          "lifecycle_and_size": "passed", "user_delete_restrict": "passed",
                          "identity_cascade_and_rollback": "passed", "identity_preservation": "passed",
                          "disposable_identity_metadata_identity_metadata": "passed"}))
    finally:
        if database is not None:
            database.close()
        if created:
            with admin.connect() as connection:
                connection.execute(
                    text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


if __name__ == "__main__":
    main()
