"""Einheitliche API-Hülle — Säule 4 Pädagogik-Vertrag."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Step(BaseModel):
    id: str
    title: str
    detail: str
    lines: list[str] = Field(default_factory=list)
    values: dict[str, str | int | float] = Field(default_factory=dict)
    formula: str | None = None
    extra: str | None = None


class CurveMeta(BaseModel):
    full_count: int
    downsampled: bool
    limit: int = 512


class WorkbenchResponse(BaseModel):
    result: dict[str, Any]
    steps: list[Step] = Field(default_factory=list)
    explain_links: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    curve_meta: CurveMeta | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    explain_link: str | None = None
    details: dict[str, str | int | float | bool] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class WorkbenchError(Exception):
    """Strukturierter API-Fehler mit HTTP-Status."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        explain_link: str | None = None,
        details: dict[str, str | int | float | bool] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.explain_link = explain_link
        self.details = details

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(
            error=ErrorDetail(
                code=self.code,
                message=self.message,
                explain_link=self.explain_link,
                details=self.details,
            )
        )
