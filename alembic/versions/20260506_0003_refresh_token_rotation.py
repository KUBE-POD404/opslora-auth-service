"""refresh token rotation

Revision ID: 20260506_auth_0003
Revises: 20260501_auth_0001
Create Date: 2026-05-06
"""

from alembic import op
import sqlalchemy as sa

revision = "20260506_auth_0003"
down_revision = "20260501_auth_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("refresh_tokens", sa.Column("token_hash", sa.String(length=128), nullable=True))
    op.add_column("refresh_tokens", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.add_column("refresh_tokens", sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("refresh_tokens", sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("refresh_tokens", sa.Column("replaced_by_token_hash", sa.String(length=128), nullable=True))
    op.create_index(op.f("ix_refresh_tokens_token_hash"), "refresh_tokens", ["token_hash"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_refresh_tokens_token_hash"), table_name="refresh_tokens")
    op.drop_column("refresh_tokens", "replaced_by_token_hash")
    op.drop_column("refresh_tokens", "revoked_at")
    op.drop_column("refresh_tokens", "revoked")
    op.drop_column("refresh_tokens", "organization_id")
    op.drop_column("refresh_tokens", "token_hash")
