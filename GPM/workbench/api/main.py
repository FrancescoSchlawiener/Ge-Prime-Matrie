"""GPM Workbench FastAPI application."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# GPM/functions on sys.path (parents[2] from api/main.py → workbench → GPM → functions)
_FUNCTIONS = Path(__file__).resolve().parents[2] / "functions"
if str(_FUNCTIONS) not in sys.path:
    sys.path.insert(0, str(_FUNCTIONS))

from api.routes import register_routes  # noqa: E402
from api.schemas.common import ErrorDetail, ErrorResponse, WorkbenchError  # noqa: E402

app = FastAPI(
    title="GPM Workbench API",
    version="1.0.0",
    description="Pedagogical API over GPM/functions",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(error=ErrorDetail(code="value_error", message=str(exc))).model_dump(),
    )


@app.exception_handler(WorkbenchError)
async def workbench_error_handler(_request: Request, exc: WorkbenchError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_response().model_dump(),
    )


@app.exception_handler(KeyError)
async def key_error_handler(_request: Request, exc: KeyError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error=ErrorDetail(code="document_ref_not_found", message=str(exc))
        ).model_dump(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    code = "http_error"
    if exc.status_code == 404:
        code = "document_ref_not_found"
    elif exc.status_code == 422:
        code = "gpm_invalid_stream"
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=ErrorDetail(code=code, message=detail)).model_dump(),
    )


register_routes(app)

_STATIC = Path(__file__).resolve().parents[1] / "web" / "dist"
if os.getenv("WORKBENCH_PROD") == "1" and _STATIC.is_dir():
    app.mount("/", StaticFiles(directory=str(_STATIC), html=True), name="static")
