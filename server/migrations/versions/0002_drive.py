"""Create canonical owner-scoped drive persistence."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_drive"
down_revision = "0001_identity"
branch_labels = None
depends_on = None

status = postgresql.ENUM("processing", "ready", "deleting",
                         name="file_status", create_type=False)


def upgrade() -> None:
    """Add only drive objects, with ownership enforced by composite foreign keys."""
    status.create(op.get_bind(), checkfirst=False)
    op.create_table(
        "folders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_folders"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"],
                                ondelete="RESTRICT", name="fk_folders_owner_id_users"),
        sa.UniqueConstraint("id", "owner_id", name="uq_folders_id_owner_id"),
        sa.ForeignKeyConstraint(
            ["parent_id", "owner_id"], ["folders.id", "folders.owner_id"],
            ondelete="RESTRICT", name="fk_folders_parent_id_owner_id_folders"),
    )
    op.create_index("ix_folders_owner_id_parent_id", "folders",
                    ["owner_id", "parent_id"], unique=False)
    op.create_table(
        "files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("folder_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("original_name", sa.Text(), nullable=False),
        sa.Column("extension", sa.Text(), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("status", status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_files"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"],
                                ondelete="RESTRICT", name="fk_files_owner_id_users"),
        sa.ForeignKeyConstraint(
            ["folder_id", "owner_id"], ["folders.id", "folders.owner_id"],
            ondelete="RESTRICT", name="fk_files_folder_id_owner_id_folders"),
        sa.CheckConstraint("size_bytes >= 0",
                           name="ck_files_size_bytes_nonnegative"),
    )
    op.create_index("ix_files_owner_id_folder_id", "files",
                    ["owner_id", "folder_id"], unique=False)


def downgrade() -> None:
    """Remove drive objects in reverse dependency order, preserving identity."""
    op.drop_index("ix_files_owner_id_folder_id", table_name="files")
    op.drop_table("files")
    op.drop_index("ix_folders_owner_id_parent_id", table_name="folders")
    op.drop_table("folders")
    status.drop(op.get_bind(), checkfirst=False)
