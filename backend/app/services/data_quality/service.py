"""Operational data-quality and ingestion diagnostics service."""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.company import Company
from app.models.company_profile import CompanyProfile, ResearchStatus
from app.models.dividend import CorporateAction, Dividend
from app.models.financial_statement import BalanceSheet, CashFlowStatement, IncomeStatement
from app.models.ingestion import IngestionRecordIssue, IngestionRun
from app.models.market_snapshot import MarketSnapshot
from app.models.news import News
from app.services.data_quality.completeness import score_records
from app.services.data_quality.freshness import score_freshness
from app.services.data_quality.provenance import provenance_label, score_provenance
from app.services.data_quality.scoring import QualityScore, average_scores

ENTITY_MODELS: dict[str, type] = {
    "companies": Company,
    "assets": Asset,
    "company_profiles": CompanyProfile,
    "income_statements": IncomeStatement,
    "balance_sheets": BalanceSheet,
    "cash_flow_statements": CashFlowStatement,
    "dividends": Dividend,
    "corporate_actions": CorporateAction,
    "news": News,
    "market_snapshots": MarketSnapshot,
}


@dataclass(frozen=True)
class Page:
    items: list[dict[str, Any]]
    total: int
    page: int
    limit: int

    def to_dict(self) -> dict[str, Any]:
        return {"items": self.items, "total": self.total, "page": self.page, "limit": self.limit}


def _iso(value: object) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()
    return None


def _duration_ms(run: IngestionRun) -> int | None:
    if not run.finished_at:
        return None
    started = run.started_at if run.started_at.tzinfo else run.started_at.replace(tzinfo=timezone.utc)
    finished = run.finished_at if run.finished_at.tzinfo else run.finished_at.replace(tzinfo=timezone.utc)
    return int((finished - started).total_seconds() * 1000)


def _run_to_dict(run: IngestionRun) -> dict[str, Any]:
    return {
        "id": run.id,
        "entity": run.entity,
        "mode": run.mode,
        "status": run.status,
        "source_name": run.source_name,
        "source_type": run.source_type,
        "source_url": run.source_url,
        "dataset_version": run.dataset_version,
        "checksum": run.checksum,
        "verification_status": run.verification_status,
        "is_development_data": run.is_development_data,
        "triggered_by": run.triggered_by,
        "started_at": _iso(run.started_at),
        "completed_at": _iso(run.finished_at),
        "duration_ms": _duration_ms(run),
        "received_count": run.total_records,
        "normalized_count": run.normalized_records,
        "valid_count": run.valid_records,
        "inserted_count": run.inserted,
        "updated_count": run.updated,
        "skipped_count": run.skipped,
        "rejected_count": run.rejected_records,
        "warning_count": run.warning_count,
        "error_count": run.error_count,
        "error_summary": run.errors,
        "warning_summary": run.warnings,
    }


def _issue_to_dict(issue: IngestionRecordIssue) -> dict[str, Any]:
    return {
        "id": issue.id,
        "ingestion_run_id": issue.ingestion_run_id,
        "entity_type": issue.entity_type,
        "record_index": issue.record_index,
        "external_key": issue.external_key,
        "severity": issue.severity,
        "issue_code": issue.issue_code,
        "field_name": issue.field_name,
        "message": issue.message,
        "raw_value_summary": issue.raw_value_summary,
        "created_at": _iso(issue.created_at),
    }


def list_runs(db: Session, page: int = 1, limit: int = 25) -> Page:
    """Return paginated ingestion runs."""
    page = max(1, page)
    limit = min(max(1, limit), 100)
    total = db.scalar(select(func.count()).select_from(IngestionRun)) or 0
    runs = db.scalars(select(IngestionRun).order_by(IngestionRun.started_at.desc()).offset((page - 1) * limit).limit(limit)).all()
    return Page([_run_to_dict(run) for run in runs], total, page, limit)


