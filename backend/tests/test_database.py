"""Database foundation tests."""

from sqlalchemy import Integer, inspect
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import get_settings
from app.database.base import NAMING_CONVENTION, Base
from app.database.session import engine
from app.models.mixins import TimestampMixin


class ConventionModel(TimestampMixin, Base):
    """Local model used only to verify base conventions."""

    __tablename__ = "test_model_conventions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


def test_base_metadata_uses_naming_convention() -> None:
    """Base metadata has deterministic constraint names for Alembic."""
    assert Base.metadata.naming_convention == NAMING_CONVENTION
    assert NAMING_CONVENTION["pk"] == "pk_%(table_name)s"
    assert NAMING_CONVENTION["fk"] == (
        "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
    )


def test_engine_uses_configured_database_url() -> None:
    """SQLAlchemy engine is built from application settings."""
    settings = get_settings()
    assert engine.url.render_as_string(hide_password=False) == settings.database_url


def test_timestamp_mixin_adds_expected_columns() -> None:
    """Timestamp mixin contributes created_at and updated_at columns."""
    columns = inspect(ConventionModel).columns

    assert "created_at" in columns
    assert "updated_at" in columns
    assert columns.created_at.nullable is False
    assert columns.updated_at.nullable is False

