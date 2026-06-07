from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    ChangePasswordRequest,
    CurrentUserResponse,
    LoginRequest,
    LogoutRequest,
    ProfileUpdate,
    RefreshTokenRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)

from app.dependencies.auth import CurrentUser, get_current_user
from app.services.auth_service import (
    change_password,
    get_current_profile,
    login,
    logout,
    refresh_access_token,
    signup,
    update_current_profile,
)

router = APIRouter(prefix="/auth", tags=["auth"])


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

    tokens = login(
        db=db,
        org_slug=payload.organization_slug,
        email=payload.email,
        password=payload.password,
    )

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer"
    }


@router.get("/me", response_model=CurrentUserResponse)
def get_me(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return get_current_profile(db, current_user.user_id, current_user.org_id)


@router.patch("/me", response_model=CurrentUserResponse)
def update_me(
    payload: ProfileUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return update_current_profile(db, current_user.user_id, current_user.org_id, payload)


@router.post("/change-password")
def change_current_user_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return change_password(
        db=db,
        user_id=current_user.user_id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Annotated[Session, Depends(get_db)]):
    tokens = refresh_access_token(db, payload.refresh_token)
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": "bearer",
    }


@router.post("/logout")
def logout_user(payload: LogoutRequest, db: Annotated[Session, Depends(get_db)]):
    return logout(db, payload.refresh_token)
