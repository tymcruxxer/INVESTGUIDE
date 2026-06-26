"""Database diagnostics tests."""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.database.diagnostics import (
    DatabaseDiagnostics,
    get_head_revision,
    run_database_diagnostics,
)


def make_sqlite_diagnostic_engine(asset_count: int = 1):
    """Create an in-memory database shaped like a migrated backend database."""
    engine = create_engine("sqlite:///:memory:")
    head_revision = get_head_revision()
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)"))
        connection.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:revision)"),
            {"revision": head_revision},
        )
        connection.execute(text("CREATE TABLE assets (id INTEGER PRIMARY KEY)"))
        for index in range(asset_count):
            connection.execute(text("INSERT INTO assets (id) VALUES (:id)"), {"id": index + 1})
    return engine


def test_run_database_diagnostics_reports_current_seeded_database() -> None:
    """Diagnostics report connected/current/seeded when all checks pass."""
    diagnostics = run_database_diagnostics(
        include_seed_check=True,
        engine=make_sqlite_diagnostic_engine(asset_count=2),
    )

    assert diagnostics.database == "connected"
    assert diagnostics.migrations == "current"
    assert diagnostics.asset_count == 2
    assert diagnostics.seed_data_present is True
    assert diagnostics.ok is True


def test_run_database_diagnostics_reports_missing_seed_data() -> None:
    """Empty assets table is a failed seed-data check."""
    diagnostics = run_database_diagnostics(
        include_seed_check=True,
        engine=make_sqlite_diagnostic_engine(asset_count=0),
    )

    assert diagnostics.database == "connected"
    assert diagnostics.migrations == "current"
    assert diagnostics.asset_count == 0
    assert diagnostics.seed_data_present is False
    assert diagnostics.ok is False


def test_run_database_diagnostics_handles_unavailable_database() -> None:
    """Unavailable database is reported without raising."""

    class BrokenEngine:
        def connect(self):
            raise SQLAlchemyError("database unavailable")

    diagnostics = run_database_diagnostics(engine=BrokenEngine())  # type: ignore[arg-type]

    assert diagnostics == DatabaseDiagnostics(
        database="unavailable",
        migrations="unavailable",
        errors=["database unavailable"],
    )
