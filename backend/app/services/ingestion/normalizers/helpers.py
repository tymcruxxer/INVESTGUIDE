"""Normalization helpers for source-agnostic ingestion."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlparse


def clean_string(value: Any) -> str | None:
    """Normalize whitespace and blank strings."""
    if value is None:
        return None
    cleaned = " ".join(str(value).replace("\ufeff", "").split())
    return cleaned or None


def normalize_ticker(value: Any) -> str | None:
    """Normalize ticker symbols."""
    cleaned = clean_string(value)
    return cleaned.upper() if cleaned else None


def normalize_exchange(value: Any) -> str | None:
    """Normalize exchange names."""
    cleaned = clean_string(value)
    return cleaned.upper() if cleaned else None


def normalize_currency(value: Any) -> str | None:
    """Normalize currency codes."""
    cleaned = clean_string(value)
    return cleaned.upper() if cleaned else None


def normalize_name(value: Any) -> str | None:
    """Normalize company names."""
    return clean_string(value)


def normalize_url(value: Any) -> str | None:
    """Return a usable URL or None."""
    cleaned = clean_string(value)
    if not cleaned:
        return None
    parsed = urlparse(cleaned)
    if not parsed.scheme:
        cleaned = f"https://{cleaned}"
        parsed = urlparse(cleaned)
    return cleaned if parsed.netloc else None


def parse_date(value: Any) -> date | None:
    """Parse common date inputs to a date."""
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def parse_datetime(value: Any) -> datetime | None:
    """Parse common datetime inputs to an aware datetime."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    parsed_date = parse_date(value)
    if parsed_date:
        return datetime.combine(parsed_date, datetime.min.time(), tzinfo=timezone.utc)
    return None


def parse_decimal(value: Any) -> Decimal | None:
    """Parse numeric inputs without floating point surprises."""
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return None


def parse_int(value: Any) -> int | None:
    """Parse integer inputs."""
    if value in (None, ""):
        return None
    try:
        return int(str(value).replace(",", "").strip())
    except ValueError:
        return None


def normalize_statement_period(value: Any) -> str:
    """Normalize statement periods."""
    cleaned = (clean_string(value) or "annual").lower()
    return "interim" if cleaned in {"interim", "half-year", "half year", "h1", "h2"} else "annual"


def normalize_dividend_type(value: Any) -> str:
    """Normalize dividend type values to model enum values."""
    cleaned = (clean_string(value) or "Other").lower()
    mapping = {"interim": "Interim", "final": "Final", "special": "Special"}
    return mapping.get(cleaned, "Other")


def normalize_corporate_action_type(value: Any) -> str:
    """Normalize corporate action values."""
    cleaned = (clean_string(value) or "other").lower().replace(" ", "_")
    allowed = {"dividend", "split", "rights_issue", "consolidation"}
    return cleaned if cleaned in allowed else "other"


def parse_string_list(value: Any) -> list[str]:
    """Parse list-ish inputs into clean strings."""
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [item for item in (clean_string(item) for item in value) if item]
    return [item for item in (clean_string(part) for part in str(value).split(";")) if item]


def normalize_asset_type(value: Any) -> str:
    """Normalize asset type values to model enum values."""
    cleaned = (clean_string(value) or "equity").lower().replace(" ", "_")
    mapping = {"reit": "REIT", "real_estate_investment_trust": "REIT"}
    allowed = {"equity", "bond", "money_market", "alternative"}
    return mapping.get(cleaned, cleaned if cleaned in allowed else "equity")


def normalize_status(value: Any) -> str:
    """Normalize lifecycle statuses."""
    cleaned = (clean_string(value) or "active").lower().replace(" ", "_")
    return cleaned if cleaned in {"active", "suspended", "delisted"} else "active"
