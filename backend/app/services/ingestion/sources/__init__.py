"""Local source adapters for ingestion."""

from app.services.ingestion.sources.csv_source import CsvSourceAdapter
from app.services.ingestion.sources.json_source import JsonSourceAdapter

__all__ = ["CsvSourceAdapter", "JsonSourceAdapter"]
