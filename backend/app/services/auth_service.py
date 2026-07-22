"""Authentication service and FastAPI dependencies."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import TokenPayload, UserCreate

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=True)
optional_bearer_scheme = HTTPBearer(auto_error=False)


class AuthServiceError(ValueError):
    """Raised when an authentication business rule fails."""

    def __init__(self, message: str, error_code: str) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return whether a plaintext password matches a stored hash."""
    return password_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str) -> User | None:
    """Return a user by normalized email address."""
    normalized_email = email.strip().lower()
    return db.scalars(select(User).where(User.email == normalized_email)).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Return a user by primary key."""
    return db.get(User, user_id)


def register_user(db: Session, payload: UserCreate) -> User:
    """Register a user with a hashed password."""
    if get_user_by_email(db, payload.email) is not None:
        raise AuthServiceError("Email is already registered", "EMAIL_ALREADY_REGISTERED")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AuthServiceError("Email is already registered", "EMAIL_ALREADY_REGISTERED") from exc
    db.refresh(user)
    return user


def verify_credentials(db: Session, email: str, password: str) -> User | None:
    """Return the user when credentials are valid."""
    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    user.last_login_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return user


def create_access_token(user: User, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token for a user."""
    settings = get_settings()
    expires_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload:
    """Decode and validate a JWT access token."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return TokenPayload.model_validate(payload)
    except (JWTError, ValueError) as exc:
        raise AuthServiceError("Invalid authentication token", "INVALID_TOKEN") from exc


def _unauthorized(message: str = "Authentication is required") -> HTTPException:
    """Build a consistent 401 exception for auth dependencies."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _user_from_credentials(db: Session, credentials: HTTPAuthorizationCredentials) -> User:
    token_payload = decode_access_token(credentials.credentials)
    user = get_user_by_id(db, token_payload.sub)
    if user is None or not user.is_active:
        raise AuthServiceError("Authenticated user was not found", "USER_NOT_FOUND")
    return user


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """FastAPI dependency returning the authenticated user."""
    try:
        return _user_from_credentials(db, credentials)
    except AuthServiceError as exc:
        raise _unauthorized(exc.message) from exc


def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    """Return the current user when a bearer token is supplied."""
    if credentials is None:
        return None
    try:
        return _user_from_credentials(db, credentials)
    except AuthServiceError as exc:
        raise _unauthorized(exc.message) from exc


