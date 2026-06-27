from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import Organization, OrganizationSettings, User  # noqa: F401
from app.schemas.auth import OrganizationSettingsUpdate
from app.services.settings_service import get_or_create_settings, update_settings


def test_lora_ai_consent_defaults_and_metadata():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        org = Organization(name="Acme", slug="acme")
        user = User(email="owner@example.com", password_hash="hash")
        db.add_all([org, user])
        db.commit()
        db.refresh(org)
        db.refresh(user)

        settings = get_or_create_settings(db, org.id)
        assert settings.lora_ai_enabled is False
        assert settings.lora_ai_consent_at is None
        assert settings.lora_ai_consent_by_user_id is None

        enabled = update_settings(
            db,
            org.id,
            OrganizationSettingsUpdate(lora_ai_enabled=True),
            actor_user_id=user.id,
        )
        assert enabled.lora_ai_enabled is True
        assert enabled.lora_ai_consent_at is not None
        assert enabled.lora_ai_consent_by_user_id == user.id

        disabled = update_settings(
            db,
            org.id,
            OrganizationSettingsUpdate(lora_ai_enabled=False),
            actor_user_id=user.id,
        )
        assert disabled.lora_ai_enabled is False
        assert disabled.lora_ai_consent_at is None
        assert disabled.lora_ai_consent_by_user_id is None
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