def get_run_detail(db: Session, run_id: int) -> dict[str, Any] | None:
    """Return one ingestion run plus issue distribution and retry guidance."""
    run = db.get(IngestionRun, run_id)
    if not run:
        return None
    issues = db.scalars(select(IngestionRecordIssue).where(IngestionRecordIssue.ingestion_run_id == run_id)).all()
    distribution: dict[str, int] = defaultdict(int)
    for issue in issues:
        distribution[issue.issue_code] += 1
    guidance = []
    if run.status in {"failed", "rejected"}:
        guidance.append("Review rejected records, correct source data, then retry with dry-run before lenient or strict import.")
    if run.is_development_data:
        guidance.append("Development fixture rows should be replaced with verified source data before production use.")
    if run.warning_count:
        guidance.append("Warnings do not block imports but should be reviewed before promoting data quality.")
    return {"run": _run_to_dict(run), "issue_code_distribution": dict(distribution), "retry_guidance": guidance}


def list_issues(
    db: Session,
    run_id: int | None = None,
    entity_type: str | None = None,
    severity: str | None = None,
    issue_code: str | None = None,
    page: int = 1,
    limit: int = 50,
) -> Page:
    """Return paginated record-level issues."""
    page = max(1, page)
    limit = min(max(1, limit), 200)
    query = select(IngestionRecordIssue)
    count_query = select(func.count()).select_from(IngestionRecordIssue)
    filters = []
    if run_id is not None:
        filters.append(IngestionRecordIssue.ingestion_run_id == run_id)
    if entity_type:
        filters.append(IngestionRecordIssue.entity_type == entity_type)
    if severity:
        filters.append(IngestionRecordIssue.severity == severity)
    if issue_code:
        filters.append(IngestionRecordIssue.issue_code == issue_code)
    for criterion in filters:
        query = query.where(criterion)
        count_query = count_query.where(criterion)
    total = db.scalar(count_query) or 0
    issues = db.scalars(query.order_by(IngestionRecordIssue.created_at.desc()).offset((page - 1) * limit).limit(limit)).all()
    return Page([_issue_to_dict(issue) for issue in issues], total, page, limit)


def export_issues(db: Session, run_id: int | None = None, output_format: str = "json") -> str:
    """Export safe issue summaries as JSON-like text or CSV."""
    rows = list_issues(db, run_id=run_id, limit=200).items
    safe_rows = [
        {
            "run_id": row["ingestion_run_id"],
            "record_index": row["record_index"],
            "entity_type": row["entity_type"],
            "external_key": row["external_key"],
            "severity": row["severity"],
            "issue_code": row["issue_code"],
            "field_name": row["field_name"],
            "message": row["message"],
        }
        for row in rows
    ]
    if output_format == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(safe_rows[0].keys()) if safe_rows else ["run_id", "record_index", "entity_type", "external_key", "severity", "issue_code", "field_name", "message"])
        writer.writeheader()
        writer.writerows(safe_rows)
        return buffer.getvalue()
    import json

    return json.dumps(safe_rows, indent=2)


def _records_for_entity(db: Session, entity_type: str, limit: int = 200) -> list[object]:
    model = ENTITY_MODELS[entity_type]
    return list(db.scalars(select(model).limit(limit)).all())


def _latest_update(records: list[object]) -> object | None:
    values = [getattr(record, "verified_at", None) or getattr(record, "last_verified", None) or getattr(record, "imported_at", None) or getattr(record, "published_at", None) or getattr(record, "snapshot_date", None) or getattr(record, "updated_at", None) or getattr(record, "created_at", None) for record in records]
    values = [value for value in values if value is not None]
    return max(values) if values else None


def _development_count(entity_type: str, records: list[object]) -> int:
    if entity_type == "company_profiles":
        return sum(1 for record in records if getattr(record, "research_status", None) == ResearchStatus.DEVELOPMENT)
    return sum(1 for record in records if bool(getattr(record, "is_development_data", False)))


def _verified_count(records: list[object]) -> int:
    return sum(1 for record in records if not bool(getattr(record, "is_development_data", False)) and (getattr(record, "verified_at", None) or getattr(record, "last_verified", None)))


