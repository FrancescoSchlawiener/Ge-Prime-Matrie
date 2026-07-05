"""POST /api/encode — Wörter encodieren und in DB speichern (db.paths.default_db_path)."""

from flask import Flask, jsonify, request

from db.language import language_label, resolve_language
from ge_prime.linguistics.language import infer_text_language_code
from pipeline.process import process_token
from web.handlers._repo import get_repo
from web.handlers._steps import build_encode_batch


def _resolve_batch_language(data: dict, text: str, repo) -> str:
    """Sprach-Tag für den Batch: explizit aus JSON oder aus Text erkannt."""
    explicit = (data.get("language") or "").strip()
    if explicit:
        return resolve_language(explicit)
    return infer_text_language_code(text, repo=repo)


def register(app: Flask, repo) -> None:
    @app.route("/api/encode", methods=["POST"])
    def api_encode():
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or data.get("word") or "").strip()
        if not text:
            return jsonify({"error": "Text oder Wörter erforderlich."}), 400

        batch = build_encode_batch(text)
        if batch["count"] == 0:
            return jsonify(
                {
                    "error": "Keine gültigen Wörter gefunden. Nur Buchstaben zählen — Leerzeichen und Satzzeichen werden ignoriert.",
                    "skipped": batch["skipped"],
                }
            ), 400

        repo = get_repo()
        repo.init_db()
        batch_lang = _resolve_batch_language(data, text, repo)

        entries = []
        for item in batch["words"]:
            entry = process_token(item["original"], language=batch_lang, source="web")
            if entry:
                entries.append(entry)

        source_id = repo.get_or_create_source("web", "ui")
        save_stats = repo.insert_words_batch(entries, source_id)
        batch["saved"] = save_stats.inserted
        batch["db_duplicates"] = save_stats.duplicates
        batch["db_total"] = repo.total_count()
        batch["language"] = language_label(batch_lang)

        entry_by_norm = {e.word_normalized: e for e in entries}
        for item in batch["words"]:
            entry = entry_by_norm.get(item["normalized"])
            if entry:
                item["language"] = entry.language
                item["language_label"] = language_label(entry.language)

        return jsonify(batch)
