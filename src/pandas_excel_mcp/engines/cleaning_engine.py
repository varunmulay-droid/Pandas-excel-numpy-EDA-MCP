"""Cleaning/transformation operations.

Delegates to ``pandas_engine.clean_dataset`` — kept as its own module so
cleaning logic can grow independently (e.g. outlier capping, text
normalisation) without bloating the general pandas engine.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from .pandas_engine import clean_dataset as _clean_dataset


def clean_dataset(df: pd.DataFrame, **kwargs: Any) -> pd.DataFrame:
    return _clean_dataset(df, **kwargs)
