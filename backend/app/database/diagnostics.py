"""Database health and migration diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings

BACKEND_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DatabaseDiagnostics:
    """Summary of local database readiness."""

    database: str
    migrations: str
    current_revision: str | None = None
    head_revision: str | None = None
    asset_count: int | None = None
    seed_data_present: bool | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Return whether all critical diagnostics passed."""
        seed_ok = self.seed_data_present is not False
        return self.database == "connected" and self.migrations == "current" and seed_ok


def create_diagnostic_engine(database_url: str | None = None, timeout_seconds: int = 2) -> Engine:
    """Create a short-lived engine for diagnostics."""
    url = database_url or get_settings().database_url
    connect_args = {}
    if url.startswith("postgresql"):
        connect_args["connect_timeout"] = timeout_seconds
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


def get_alembic_config() -> Config:
    """Return Alembic config with paths resolved for script execution from any cwd."""
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.set_main_option("sqlalchemy.url", get_settings().database_url)
    return config


def get_head_revision(config: Config | None = None) -> str | None:
    """Return the latest Alembic revision known to the repository."""
    script = ScriptDirectory.from_config(config or get_alembic_config())
    return script.get_current_head()


def get_current_revision(engine: Engine) -> str | None:
    """Return the database's current Alembic revision."""
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        return context.get_current_revision()


def get_asset_count(engine: Engine) -> int:
    """Return the number of seeded investment assets."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM assets"))
        return int(result.scalar_one())


def run_database_diagnostics(
    *,
    include_seed_check: bool = False,
    engine: Engine | None = None,
) -> DatabaseDiagnostics:
    """Check database connectivity, migration status, and optionally seed data."""
    errors: list[str] = []
    diagnostic_engine = engine or create_diagnostic_engine()

    try:
        with diagnostic_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        return DatabaseDiagnostics(
            database="unavailable",
            migrations="unavailable",
            errors=[str(exc)],
        )

    current_revision: str | None = None
    head_revision: str | None = None
    migrations = "unavailable"
    try:
        current_revision = get_current_revision(diagnostic_engine)
        head_revision = get_head_revision()
        migrations = "current" if current_revision == head_revision else "not_current"
    except Exception as exc:  # Alembic can raise non-SQLAlchemy config errors.
        errors.append(str(exc))

    asset_count: int | None = None
    seed_data_present: bool | None = None
    if include_seed_check:
        try:
            asset_count = get_asset_count(diagnostic_engine)
            seed_data_present = asset_count > 0
        except SQLAlchemyError as exc:
            seed_data_present = False
            errors.append(str(exc))

    return DatabaseDiagnostics(
        database="connected",
        migrations=migrations,
        current_revision=current_revision,
        head_revision=head_revision,
        asset_count=asset_count,
        seed_data_present=seed_data_present,
        errors=errors,
    )
