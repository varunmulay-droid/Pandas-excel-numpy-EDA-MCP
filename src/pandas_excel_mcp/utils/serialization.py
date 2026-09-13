"""Convert pandas/numpy/datetime values into JSON-safe Python primitives."""
from __future__ import annotations

import math
from datetime import date, datetime, time
from typing import Any

import numpy as np
import pandas as pd

from ..schemas.exceptions import AppError
from ..schemas.responses import ErrorResponse, ErrorPayload, SuccessResponse


def to_json_safe(value: Any) -> Any:
    """Recursively convert a value into something json.dumps can handle."""
    if value is None:
        return None
    if isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        f = float(value)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (np.ndarray,)):
        return [to_json_safe(v) for v in value.tolist()]
    if isinstance(value, (pd.Timestamp, datetime, date, time)):
        return value.isoformat()
    if isinstance(value, pd.Timedelta):
        return str(value)
    if value is pd.NaT:
        return None
    if isinstance(value, (pd.Series,)):
        return [to_json_safe(v) for v in value.tolist()]
    if isinstance(value, pd.DataFrame):
        return dataframe_to_records(value)
    if isinstance(value, dict):
        return {str(k): to_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(v) for v in value]
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    # Fallback: try native pandas/numpy scalar handling, else stringify.
    if pd.isna(value) if not isinstance(value, (list, dict)) else False:
        return None
    try:
        return str(value)
    except Exception:  # pragma: no cover - defensive
        return None


def dataframe_to_records(df: pd.DataFrame, max_rows: int | None = None) -> list[dict[str, Any]]:
    frame = df if max_rows is None else df.head(max_rows)
    records = frame.to_dict(orient="records")
    return [{str(k): to_json_safe(v) for k, v in row.items()} for row in records]


def success_response(
    operation: str,
    *,
    dataset_id: str | None = None,
    data: Any = None,
    rows: int | None = None,
    columns: list[str] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = SuccessResponse(
        operation=operation,
        dataset_id=dataset_id,
        data=to_json_safe(data),
        rows=rows,
        columns=columns,
        meta=meta or {},
    )
    return payload.to_dict()


def error_response(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, AppError):
        payload = ErrorResponse(
            error=ErrorPayload(type=exc.error_type, message=exc.message, details=exc.details)
        )
    else:
        payload = ErrorResponse(
            error=ErrorPayload(type="InternalError", message=str(exc), details={})
        )
    return payload.to_dict()
