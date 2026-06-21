from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.permissions import require_permission
from app.schemas.auth import (
    FeatureFlagResponse,
    FeatureFlagUpdate,
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
)
from app.services.settings_service import (
    get_or_create_settings,
    list_feature_flags,
    set_feature_flag,
    update_settings,
)

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/organization", response_model=OrganizationSettingsResponse)
def get_organization_settings(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(require_permission("organization.settings.read"))],
):
    return get_or_create_settings(db, current_user.org_id)


@router.put("/organization", response_model=OrganizationSettingsResponse)
def update_organization_settings(
    payload: OrganizationSettingsUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(require_permission("organization.settings.update"))],
):
    return update_settings(db, current_user.org_id, payload)


@router.get("/feature-flags", response_model=list[FeatureFlagResponse])
def get_organization_feature_flags(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(require_permission("organization.settings.read"))],
):
    return list_feature_flags(db, current_user.org_id)


@router.put("/feature-flags/{flag_key}", response_model=FeatureFlagResponse)
def update_organization_feature_flag(
    flag_key: str,
    payload: FeatureFlagUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[object, Depends(require_permission("organization.settings.update"))],
):
    return set_feature_flag(db, current_user.org_id, flag_key, payload.is_enabled)
