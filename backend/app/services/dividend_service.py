"""Service helpers for dividend data retrieval with fixture isolation."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.development_data_guard import get_development_data_policy
from app.models.dividend import Dividend


def get_company_dividends(db: Session, company: Any) -> list[Dividend]:
    """Return dividend records using verified-over-development precedence."""
    rows = list(
        db.scalars(
            select(Dividend)
            .where(Dividend.company_id == company.id)
            .order_by(Dividend.fiscal_year.desc().nullslast(), Dividend.payment_date.desc().nullslast(), Dividend.id.desc())
        ).all()
    )
    if not rows:
        return []

    verified_rows = [row for row in rows if not row.is_development_data]
    if verified_rows:
        return verified_rows

    policy = get_development_data_policy()
    if policy.permits_fixtures:
        return rows
    return []
