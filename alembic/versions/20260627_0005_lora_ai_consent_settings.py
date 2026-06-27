"""lora ai consent settings

Revision ID: 20260627_auth_0005
Revises: 20260520_auth_0004
Create Date: 2026-06-27
"""

from alembic import op
import sqlalchemy as sa


revision = "20260627_auth_0005"
down_revision = "20260520_auth_0004"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "organization_settings",
        sa.Column("lora_ai_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "organization_settings",
        sa.Column("lora_ai_consent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "organization_settings",
        sa.Column("lora_ai_consent_by_user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_organization_settings_lora_ai_consent_by_user",
        "organization_settings",
        "users",
        ["lora_ai_consent_by_user_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint(
        "fk_organization_settings_lora_ai_consent_by_user",
        "organization_settings",
        type_="foreignkey",
    )
    op.drop_column("organization_settings", "lora_ai_consent_by_user_id")
    op.drop_column("organization_settings", "lora_ai_consent_at")
    op.drop_column("organization_settings", "lora_ai_enabled")
