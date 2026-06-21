"""Gemeinsame Konfiguration für CLI, Web-Server und DB.

APP_VERSION, GPM_VERSION, REQUIRED_API_ROUTES (Preflight), Pfade (ROOT, DB).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_VERSION = "2026.06-gpm-v49"
STATIC_ASSET_VERSION = 58
GPM_VERSION = 7
MAX_CELL_TOKENS = 50
MAX_I_CURVE_TOKENS = 10_000
DTW_SEQUENCE_LIMIT = 512
WINDOW_SEQUENCE_LIMIT = 1024
API_PREVIEW_POINT_LIMIT = 30

# Kurzinfo für GPM-Statistik (keine Regeltabelle in der UI)
GPM_SI_STORAGE = {
    "label": "Speicher S und I",
    "summary": "Je 2, 4, 8 oder 16 Byte pro Zahl (S im Genom, I_Wort und I_Satz in der Geometrie)",
}


def gpm_si_storage_payload(*, gpm_version: int | None = None) -> dict:
    """API/UI-Payload für Speicher-Hinweis bei .gpm v4–v7."""
    return {
        "label": GPM_SI_STORAGE["label"],
        "summary": GPM_SI_STORAGE["summary"],
        "gpm_version": GPM_VERSION if gpm_version is None else gpm_version,
    }

REQUIRED_API_ROUTES = (
    "/api/health",
    "/api/version",
    "/api/db/stats",
    "/api/encode",
    "/api/decode",
    "/api/compare",
    "/api/diff",
    "/api/i-curve",
    "/api/hierarchy/search",
    "/api/spectroscope",
    "/api/cipher/encrypt",
    "/api/cipher/decrypt",
    "/api/gpm/compile",
    "/api/gpm/read",
    "/api/gpm/search",
    "/api/size/encode-word",
    "/api/size/decode",
    "/api/size/encode-batch",
    "/api/size/gpm",
)


def db_path() -> Path:
    """SQLite-Datei — siehe ``db.paths.default_db_path`` (nicht duplizieren)."""
    from db.paths import default_db_path

    return default_db_path()
