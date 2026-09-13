"""All Pandas logic lives here. MCP tools stay thin and only call into this
engine; nothing here knows about MCP request/response shapes.
"""
from __future__ import annotations

from typing import Any, Literal

import pandas as pd

from ..core.validators import require_columns, validate_operator
from ..schemas.exceptions import OperationError, ValidationError

_FILTER_OPS = {"==", "!=", ">", ">=", "<", "<=", "in", "not in", "contains", "isnull", "notnull"}


def filter_rows(df: pd.DataFrame, column: str, operator: str, value: Any = None) -> pd.DataFrame:
    require_columns(df, [column])
    validate_operator(operator, _FILTER_OPS)
    series = df[column]
    if operator == "==":
        mask = series == value
    elif operator == "!=":
        mask = series != value
    elif operator == ">":
        mask = series > value
    elif operator == ">=":
        mask = series >= value
    elif operator == "<":
        mask = series < value
    elif operator == "<=":
        mask = series <= value
    elif operator == "in":
        mask = series.isin(value if isinstance(value, (list, tuple, set)) else [value])
    elif operator == "not in":
        mask = ~series.isin(value if isinstance(value, (list, tuple, set)) else [value])
    elif operator == "contains":
        mask = series.astype(str).str.contains(str(value), case=False, na=False)
    elif operator == "isnull":
        mask = series.isna()
    elif operator == "notnull":
        mask = series.notna()
    else:  # pragma: no cover - guarded by validate_operator
        raise ValidationError(f"Unsupported operator '{operator}'.")
    return df[mask]


def sort_data(df: pd.DataFrame, columns: list[str], ascending: bool | list[bool] = True) -> pd.DataFrame:
    require_columns(df, columns)
    return df.sort_values(by=columns, ascending=ascending)


def group_by(
    df: pd.DataFrame,
    group_columns: list[str],
    agg_column: str,
    agg_func: str = "sum",
) -> pd.DataFrame:
    require_columns(df, [*group_columns, agg_column])
    validate_operator(agg_func, {"sum", "mean", "median", "min", "max", "count", "std", "var", "nunique"})
    grouped = df.groupby(group_columns, dropna=False)[agg_column].agg(agg_func)
    return grouped.reset_index()


def aggregate(df: pd.DataFrame, aggregations: dict[str, str | list[str]]) -> pd.DataFrame:
    require_columns(df, list(aggregations.keys()))
    result = df.agg(aggregations)
    if isinstance(result, pd.Series):
        return result.to_frame().T
    return result.reset_index().rename(columns={"index": "aggregation"})


def merge_datasets(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: list[str] | str,
    how: Literal["inner", "left", "right", "outer"] = "inner",
) -> pd.DataFrame:
    validate_operator(how, {"inner", "left", "right", "outer"})
    on_cols = on if isinstance(on, list) else [on]
    require_columns(left, on_cols)
    require_columns(right, on_cols)
    return left.merge(right, on=on_cols, how=how)


def pivot_table(
    df: pd.DataFrame,
    index: list[str],
    columns: list[str] | None,
    values: list[str],
    aggfunc: str = "mean",
) -> pd.DataFrame:
    require_columns(df, [*index, *(columns or []), *values])
    validate_operator(aggfunc, {"sum", "mean", "median", "min", "max", "count", "std", "var"})
    table = pd.pivot_table(
        df, index=index, columns=columns or None, values=values, aggfunc=aggfunc
    )
    return table.reset_index()


def clean_dataset(
    df: pd.DataFrame,
    drop_missing: bool = False,
    fill_missing: dict[str, Any] | None = None,
    remove_duplicates: bool = False,
    rename_columns: dict[str, str] | None = None,
    convert_types: dict[str, str] | None = None,
) -> pd.DataFrame:
    result = df.copy()
    if rename_columns:
        require_columns(result, list(rename_columns.keys()))
        result = result.rename(columns=rename_columns)
    if fill_missing:
        require_columns(result, list(fill_missing.keys()))
        result = result.fillna(value=fill_missing)
    if drop_missing:
        result = result.dropna()
    if remove_duplicates:
        result = result.drop_duplicates()
    if convert_types:
        require_columns(result, list(convert_types.keys()))
        for col, dtype in convert_types.items():
            try:
                if dtype == "datetime":
                    result[col] = pd.to_datetime(result[col], errors="coerce")
                else:
                    result[col] = result[col].astype(dtype)
            except Exception as exc:  # noqa: BLE001
                raise OperationError(
                    f"Could not convert column '{col}' to type '{dtype}': {exc}"
                ) from exc
    return result


def value_counts(df: pd.DataFrame, column: str, normalize: bool = False, top_n: int | None = None) -> pd.DataFrame:
    require_columns(df, [column])
    counts = df[column].value_counts(normalize=normalize, dropna=False)
    if top_n:
        counts = counts.head(top_n)
    return counts.reset_index()
