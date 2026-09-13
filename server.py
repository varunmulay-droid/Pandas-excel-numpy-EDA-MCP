"""Pandas Excel Analytics MCP — main server entrypoint.

Built on the current stable MCP Python SDK (``mcp`` >= 2.x), where the
server class is ``mcp.server.mcpserver.MCPServer`` (the successor to the
older ``mcp.server.fastmcp.FastMCP`` name used in pre-2.0 tutorials).

Run locally:
    uvicorn server:app --reload --host 127.0.0.1 --port 8000

Run on Render:
    uvicorn server:app --host 0.0.0.0 --port $PORT
"""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from src.pandas_excel_mcp.config.settings import settings
from src.pandas_excel_mcp.tools import register_all_tools
from src.pandas_excel_mcp.utils.logging import get_logger

logger = get_logger(__name__)

# --------------------------------------------------------------------------
# 1. Create the MCP server
# --------------------------------------------------------------------------
mcp = MCPServer(
    name=settings.server_name,
    version=settings.server_version,
    instructions=(
        "Deterministic data-analysis tools over uploaded tabular datasets: "
        "Pandas, NumPy, Excel/openpyxl, and automated EDA. This server does "
        "not call any LLM and does not execute arbitrary code."
    ),
)

# --------------------------------------------------------------------------
# 2. Register all 27 tools
# --------------------------------------------------------------------------
register_all_tools(mcp)

# --------------------------------------------------------------------------
# 3. Configure transport security for the deployed hostname (Render)
#    The MCP SDK rejects requests to a non-localhost Host header unless it
#    is explicitly allow-listed here. Do NOT disable this check.
# --------------------------------------------------------------------------
transport_security = TransportSecuritySettings(
    allowed_hosts=settings.transport_allowed_hosts,
    allowed_origins=settings.transport_allowed_hosts,
)

# --------------------------------------------------------------------------
# 4. Build the production Streamable HTTP ASGI app, mounted at /mcp
# --------------------------------------------------------------------------
app = mcp.streamable_http_app(
    streamable_http_path=settings.mcp_path,
    transport_security=transport_security,
    host=settings.host,
)


async def health(request: Request) -> JSONResponse:  # noqa: D401 - simple health check
    """Liveness probe. Never exposes datasets, tokens, or filesystem paths."""
    return JSONResponse({"status": "ok"})


app.add_route("/health", health, methods=["GET"])


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting %s on %s:%s%s", settings.server_name, settings.host, settings.port, settings.mcp_path)
    uvicorn.run(app, host=settings.host, port=settings.port)
