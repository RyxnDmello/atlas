import io
from uuid import UUID
from typing import cast
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import BigInteger, CheckConstraint, ColumnDefault, DateTime, ForeignKeyConstraint, Text, UniqueConstraint, Uuid

from app.models.postgres import Base, File, Folder

from tests import drive_live


class DriveMetadataTests(TestCase):
    """Prove the exact drive contract without connecting to a datastore."""

    def test_inventory_columns_types_nullability_and_defaults(self) -> None:
        self.assertEqual(set(Base.metadata.tables), {
            "users", "verifications", "sessions", "folders", "files"})
        expected = {
            Folder: {"id", "owner_id", "parent_id", "name", "description", "created_at", "updated_at"},
            File: {"id", "owner_id", "folder_id", "name", "description", "original_name",
                   "extension", "size_bytes", "status", "created_at", "updated_at"},
        }
        for model, names in expected.items():
            table = Base.metadata.tables[model.__tablename__]
            self.assertIs(table.metadata, Base.metadata)
            self.assertEqual(set(table.columns.keys()), names)
            self.assertEqual(list(table.primary_key.columns.keys()), ["id"])
            self.assertEqual(table.primary_key.name, f"pk_{table.name}")
            for column in table.columns:
                with self.subTest(table=table.name, column=column.name):
                    self.assertEqual(column.nullable, column.name in {
                        "parent_id", "folder_id", "description"})
                    self.assertIsNone(column.server_default)
                    self.assertIsNone(column.onupdate)
                    self.assertIsNone(column.server_onupdate)
                    if column.name == "id":
                        self.assertIsNotNone(column.default)
                        default = column.default
                        assert isinstance(
                            default, ColumnDefault) and callable(default.arg)
                        first, second = default.arg(None), default.arg(None)
                        self.assertIsInstance(first, UUID)
                        assert isinstance(first, UUID)
                        self.assertEqual(first.version, 4)
                        self.assertNotEqual(first, second)
                    else:
                        self.assertIsNone(column.default)
                    if column.name == "id" or column.name.endswith("_id"):
                        self.assertIsInstance(column.type, Uuid)
                    elif column.name.endswith("_at"):
                        self.assertIsInstance(column.type, DateTime)
                        self.assertTrue(cast(DateTime, column.type).timezone)
                    elif column.name == "size_bytes":
                        self.assertIsInstance(column.type, BigInteger)
                    elif column.name == "status":
                        self.assertIsInstance(column.type, ENUM)
                    else:
                        self.assertIsInstance(column.type, Text)

    def test_exact_enum_and_constraints(self) -> None:
        status = cast(ENUM, File.__table__.c.status.type)
        self.assertEqual(status.name, "file_status")
        self.assertEqual(status.enums, ["processing", "ready", "deleting"])
        for model, location in ((Folder, "parent_id"), (File, "folder_id")):
            table = Base.metadata.tables[model.__tablename__]
            foreign = {
                item.name: (tuple(item.columns.keys()),
                            tuple(element.target_fullname for element in item.elements), item.ondelete)
                for item in table.constraints if isinstance(item, ForeignKeyConstraint)
            }
            self.assertEqual(foreign, {
                f"fk_{table.name}_owner_id_users": (("owner_id",), ("users.id",), "RESTRICT"),
                f"fk_{table.name}_{location}_owner_id_folders": (
                    (location, "owner_id"), ("folders.id", "folders.owner_id"), "RESTRICT"),
            })
            unique = {item.name: tuple(item.columns.keys()) for item in table.constraints
                      if isinstance(item, UniqueConstraint)}
            self.assertEqual(unique, {"uq_folders_id_owner_id": (
                "id", "owner_id")} if model is Folder else {})
            checks = {item.name: str(item.sqltext) for item in table.constraints
                      if isinstance(item, CheckConstraint)}
            self.assertEqual(checks, {"ck_files_size_bytes_nonnegative":
                                      "size_bytes >= 0"} if model is File else {})
            self.assertEqual(len(table.constraints), 4)
            self.assertTrue(all(item.name for item in table.constraints))
            self.assertEqual({item.name: (tuple(item.columns.keys()), item.unique)
                              for item in table.indexes}, {
                f"ix_{table.name}_owner_id_{location}": (("owner_id", location), False)})


