"""add portfolio domain tables

Revision ID: 0002_portfolio_domain
Revises: 0001_auth_tables
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_portfolio_domain"
down_revision = "0001_auth_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("short_description", sa.String(length=500)),
        sa.Column("description", sa.Text()),
        sa.Column("problem", sa.Text()),
        sa.Column("solution", sa.Text()),
        sa.Column("technical_details", sa.Text()),
        sa.Column("technical_decisions", sa.Text()),
        sa.Column("challenges", sa.Text()),
        sa.Column("outcome", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planning"),
        sa.Column("publication_status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("github_url", sa.String(length=2048)),
        sa.Column("live_url", sa.String(length=2048)),
        sa.Column("meta_title", sa.String(length=255)),
        sa.Column("meta_description", sa.String(length=500)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_projects_slug"),
    )
    op.create_index("ix_projects_slug", "projects", ["slug"], unique=True)

    op.create_table(
        "technologies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("short_description", sa.String(length=500)),
        sa.Column("category", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("icon", sa.String(length=255)),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_technologies_name"),
        sa.UniqueConstraint("slug", name="uq_technologies_slug"),
    )
    op.create_index("ix_technologies_name", "technologies", ["name"], unique=True)
    op.create_index("ix_technologies_slug", "technologies", ["slug"], unique=True)

    op.create_table(
        "project_features",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_project_features_project_id", "project_features", ["project_id"])

    op.create_table(
        "project_technologies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("technology_id", sa.Uuid(), sa.ForeignKey("technologies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("project_id", "technology_id", name="uq_project_technology_pair"),
    )
    op.create_index("ix_project_technologies_project_id", "project_technologies", ["project_id"])
    op.create_index("ix_project_technologies_technology_id", "project_technologies", ["technology_id"])

    op.create_table(
        "media",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("original_filename", sa.String(length=255)),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=64), nullable=False),
        sa.Column("file_size", sa.Integer()),
        sa.Column("width", sa.Integer()),
        sa.Column("height", sa.Integer()),
        sa.Column("title", sa.String(length=255)),
        sa.Column("alt_text", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("storage_key", name="uq_media_storage_key"),
    )
    op.create_index("ix_media_storage_key", "media", ["storage_key"], unique=True)

    op.create_table(
        "project_media",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("project_id", sa.Uuid(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("title", sa.String(length=255)),
        sa.Column("caption", sa.Text()),
        sa.Column("alt_text", sa.String(length=500)),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_cover", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "media_id", name="uq_project_media_pair"),
    )
    op.create_index("ix_project_media_project_id", "project_media", ["project_id"])
    op.create_index("ix_project_media_media_id", "project_media", ["media_id"])


def downgrade() -> None:
    op.drop_table("project_media")
    op.drop_table("media")
    op.drop_table("project_technologies")
    op.drop_table("project_features")
    op.drop_table("technologies")
    op.drop_table("projects")
