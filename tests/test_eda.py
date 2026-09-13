import pandas as pd

from src.pandas_excel_mcp.engines import eda_engine


def test_eda_report_shape(sample_df):
    report = eda_engine.eda_report(sample_df)
    assert report["shape"] == {"rows": 8, "columns": 4}
    assert "Region" in report["columns"]


def test_eda_report_detects_missing():
    df = pd.DataFrame({"a": [1, None, 3]})
    report = eda_engine.eda_report(df)
    assert report["missing_values"]["a"] == 1
    assert any("missing" in w.lower() for w in report["warnings"])


def test_eda_report_detects_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2]})
    report = eda_engine.eda_report(df)
    assert report["duplicates"] == 1


def test_eda_report_constant_column():
    df = pd.DataFrame({"a": [1, 1, 1], "b": [1, 2, 3]})
    report = eda_engine.eda_report(df)
    assert "a" in report["constant_columns"]


def test_data_quality_report_score_range(sample_df):
    report = eda_engine.data_quality_report(sample_df)
    assert 0 <= report["quality_score"] <= 100


def test_data_quality_report_penalizes_missing():
    df = pd.DataFrame({"a": [1, None, None, None]})
    report = eda_engine.data_quality_report(df)
    assert report["quality_score"] < 100
    assert report["details"]["missing_values"] == 3