def score_entity(db: Session, entity_type: str) -> dict[str, Any]:
    """Return deterministic data-quality summary for one entity."""
    if entity_type not in ENTITY_MODELS:
        raise KeyError(f"Unsupported entity type: {entity_type}")
    model = ENTITY_MODELS[entity_type]
    total = db.scalar(select(func.count()).select_from(model)) or 0
    records = _records_for_entity(db, entity_type)
    development_count = _development_count(entity_type, records)
    verified_count = _verified_count(records)
    latest_import = db.scalar(select(func.max(IngestionRun.finished_at)).where(IngestionRun.entity == entity_type))
    latest_verified_update = _latest_update([record for record in records if not bool(getattr(record, "is_development_data", False))])
    completeness = score_records(entity_type, records)
    provenance = score_provenance(records)
    freshness = score_freshness(entity_type, latest_verified_update or latest_import, development_only=total > 0 and development_count == total)
    warning_count = db.scalar(select(func.count()).select_from(IngestionRecordIssue).where(IngestionRecordIssue.entity_type == entity_type, IngestionRecordIssue.severity == "Warning")) or 0
    rejection_count = db.scalar(select(func.count()).select_from(IngestionRecordIssue).where(IngestionRecordIssue.entity_type == entity_type, IngestionRecordIssue.severity == "Rejected")) or 0
    validity_value = 100 if total == 0 else max(0, 100 - min(100, (rejection_count / max(total, 1)) * 20))
    validity = QualityScore.from_value(validity_value, [f"{rejection_count} rejected record issue(s) are recorded for {entity_type}."])
    consistency = QualityScore.from_value(70 if warning_count else 90, [f"{warning_count} warning issue(s) are recorded for {entity_type}."])
    overall = average_scores([completeness, validity, provenance, freshness.score, consistency])
    source_count = db.scalar(select(func.count(func.distinct(IngestionRun.source_name))).where(IngestionRun.entity == entity_type)) or 0
    return {
        "entity_type": entity_type,
        "total_records": total,
        "verified_records": verified_count,
        "development_records": development_count,
        "unverified_records": max(0, total - verified_count - development_count),
        "latest_import": _iso(latest_import),
        "latest_verified_update": _iso(latest_verified_update) if isinstance(latest_verified_update, datetime) else str(latest_verified_update) if latest_verified_update else None,
        "quality_score": overall.to_dict(),
        "completeness": completeness.to_dict(),
        "validity": validity.to_dict(),
        "provenance": provenance.to_dict(),
        "freshness": freshness.to_dict(),
        "consistency": consistency.to_dict(),
        "freshness_status": freshness.status,
        "open_warning_count": warning_count,
        "open_rejection_count": rejection_count,
        "source_count": source_count,
    }


def data_quality_summary(db: Session) -> dict[str, Any]:
    """Return entity-level quality summaries and aggregate health."""
    entities = [score_entity(db, entity) for entity in ENTITY_MODELS]
    stale = sum(1 for entity in entities if entity["freshness_status"] in {"Stale", "Unknown"})
    latest_run = db.scalar(select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(1))
    return {
        "pipeline_health": "Degraded" if stale else "Healthy",
        "latest_ingestion_run": _run_to_dict(latest_run) if latest_run else None,
        "verified_record_count": sum(int(entity["verified_records"]) for entity in entities),
        "development_record_count": sum(int(entity["development_records"]) for entity in entities),
        "stale_dataset_count": stale,
        "rejected_record_count": sum(int(entity["open_rejection_count"]) for entity in entities),
        "entities": entities,
    }


def source_health(db: Session) -> list[dict[str, Any]]:
    """Return deterministic source health from ingestion runs."""
    runs = db.scalars(select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(500)).all()
    grouped: dict[tuple[str, str], list[IngestionRun]] = defaultdict(list)
    for run in runs:
        grouped[(run.source_name, run.source_type)].append(run)
    results = []
    for (source_name, source_type), source_runs in grouped.items():
        successful = [run for run in source_runs if run.status == "completed"]
        failed = [run for run in source_runs if run.status in {"failed", "rejected"}]
        success_rate = round((len(successful) / len(source_runs)) * 100, 2) if source_runs else 0
        latest_success = successful[0] if successful else None
        latest_failed = failed[0] if failed else None
        avg_duration = None
        durations = [_duration_ms(run) for run in source_runs if _duration_ms(run) is not None]
        if durations:
            avg_duration = int(sum(durations) / len(durations))
        warnings = sum(run.warning_count for run in source_runs[:20])
        rejected = sum(run.rejected_records for run in source_runs[:20])
        freshness = score_freshness(source_runs[0].entity, latest_success.finished_at if latest_success else None, development_only=source_runs[0].is_development_data)
        if not source_runs:
            health = "Unknown"
        elif latest_failed and (not latest_success or latest_failed.started_at >= latest_success.started_at):
            health = "Failing"
        elif success_rate < 75 or warnings or rejected:
            health = "Degraded"
        elif freshness.status in {"Fresh", "Aging"}:
            health = "Healthy"
        else:
            health = "Inactive"
        results.append(
            {
                "source_name": source_name,
                "source_type": source_type,
                "last_successful_run": _iso(latest_success.finished_at) if latest_success else None,
                "last_failed_run": _iso(latest_failed.finished_at) if latest_failed else None,
                "success_rate": success_rate,
                "recent_rejected_record_count": rejected,
                "recent_warning_count": warnings,
                "average_run_duration_ms": avg_duration,
                "latest_dataset_version": source_runs[0].dataset_version,
                "latest_checksum": source_runs[0].checksum,
                "freshness_status": freshness.status,
                "current_health": health,
            }
        )
    return sorted(results, key=lambda item: item["source_name"])


