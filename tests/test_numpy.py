import pytest

from src.pandas_excel_mcp.engines import numpy_engine
from src.pandas_excel_mcp.schemas.exceptions import ValidationError


def test_numpy_statistics_mean(sample_df):
    result = numpy_engine.numpy_statistics(sample_df, "Sales", "mean")
    assert result["stat"] == "mean"
    assert result["n"] == 8


def test_numpy_statistics_bad_stat_raises(sample_df):
    with pytest.raises(ValidationError):
        numpy_engine.numpy_statistics(sample_df, "Sales", "not_a_stat")


def test_correlation_analysis(sample_df):
    result = numpy_engine.correlation_analysis(sample_df)
    assert "Sales" in result["columns"]
    assert "Sales" in result["correlation_matrix"]


def test_outlier_analysis_iqr(sample_df):
    result = numpy_engine.outlier_analysis(sample_df, "Sales", method="iqr")
    assert "outlier_count" in result


def test_outlier_analysis_zscore(sample_df):
    result = numpy_engine.outlier_analysis(sample_df, "Sales", method="zscore", threshold=2.0)
    assert "outlier_count" in result