class DriveMigrationTests(TestCase):
    """Check the revision graph and isolated drive DDL in both directions."""

    def config(self, buffer: io.StringIO) -> Config:
        """Use the production Alembic environment with an offline output buffer."""
        return Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"),
                      output_buffer=buffer)

    def test_single_head_and_linear_identity_dependency(self) -> None:
        script = ScriptDirectory.from_config(self.config(io.StringIO()))
        self.assertEqual(script.get_heads(), ["0002_drive"])
        revision = script.get_revision("0002_drive")
        assert revision is not None
        self.assertEqual(revision.down_revision, "0001_identity")
        self.assertEqual([item.revision for item in script.walk_revisions()],
                         ["0002_drive", "0001_identity"])

    def test_offline_upgrade_is_additive_and_dependency_safe(self) -> None:
        buffer = io.StringIO()
        command.upgrade(self.config(buffer),
                        "0001_identity:0002_drive", sql=True)
        sql = buffer.getvalue()
        self.assertEqual(sql.count("CREATE TYPE file_status"), 1)
        self.assertIn("ENUM ('processing', 'ready', 'deleting')", sql)
        self.assertLess(sql.index("CREATE TYPE file_status"),
                        sql.index("CREATE TABLE folders"))
        self.assertLess(sql.index("CREATE TABLE folders"),
                        sql.index("CREATE TABLE files"))
        self.assertEqual(sql.count("CREATE TABLE "), 2)
        for fragment in (
            "CONSTRAINT uq_folders_id_owner_id UNIQUE (id, owner_id)",
            "FOREIGN KEY(parent_id, owner_id) REFERENCES folders (id, owner_id) ON DELETE RESTRICT",
            "FOREIGN KEY(folder_id, owner_id) REFERENCES folders (id, owner_id) ON DELETE RESTRICT",
            "CONSTRAINT ck_files_size_bytes_nonnegative CHECK (size_bytes >= 0)",
            "CREATE INDEX ix_folders_owner_id_parent_id ON folders (owner_id, parent_id)",
            "CREATE INDEX ix_files_owner_id_folder_id ON files (owner_id, folder_id)",
            "status file_status NOT NULL", "size_bytes BIGINT NOT NULL",
        ):
            self.assertIn(fragment, sql)
        self.assertEqual(sql.count("ON DELETE RESTRICT"), 4)
        self.assertEqual(sql.count("TIMESTAMP WITH TIME ZONE NOT NULL"), 4)
        for fragment in ("ALTER TABLE", "CREATE UNIQUE INDEX", "UNIQUE (name)",
                         "verification_type", "CASCADE", "DEFAULT", "postgresql+psycopg"):
            self.assertNotIn(fragment, sql)

    def test_offline_downgrade_preserves_identity(self) -> None:
        buffer = io.StringIO()
        command.downgrade(self.config(buffer),
                          "0002_drive:0001_identity", sql=True)
        sql = buffer.getvalue()
        self.assertLess(sql.index("DROP TABLE files"),
                        sql.index("DROP TABLE folders"))
        self.assertLess(sql.index("DROP TABLE folders"),
                        sql.index("DROP TYPE file_status"))
        self.assertEqual(sql.count("DROP TABLE "), 2)
        self.assertEqual(sql.count("DROP TYPE "), 1)
        for name in ("users", "verifications", "sessions", "verification_type"):
            self.assertNotIn(f"DROP TABLE {name}", sql)
            self.assertNotIn(f"DROP TYPE {name}", sql)


class DriveAcceptanceSafetyTests(TestCase):
    """Verify destructive acceptance cannot target the configured normal database."""

    def test_migration_rejects_non_disposable_database_names(self) -> None:
        with patch.object(drive_live.subprocess, "run") as run:
            for name in ("postgres", "atlas", "atlas_drive_verify_", "other_" + "a" * 32):
                with self.subTest(name=name), self.assertRaises(AssertionError):
                    drive_live.migrate(name, "downgrade", "0001_identity")
            run.assert_not_called()

    def test_failure_after_creation_still_drops_only_disposable_database(self) -> None:
        admin = Mock()
        connection = Mock()
        scope = Mock()
        scope.__enter__ = Mock(return_value=connection)
        scope.__exit__ = Mock(return_value=False)
        admin.connect.return_value = scope
        with patch.object(drive_live, "create_engine", return_value=admin), patch.object(
                drive_live, "migrate", side_effect=RuntimeError("injected")) as migrate:
            with self.assertRaisesRegex(RuntimeError, "injected"):
                drive_live.main()
        name = migrate.call_args.args[0]
        self.assertTrue(name.startswith("atlas_drive_verify_"))
        self.assertEqual(len(name), 51)
        self.assertEqual([str(call.args[0]) for call in connection.execute.call_args_list], [
            f'CREATE DATABASE "{name}"', f'DROP DATABASE "{name}" WITH (FORCE)'])
        admin.dispose.assert_called_once_with()
