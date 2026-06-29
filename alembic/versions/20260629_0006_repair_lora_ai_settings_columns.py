"""repair lora ai settings columns

Revision ID: 20260629_auth_0006
Revises: 20260627_auth_0005
Create Date: 2026-06-29
"""

from alembic import op
import sqlalchemy as sa


revision = "20260629_auth_0006"
down_revision = "20260627_auth_0005"
branch_labels = None
depends_on = None


LORA_CONSENT_FK = "fk_organization_settings_lora_ai_consent_by_user"


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def _foreign_key_names(table_name: str) -> set[str | None]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {fk.get("name") for fk in inspector.get_foreign_keys(table_name)}


def upgrade():
    columns = _column_names("organization_settings")

    if "lora_ai_enabled" not in columns:
        op.add_column(
            "organization_settings",
            sa.Column("lora_ai_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        )

    if "lora_ai_consent_at" not in columns:
        op.add_column(
            "organization_settings",
            sa.Column("lora_ai_consent_at", sa.DateTime(timezone=True), nullable=True),
        )

    if "lora_ai_consent_by_user_id" not in columns:
        op.add_column(
            "organization_settings",
            sa.Column("lora_ai_consent_by_user_id", sa.Integer(), nullable=True),
        )

    if LORA_CONSENT_FK not in _foreign_key_names("organization_settings"):
        op.create_foreign_key(
            LORA_CONSENT_FK,
            "organization_settings",
            "users",
            ["lora_ai_consent_by_user_id"],
            ["id"],
        )


def downgrade():
    if LORA_CONSENT_FK in _foreign_key_names("organization_settings"):
        op.drop_constraint(
            LORA_CONSENT_FK,
            "organization_settings",
            type_="foreignkey",
        )

    columns = _column_names("organization_settings")
    if "lora_ai_consent_by_user_id" in columns:
        op.drop_column("organization_settings", "lora_ai_consent_by_user_id")
    if "lora_ai_consent_at" in columns:
        op.drop_column("organization_settings", "lora_ai_consent_at")
    if "lora_ai_enabled" in columns:
        op.drop_column("organization_settings", "lora_ai_enabled")
