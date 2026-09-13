"""Reusable validation helpers shared by tools and engines."""
from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from ..config.settings import settings
from ..schemas.exceptions import ColumnNotFoundError, ValidationError


def require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ColumnNotFoundError(
            f"Column(s) not found: {', '.join(missing)}",
            {"missing": missing, "available_columns": list(df.columns)},
        )


def require_numeric_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    require_columns(df, columns)
    non_numeric = [c for c in columns if not pd.api.types.is_numeric_dtype(df[c])]
    if non_numeric:
        raise ValidationError(
            f"Column(s) are not numeric: {', '.join(non_numeric)}",
            {"non_numeric": non_numeric},
        )


def validate_shape(rows: int, cols: int) -> None:
    if rows > settings.max_rows:
        raise ValidationError(
            f"Dataset has {rows} rows, exceeding the limit of {settings.max_rows}.",
            {"rows": rows, "limit": settings.max_rows},
        )
    if cols > settings.max_columns:
        raise ValidationError(
            f"Dataset has {cols} columns, exceeding the limit of {settings.max_columns}.",
            {"columns": cols, "limit": settings.max_columns},
        )


def validate_non_empty(value: Any, field_name: str) -> None:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"'{field_name}' is required and cannot be empty.")


def clamp_output_rows(n: int | None) -> int:
    n = n or settings.max_output_rows
    return max(1, min(n, settings.max_output_rows))


def validate_operator(op: str, allowed: Iterable[str]) -> None:
    if op not in allowed:
        raise ValidationError(
            f"Unsupported operator '{op}'.", {"allowed": sorted(set(allowed))}
        )
