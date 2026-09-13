"""Registers all MCP tools onto a server instance.

Call ``register_all_tools(mcp)`` once at server startup.
"""
from __future__ import annotations

from . import (
    cleaning_tools,
    dataset_tools,
    eda_tools,
    excel_tools,
    export_tools,
    numpy_tools,
    pandas_tools,
)


def register_all_tools(mcp) -> None:
    dataset_tools.register(mcp)      # 6 tools
    pandas_tools.register(mcp)       # 8 tools (includes clean_dataset)
    numpy_tools.register(mcp)        # 3 tools
    eda_tools.register(mcp)          # 2 tools
    excel_tools.register(mcp)        # 5 tools
    export_tools.register(mcp)       # 3 tools
    cleaning_tools.register(mcp)     # 0 additional tools (see module docstring)


__all__ = ["register_all_tools"]
