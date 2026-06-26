"""Check local InvestGuide database readiness."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / '.env')

from app.database.diagnostics import DatabaseDiagnostics, run_database_diagnostics  # noqa: E402


def format_diagnostics(diagnostics: DatabaseDiagnostics) -> str:
    """Format diagnostics for operator-readable CLI output."""
    lines = [
        "InvestGuide database diagnostics",
        f"Database: {diagnostics.database}",
        f"Migrations: {diagnostics.migrations}",
        f"Current revision: {diagnostics.current_revision or 'unknown'}",
        f"Head revision: {diagnostics.head_revision or 'unknown'}",
        f"Seed data present: {diagnostics.seed_data_present}",
        f"Asset count: {diagnostics.asset_count if diagnostics.asset_count is not None else 'unknown'}",
    ]
    if diagnostics.errors:
        lines.append("Errors:")
        lines.extend(f"- {error}" for error in diagnostics.errors)
    return "\n".join(lines)


def check_database() -> DatabaseDiagnostics:
    """Run all local database readiness checks."""
    return run_database_diagnostics(include_seed_check=True)


def main() -> int:
    """Run database diagnostics and return a process exit code."""
    diagnostics = check_database()
    print(format_diagnostics(diagnostics))
    return 0 if diagnostics.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
