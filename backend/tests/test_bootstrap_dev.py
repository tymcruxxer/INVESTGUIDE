"""Development bootstrap script tests."""

import subprocess

import pytest

from app.database.diagnostics import DatabaseDiagnostics
from scripts import bootstrap_dev


def test_bootstrap_development_database_runs_migrations_and_seed(monkeypatch) -> None:
    """Bootstrap waits for DB, migrates, seeds, and returns summary."""
    calls: list[str] = []

    monkeypatch.setattr(bootstrap_dev, "wait_for_database", lambda: True)
    monkeypatch.setattr(bootstrap_dev, "apply_migrations", lambda: calls.append("migrate"))
    monkeypatch.setattr(bootstrap_dev, "seed_database", lambda: calls.append("seed"))
    monkeypatch.setattr(
        bootstrap_dev,
        "run_database_diagnostics",
        lambda include_seed_check: DatabaseDiagnostics(
            database="connected",
            migrations="current",
            asset_count=9,
            seed_data_present=True,
        ),
    )

    summary = bootstrap_dev.bootstrap_development_database()

    assert calls == ["migrate", "seed"]
    assert summary.database_connected is True
    assert summary.migrations_applied is True
    assert summary.seed_completed is True
    assert summary.asset_count == 9


def test_bootstrap_development_database_fails_when_database_unreachable(monkeypatch) -> None:
    """Bootstrap fails clearly if PostgreSQL never becomes reachable."""
    monkeypatch.setattr(bootstrap_dev, "wait_for_database", lambda: False)

    with pytest.raises(RuntimeError, match="PostgreSQL is not reachable"):
        bootstrap_dev.bootstrap_development_database()


def test_run_backend_command_uses_backend_working_directory(monkeypatch) -> None:
    """Backend commands execute from the backend directory."""
    captured: dict[str, object] = {}

    def fake_run(args, cwd, check):
        captured["args"] = args
        captured["cwd"] = cwd
        captured["check"] = check

    monkeypatch.setattr(subprocess, "run", fake_run)

    bootstrap_dev.run_backend_command(["-m", "alembic", "current"])

    assert captured["args"][1:] == ["-m", "alembic", "current"]
    assert captured["cwd"] == bootstrap_dev.BACKEND_DIR
    assert captured["check"] is True
