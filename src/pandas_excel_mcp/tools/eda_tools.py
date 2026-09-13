"""EDA MCP tools: eda_report, data_quality_report."""
from __future__ import annotations

from typing import Any

from ..core.dataset_manager import dataset_manager
from ..engines import eda_engine
from ..schemas.exceptions import AppError
from ..utils.serialization import error_response, success_response


def register(mcp) -> None:
    @mcp.tool()
    def eda_report(dataset_id: str) -> dict[str, Any]:
        """Produce a full automated exploratory data analysis report."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = eda_engine.eda_report(df)
            return success_response("eda_report", dataset_id=dataset_id, data=result)
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def data_quality_report(dataset_id: str) -> dict[str, Any]:
        """Produce a data-quality score plus issues/warnings/recommendations."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = eda_engine.data_quality_report(df)
            return success_response("data_quality_report", dataset_id=dataset_id, data=result)
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)
