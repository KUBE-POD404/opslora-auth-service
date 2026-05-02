from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import (  # noqa: F401
    Organization,
    OrganizationFeatureFlag,
    OrganizationSettings,
    OrganizationUser,
    Permission,
    RefreshToken,
    Role,
    RolePermission,
    User,
    UserRole,
)


def test_auth_api_signup_login_and_duplicate_org(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(Role(name="OWNER"))
    db.commit()
    db.close()

    class CeleryStub:
        def __init__(self):
            self.tasks = []

        def send_task(self, *args, **kwargs):
            self.tasks.append((args, kwargs))

    celery_stub = CeleryStub()
    monkeypatch.setattr("app.services.auth_service.celery", celery_stub)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        health_response = client.get("/api/v1/auth/health")
        assert health_response.status_code == 200
        assert health_response.json() == {"status": "ok"}

        signup_response = client.post(
            "/api/v1/auth/signup",
            json={
                "organization_name": "Acme Industries",
                "organization_slug": "acme-industries",
                "email": "owner@example.com",
                "password": "super-secret",
            },
        )
        assert signup_response.status_code == 200
        signup = signup_response.json()
        assert signup["email"] == "owner@example.com"
        assert signup["organization_name"] == "Acme Industries"
        assert signup["access_token"]
        assert len(celery_stub.tasks) == 1

        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "organization_slug": "acme-industries",
                "email": "owner@example.com",
                "password": "super-secret",
            },
        )
        assert login_response.status_code == 200
        assert login_response.json()["token_type"] == "bearer"
        assert login_response.json()["access_token"]

        duplicate_response = client.post(
            "/api/v1/auth/signup",
            json={
                "organization_name": "Acme Industries",
                "organization_slug": "acme-industries",
                "email": "second@example.com",
                "password": "super-secret",
            },
        )
        assert duplicate_response.status_code == 409
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
