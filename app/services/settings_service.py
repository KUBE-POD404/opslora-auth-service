from sqlalchemy.orm import Session

from app.models.organization_settings import OrganizationFeatureFlag, OrganizationSettings


def get_or_create_settings(db: Session, organization_id: int) -> OrganizationSettings:
    settings = (
        db.query(OrganizationSettings)
        .filter(OrganizationSettings.organization_id == organization_id)
        .first()
    )

    if settings:
        return settings

    settings = OrganizationSettings(organization_id=organization_id)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_settings(db: Session, organization_id: int, payload) -> OrganizationSettings:
    settings = get_or_create_settings(db, organization_id)

    for key, value in payload.model_dump().items():
        setattr(settings, key, value)

    db.commit()
    db.refresh(settings)
    return settings


def list_feature_flags(db: Session, organization_id: int) -> list[OrganizationFeatureFlag]:
    return (
        db.query(OrganizationFeatureFlag)
        .filter(OrganizationFeatureFlag.organization_id == organization_id)
        .order_by(OrganizationFeatureFlag.flag_key.asc())
        .all()
    )


def set_feature_flag(
    db: Session,
    organization_id: int,
    flag_key: str,
    is_enabled: bool,
) -> OrganizationFeatureFlag:
    flag = (
        db.query(OrganizationFeatureFlag)
        .filter(
            OrganizationFeatureFlag.organization_id == organization_id,
            OrganizationFeatureFlag.flag_key == flag_key,
        )
        .first()
    )

    if not flag:
        flag = OrganizationFeatureFlag(
            organization_id=organization_id,
            flag_key=flag_key,
            is_enabled=is_enabled,
        )
        db.add(flag)
    else:
        flag.is_enabled = is_enabled

    db.commit()
    db.refresh(flag)
    return flag
