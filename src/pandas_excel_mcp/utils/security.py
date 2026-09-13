"""Security helpers: filename sanitisation, path containment, auth checks.

Nothing in this module ever executes user-supplied code, opens an
arbitrary filesystem path, or logs a secret.
"""
from __future__ import annotations

import os
import re
import uuid

from ..config.settings import settings
from ..schemas.exceptions import AuthenticationError, SecurityError

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def sanitize_filename(filename: str) -> str:
    """Strip directory components and unsafe characters from a filename."""
    base = os.path.basename(filename.strip())
    base = base.replace("..", "_")
    base = _SAFE_CHARS.sub("_", base)
    if not base:
        base = f"file_{uuid.uuid4().hex[:8]}"
    return base


def safe_join(root: str, filename: str) -> str:
    """Join ``filename`` under ``root`` and guarantee no path traversal."""
    root_abs = os.path.abspath(root)
    candidate = os.path.abspath(os.path.join(root_abs, sanitize_filename(filename)))
    if not candidate.startswith(root_abs + os.sep) and candidate != root_abs:
        raise SecurityError("Resolved path escapes the storage root.", {"filename": filename})
    return candidate


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def verify_bearer_token(authorization_header: str | None) -> None:
    """Raise AuthenticationError unless a valid bearer token is present.

    No-op when MCP_API_TOKEN / MCP_REQUIRE_AUTH is not configured, which is
    convenient for local development. Never logs the header value.
    """
    if not settings.require_auth:
        return
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise AuthenticationError("Missing or malformed Authorization header.")
    token = authorization_header.removeprefix("Bearer ").strip()
    if not settings.api_token or token != settings.api_token:
        raise AuthenticationError("Invalid bearer token.")


def redact(value: str, keep: int = 4) -> str:
    """Redact a secret-like string for safe logging."""
    if not value:
        return ""
    if len(value) <= keep:
        return "*" * len(value)
    return value[:keep] + "*" * (len(value) - keep)
