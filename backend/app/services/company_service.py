"""Read-only company service functions."""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.asset import Asset, Exchange
from app.models.company import Company
from app.models.news import News


def list_companies(
    db: Session,
    *,
    exchange: Exchange | None = None,
    sector: str | None = None,
    industry: str | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[Company], int]:
    """Return paginated companies matching optional filters."""
    filters = []

    if exchange is not None:
        filters.append(Company.exchange == exchange)
    if sector:
        filters.append(func.lower(Company.sector) == sector.strip().lower())
    if industry:
        filters.append(func.lower(Company.industry) == industry.strip().lower())
    if search:
        normalized_search = f"%{search.strip()}%"
        filters.append(
            or_(
                Company.ticker.ilike(normalized_search),
                Company.name.ilike(normalized_search),
                Company.legal_name.ilike(normalized_search),
                Company.sector.ilike(normalized_search),
                Company.industry.ilike(normalized_search),
                Company.description.ilike(normalized_search),
            )
        )

    offset = (page - 1) * limit
    total_query = select(func.count()).select_from(Company).where(*filters)
    companies_query = (
        select(Company)
        .where(*filters)
        .order_by(Company.name.asc())
        .offset(offset)
        .limit(limit)
    )

    total = db.scalar(total_query) or 0
    companies = list(db.scalars(companies_query).all())
    return companies, total


def get_company_by_ticker(db: Session, ticker: str) -> Company | None:
    """Return one company by ticker, case-insensitively."""
    normalized_ticker = ticker.strip().upper()
    query = (
        select(Company)
        .options(selectinload(Company.assets), selectinload(Company.news_articles))
        .where(func.upper(Company.ticker) == normalized_ticker)
    )
    return db.scalar(query)


def get_company_news(db: Session, company: Company, limit: int = 4) -> list[News]:
    """Return latest company news directly linked or derived through related assets."""
    direct_news = sorted(
        company.news_articles,
        key=lambda article: (article.published_at, article.id),
        reverse=True,
    )
    if direct_news:
        return direct_news[:limit]

    asset_ids = [asset.id for asset in company.assets if asset.id is not None]
    if not asset_ids:
        return []

    query = (
        select(News)
        .join(News.assets)
        .where(Asset.id.in_(asset_ids))
        .order_by(News.published_at.desc(), News.id.desc())
        .limit(limit)
    )
    return list(db.scalars(query).unique().all())