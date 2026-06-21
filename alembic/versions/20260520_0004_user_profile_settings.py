"""user profile settings

Revision ID: 20260520_auth_0004
Revises: 20260506_auth_0003
Create Date: 2026-05-20
"""

from alembic import op
import sqlalchemy as sa


revision = "20260520_auth_0004"
down_revision = "20260506_auth_0003"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("full_name", sa.String(length=150), nullable=True))
    op.add_column("users", sa.Column("display_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column("users", sa.Column("timezone", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("language", sa.String(length=50), nullable=True))
    op.add_column(
        "users",
        sa.Column(
            "email_workflow_summaries",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.add_column(
        "users",
        sa.Column("compact_tables", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade():
    op.drop_column("users", "compact_tables")
    op.drop_column("users", "email_workflow_summaries")
    op.drop_column("users", "language")
    op.drop_column("users", "timezone")
    op.drop_column("users", "phone")
    op.drop_column("users", "display_name")
    op.drop_column("users", "full_name")
