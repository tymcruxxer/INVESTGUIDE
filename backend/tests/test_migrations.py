"""Alembic migration registry tests."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def test_content_hash_migration_is_registered() -> None:
    """Content hash migration follows the Alembic revision chain."""
    migration_path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "20260625_0003_add_news_content_hash.py"
    )
    spec = spec_from_file_location("content_hash_migration", migration_path)
    assert spec is not None
    assert spec.loader is not None

    migration = module_from_spec(spec)
    spec.loader.exec_module(migration)

    assert migration.revision == "20260625_0003"
    assert migration.down_revision == "20260625_0002"
    assert callable(migration.upgrade)
    assert callable(migration.downgrade)