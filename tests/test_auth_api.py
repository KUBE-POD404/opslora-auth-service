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
        assert signup["refresh_token"]
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
        login = login_response.json()
        assert login["token_type"] == "bearer"
        assert login["access_token"]
        assert login["refresh_token"]

        auth_headers = {"Authorization": f"Bearer {login['access_token']}"}

        me_response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert me_response.status_code == 200
        profile = me_response.json()
        assert profile["email"] == "owner@example.com"
        assert profile["organization_name"] == "Acme Industries"
        assert profile["organization_slug"] == "acme-industries"
        assert profile["roles"] == ["OWNER"]
        assert profile["permissions"] == []
        assert profile["compact_tables"] is True
        assert profile["email_workflow_summaries"] is True

        update_profile_response = client.patch(
            "/api/v1/auth/me",
            headers=auth_headers,
            json={
                "full_name": "Opslora Owner",
                "display_name": "Owner",
                "phone": "+91 90000 00000",
                "timezone": "Asia/Calcutta",
                "language": "English",
                "email_workflow_summaries": False,
                "compact_tables": True,
            },
        )
        assert update_profile_response.status_code == 200
        updated_profile = update_profile_response.json()
        assert updated_profile["full_name"] == "Opslora Owner"
        assert updated_profile["display_name"] == "Owner"
        assert updated_profile["email_workflow_summaries"] is False

        wrong_password_response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "wrong-password",
                "new_password": "new-super-secret",
            },
        )
        assert wrong_password_response.status_code == 401

        change_password_response = client.post(
            "/api/v1/auth/change-password",
            headers=auth_headers,
            json={
                "current_password": "super-secret",
                "new_password": "new-super-secret",
            },
        )
        assert change_password_response.status_code == 200
        assert change_password_response.json() == {"status": "password_changed"}

        old_password_login_response = client.post(
            "/api/v1/auth/login",
            json={
                "organization_slug": "acme-industries",
                "email": "owner@example.com",
                "password": "super-secret",
            },
        )
        assert old_password_login_response.status_code == 401

        new_password_login_response = client.post(
            "/api/v1/auth/login",
            json={
                "organization_slug": "acme-industries",
                "email": "owner@example.com",
                "password": "new-super-secret",
            },
        )
        assert new_password_login_response.status_code == 200

        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": login["refresh_token"]},
        )
        assert refresh_response.status_code == 200
        refreshed = refresh_response.json()
        assert refreshed["access_token"]
        assert refreshed["refresh_token"]
        assert refreshed["refresh_token"] != login["refresh_token"]

        reused_refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": login["refresh_token"]},
        )
        assert reused_refresh_response.status_code == 401

        logout_response = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refreshed["refresh_token"]},
        )
        assert logout_response.status_code == 200
        assert logout_response.json() == {"status": "logged_out"}

        logged_out_refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refreshed["refresh_token"]},
        )
        assert logged_out_refresh_response.status_code == 401

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
