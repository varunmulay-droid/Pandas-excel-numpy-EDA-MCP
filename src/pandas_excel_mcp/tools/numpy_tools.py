"""NumPy MCP tools: numpy_statistics, correlation_analysis, outlier_analysis."""
from __future__ import annotations

from typing import Any

from ..core.dataset_manager import dataset_manager
from ..engines import numpy_engine
from ..schemas.exceptions import AppError
from ..utils.serialization import error_response, success_response


def register(mcp) -> None:
    @mcp.tool()
    def numpy_statistics(dataset_id: str, column: str, stat: str, q: float | None = None) -> dict[str, Any]:
        """Compute a NumPy statistic for a numeric column.

        stat in mean/median/std/var/min/max/sum/percentile/quantile/ptp.
        q is the percentile (0-100) or quantile (0-1) when relevant.
        """
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = numpy_engine.numpy_statistics(df, column, stat, q)
            return success_response("numpy_statistics", dataset_id=dataset_id, data=result)
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def correlation_analysis(
        dataset_id: str, columns: list[str] | None = None, method: str = "pearson"
    ) -> dict[str, Any]:
        """Compute a correlation and covariance matrix over numeric columns."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = numpy_engine.correlation_analysis(df, columns, method)
            return success_response("correlation_analysis", dataset_id=dataset_id, data=result)
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)

    @mcp.tool()
    def outlier_analysis(
        dataset_id: str, column: str, method: str = "iqr", threshold: float = 1.5
    ) -> dict[str, Any]:
        """Detect outliers in a numeric column using IQR or Z-score."""
        try:
            df = dataset_manager.get_dataframe(dataset_id)
            result = numpy_engine.outlier_analysis(df, column, method, threshold)
            return success_response("outlier_analysis", dataset_id=dataset_id, data=result)
        except AppError as exc:
            return error_response(exc)
        except Exception as exc:  # noqa: BLE001
            return error_response(exc)
