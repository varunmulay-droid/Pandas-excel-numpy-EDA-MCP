"""Pydantic models describing the structured success/error envelope.

Every MCP tool returns a JSON-serialisable dict shaped like one of these
two models, produced via ``to_dict()``.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorPayload(BaseModel):
    type: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorPayload

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class SuccessResponse(BaseModel):
    success: bool = True
    operation: str
    dataset_id: str | None = None
    data: Any = None
    rows: int | None = None
    columns: list[str] | None = None
    meta: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.model_dump().items() if v is not None}
