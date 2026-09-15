"""Dataset registry and metadata tracking for TruthLens."""

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class DatasetMetadata:
    dataset_name: str
    version: str
    source: str
    license: str
    download_date: str
    record_count: int
    label_mapping: Dict[str, int]
    language: str
    preprocessing_version: str
    checksum: str
    description: str

    def to_dict(self) -> Dict[str, any]:
        return asdict(self)


class DatasetRegistry:
    """Manages registered datasets and their audit metadata."""

    def __init__(self, registry_file: Optional[Path] = None):
        self.registry_file = registry_file or Path("data/dataset_registry.json")
        self._entries: Dict[str, DatasetMetadata] = {}
        self.load()

    def register(self, meta: DatasetMetadata) -> None:
        key = f"{meta.dataset_name}:{meta.version}"
        self._entries[key] = meta
        self.save()

    def get(self, dataset_name: str, version: str) -> Optional[DatasetMetadata]:
        return self._entries.get(f"{dataset_name}:{version}")

    def list_all(self) -> List[Dict[str, any]]:
        return [meta.to_dict() for meta in self._entries.values()]

    def save(self) -> None:
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        data = {k: v.to_dict() for k, v in self._entries.items()}
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self._entries[k] = DatasetMetadata(**v)
            except Exception:
                self._entries = {}

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        """Calculate SHA256 checksum of a dataset file."""
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha.update(chunk)
        return sha.hexdigest()
