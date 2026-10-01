"""enforce one cover media item per project

Revision ID: 0003_project_media_cover
Revises: 0002_portfolio_domain
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_project_media_cover"
down_revision = "0002_portfolio_domain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_project_media_cover",
        "project_media",
        ["project_id"],
        unique=True,
        sqlite_where=sa.text("is_cover"),
        postgresql_where=sa.text("is_cover"),
    )


def downgrade() -> None:
    op.drop_index("uq_project_media_cover", table_name="project_media")