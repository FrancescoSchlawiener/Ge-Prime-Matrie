"""Zugriff auf das aktuelle WordRepository (für Tests austauschbar)."""

from __future__ import annotations


def get_repo():
    import web.app as web_app

    return web_app.repo
