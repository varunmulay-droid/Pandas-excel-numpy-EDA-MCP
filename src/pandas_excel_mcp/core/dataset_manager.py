"""Central dataset lifecycle manager.

Datasets live in memory keyed by dataset_id. The LLM/tool caller never
sees or controls a filesystem path — only opaque dataset_id strings.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from ..config.settings import settings
from ..schemas.exceptions import DatasetNotFoundError, DatasetTooLargeError
from ..utils.security import new_id
from .validators import validate_shape


@dataclass
class DatasetRecord:
    dataset_id: str
    filename: str
    file_type: str
    dataframe: pd.DataFrame
    sheet_names: list[str] | None = None
    created_at: float = field(default_factory=time.time)
    # Raw workbook bytes, kept only for datasets that originated from an
    # Excel upload, so excel_* tools can operate on the full workbook
    # (multiple sheets, formatting, charts) rather than just one DataFrame.
    workbook_bytes: bytes | None = None

    @property
    def shape(self) -> tuple[int, int]:
        return self.dataframe.shape

    @property
    def columns(self) -> list[str]:
        return [str(c) for c in self.dataframe.columns]

    @property
    def dtypes(self) -> dict[str, str]:
        return {str(c): str(t) for c, t in self.dataframe.dtypes.items()}


class DatasetManager:
    """Owns every DataFrame currently loaded by the server."""

    def __init__(self) -> None:
        self._datasets: dict[str, DatasetRecord] = {}

    # ---- lifecycle ------------------------------------------------------
    def register(
        self,
        filename: str,
        file_type: str,
        dataframe: pd.DataFrame,
        sheet_names: list[str] | None = None,
        workbook_bytes: bytes | None = None,
    ) -> DatasetRecord:
        rows, cols = dataframe.shape
        try:
            validate_shape(rows, cols)
        except Exception as exc:
            raise DatasetTooLargeError(str(exc)) from exc
        dataset_id = new_id("ds")
        record = DatasetRecord(
            dataset_id=dataset_id,
            filename=filename,
            file_type=file_type,
            dataframe=dataframe,
            sheet_names=sheet_names,
            workbook_bytes=workbook_bytes,
        )
        self._datasets[dataset_id] = record
        return record

    def replace(self, dataset_id: str, dataframe: pd.DataFrame) -> DatasetRecord:
        """Used by cleaning/transform tools that mutate a dataset in place."""
        record = self.get(dataset_id)
        rows, cols = dataframe.shape
        try:
            validate_shape(rows, cols)
        except Exception as exc:
            raise DatasetTooLargeError(str(exc)) from exc
        record.dataframe = dataframe
        return record

    def get(self, dataset_id: str) -> DatasetRecord:
        record = self._datasets.get(dataset_id)
        if record is None:
            raise DatasetNotFoundError(
                f"Dataset '{dataset_id}' was not found.",
                {"available_datasets": list(self._datasets.keys())},
            )
        return record

    def get_dataframe(self, dataset_id: str) -> pd.DataFrame:
        return self.get(dataset_id).dataframe

    def delete(self, dataset_id: str) -> None:
        self.get(dataset_id)
        del self._datasets[dataset_id]

    def list_all(self) -> list[DatasetRecord]:
        return list(self._datasets.values())

    def exists(self, dataset_id: str) -> bool:
        return dataset_id in self._datasets


# Process-wide singleton. V1 is a single-process deterministic data layer;
# swap for a per-session or persistent store in V2 without changing tools.
dataset_manager = DatasetManager()
