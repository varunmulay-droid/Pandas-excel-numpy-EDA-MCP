import pytest

from src.pandas_excel_mcp.engines import pandas_engine
from src.pandas_excel_mcp.schemas.exceptions import ColumnNotFoundError, ValidationError


def test_filter_rows_equals(sample_df):
    result = pandas_engine.filter_rows(sample_df, "Region", "==", "West")
    assert len(result) == 2
    assert set(result["Region"]) == {"West"}


def test_filter_rows_greater_than(sample_df):
    result = pandas_engine.filter_rows(sample_df, "Sales", ">", 10000)
    assert len(result) == 2


def test_filter_rows_unknown_column_raises(sample_df):
    with pytest.raises(ColumnNotFoundError):
        pandas_engine.filter_rows(sample_df, "NotAColumn", "==", "x")


def test_filter_rows_bad_operator_raises(sample_df):
    with pytest.raises(ValidationError):
        pandas_engine.filter_rows(sample_df, "Sales", "~=", 1)


def test_sort_data(sample_df):
    result = pandas_engine.sort_data(sample_df, ["Sales"], ascending=False)
    assert result.iloc[0]["Sales"] == sample_df["Sales"].max()


def test_group_by_sum(sample_df):
    result = pandas_engine.group_by(sample_df, ["Region"], "Profit", "sum")
    west = result[result["Region"] == "West"]["Profit"].iloc[0]
    assert west == 4800 + 6200


def test_aggregate(sample_df):
    result = pandas_engine.aggregate(sample_df, {"Sales": "sum", "Profit": "mean"})
    assert not result.empty


def test_merge_datasets():
    import pandas as pd

    left = pd.DataFrame({"id": [1, 2], "a": ["x", "y"]})
    right = pd.DataFrame({"id": [1, 2], "b": ["p", "q"]})
    merged = pandas_engine.merge_datasets(left, right, on=["id"], how="inner")
    assert list(merged.columns) == ["id", "a", "b"]


def test_pivot_table(sample_df):
    result = pandas_engine.pivot_table(sample_df, index=["Region"], columns=None, values=["Sales"], aggfunc="sum")
    assert "Sales" in result.columns


def test_clean_dataset_drop_missing():
    import numpy as np
    import pandas as pd

    df = pd.DataFrame({"a": [1, None, 3]})
    result = pandas_engine.clean_dataset(df, drop_missing=True)
    assert result.shape[0] == 2


def test_clean_dataset_remove_duplicates():
    import pandas as pd

    df = pd.DataFrame({"a": [1, 1, 2]})
    result = pandas_engine.clean_dataset(df, remove_duplicates=True)
    assert result.shape[0] == 2


def test_value_counts(sample_df):
    result = pandas_engine.value_counts(sample_df, "Region")
    assert len(result) == 4
