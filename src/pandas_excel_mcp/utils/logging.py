"""Application logging setup.

Rule: never log Authorization headers, API tokens, or full dataset
contents. Log identifiers (dataset_id, tool name, row/col counts) only.
"""
from __future__ import annotations

import logging
import sys

_CONFIGURED = False


def get_logger(name: str = "pandas_excel_mcp") -> logging.Logger:
    global _CONFIGURED
    logger = logging.getLogger(name)
    if not _CONFIGURED:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        root = logging.getLogger("pandas_excel_mcp")
        root.setLevel(logging.INFO)
        root.addHandler(handler)
        _CONFIGURED = True
    return logger
