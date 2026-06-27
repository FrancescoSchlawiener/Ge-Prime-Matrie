"""URL prefix for reverse-proxy subpaths (e.g. /GPM on schlawiener.space)."""

from __future__ import annotations

import os

from flask import has_request_context, request


def configured_prefix() -> str:
    raw = os.environ.get("GE_PRIME_URL_PREFIX", "").strip()
    if not raw:
        return ""
    if not raw.startswith("/"):
        raw = f"/{raw}"
    return raw.rstrip("/")


def active_prefix() -> str:
    if has_request_context():
        script_root = (request.script_root or "").rstrip("/")
        if script_root:
            return script_root
    return configured_prefix()
