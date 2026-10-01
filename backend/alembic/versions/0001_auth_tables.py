"""create authentication tables

Revision ID: 0001_auth_tables
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_auth_tables"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("users", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("email", sa.String(320), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(32), nullable=False, server_default="admin"), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("email_verified_at", sa.DateTime(timezone=True)), sa.Column("last_login_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("email"))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("refresh_tokens", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("token_hash", sa.String(64), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("revoked_at", sa.DateTime(timezone=True)), sa.Column("replaced_by_token_id", sa.Uuid(), sa.ForeignKey("refresh_tokens.id", ondelete="SET NULL")), sa.Column("created_by_ip", sa.String(45)), sa.Column("user_agent", sa.String(512)), sa.UniqueConstraint("token_hash"))
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])

def downgrade() -> None:
    op.drop_table("refresh_tokens")
    op.drop_table("users")
