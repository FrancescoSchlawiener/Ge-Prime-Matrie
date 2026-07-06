"""System routes — health, version, profiles."""

from __future__ import annotations

from fastapi import APIRouter

from alphabets.profiles import AlphabetProfile
from analysis.corpus.sqlite_roman import open_roman_alpha_corpus, roman_alpha_db_name
from db.paths import GPM_ROMAN_ALPHA_DB

router = APIRouter(prefix="/api", tags=["system"])

WORKBENCH_VERSION = "1.0.0"


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/version")
def version() -> dict:
    return {"workbench": WORKBENCH_VERSION, "api": "gpm-workbench"}


@router.get("/profiles")
def profiles() -> dict:
    items = [
        {"id": p.value, "label": p.name.replace("_", " ").title()}
        for p in AlphabetProfile
    ]
    return {"profiles": items, "count": len(items)}


@router.get("/db/stats")
def db_stats() -> dict:
    if not GPM_ROMAN_ALPHA_DB.is_file():
        return {
            "total": 0,
            "by_language": [],
            "db_name": roman_alpha_db_name(),
            "connected": False,
        }
    try:
        corpus = open_roman_alpha_corpus()
        by_language = [
            {"language": lang, "count": count} for lang, count in corpus.count_by_language()
        ]
        return {
            "total": corpus.count_words(),
            "by_language": by_language,
            "db_name": roman_alpha_db_name(),
            "connected": True,
        }
    except OSError:
        return {
            "total": 0,
            "by_language": [],
            "db_name": roman_alpha_db_name(),
            "connected": False,
        }
