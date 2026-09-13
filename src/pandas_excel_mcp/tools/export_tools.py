"""Export MCP tools: export_excel, export_csv, export_json.

Exports are returned as base64-encoded bytes plus a suggested filename so
the MCP client can save them without the server needing arbitrary
filesystem write access on behalf of the caller.
"""
from __future__ import annotations

import base64
import io
from typing import Any

from ..core.dataset_manager import dataset_manager
from ..schemas.exceptions import AppError, ExportError
from ..utils.serialization import error_response, success_response


def register(mcp) -> None:
    @mcp.tool()
    def export_excel(dataset_id: str, filename: str | None = None) -> dict[str, Any]:
        """Export a dataset to an XLSX file, returned as base64."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            buf = io.BytesIO()
            try:
                df.to_excel(buf, index=False, engine="openpyxl")
            except Exception as exc:  # noqa: BLE001
                raise ExportError(f"Failed to export to XLSX: {exc}") from exc
            encoded = base64.b64encode(buf.getvalue()).decode("ascii")
            name = filename or f"{dataset_id}.xlsx"
            return success_response(
                "export_excel",
                dataset_id=dataset_id,
                data={"filename": name, "content_base64": encoded, "size_bytes": buf.tell()},
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def export_csv(dataset_id: str, filename: str | None = None) -> dict[str, Any]:
        """Export a dataset to a CSV file, returned as base64."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            encoded = base64.b64encode(csv_bytes).decode("ascii")
            name = filename or f"{dataset_id}.csv"
            return success_response(
                "export_csv",
                dataset_id=dataset_id,
                data={"filename": name, "content_base64": encoded, "size_bytes": len(csv_bytes)},
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def export_json(dataset_id: str, filename: str | None = None) -> dict[str, Any]:
        """Export a dataset to a JSON file, returned as base64."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            json_bytes = df.to_json(orient="records").encode("utf-8")
            encoded = base64.b64encode(json_bytes).decode("ascii")
            name = filename or f"{dataset_id}.json"
            return success_response(
                "export_json",
                dataset_id=dataset_id,
                data={"filename": name, "content_base64": encoded, "size_bytes": len(json_bytes)},
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)
