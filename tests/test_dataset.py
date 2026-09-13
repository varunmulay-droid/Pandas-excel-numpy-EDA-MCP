import base64

import pandas as pd
import pytest

from src.pandas_excel_mcp.core.dataset_manager import dataset_manager
from src.pandas_excel_mcp.core.file_manager import FileManager
from src.pandas_excel_mcp.schemas.exceptions import (
    DatasetNotFoundError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)


def test_register_and_get(sample_df):
    record = dataset_manager.register("sales.csv", "csv", sample_df)
    assert record.dataset_id.startswith("ds_")
    fetched = dataset_manager.get(record.dataset_id)
    assert fetched.shape == (8, 4)


def test_get_missing_dataset_raises():
    with pytest.raises(DatasetNotFoundError):
        dataset_manager.get("ds_does_not_exist")


def test_delete_dataset(sample_df):
    record = dataset_manager.register("sales.csv", "csv", sample_df)
    dataset_manager.delete(record.dataset_id)
    with pytest.raises(DatasetNotFoundError):
        dataset_manager.get(record.dataset_id)


def test_file_manager_rejects_bad_extension():
    fm = FileManager()
    with pytest.raises(UnsupportedFileTypeError):
        fm.load_dataframe("script.exe", b"not real data")


def test_file_manager_rejects_oversized_file():
    fm = FileManager()
    with pytest.raises(FileTooLargeError):
        fm.validate_size(10**9)


def test_file_manager_loads_csv():
    fm = FileManager()
    raw = b"a,b\n1,2\n3,4\n"
    df, sheets = fm.load_dataframe("data.csv", raw)
    assert sheets is None
    assert list(df.columns) == ["a", "b"]
    assert df.shape == (2, 2)


def test_decode_payload_rejects_invalid_base64():
    fm = FileManager()
    with pytest.raises(Exception):
        fm.decode_payload("not base64!!")


def test_decode_payload_roundtrip():
    fm = FileManager()
    raw = b"hello world"
    encoded = base64.b64encode(raw).decode()
    assert fm.decode_payload(encoded) == raw
