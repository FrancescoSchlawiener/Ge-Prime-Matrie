"""Datenbank-Schicht (SQLite). Pfad: ``db.paths.default_db_path``."""

__all__ = [
    "WordRepository",
    "StoredWord",
    "language_label",
    "resolve_language",
    "default_db_path",
]


def __getattr__(name: str):
    if name == "WordRepository":
        from db.repository import WordRepository

        return WordRepository
    if name == "StoredWord":
        from db.models import StoredWord

        return StoredWord
    if name == "language_label":
        from db.language import language_label

        return language_label
    if name == "resolve_language":
        from db.language import resolve_language

        return resolve_language
    if name == "default_db_path":
        from db.paths import default_db_path

        return default_db_path
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
