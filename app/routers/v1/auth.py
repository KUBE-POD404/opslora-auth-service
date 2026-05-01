from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    FeatureFlagResponse,
    FeatureFlagUpdate,
    SignupRequest,
    SignupResponse,
    LoginRequest,
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
    TokenResponse,
)

from app.services.auth_service import signup, login
from app.services.settings_service import (
    get_or_create_settings,
    list_feature_flags,
    set_feature_flag,
    update_settings,
)
from app.dependencies.permissions import require_permission

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/signup", response_model=SignupResponse)
def signup_user(payload: SignupRequest, db: Annotated[Session, Depends(get_db)]):

    result = signup(
        db=db,
        org_name=payload.organization_name,
        org_slug=payload.organization_slug,
        email=payload.email,
        password=payload.password,
    )

    return result


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]):

    token = login(
        db=db,
        org_slug=payload.organization_slug,
        email=payload.email,
        password=payload.password,
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/organization/settings", response_model=OrganizationSettingsResponse)
def get_organization_settings(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(require_permission("organization.settings.read"))],
):
    return get_or_create_settings(db, current_user.org_id)


@router.put("/organization/settings", response_model=OrganizationSettingsResponse)
def update_organization_settings(
    payload: OrganizationSettingsUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(require_permission("organization.settings.update"))],
):
    return update_settings(db, current_user.org_id, payload)


@router.get("/organization/feature-flags", response_model=list[FeatureFlagResponse])
def get_organization_feature_flags(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(require_permission("organization.settings.read"))],
):
    return list_feature_flags(db, current_user.org_id)


@router.put("/organization/feature-flags/{flag_key}", response_model=FeatureFlagResponse)
def update_organization_feature_flag(
    flag_key: str,
    payload: FeatureFlagUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(require_permission("organization.settings.update"))],
):
    return set_feature_flag(db, current_user.org_id, flag_key, payload.is_enabled)
