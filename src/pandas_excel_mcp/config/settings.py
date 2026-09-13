"""Central configuration for the Pandas Excel Analytics MCP server.

All limits and environment-driven values live here so the rest of the
codebase never reads os.environ directly.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


def _bool_env(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    # --- Server identity -------------------------------------------------
    server_name: str = "Pandas Excel Analytics MCP"
    server_version: str = "1.0.0"

    # --- Networking --------------------------------------------------------
    host: str = "0.0.0.0"
    port: int = int(os.environ.get("PORT", "8000"))
    mcp_path: str = "/mcp"

    # Comma-separated list of hostnames Render (or any deployment) is
    # reachable at, e.g. "my-service.onrender.com". Wildcard ports are
    # appended automatically. localhost/127.0.0.1 are always included for
    # local development.
    allowed_hosts: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            h.strip()
            for h in os.environ.get("MCP_ALLOWED_HOSTS", "").split(",")
            if h.strip()
        )
    )

    # --- Auth ----------------------------------------------------------
    api_token: str | None = os.environ.get("MCP_API_TOKEN")
    require_auth: bool = _bool_env("MCP_REQUIRE_AUTH", bool(os.environ.get("MCP_API_TOKEN")))

    # --- Storage ---------------------------------------------------------
    storage_root: str = os.environ.get("MCP_STORAGE_ROOT", "storage")
    upload_dir: str = field(init=False)
    output_dir: str = field(init=False)

    # --- Limits ------------------------------------------------------------
    max_file_size_mb: int = int(os.environ.get("MCP_MAX_FILE_SIZE_MB", "50"))
    max_rows: int = int(os.environ.get("MCP_MAX_ROWS", "1_000_000"))
    max_columns: int = int(os.environ.get("MCP_MAX_COLUMNS", "500"))
    max_excel_sheets: int = int(os.environ.get("MCP_MAX_EXCEL_SHEETS", "50"))
    max_output_rows: int = int(os.environ.get("MCP_MAX_OUTPUT_ROWS", "5_000"))
    max_datasets_per_session: int = int(os.environ.get("MCP_MAX_DATASETS_PER_SESSION", "50"))
    session_idle_seconds: int = int(os.environ.get("MCP_SESSION_IDLE_SECONDS", "3600"))

    supported_extensions: tuple[str, ...] = (".csv", ".xlsx", ".xlsm", ".json", ".parquet")

    def __post_init__(self) -> None:
        object.__setattr__(self, "upload_dir", os.path.join(self.storage_root, "uploads"))
        object.__setattr__(self, "output_dir", os.path.join(self.storage_root, "outputs"))

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def transport_allowed_hosts(self) -> list[str]:
        hosts: list[str] = ["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*"]
        for h in self.allowed_hosts:
            hosts.append(h)
            if ":" not in h:
                hosts.append(f"{h}:*")
        return hosts


settings = Settings()
