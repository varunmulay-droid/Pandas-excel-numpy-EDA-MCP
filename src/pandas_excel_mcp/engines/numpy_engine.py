"""NumPy-backed numerical operations over one or more dataframe columns."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..core.validators import require_numeric_columns, validate_operator

_STATS = {"mean", "median", "std", "var", "min", "max", "sum", "percentile", "quantile", "ptp"}


def numpy_statistics(
    df: pd.DataFrame, column: str, stat: str, q: float | None = None
) -> dict:
    require_numeric_columns(df, [column])
    validate_operator(stat, _STATS)
    arr = df[column].dropna().to_numpy(dtype=float)
    if arr.size == 0:
        return {"column": column, "stat": stat, "value": None, "n": 0}
    if stat == "mean":
        value = float(np.mean(arr))
    elif stat == "median":
        value = float(np.median(arr))
    elif stat == "std":
        value = float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0
    elif stat == "var":
        value = float(np.var(arr, ddof=1)) if arr.size > 1 else 0.0
    elif stat == "min":
        value = float(np.min(arr))
    elif stat == "max":
        value = float(np.max(arr))
    elif stat == "sum":
        value = float(np.sum(arr))
    elif stat == "ptp":
        value = float(np.ptp(arr))
    elif stat in ("percentile", "quantile"):
        qq = q if q is not None else 50.0 if stat == "percentile" else 0.5
        value = float(np.percentile(arr, qq if stat == "percentile" else qq * 100))
    else:  # pragma: no cover
        value = None
    return {"column": column, "stat": stat, "value": value, "n": int(arr.size)}


def correlation_analysis(
    df: pd.DataFrame, columns: list[str] | None = None, method: str = "pearson"
) -> dict:
    validate_operator(method, {"pearson", "spearman", "kendall"})
    numeric_df = df.select_dtypes(include="number") if not columns else df[columns]
    if columns:
        require_numeric_columns(df, columns)
    corr = numeric_df.corr(method=method)
    cov = numeric_df.cov()
    return {
        "method": method,
        "columns": list(numeric_df.columns),
        "correlation_matrix": corr.round(6).to_dict(),
        "covariance_matrix": cov.round(6).to_dict(),
    }


def outlier_analysis(df: pd.DataFrame, column: str, method: str = "iqr", threshold: float = 1.5) -> dict:
    require_numeric_columns(df, [column])
    validate_operator(method, {"iqr", "zscore"})
    series = df[column].dropna()
    if method == "iqr":
        q1, q3 = np.percentile(series, [25, 75])
        iqr = q3 - q1
        lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
        mask = (series < lower) | (series > upper)
        bounds = {"lower": float(lower), "upper": float(upper), "q1": float(q1), "q3": float(q3)}
    else:
        mean, std = series.mean(), series.std(ddof=1) or 1.0
        z = (series - mean) / std
        mask = z.abs() > threshold
        bounds = {"mean": float(mean), "std": float(std), "threshold": threshold}
    outlier_idx = series[mask].index.tolist()
    return {
        "column": column,
        "method": method,
        "bounds": bounds,
        "outlier_count": int(mask.sum()),
        "outlier_indices": outlier_idx[:1000],
        "outlier_values": [float(v) for v in series[mask].tolist()[:1000]],
    }