def company_quality_report(db: Session, ticker: str) -> dict[str, Any] | None:
    """Return company-level data-quality report and deterministic operator actions."""
    company = db.scalar(select(Company).where(Company.ticker == ticker.upper()))
    if not company:
        return None
    assets = list(db.scalars(select(Asset).where(Asset.company_id == company.id)).all())
    profile = db.scalar(select(CompanyProfile).where(CompanyProfile.company_id == company.id))
    income = list(db.scalars(select(IncomeStatement).where(IncomeStatement.company_id == company.id)).all())
    balance = list(db.scalars(select(BalanceSheet).where(BalanceSheet.company_id == company.id)).all())
    cash = list(db.scalars(select(CashFlowStatement).where(CashFlowStatement.company_id == company.id)).all())
    dividends = list(db.scalars(select(Dividend).where(Dividend.company_id == company.id)).all())
    snapshots = list(db.scalars(select(MarketSnapshot).join(Asset).where(Asset.company_id == company.id)).all())
    news_count = len(company.news_articles)
    components = {
        "company_completeness": score_records("companies", [company]).to_dict(),
        "profile_completeness": score_records("company_profiles", [profile] if profile else []).to_dict(),
        "asset_completeness": score_records("assets", assets).to_dict(),
        "income_statement_coverage": score_records("income_statements", income).to_dict(),
        "balance_sheet_coverage": score_records("balance_sheets", balance).to_dict(),
        "cash_flow_coverage": score_records("cash_flow_statements", cash).to_dict(),
        "dividend_coverage": score_records("dividends", dividends).to_dict(),
        "market_snapshot_freshness": score_freshness("market_snapshots", _latest_update(snapshots), development_only=bool(snapshots) and _development_count("market_snapshots", snapshots) == len(snapshots)).to_dict(),
        "provenance": score_provenance([item for item in [company, profile, *assets, *income, *balance, *cash, *dividends, *snapshots] if item is not None]).to_dict(),
    }
    development_presence = any(bool(getattr(item, "is_development_data", False)) for item in [*income, *balance, *cash, *dividends, *snapshots]) or (profile is not None and profile.research_status == ResearchStatus.DEVELOPMENT)
    actions = []
    if not profile:
        actions.append("Import a verified company profile.")
    elif profile.research_status == ResearchStatus.DEVELOPMENT:
        actions.append("Replace development company profile data with verified source material.")
    if not balance:
        actions.append("Financial statements are missing balance sheet periods.")
    if not cash:
        actions.append("Financial statements are missing cash flow periods.")
    if not snapshots:
        actions.append("Import a verified market snapshot for reference-price evidence.")
    if development_presence:
        actions.append("Development records are present; review cleanup eligibility after verified data is imported.")
    if news_count == 0:
        actions.append("Link verified news or announcements to this company when available.")
    if not actions:
        actions.append("No critical data-quality action is currently detected for this company.")
    return {
        "ticker": company.ticker,
        "company_name": company.name,
        "components": components,
        "development_data_present": development_presence,
        "missing_critical_fields": [reason for score in components.values() for reason in score.get("reasons", []) if "Missing" in reason],
        "news_coverage": {"linked_articles": news_count},
        "suggested_operator_actions": actions,
        "provenance_status": provenance_label(getattr(profile, "source_name", None), None, development_presence, getattr(profile, "last_verified", None) if profile else None),
    }
