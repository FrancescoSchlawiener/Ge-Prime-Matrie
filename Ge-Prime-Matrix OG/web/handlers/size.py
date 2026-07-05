"""API-Handler für Speichervergleiche (on-demand per Button)."""

from __future__ import annotations

import base64

from flask import Request, jsonify, request

from gpm.compiler import compile_text
from gpm.format import GpmFormatError, read_gpm
from ge_prime.decode import decode_word
from pipeline.process import process_token
from pipeline.size_compare import (
    compare_decode_word,
    compare_encode_batch,
    compare_encoded_word,
    compare_gpm_document,
)


def _parse_int(raw, field: str) -> int:
    try:
        return int(str(raw).strip().replace(".", "").replace(",", ""))
    except (TypeError, ValueError, AttributeError):
        raise ValueError(f"{field} muss eine ganze Zahl sein.") from None


def handle_size_encode_word(request: Request):
    data = request.get_json(silent=True) or {}
    original = (data.get("original") or "").strip()
    normalized = (data.get("normalized") or "").strip()
    try:
        substance = _parse_int(data.get("substance"), "Substanz S")
        perm_index = _parse_int(data.get("perm_index"), "Index I")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not normalized and original:
        processed = process_token(original, source="size")
        if processed is None:
            return jsonify({"error": "Wort ungültig."}), 400
        original = processed.word_original
        normalized = processed.word_normalized
        substance = processed.substance
        perm_index = processed.perm_index
    elif not normalized:
        return jsonify({"error": "Wort oder S/I erforderlich."}), 400

    if substance < 1 or perm_index < 1:
        return jsonify({"error": "S und I müssen größer als 0 sein."}), 400

    if not original:
        original = normalized

    result = compare_encoded_word(
        original=original,
        normalized=normalized,
        substance=substance,
        perm_index=perm_index,
    )
    return jsonify(result.to_dict())


def handle_size_decode(request: Request):
    data = request.get_json(silent=True) or {}
    try:
        substance = _parse_int(data.get("substance"), "Substanz S")
        perm_index = _parse_int(data.get("perm_index"), "Index I")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if substance < 1 or perm_index < 1:
        return jsonify({"error": "S und I müssen größer als 0 sein."}), 400

    word = (data.get("word") or "").strip()
    if not word:
        try:
            word = decode_word(substance, perm_index)
        except (ValueError, TypeError):
            return jsonify({"error": "S/I ungültig — kein Wort rekonstruierbar."}), 400

    result = compare_decode_word(word=word, substance=substance, perm_index=perm_index)
    return jsonify(result.to_dict())


def handle_size_encode_batch(request: Request):
    data = request.get_json(silent=True) or {}
    words = data.get("words")
    if not isinstance(words, list) or not words:
        return jsonify({"error": "Liste words erforderlich."}), 400

    cleaned: list[dict] = []
    for item in words:
        if not isinstance(item, dict):
            continue
        try:
            original = str(item.get("original") or "").strip()
            normalized = str(item.get("normalized") or "").strip()
            substance = int(item.get("substance"))
            perm_index = int(item.get("perm_index"))
            if not normalized and original:
                processed = process_token(original, source="size")
                if processed is None:
                    continue
                original = processed.word_original
                normalized = processed.word_normalized
                substance = processed.substance
                perm_index = processed.perm_index
            if not normalized:
                continue
            cleaned.append(
                {
                    "original": original or normalized,
                    "normalized": normalized,
                    "substance": substance,
                    "perm_index": perm_index,
                }
            )
        except (TypeError, ValueError):
            continue

    if not cleaned:
        return jsonify({"error": "Keine gültigen Wörter in words."}), 400

    try:
        result = compare_encode_batch(cleaned)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result.to_dict())


def handle_size_gpm(request: Request):
    data = request.get_json(silent=True) or {}
    source_text = (data.get("source_text") or "").strip()
    file_b64 = (data.get("file_base64") or "").strip()

    if not file_b64 and data.get("text"):
        try:
            _, blob, _ = compile_text(str(data.get("text")).strip())
            file_b64 = base64.b64encode(blob).decode("ascii")
            if not source_text:
                source_text = str(data.get("text")).strip()
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    if not file_b64:
        return jsonify({"error": "file_base64 oder text erforderlich."}), 400

    try:
        blob = base64.b64decode(file_b64)
        if not source_text:
            from gpm.reader import reconstruct_text

            source_text = reconstruct_text(read_gpm(blob))
        result = compare_gpm_document(source_text=source_text, blob=blob)
    except (ValueError, GpmFormatError) as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result.to_dict())


def register(app, repo) -> None:
    @app.route("/api/size/encode-word", methods=["POST"])
    def api_size_encode_word():
        return handle_size_encode_word(request)

    @app.route("/api/size/decode", methods=["POST"])
    def api_size_decode():
        return handle_size_decode(request)

    @app.route("/api/size/encode-batch", methods=["POST"])
    def api_size_encode_batch():
        return handle_size_encode_batch(request)

    @app.route("/api/size/gpm", methods=["POST"])
    def api_size_gpm():
        return handle_size_gpm(request)
