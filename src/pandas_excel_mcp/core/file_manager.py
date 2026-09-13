"""Handles reading uploaded file bytes into DataFrames, and writing exports.

No arbitrary filesystem path is ever accepted from a tool caller — every
path used here is derived from a sanitised filename joined under the
configured storage root.
"""
from __future__ import annotations

import base64
import io
import os

import pandas as pd

from ..config.settings import settings
from ..schemas.exceptions import UnsupportedFileTypeError, FileTooLargeError, ValidationError
from ..utils.security import safe_join, sanitize_filename


class FileManager:
    def __init__(self) -> None:
        os.makedirs(settings.upload_dir, exist_ok=True)
        os.makedirs(settings.output_dir, exist_ok=True)

    # ---- validation --------------------------------------------------
    @staticmethod
    def validate_extension(filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext not in settings.supported_extensions:
            raise UnsupportedFileTypeError(
                f"Unsupported file type '{ext}'.",
                {"supported": list(settings.supported_extensions)},
            )
        return ext

    @staticmethod
    def validate_size(num_bytes: int) -> None:
        if num_bytes > settings.max_file_size_bytes:
            raise FileTooLargeError(
                f"File is {num_bytes} bytes, exceeding the limit of "
                f"{settings.max_file_size_bytes} bytes ({settings.max_file_size_mb} MB).",
                {"size_bytes": num_bytes, "limit_bytes": settings.max_file_size_bytes},
            )

    # ---- decoding -------------------------------------------------------
    @staticmethod
    def decode_payload(data_base64: str) -> bytes:
        try:
            return base64.b64decode(data_base64, validate=True)
        except Exception as exc:  # noqa: BLE001
            raise ValidationError("Uploaded data is not valid base64.") from exc

    # ---- loading into DataFrame(s) --------------------------------------
    def load_dataframe(
        self, filename: str, raw_bytes: bytes, sheet_name: str | int | None = 0
    ) -> tuple[pd.DataFrame, list[str] | None]:
        """Return (dataframe, sheet_names_or_None)."""
        ext = self.validate_extension(filename)
        self.validate_size(len(raw_bytes))
        buf = io.BytesIO(raw_bytes)

        if ext == ".csv":
            return pd.read_csv(buf), None
        if ext == ".json":
            return pd.read_json(buf), None
        if ext == ".parquet":
            return pd.read_parquet(buf), None
        if ext in (".xlsx", ".xlsm"):
            xls = pd.ExcelFile(buf, engine="openpyxl")
            if len(xls.sheet_names) > settings.max_excel_sheets:
                raise ValidationError(
                    f"Workbook has {len(xls.sheet_names)} sheets, exceeding the limit of "
                    f"{settings.max_excel_sheets}.",
                    {"sheets": len(xls.sheet_names)},
                )
            df = xls.parse(sheet_name if sheet_name is not None else xls.sheet_names[0])
            return df, xls.sheet_names
        raise UnsupportedFileTypeError(f"Unsupported file type '{ext}'.")

    def persist_upload(self, filename: str, raw_bytes: bytes) -> str:
        safe_name = sanitize_filename(filename)
        path = safe_join(settings.upload_dir, safe_name)
        with open(path, "wb") as fh:
            fh.write(raw_bytes)
        return path

    def output_path(self, filename: str) -> str:
        return safe_join(settings.output_dir, sanitize_filename(filename))
