"""Read-only company endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.responses import error_response, success_response
from app.database.session import get_db
from app.models.asset import Exchange
from app.schemas.asset import AssetRead
from app.schemas.company import CompanyDetailRead, CompanyRead
from app.schemas.company_profile import CompanyProfileDetailRead, CompanyProfileRead, CompanyProfileVerificationRead
from app.schemas.news import NewsRead
from app.services import company_enrichment, company_service
from app.services.intelligence.assessment_service import build_asset_assessment
from app.services.intelligence.business_engine import build_business_intelligence
from app.services.intelligence.research_service import build_company_research
from app.services.intelligence.related_engine import build_related_research

router = APIRouter(prefix="/companies", tags=["companies"])


def _serialize_company(company: Any) -> dict[str, Any]:
    """Serialize company ORM objects into API-safe dictionaries."""
    return CompanyRead.model_validate(company).model_dump(mode="json")


def _serialize_asset(asset: Any) -> dict[str, Any]:
    """Serialize related assets into API-safe dictionaries."""
    return AssetRead.model_validate(asset).model_dump(mode="json")


def _serialize_news(article: Any) -> dict[str, Any]:
    """Serialize related news into API-safe dictionaries."""
    payload = {
        "id": article.id,
        "title": article.title,
        "summary": article.summary,
        "content": article.content,
        "content_hash": article.content_hash,
        "source": article.source,
        "author": article.author,
        "published_at": article.published_at,
        "url": article.url,
        "image_url": article.image_url,
        "language": article.language,
        "sentiment": article.sentiment,
        "relevance_score": article.relevance_score,
        "credibility_score": article.credibility_score,
        "asset_tickers": [asset.ticker for asset in article.assets],
        "created_at": article.created_at,
        "updated_at": article.updated_at,
    }
    return NewsRead.model_validate(payload).model_dump(mode="json")


@router.get("")
async def list_companies(
    exchange: Exchange | None = Query(default=None),
    sector: str | None = Query(default=None, min_length=1, max_length=100),
    industry: str | None = Query(default=None, min_length=1, max_length=100),
    search: str | None = Query(default=None, min_length=1, max_length=100),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """List companies with optional filters and pagination."""
    companies, total = company_service.list_companies(
        db,
        exchange=exchange,
        sector=sector,
        industry=industry,
        search=search,
        page=page,
        limit=limit,
    )

    return success_response(
        message="Companies retrieved successfully",
        data=[_serialize_company(company) for company in companies],
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "has_next": page * limit < total,
            "exchange": exchange.value if exchange else None,
            "sector": sector,
            "industry": industry,
        },
    )


@router.get("/{ticker}", response_model=None)
async def get_company(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return company intelligence details for a ticker symbol."""
    company = company_service.get_company_by_ticker(db, ticker)
    if company is None:
        normalized_ticker = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Company '{normalized_ticker}' was not found",
                error_code="COMPANY_NOT_FOUND",
            ),
        )

    latest_news = company_service.get_company_news(db, company, limit=4)
    detail = CompanyDetailRead.model_validate(
        {
            "company": company,
            "related_assets": company.assets,
            "latest_news": [NewsRead.model_validate(_serialize_news(article)) for article in latest_news],
            "assessment_available": bool(company.assets),
        }
    )

    return success_response(
        message="Company retrieved successfully",
        data=detail.model_dump(mode="json"),
    )


@router.get("/{ticker}/profile", response_model=None)
async def get_company_profile(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return structured company enrichment profile and source transparency."""
    company = company_service.get_company_by_ticker(db, ticker)
    if company is None:
        normalized_ticker = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Company '{normalized_ticker}' was not found",
                error_code="COMPANY_NOT_FOUND",
            ),
        )

    profile = company_enrichment.get_or_build_company_profile(db, company)
    verification = CompanyProfileVerificationRead.model_validate(
        company_enrichment.build_verification_payload(profile)
    )
    detail = CompanyProfileDetailRead.model_validate(
        {
            "company": company,
            "profile": CompanyProfileRead.model_validate(profile),
            "verification": verification,
        }
    )

    return success_response(
        message="Company profile retrieved successfully",
        data=detail.model_dump(mode="json"),
    )


@router.get("/{ticker}/business", response_model=None)
async def get_company_business(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return deterministic Business Intelligence for a company."""
    company = company_service.get_company_by_ticker(db, ticker)
    if company is None:
        normalized_ticker = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Company '{normalized_ticker}' was not found",
                error_code="COMPANY_NOT_FOUND",
            ),
        )

    profile = company_enrichment.get_or_build_company_profile(db, company)
    companies, _total = company_service.list_companies(db, limit=100)
    return success_response(
        message="Company business intelligence retrieved successfully",
        data=build_business_intelligence(company, companies=companies, profile=profile),
    )

@router.get("/{ticker}/research", response_model=None)
async def get_company_research(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return deterministic AI Research for a company."""
    company = company_service.get_company_by_ticker(db, ticker)
    if company is None:
        normalized_ticker = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Company '{normalized_ticker}' was not found",
                error_code="COMPANY_NOT_FOUND",
            ),
        )

    profile = company_enrichment.get_or_build_company_profile(db, company)
    primary_asset = company.assets[0] if company.assets else None
    research_payload = build_company_research(company, primary_asset=primary_asset, profile=profile)
    return success_response(
        message="Company research retrieved successfully",
        data=research_payload,
    )



@router.get("/{ticker}/related", response_model=None)
async def get_company_related(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return deterministic related companies and Learn Next relationships."""
    company = company_service.get_company_by_ticker(db, ticker)
    if company is None:
        normalized_ticker = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Company '{normalized_ticker}' was not found",
                error_code="COMPANY_NOT_FOUND",
            ),
        )

    companies, _total = company_service.list_companies(db, limit=100)
    related_payload = build_related_research(company, companies)
    return success_response(
        message="Company relationships retrieved successfully",
        data=related_payload,
    )

@router.get("/{ticker}/assessment", response_model=None)
async def get_company_assessment(
    ticker: str,
    db: Session = Depends(get_db),
):
    """Return deterministic assessment for a company's primary related asset."""
    company = company_service.get_company_by_ticker(db, ticker)
    if company is None:
        normalized_ticker = ticker.strip().upper()
        return JSONResponse(
            status_code=404,
            content=error_response(
                message=f"Company '{normalized_ticker}' was not found",
                error_code="COMPANY_NOT_FOUND",
            ),
        )

    assessment_subject = company.assets[0] if company.assets else company
    assessment_payload = build_asset_assessment(assessment_subject)
    return success_response(
        message="Company assessment retrieved successfully",
        data=assessment_payload,
    )


