"""Dataset tools: upload_dataset, list_datasets, dataset_info, preview_data,
column_profile, list_sheets.
"""
from __future__ import annotations

from typing import Any

from ..core.dataset_manager import dataset_manager
from ..core.file_manager import FileManager
from ..core.validators import clamp_output_rows, require_columns
from ..schemas.exceptions import AppError
from ..utils.serialization import dataframe_to_records, error_response, success_response
from ..utils.security import sanitize_filename

_file_manager = FileManager()


def register(mcp) -> None:
    @mcp.tool()
    def upload_dataset(filename: str, data_base64: str, sheet_name: str | None = None) -> dict[str, Any]:
        """Upload a dataset (CSV, XLSX, XLSM, JSON, or Parquet) given as base64.

        Args:
            filename: Original filename, used only to infer type (e.g. 'sales.csv').
            data_base64: Base64-encoded file bytes.
            sheet_name: Optional sheet name for Excel uploads (defaults to first sheet).
        """
        try:
            safe_name = sanitize_filename(filename)
            raw = _file_manager.decode_payload(data_base64)
            df, sheets = _file_manager.load_dataframe(safe_name, raw, sheet_name=sheet_name)
            ext = safe_name.rsplit(".", 1)[-1].lower()
            wb_bytes = raw if ext in ("xlsx", "xlsm") else None
            record = dataset_manager.register(safe_name, ext, df, sheet_names=sheets, workbook_bytes=wb_bytes)
            return success_response(
                "upload_dataset",
                dataset_id=record.dataset_id,
                data={
                    "filename": record.filename,
                    "shape": {"rows": record.shape[0], "columns": record.shape[1]},
                    "columns": record.columns,
                    "dtypes": record.dtypes,
                    "sheets": sheets,
                },
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def list_datasets() -> dict[str, Any]:
        """List every dataset currently loaded on the server."""
        try:
            records = dataset_manager.list_all()
            data = [
                {
                    "dataset_id": r.dataset_id,
                    "filename": r.filename,
                    "type": r.file_type,
                    "shape": {"rows": r.shape[0], "columns": r.shape[1]},
                }
                for r in records
            ]
            return success_response("list_datasets", data=data, rows=len(data))
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def dataset_info(dataset_id: str) -> dict[str, Any]:
        """Get metadata (shape, columns, dtypes, memory usage) for a dataset."""
        try:
            record = dataset_manager.get(dataset_id)
            df = record.dataframe
            return success_response(
                "dataset_info",
                dataset_id=dataset_id,
                data={
                    "rows": int(df.shape[0]),
                    "columns": int(df.shape[1]),
                    "column_names": record.columns,
                    "dtypes": record.dtypes,
                    "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
                },
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def preview_data(dataset_id: str, rows: int = 10, columns: list[str] | None = None) -> dict[str, Any]:
        """Preview the first N rows of a dataset, optionally a column subset."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            if columns:
                require_columns(df, columns)
                df = df[columns]
            n = clamp_output_rows(rows)
            preview = df.head(n)
            return success_response(
                "preview_data",
                dataset_id=dataset_id,
                data=dataframe_to_records(preview),
                rows=len(preview),
                columns=[str(c) for c in preview.columns],
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def column_profile(dataset_id: str, column: str) -> dict[str, Any]:
        """Profile a single column: dtype, null/unique counts, min/max/mean/median, samples."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            require_columns(df, [column])
            series = df[column]
            profile: dict[str, Any] = {
                "dtype": str(series.dtype),
                "null_count": int(series.isna().sum()),
                "unique_count": int(series.nunique(dropna=True)),
                "sample_values": series.dropna().head(5).tolist(),
            }
            if pd_series_is_numeric(series):
                profile.update(
                    {
                        "min": float(series.min()) if series.notna().any() else None,
                        "max": float(series.max()) if series.notna().any() else None,
                        "mean": float(series.mean()) if series.notna().any() else None,
                        "median": float(series.median()) if series.notna().any() else None,
                    }
                )
            return success_response("column_profile", dataset_id=dataset_id, data=profile)
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def list_sheets(dataset_id: str) -> dict[str, Any]:
        """List sheet names for a dataset that originated from an Excel workbook."""
        try:
            record = dataset_manager.get(dataset_id)
            return success_response(
                "list_sheets",
                dataset_id=dataset_id,
                data={"sheets": record.sheet_names or []},
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)


def pd_series_is_numeric(series) -> bool:
    import pandas as pd

    return pd.api.types.is_numeric_dtype(series)
