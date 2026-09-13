import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Region": ["West", "East", "South", "North", "West", "East", "South", "North"],
            "Sales": [12000, 9500, 8700, 6100, 15000, 9800, 7600, 5200],
            "Profit": [4800, 2100, 1900, 900, 6200, 2300, 1500, 700],
            "Units": [120, 95, 87, 61, 150, 98, 76, 52],
        }
    )


@pytest.fixture(autouse=True)
def _clear_datasets():
    """Keep the process-wide DatasetManager singleton clean between tests."""
    from src.pandas_excel_mcp.core.dataset_manager import dataset_manager

    yield
    for record in list(dataset_manager.list_all()):
        dataset_manager.delete(record.dataset_id)
