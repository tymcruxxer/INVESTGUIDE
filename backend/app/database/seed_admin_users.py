"""Development-only seed data for admin user management."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database.development_data_guard import ensure_development_data_allowed
from app.models.user import User
from app.schemas.auth import UserCreate
from app.services.auth_service import register_user
from app.services.rbac_service import (
    FINANCE_ADMIN_ROLE,
    MODERATOR_ROLE,
    OPERATIONS_ADMIN_ROLE,
    SUPPORT_ADMIN_ROLE,
    USER_ROLE,
    assign_role_to_user,
)

logger = get_logger(__name__)

DEFAULT_ADMIN_USERS: tuple[dict[str, str], ...] = (
    {"email": "operations@investguide.local", "username": "operations-admin", "role": OPERATIONS_ADMIN_ROLE},
    {"email": "finance@investguide.local", "username": "finance-admin", "role": FINANCE_ADMIN_ROLE},
    {"email": "support@investguide.local", "username": "support-admin", "role": SUPPORT_ADMIN_ROLE},
    {"email": "moderator@investguide.local", "username": "moderator", "role": MODERATOR_ROLE},
    {"email": "investor.demo@investguide.local", "username": "demo-investor", "role": USER_ROLE},
)


@dataclass(frozen=True)
class AdminUserSeedResult:
    """Summary of development admin sample user seed execution."""

    inserted: int
    skipped: int
    roles_assigned: int


def seed_admin_users(db: Session, password: str = "ChangeMe123!") -> AdminUserSeedResult:
    """Seed development admin sample users and role assignments safely."""
    ensure_development_data_allowed()
    inserted = 0
    skipped = 0
    roles_assigned = 0

    try:
        for seed_user in DEFAULT_ADMIN_USERS:
            email = seed_user["email"].strip().lower()
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = register_user(
                    db,
                    UserCreate(email=email, username=seed_user["username"], password=password),
                )
                user.is_verified = True
                inserted += 1
                logger.info("Seeded development admin user: %s", email)
            else:
                skipped += 1
                logger.info("Skipping existing development admin user: %s", email)

            assigned = assign_role_to_user(
                db,
                user,
                seed_user["role"],
                reason="Development admin sample seed",
            )
            if assigned:
                roles_assigned += 1
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Admin user seed failed; transaction rolled back")
        raise

    return AdminUserSeedResult(inserted=inserted, skipped=skipped, roles_assigned=roles_assigned)
