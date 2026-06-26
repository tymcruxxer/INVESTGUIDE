"""Database diagnostics script tests."""

from app.database.diagnostics import DatabaseDiagnostics
from scripts import check_database


def test_format_diagnostics_includes_critical_fields() -> None:
    """Operator output includes database, migration, and seed status."""
    output = check_database.format_diagnostics(
        DatabaseDiagnostics(
            database="connected",
            migrations="current",
            current_revision="rev1",
            head_revision="rev1",
            asset_count=9,
            seed_data_present=True,
        )
    )

    assert "Database: connected" in output
    assert "Migrations: current" in output
    assert "Asset count: 9" in output


def test_check_database_main_returns_zero_when_ready(monkeypatch, capsys) -> None:
    """CLI exits successfully when critical diagnostics pass."""
    monkeypatch.setattr(
        check_database,
        "check_database",
        lambda: DatabaseDiagnostics(
            database="connected",
            migrations="current",
            asset_count=1,
            seed_data_present=True,
        ),
    )

    assert check_database.main() == 0
    assert "Database: connected" in capsys.readouterr().out


def test_check_database_main_returns_nonzero_when_not_ready(monkeypatch) -> None:
    """CLI exits non-zero when critical diagnostics fail."""
    monkeypatch.setattr(
        check_database,
        "check_database",
        lambda: DatabaseDiagnostics(
            database="unavailable",
            migrations="unavailable",
            errors=["connection failed"],
        ),
    )

    assert check_database.main() == 1
