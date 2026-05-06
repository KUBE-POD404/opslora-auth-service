from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)

from app.services.auth_service import login, logout, refresh_access_token, signup

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
