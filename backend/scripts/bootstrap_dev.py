"""Prepare a local InvestGuide backend development database."""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / '.env')

from app.database.diagnostics import create_diagnostic_engine, run_database_diagnostics  # noqa: E402


@dataclass(frozen=True)
class BootstrapSummary:
    """Summary of local development bootstrap work."""

    database_connected: bool
    migrations_applied: bool
    seed_completed: bool
    asset_count: int | None


def wait_for_database(timeout_seconds: int = 60, interval_seconds: float = 2.0) -> bool:
    """Wait until the configured PostgreSQL database accepts connections."""
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            engine = create_diagnostic_engine(timeout_seconds=2)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as exc:
            last_error = exc
            time.sleep(interval_seconds)

    if last_error is not None:
        print(f"Database connection failed: {last_error}")
    return False


def run_backend_command(args: Sequence[str]) -> None:
    """Run a backend command from the backend directory."""
    subprocess.run([sys.executable, *args], cwd=BACKEND_DIR, check=True)


def apply_migrations() -> None:
    """Apply Alembic migrations to the configured database."""
    run_backend_command(["-m", "alembic", "upgrade", "head"])


def seed_database() -> None:
    """Seed development assets into the configured database."""
    run_backend_command(["-m", "app.database.seed"])


def bootstrap_development_database() -> BootstrapSummary:
    """Wait for PostgreSQL, migrate, seed, and return a readiness summary."""
    print("Waiting for PostgreSQL...")
    if not wait_for_database():
        raise RuntimeError("PostgreSQL is not reachable. Run `docker compose up -d` and retry.")

    print("Applying Alembic migrations...")
    apply_migrations()

    print("Seeding development assets...")
    seed_database()

    diagnostics = run_database_diagnostics(include_seed_check=True)
    return BootstrapSummary(
        database_connected=diagnostics.database == "connected",
        migrations_applied=diagnostics.migrations == "current",
        seed_completed=diagnostics.seed_data_present is True,
        asset_count=diagnostics.asset_count,
    )


def main() -> int:
    """Run the local development bootstrap command."""
    try:
        summary = bootstrap_development_database()
    except (RuntimeError, subprocess.CalledProcessError, SQLAlchemyError) as exc:
        print(f"Bootstrap failed: {exc}")
        return 1

    print("Bootstrap complete")
    print(f"Database connected: {summary.database_connected}")
    print(f"Migrations current: {summary.migrations_applied}")
    print(f"Seed data present: {summary.seed_completed}")
    print(f"Asset count: {summary.asset_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
