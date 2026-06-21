from types import SimpleNamespace

import pytest

from app.dependencies.permissions import require_permission
from app.exceptions.custom_exception import ForbiddenException
from app.security.jwt import create_access_token, decode_token
from app.security.password import hash_password, verify_password


def test_access_token_round_trip_contains_tenant_and_permissions():
    token = create_access_token(
        {
            "user_id": 10,
            "email": "owner@example.com",
            "org_id": 20,
            "permissions": ["customer.create", "invoice.read"],
        }
    )

    payload = decode_token(token)

    assert payload["user_id"] == 10
    assert payload["org_id"] == 20
    assert payload["permissions"] == ["customer.create", "invoice.read"]
    assert payload["type"] == "access"


def test_password_hash_verification():
    hashed = hash_password("Secret@123")

    assert hashed != "Secret@123"
    assert verify_password("Secret@123", hashed)
    assert not verify_password("wrong-password", hashed)


def test_permission_dependency_allows_required_permission():
    checker = require_permission("customer.create")
    current_user = SimpleNamespace(permissions=["customer.create"])

    assert checker(current_user=current_user) is current_user


def test_permission_dependency_rejects_missing_permission():
    checker = require_permission("customer.create")

    with pytest.raises(ForbiddenException):
        checker(current_user=SimpleNamespace(permissions=["customer.read"]))
