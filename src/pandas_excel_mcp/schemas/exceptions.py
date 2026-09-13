"""Custom exception hierarchy used throughout the server.

Every exception carries a machine-readable ``error_type`` and an optional
``details`` dict so it can be turned directly into a structured error
response by ``utils.serialization.error_response``.
"""
from __future__ import annotations

from typing import Any


class AppError(Exception):
    """Base class for all handled application errors."""

    error_type: str = "AppError"

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(AppError):
    error_type = "ValidationError"


class DatasetNotFoundError(AppError):
    error_type = "DatasetNotFound"


class ColumnNotFoundError(AppError):
    error_type = "ColumnNotFound"


class SheetNotFoundError(AppError):
    error_type = "SheetNotFound"


class UnsupportedFileTypeError(AppError):
    error_type = "UnsupportedFileType"


class FileTooLargeError(AppError):
    error_type = "FileTooLarge"


class DatasetTooLargeError(AppError):
    error_type = "DatasetTooLarge"


class SecurityError(AppError):
    error_type = "SecurityError"


class AuthenticationError(AppError):
    error_type = "AuthenticationError"


class OperationError(AppError):
    error_type = "OperationError"


class ExportError(AppError):
    error_type = "ExportError"
