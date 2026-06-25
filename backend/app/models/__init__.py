"""SQLAlchemy model registry.

Import future model modules here so Alembic can discover them through
``Base.metadata`` during autogeneration.
"""

from app.models.mixins import TimestampMixin

__all__ = ["TimestampMixin"]
