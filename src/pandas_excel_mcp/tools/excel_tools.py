"""Excel MCP tools: excel_read_range, excel_write_range, excel_format,
excel_chart, excel_list_sheets.

These operate on the original workbook bytes attached to a dataset that
was uploaded from an .xlsx/.xlsm file (see DatasetManager.workbook_bytes).
Writes persist back onto the in-memory dataset record.
"""
from __future__ import annotations

from typing import Any

from ..core.dataset_manager import dataset_manager
from ..engines import excel_engine
from ..schemas.exceptions import ValidationError, AppError
from ..utils.serialization import error_response, success_response


def _load_wb(dataset_id: str):
    record = dataset_manager.get(dataset_id)
    if not record.workbook_bytes:
        raise ValidationError(
            "This dataset has no associated Excel workbook. "
            "Upload an .xlsx/.xlsm file to use Excel tools.",
        )
    return record, excel_engine.load_workbook_bytes(record.workbook_bytes)


def register(mcp) -> None:
    @mcp.tool()
    def excel_list_sheets(dataset_id: str) -> dict[str, Any]:
        """List sheet names and dimensions for an Excel-backed dataset."""
        try:
            _, wb = _load_wb(dataset_id)
            return success_response("excel_list_sheets", dataset_id=dataset_id, data=excel_engine.list_sheets(wb))
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def excel_read_range(dataset_id: str, sheet: str, cell_range: str) -> dict[str, Any]:
        """Read a cell range, e.g. sheet='Sheet1', cell_range='A1:F20'."""
        try:
            _, wb = _load_wb(dataset_id)
            values = excel_engine.read_range(wb, sheet, cell_range)
            return success_response(
                "excel_read_range", dataset_id=dataset_id, data=values, rows=len(values)
            )
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def excel_write_range(
        dataset_id: str, sheet: str, start_cell: str, values: list[list[Any]]
    ) -> dict[str, Any]:
        """Write a 2D array of values into a sheet starting at start_cell."""
        try:
            record, wb = _load_wb(dataset_id)
            result = excel_engine.write_range(wb, sheet, start_cell, values)
            record.workbook_bytes = excel_engine.workbook_to_bytes(wb)
            return success_response("excel_write_range", dataset_id=dataset_id, data=result)
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def excel_format(
        dataset_id: str,
        sheet: str,
        cell_range: str,
        font: dict[str, Any] | None = None,
        fill_color: str | None = None,
        border: bool = False,
        alignment: str | None = None,
        number_format: str | None = None,
        column_widths: dict[str, float] | None = None,
        row_heights: dict[str, float] | None = None,
        freeze_panes: str | None = None,
    ) -> dict[str, Any]:
        """Apply formatting to a range: font, fill, border, alignment, number format, widths/heights, freeze panes."""
        try:
            record, wb = _load_wb(dataset_id)
            result = excel_engine.excel_format(
                wb,
                sheet,
                cell_range,
                font=font,
                fill_color=fill_color,
                border=border,
                alignment=alignment,
                number_format=number_format,
                column_widths=column_widths,
                row_heights=row_heights,
                freeze_panes=freeze_panes,
            )
            record.workbook_bytes = excel_engine.workbook_to_bytes(wb)
            return success_response("excel_format", dataset_id=dataset_id, data=result)
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def excel_chart(
        dataset_id: str,
        sheet: str,
        chart_type: str,
        data_range: str,
        anchor: str,
        categories_range: str | None = None,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Insert a chart. chart_type in bar/line/pie/scatter/area."""
        try:
            record, wb = _load_wb(dataset_id)
            result = excel_engine.excel_chart(wb, sheet, chart_type, data_range, categories_range, anchor, title)
            record.workbook_bytes = excel_engine.workbook_to_bytes(wb)
            return success_response("excel_chart", dataset_id=dataset_id, data=result)
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)
