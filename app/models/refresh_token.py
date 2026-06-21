from sqlalchemy import Boolean, Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=False)

    token_hash = Column(String(128), nullable=True, index=True)

    token = Column(String(500), nullable=True)

    organization_id = Column(Integer, nullable=True)

    revoked = Column(Boolean, nullable=False, default=False)

    revoked_at = Column(DateTime(timezone=True), nullable=True)

    replaced_by_token_hash = Column(String(128), nullable=True)

    expires_at = Column(DateTime(timezone=True))

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
