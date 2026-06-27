"""Authentication request and response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_email(value: str) -> str:
    email = value.strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValueError("A valid email address is required")
    return email


class UserCreate(BaseModel):
    """Signup payload."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    username: str | None = Field(default=None, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Normalize and lightly validate email without optional extras."""
        return _normalize_email(value)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str | None) -> str | None:
        """Store blank usernames as null."""
        if value is None:
            return None
        username = value.strip()
        return username or None


class UserRead(BaseModel):
    """Public user representation."""

    id: int
    email: str
    username: str | None = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Login payload."""

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Normalize and lightly validate email without optional extras."""
        return _normalize_email(value)


class LoginResponse(BaseModel):
    """Successful authentication response."""

    access_token: str
    token_type: str = "bearer"
    user: UserRead


class SignupResponse(BaseModel):
    """Successful signup response."""

    user: UserRead
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT claims used by the backend."""

    sub: int
    email: str
    exp: int | datetime

    @field_validator("sub", mode="before")
    @classmethod
    def parse_subject(cls, value: Any) -> int:
        """JWT subjects are strings on the wire but user ids internally."""
        return int(value)
