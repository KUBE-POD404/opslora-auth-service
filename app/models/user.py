from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone as utc_timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(150), unique=True, nullable=False, index=True)

    password_hash = Column(String(255), nullable=False)

    full_name = Column(String(150), nullable=True)

    display_name = Column(String(100), nullable=True)

    phone = Column(String(50), nullable=True)

    timezone = Column(String(100), nullable=True)

    language = Column(String(50), nullable=True)

    email_workflow_summaries = Column(Boolean, default=True, nullable=False)

    compact_tables = Column(Boolean, default=True, nullable=False)

    is_active = Column(Boolean, default=True)

    is_verified = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(utc_timezone.utc)
    )
