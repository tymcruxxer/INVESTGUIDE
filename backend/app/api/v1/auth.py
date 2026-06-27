"""Authentication endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, SignupResponse, UserCreate, UserRead
from app.services.auth_service import (
    AuthServiceError,
    create_access_token,
    get_current_user,
    register_user,
    verify_credentials,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _serialize_user(user: User) -> dict[str, Any]:
    """Serialize user ORM data for API responses."""
    return UserRead.model_validate(user).model_dump(mode="json")


@router.post("/signup", response_model=None)
async def signup(payload: UserCreate, db: Session = Depends(get_db)) -> dict[str, Any] | JSONResponse:
    """Register a user and return an access token."""
    try:
        user = register_user(db, payload)
    except AuthServiceError as exc:
        return JSONResponse(
            status_code=409,
            content=error_response(message=exc.message, error_code=exc.error_code),
        )

    token = create_access_token(user)
    data = SignupResponse(
        user=UserRead.model_validate(user),
        access_token=token,
    ).model_dump(mode="json")
    return success_response(message="User registered successfully", data=data)


@router.post("/login", response_model=None)
async def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict[str, Any] | JSONResponse:
    """Authenticate a user and return a bearer token."""
    user = verify_credentials(db, payload.email, payload.password)
    if user is None:
        return JSONResponse(
            status_code=401,
            content=error_response(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
            ),
        )

    data = LoginResponse(
        access_token=create_access_token(user),
        user=UserRead.model_validate(user),
    ).model_dump(mode="json")
    return success_response(message="Login successful", data=data)


@router.get("/me", response_model=None)
async def me(current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Return the authenticated user."""
    return success_response(message="Current user retrieved successfully", data=_serialize_user(current_user))
