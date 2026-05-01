from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.logging_config import organization_id_ctx, user_id_ctx
from app.exceptions.custom_exception import UnauthorizedException
from app.security.jwt import InvalidTokenError, decode_token

security = HTTPBearer(auto_error=False)


class CurrentUser:
    def __init__(self, user_id: int, org_id: int, permissions: list[str], email: str | None = None):
        self.user_id = user_id
        self.org_id = org_id
        self.permissions = permissions
        self.email = email


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authorization header missing")

    if credentials.scheme.lower() != "bearer":
        raise UnauthorizedException("Invalid authentication scheme")

    try:
        payload = decode_token(credentials.credentials)
    except InvalidTokenError:
        raise UnauthorizedException("Invalid or expired token")

    user_id = payload.get("user_id")
    org_id = payload.get("org_id")
    permissions = payload.get("permissions", [])
    email = payload.get("email")

    if not user_id or not org_id:
        raise UnauthorizedException("Invalid token payload")

    user_id_ctx.set(user_id)
    organization_id_ctx.set(org_id)
    return CurrentUser(user_id=user_id, org_id=org_id, permissions=permissions, email=email)
