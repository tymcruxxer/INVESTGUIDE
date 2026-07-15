"""JSON source adapter for local fixture ingestion."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.ingestion.types import LoadedDataset, SourceMetadata, SourceType, VerificationStatus


class JsonSourceAdapter:
    """Load local JSON records without network access."""

    def __init__(
        self,
        source_file: str | Path,
        source_name: str,
        source_type: SourceType = SourceType.JSON_IMPORT,
        dataset_version: str | None = None,
        is_development_data: bool = False,
    ) -> None:
        self.source_file = Path(source_file)
        self.source_name = source_name
        self.source_type = source_type
        self.dataset_version = dataset_version
        self.is_development_data = is_development_data

    def load(self) -> LoadedDataset:
        """Load JSON records from disk."""
        raw_bytes = self.source_file.read_bytes()
        payload = json.loads(raw_bytes.decode("utf-8-sig"))
        if isinstance(payload, dict):
            records = payload.get("records", [])
        else:
            records = payload
        if not isinstance(records, list):
            raise ValueError("JSON source must contain a list or a {'records': [...]} object.")
        metadata = SourceMetadata(
            source_name=self.source_name,
            source_type=self.source_type,
            source_url=str(self.source_file),
            verification_status=VerificationStatus.DEVELOPMENT
            if self.is_development_data or self.source_type == SourceType.DEVELOPMENT_FIXTURE
            else VerificationStatus.UNVERIFIED,
            dataset_version=self.dataset_version,
            checksum=self.source_file_checksum(raw_bytes),
            record_count=len(records),
            is_development_data=self.is_development_data or self.source_type == SourceType.DEVELOPMENT_FIXTURE,
        )
        return LoadedDataset(records=[dict(record) for record in records], metadata=metadata)

    @staticmethod
    def source_file_checksum(raw_bytes: bytes) -> str:
        """Return a deterministic checksum for the source file."""
        import hashlib

        return hashlib.sha256(raw_bytes).hexdigest()
