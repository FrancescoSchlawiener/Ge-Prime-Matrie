"""CLI — OG-DB kopieren, Roman-Alpha filtern, VACUUM, Integrität prüfen."""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alphabets.roman.map import uses_roman_alpha
from db.paths import DATA_DIR, GPM_ROMAN_ALPHA_DB, OG_DB_READONLY


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_and_filter_roman_alpha_db(
    *,
    source: Path = OG_DB_READONLY,
    dest: Path = GPM_ROMAN_ALPHA_DB,
) -> dict:
    if not source.is_file():
        raise FileNotFoundError(f"OG-Quell-DB nicht gefunden: {source}")

    source_hash_before = _file_sha256(source)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        dest.unlink()
    shutil.copy2(source, dest)

    delete_ids: list[int] = []
    remaining = 0

    conn = sqlite3.connect(dest)
    try:
        cur = conn.cursor()
        rows = cur.execute("SELECT id, word_normalized FROM words").fetchall()
        delete_ids = [row[0] for row in rows if not uses_roman_alpha(row[1])]
        if delete_ids:
            cur.executemany("DELETE FROM words WHERE id = ?", [(i,) for i in delete_ids])
        cur.execute(
            "DELETE FROM sources WHERE id NOT IN (SELECT DISTINCT source_id FROM words)"
        )
        conn.commit()
        remaining = cur.execute("SELECT COUNT(*) FROM words").fetchone()[0]
    finally:
        conn.close()

    # VACUUM cannot run inside a transaction; separate autocommit connection.
    vacuum_conn = sqlite3.connect(dest)
    try:
        vacuum_conn.isolation_level = None
        vacuum_conn.execute("VACUUM")
    finally:
        vacuum_conn.close()

    og_conn = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    try:
        integrity = og_conn.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        og_conn.close()

    source_hash_after = _file_sha256(source)

    return {
        "source": str(source),
        "dest": str(dest),
        "deleted_words": len(delete_ids),
        "remaining_words": remaining,
        "source_hash_before": source_hash_before,
        "source_hash_after": source_hash_after,
        "source_unchanged": source_hash_before == source_hash_after,
        "integrity_check": integrity,
    }


def _emit(msg: str, *, err: bool = False) -> None:
    stream = sys.stderr if err else sys.stdout
    data = (msg + "\n").encode("utf-8", errors="replace")
    buf = getattr(stream, "buffer", None)
    if buf is not None:
        buf.write(data)
        buf.flush()
        return
    stream.write(data.decode("ascii", errors="backslashreplace"))
    stream.flush()


def main() -> int:
    result = copy_and_filter_roman_alpha_db()
    _emit(f"Quelle: {result['source']}")
    _emit(f"Ziel:   {result['dest']}")
    _emit(f"Gelöscht: {result['deleted_words']} Wörter (Non-Roman-Zeichen)")
    _emit(f"Verbleibend: {result['remaining_words']} Wörter")
    _emit(f"Quelle unverändert (SHA-256): {result['source_unchanged']}")
    _emit(f"PRAGMA integrity_check (Original): {result['integrity_check']}")
    if result["integrity_check"] != "ok":
        return 1
    if not result["source_unchanged"]:
        _emit("WARNUNG: Original-Hash hat sich geändert!", err=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
