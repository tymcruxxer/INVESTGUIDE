"""CSV source adapter for local fixture ingestion."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from app.services.ingestion.types import LoadedDataset, SourceMetadata, SourceType, VerificationStatus


class CsvSourceAdapter:
    """Load local CSV records without network access."""

    def __init__(
        self,
        source_file: str | Path,
        source_name: str,
        source_type: SourceType = SourceType.CSV_IMPORT,
        dataset_version: str | None = None,
        is_development_data: bool = False,
    ) -> None:
        self.source_file = Path(source_file)
        self.source_name = source_name
        self.source_type = source_type
        self.dataset_version = dataset_version
        self.is_development_data = is_development_data

    def load(self) -> LoadedDataset:
        """Load CSV records from disk."""
        raw_bytes = self.source_file.read_bytes()
        text = raw_bytes.decode("utf-8-sig")
        records = list(csv.DictReader(text.splitlines()))
        metadata = SourceMetadata(
            source_name=self.source_name,
            source_type=self.source_type,
            source_url=str(self.source_file),
            verification_status=VerificationStatus.DEVELOPMENT
            if self.is_development_data or self.source_type == SourceType.DEVELOPMENT_FIXTURE
            else VerificationStatus.UNVERIFIED,
            dataset_version=self.dataset_version,
            checksum=hashlib.sha256(raw_bytes).hexdigest(),
            record_count=len(records),
            is_development_data=self.is_development_data or self.source_type == SourceType.DEVELOPMENT_FIXTURE,
        )
        return LoadedDataset(records=[dict(record) for record in records], metadata=metadata)
