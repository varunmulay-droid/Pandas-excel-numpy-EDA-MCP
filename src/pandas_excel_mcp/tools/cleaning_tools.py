"""Cleaning tools.

The ``clean_dataset`` MCP tool is registered once, in ``pandas_tools``, to
avoid double-registering the same tool name with the MCP server. This
module exists for directory-structure parity with the spec and as the
place to add future dedicated cleaning tools (e.g. outlier capping) that
don't belong under the general pandas tool surface.
"""
from __future__ import annotations


def register(mcp) -> None:  # pragma: no cover - intentionally a no-op
    """No-op: clean_dataset lives in pandas_tools.register()."""
    return None
