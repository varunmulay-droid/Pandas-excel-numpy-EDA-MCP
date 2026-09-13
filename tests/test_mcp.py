import base64
import json

import pytest
from mcp.server.mcpserver import MCPServer

from src.pandas_excel_mcp.tools import register_all_tools


def _payload(result):
    return json.loads(result.content[0].text)


@pytest.fixture
def mcp():
    server = MCPServer(name="test-server")
    register_all_tools(server)
    return server


@pytest.mark.asyncio
async def test_all_27_tools_registered(mcp):
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    expected = {
        "upload_dataset", "list_datasets", "dataset_info", "preview_data",
        "column_profile", "list_sheets",
        "filter_rows", "sort_data", "group_by", "aggregate", "merge_datasets",
        "pivot_table", "clean_dataset", "value_counts",
        "numpy_statistics", "correlation_analysis", "outlier_analysis",
        "eda_report", "data_quality_report",
        "excel_read_range", "excel_write_range", "excel_format", "excel_chart",
        "excel_list_sheets",
        "export_excel", "export_csv", "export_json",
    }
    assert names == expected
    assert len(expected) == 27


@pytest.mark.asyncio
async def test_upload_and_preview(mcp):
    csv_bytes = b"a,b\n1,2\n3,4\n"
    b64 = base64.b64encode(csv_bytes).decode()
    result = await mcp.call_tool("upload_dataset", {"filename": "t.csv", "data_base64": b64})
    payload = _payload(result)
    assert payload["success"] is True
    ds = payload["dataset_id"]

    result = await mcp.call_tool("preview_data", {"dataset_id": ds, "rows": 5})
    payload = _payload(result)
    assert payload["rows"] == 2


@pytest.mark.asyncio
async def test_error_response_shape_for_missing_dataset(mcp):
    result = await mcp.call_tool("dataset_info", {"dataset_id": "ds_missing"})
    payload = _payload(result)
    assert payload["success"] is False
    assert payload["error"]["type"] == "DatasetNotFound"


@pytest.mark.asyncio
async def test_authentication_helper_noop_without_token():
    from src.pandas_excel_mcp.utils.security import verify_bearer_token

    # require_auth is False unless MCP_API_TOKEN is set, so this must not raise.
    verify_bearer_token(None)


def test_authentication_helper_rejects_bad_token(monkeypatch):
    from src.pandas_excel_mcp.schemas.exceptions import AuthenticationError
    from src.pandas_excel_mcp.utils import security

    class _FakeSettings:
        require_auth = True
        api_token = "secret123"

    monkeypatch.setattr(security, "settings", _FakeSettings())
    with pytest.raises(AuthenticationError):
        security.verify_bearer_token("Bearer wrong-token")
    security.verify_bearer_token("Bearer secret123")  # should not raise
