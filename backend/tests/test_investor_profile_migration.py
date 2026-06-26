"""Investor profile migration registry tests."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def test_investor_profile_migration_is_registered() -> None:
    """Investor profile migration follows the Alembic revision chain."""
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "20260626_0004_create_investor_profiles_table.py"
    )
    spec = spec_from_file_location("investor_profile_migration", migration_path)
    assert spec is not None
    assert spec.loader is not None

    migration = module_from_spec(spec)
    spec.loader.exec_module(migration)

    assert migration.revision == "20260626_0004"
    assert migration.down_revision == "20260625_0003"
    assert callable(migration.upgrade)
    assert callable(migration.downgrade)
