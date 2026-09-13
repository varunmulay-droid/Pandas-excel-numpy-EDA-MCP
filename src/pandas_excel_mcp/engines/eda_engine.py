"""Automated exploratory data analysis and data-quality scoring."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _numeric_stats(df: pd.DataFrame) -> dict[str, Any]:
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return {}
    desc = numeric.describe().to_dict()
    return {col: {k: (None if pd.isna(v) else float(v)) for k, v in stats.items()} for col, stats in desc.items()}


def _categorical_stats(df: pd.DataFrame) -> dict[str, Any]:
    cat = df.select_dtypes(exclude="number")
    out: dict[str, Any] = {}
    for col in cat.columns:
        vc = df[col].value_counts(dropna=False).head(5)
        out[col] = {
            "unique": int(df[col].nunique(dropna=True)),
            "top_values": {str(k): int(v) for k, v in vc.items()},
        }
    return out


def _constant_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if df[c].nunique(dropna=False) <= 1]


def _high_cardinality_columns(df: pd.DataFrame, threshold: float = 0.9) -> list[str]:
    n = len(df) or 1
    return [c for c in df.columns if df[c].nunique(dropna=True) / n > threshold and n > 1]


def _possible_id_columns(df: pd.DataFrame) -> list[str]:
    n = len(df) or 1
    return [c for c in df.columns if df[c].nunique(dropna=True) == n and n > 1]


def _outlier_summary(df: pd.DataFrame) -> dict[str, int]:
    out: dict[str, int] = {}
    for col in df.select_dtypes(include="number").columns:
        series = df[col].dropna()
        if series.empty:
            continue
        q1, q3 = np.percentile(series, [25, 75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        out[col] = int(((series < lower) | (series > upper)).sum())
    return out


def eda_report(df: pd.DataFrame) -> dict[str, Any]:
    missing = df.isna().sum()
    missing_pct = (missing / len(df) * 100) if len(df) else missing * 0
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    corr = df[numeric_cols].corr().round(4).to_dict() if len(numeric_cols) >= 2 else {}
    constant_cols = _constant_columns(df)
    high_card_cols = _high_cardinality_columns(df)
    id_cols = _possible_id_columns(df)

    warnings: list[str] = []
    if constant_cols:
        warnings.append(f"{len(constant_cols)} constant column(s) carry no information.")
    if df.duplicated().sum() > 0:
        warnings.append(f"{int(df.duplicated().sum())} duplicate row(s) detected.")
    if missing.sum() > 0:
        warnings.append(f"{int(missing.sum())} missing value(s) across the dataset.")

    recommendations: list[str] = []
    if constant_cols:
        recommendations.append(f"Consider dropping constant columns: {constant_cols}.")
    if id_cols:
        recommendations.append(f"Columns {id_cols} look like identifiers — likely exclude from modeling.")
    if high_card_cols:
        recommendations.append(f"High-cardinality columns {high_card_cols} may need encoding or grouping.")

    return {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": list(df.columns.astype(str)),
        "dtypes": {str(c): str(t) for c, t in df.dtypes.items()},
        "missing_values": {str(c): int(v) for c, v in missing.items()},
        "missing_percentage": {str(c): round(float(v), 2) for c, v in missing_pct.items()},
        "duplicates": int(df.duplicated().sum()),
        "numeric_statistics": _numeric_stats(df),
        "categorical_statistics": _categorical_stats(df),
        "correlations": corr,
        "outliers": _outlier_summary(df),
        "constant_columns": constant_cols,
        "high_cardinality_columns": high_card_cols,
        "possible_id_columns": id_cols,
        "warnings": warnings,
        "recommendations": recommendations,
    }


def data_quality_report(df: pd.DataFrame) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    missing_total = int(df.isna().sum().sum())
    dup_count = int(df.duplicated().sum())
    constant_cols = _constant_columns(df)
    high_card_cols = _high_cardinality_columns(df)
    id_cols = _possible_id_columns(df)

    if missing_total:
        issues.append(f"{missing_total} missing value(s).")
    if dup_count:
        issues.append(f"{dup_count} duplicate row(s).")
    if constant_cols:
        warnings.append(f"Constant columns: {constant_cols}.")
    if high_card_cols:
        warnings.append(f"High-cardinality columns: {high_card_cols}.")

    negative_cols = []
    for col in df.select_dtypes(include="number").columns:
        if (df[col] < 0).any():
            negative_cols.append(col)
    if negative_cols:
        warnings.append(f"Negative values found in: {negative_cols}.")

    outliers = _outlier_summary(df)
    outlier_cols = {c: n for c, n in outliers.items() if n > 0}
    if outlier_cols:
        warnings.append(f"Outliers detected in: {list(outlier_cols.keys())}.")

    if constant_cols:
        recommendations.append("Drop constant columns before modeling.")
    if dup_count:
        recommendations.append("Remove duplicate rows via clean_dataset.")
    if missing_total:
        recommendations.append("Impute or drop missing values via clean_dataset.")

    # Simple 0-100 score: penalise missing %, duplicates %, and constant cols.
    n_cells = max(df.shape[0] * df.shape[1], 1)
    missing_penalty = min(40, (missing_total / n_cells) * 100)
    dup_penalty = min(30, (dup_count / max(df.shape[0], 1)) * 100)
    constant_penalty = min(20, len(constant_cols) * 5)
    quality_score = round(max(0.0, 100 - missing_penalty - dup_penalty - constant_penalty), 1)

    return {
        "quality_score": quality_score,
        "issues": issues,
        "warnings": warnings,
        "recommendations": recommendations,
        "details": {
            "missing_values": missing_total,
            "duplicate_rows": dup_count,
            "constant_columns": constant_cols,
            "high_cardinality_columns": high_card_cols,
            "possible_id_columns": id_cols,
            "negative_value_columns": negative_cols,
            "outlier_counts": outlier_cols,
        },
    }
