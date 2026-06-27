"""Investor profile endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.models.user import User
from app.schemas.investor_profile import InvestorProfileCreate, InvestorProfileRead, InvestorProfileUpdate
from app.services.auth_service import get_optional_current_user
from app.services.personalization_service import (
    InvestorProfileConflictError,
    InvestorProfileValidationError,
    create_investor_profile,
    get_investor_profile,
    update_investor_profile,
)

router = APIRouter(prefix="/investor-profile", tags=["investor-profile"])


def _serialize_profile(profile: InvestorProfileRead) -> dict[str, Any]:
    """Serialize a profile schema into an API-safe dictionary."""
    return profile.model_dump(mode="json")


def _is_development_environment() -> bool:
    """Return whether unauthenticated development fallback is allowed."""
    return get_settings().environment.lower() == "development"


def _unauthenticated_response() -> JSONResponse:
    """Return a consistent 401 response for non-development unauthenticated requests."""
    return JSONResponse(
        status_code=401,
        content=error_response(
            message="Authentication is required",
            error_code="AUTHENTICATION_REQUIRED",
        ),
    )


def _not_found_response() -> JSONResponse:
    """Return a consistent missing profile response."""
    return JSONResponse(
        status_code=404,
        content=error_response(
            message="Investor profile was not found",
            error_code="INVESTOR_PROFILE_NOT_FOUND",
        ),
    )


def _validation_error_response(exc: InvestorProfileValidationError) -> JSONResponse:
    """Return a consistent profile validation error envelope."""
    return JSONResponse(
        status_code=422,
        content=error_response(
            message="Investor profile validation failed",
            error_code="INVESTOR_PROFILE_VALIDATION_ERROR",
            details=exc.details,
        ),
    )


def _profile_resolution(current_user: User | None) -> str:
    """Describe how the current profile was resolved."""
    if current_user is not None:
        return "authenticated_user"
    return "development_fallback_first_profile"


@router.get("", response_model=None)
async def get_profile(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict[str, Any] | JSONResponse:
    """Return the authenticated user's profile or the development fallback profile."""
    if current_user is None and not _is_development_environment():
        return _unauthenticated_response()

    profile = get_investor_profile(db, current_user)
    if profile is None:
        return _not_found_response()

    return success_response(
        message="Investor profile retrieved successfully",
        data=_serialize_profile(profile),
        meta={"profile_resolution": _profile_resolution(current_user)},
    )


@router.post("", response_model=None)
async def create_profile(
    payload: InvestorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict[str, Any] | JSONResponse:
    """Create an investor profile for the authenticated user or development fallback."""
    if current_user is None and not _is_development_environment():
        return _unauthenticated_response()

    try:
        profile = create_investor_profile(db, payload, current_user)
    except InvestorProfileValidationError as exc:
        return _validation_error_response(exc)
    except InvestorProfileConflictError:
        return JSONResponse(
            status_code=409,
            content=error_response(
                message="Investor profile already exists for this user",
                error_code="INVESTOR_PROFILE_ALREADY_EXISTS",
            ),
        )

    return success_response(
        message="Investor profile created successfully",
        data=_serialize_profile(profile),
        meta={"profile_resolution": _profile_resolution(current_user)},
    )


@router.put("", response_model=None)
async def update_profile(
    payload: InvestorProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict[str, Any] | JSONResponse:
    """Update the authenticated user's profile or the development fallback profile."""
    if current_user is None and not _is_development_environment():
        return _unauthenticated_response()

    try:
        profile = update_investor_profile(db, payload, current_user)
    except InvestorProfileValidationError as exc:
        return _validation_error_response(exc)

    if profile is None:
        return _not_found_response()

    return success_response(
        message="Investor profile updated successfully",
        data=_serialize_profile(profile),
        meta={"profile_resolution": _profile_resolution(current_user)},
    )
