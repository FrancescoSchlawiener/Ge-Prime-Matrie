"""Flask-Hilfsfunktionen für .gpm-API."""

from __future__ import annotations

import base64
import json

from flask import Request, jsonify, request

from ge_prime.cipher import VALID_MODES
from ge_prime.config import GPM_VERSION, gpm_si_storage_payload
from ge_prime.i_curve import cell_geometry_payload
from gpm.cipher_wrap import (
    GpcFormatError,
    decrypt_gpm_file,
    encrypt_gpm_file,
    is_encrypted_gpm_blob,
    peek_gpc_meta,
)
from gpm.compiler import compile_text
from gpm.format import GpmFormatError, read_gpm, FLAG_BODY_CELL
from gpm.model import GpmAnalysis, GpmCompileStats, GpmDocument
from gpm.reader import analyze_gpm, search_by_gcd, search_by_lcm, search_by_word
from gpm.separator_codec import perm_code_label
from pipeline.normalize import normalize_text_nfc

MAX_GPM_UPLOAD_BYTES = 50 * 1024 * 1024


def _int_json(value: int) -> int | str:
    """Große Substanzen sicher als JSON (Fallback String)."""
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError, OverflowError):
        return str(value)


def _compile_stats_payload(stats: GpmCompileStats) -> dict:
    return {
        "gpm_version": GPM_VERSION,
        "si_storage": gpm_si_storage_payload(),
        "source_bytes": stats.source_bytes,
        "file_bytes": stats.file_bytes,
        "header_bytes": stats.header_bytes,
        "body_bytes": stats.body_bytes,
        "separator_bytes": stats.separator_bytes,
        "separator_perm": stats.separator_perm,
        "separator_perm_label": perm_code_label(stats.separator_perm),
        "gap_bytes": stats.gap_bytes,
        "unique_words": stats.unique_words,
        "total_tokens": stats.total_tokens,
        "skipped_tokens": stats.skipped_tokens,
        "compression_ratio": stats.compression_ratio,
        "compression_percent": round(stats.compression_ratio * 100, 2),
        "lossless": stats.lossless,
        "zellen_anzahl": stats.zellen_anzahl,
        "body_mode": stats.body_mode,
        "cell_count_encodable": stats.cell_count_encodable,
    }


def _body_mode_from_blob(data: bytes) -> str:
    if len(data) >= 5 and data[:3] == b"GPM" and data[3] >= 5:
        flags = data[4]
        return "cell" if flags & FLAG_BODY_CELL else "flat"
    return "flat"


def _analysis_payload(analysis: GpmAnalysis, *, document: GpmDocument | None = None, blob: bytes | None = None) -> dict:
    payload = {
        "gpm_version": analysis.version,
        "si_storage": gpm_si_storage_payload(gpm_version=analysis.version)
            if analysis.version >= 4
            else None,
        "version": analysis.version,
        "unique_words": analysis.unique_words,
        "total_tokens": analysis.total_tokens,
        "file_bytes": analysis.file_bytes,
        "header_bytes": analysis.header_bytes,
        "body_bytes": analysis.body_bytes,
        "separator_bytes": analysis.separator_bytes,
        "separator_perm": analysis.separator_perm,
        "separator_perm_label": perm_code_label(analysis.separator_perm),
        "gap_bytes": analysis.gap_bytes,
        "lossless": analysis.lossless,
        "header": [
            {**row, "substance": _int_json(row["substance"])}
            for row in analysis.header
        ],
        "body_preview": [
            {**row, "substance": _int_json(row["substance"])}
            for row in analysis.body_preview
        ],
        "reconstructed_text": analysis.reconstructed_text,
    }
    if document is not None:
        payload["cell_geometry"] = cell_geometry_payload(document)
        payload["body_mode"] = _body_mode_from_blob(blob) if blob else "cell"
        payload["zellen_anzahl"] = payload["cell_geometry"]["count"]
    elif blob is not None:
        payload["body_mode"] = _body_mode_from_blob(blob)
    return payload


def _read_request_bytes(request: Request) -> bytes:
    if request.files and request.files.get("file"):
        data = request.files["file"].read()
    else:
        payload = request.get_json(silent=True) or {}
        data = _decode_gpm_blob(payload)

    if not data:
        raise ValueError("Leere Datei.")
    if len(data) > MAX_GPM_UPLOAD_BYTES:
        raise ValueError("Datei zu groß (max. 50 MB).")
    return data


def _decode_gpm_blob(payload: dict) -> bytes:
    encoded = (payload.get("file_base64") or "").strip()
    if not encoded:
        raise ValueError("Keine Datei — file_base64 erforderlich.")
    return base64.b64decode(encoded)


def handle_gpm_compile(request: Request):
    data = request.get_json(silent=True) or {}
    text = normalize_text_nfc((data.get("text") or "").strip())
    if not text:
        return jsonify({"error": "Text erforderlich."}), 400

    encrypt = data.get("encrypt") in (True, "true", 1, "1")
    cipher_mode = (data.get("cipher_mode") or "word").strip().lower()
    cipher_keys = data.get("cipher_keys") if data.get("cipher_keys") is not None else data.get("keys", "")

    if encrypt and cipher_mode not in VALID_MODES:
        return jsonify({"error": f"cipher_mode muss einer von {', '.join(VALID_MODES)} sein."}), 400
    if encrypt and not str(cipher_keys or "").strip():
        return jsonify({"error": "Verschlüsselung: Schlüssel erforderlich."}), 400

    try:
        document, plain_blob, stats = compile_text(text)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    from gpm.reader import reconstruct_text

    header_limit = 500
    body_limit = 500
    header_preview = [
        {
            "word_id": entry.word_id,
            "original": entry.word_original,
            "normalized": entry.word_normalized,
            "substance": _int_json(entry.substance),
        }
        for entry in document.header[:header_limit]
    ]
    body_preview = [
        {
            "position": idx,
            "word_id": token.word_id,
            "perm_index": token.perm_index,
            "case_code": token.case_code,
            "word": document.header[token.word_id].word_original,
        }
        for idx, token in enumerate(document.tokens[:body_limit])
    ]

    if encrypt:
        try:
            blob, enc = encrypt_gpm_file(text, mode=cipher_mode, keys_raw=cipher_keys)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        enc_stats = dict(_compile_stats_payload(stats))
        enc_stats["file_bytes"] = len(blob)
        enc_stats["compression_ratio"] = round(len(blob) / max(stats.source_bytes, 1), 4)
        enc_stats["compression_percent"] = round(enc_stats["compression_ratio"] * 100, 2)

        return jsonify(
            {
                "gpm_version": GPM_VERSION,
                "filename": "document.gpm",
                "file_base64": base64.b64encode(blob).decode("ascii"),
                "plain_file_base64": base64.b64encode(plain_blob).decode("ascii"),
                "encrypted": True,
                "cipher_mode": cipher_mode,
                "security": enc["security"],
                "stats": enc_stats,
                "header_preview": [],
                "body_preview": [],
                "header_preview_hidden": True,
                "reconstructed_text": reconstruct_text(document),
                "lossless": stats.lossless,
                "cell_geometry": cell_geometry_payload(document),
                "encrypt_note": (
                    "Genom und Geometrie sind in der Datei verschlüsselt — "
                    "read_gpm und Suche funktionieren ohne Schlüssel nicht."
                ),
            }
        )

    return jsonify(
        {
            "gpm_version": GPM_VERSION,
            "filename": "document.gpm",
            "file_base64": base64.b64encode(plain_blob).decode("ascii"),
            "encrypted": False,
            "stats": _compile_stats_payload(stats),
            "header_preview": header_preview,
            "body_preview": body_preview,
            "reconstructed_text": reconstruct_text(document),
            "lossless": stats.lossless,
            "cell_geometry": cell_geometry_payload(document),
        }
    )


def handle_gpm_read(request: Request):
    try:
        blob = _read_request_bytes(request)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    cipher_keys = ""
    if request.files and request.files.get("file"):
        cipher_keys = (request.form.get("cipher_keys") or request.form.get("keys") or "").strip()
    else:
        payload = request.get_json(silent=True) or {}
        cipher_keys = (payload.get("cipher_keys") or payload.get("keys") or "").strip()

    if is_encrypted_gpm_blob(blob):
        try:
            meta = peek_gpc_meta(blob)
        except GpcFormatError as exc:
            return jsonify({"error": str(exc)}), 400
        if not cipher_keys:
            return jsonify(
                {
                    "error": (
                        "Verschlüsselte .gpm — ohne Schlüssel sind Genom und Geometrie nicht lesbar. "
                        "Schlüssel eingeben und erneut analysieren."
                    ),
                    "encrypted": True,
                    "needs_keys": True,
                    "cipher_mode": meta["mode"],
                    "file_bytes": meta["file_bytes"],
                }
            ), 400
        try:
            decrypted = decrypt_gpm_file(blob, keys_raw=cipher_keys)
            text = decrypted["text"]
            document, plain_blob, stats = compile_text(text)
            analysis = analyze_gpm(plain_blob)
        except (ValueError, GpcFormatError) as exc:
            return jsonify({"error": str(exc)}), 400
        except GpmFormatError as exc:
            return jsonify({"error": str(exc)}), 400

        payload = _analysis_payload(analysis, document=document, blob=plain_blob)
        payload["decrypted_from_encrypted"] = True
        payload["cipher_mode"] = decrypted.get("cipher_mode")
        payload["cipher_security"] = decrypted.get("security")
        return jsonify(
            {
                "analysis": payload,
                "file_base64": base64.b64encode(plain_blob).decode("ascii"),
                "encrypted_source": True,
                "source_file_base64": base64.b64encode(blob).decode("ascii"),
            }
        )

    try:
        analysis = analyze_gpm(blob)
        document = read_gpm(blob)
    except GpmFormatError as exc:
        if blob[:3] == b"GPC":
            return jsonify({"error": str(exc), "encrypted": True, "needs_keys": True}), 400
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "analysis": _analysis_payload(analysis, document=document, blob=blob),
            "file_base64": base64.b64encode(blob).decode("ascii"),
            "encrypted_source": False,
        }
    )


def _serialize_lcm_result(result: dict) -> dict:
    result["query_substance"] = _int_json(result["query_substance"])
    result["query2_substance"] = _int_json(result["query2_substance"])
    result["lcm_value"] = _int_json(result["lcm_value"])
    for row in result.get("matches", []):
        row["substance"] = _int_json(row["substance"])
    return result


def handle_gpm_search(request: Request):
    payload = request.get_json(silent=True) if request.is_json else None
    query = ""
    query2 = ""
    mode = "substance"

    try:
        if request.files and request.files.get("file"):
            blob = request.files["file"].read()
            query = (request.form.get("query") or "").strip()
            query2 = (request.form.get("query2") or "").strip()
            mode = (request.form.get("mode") or "substance").strip()
        elif payload:
            blob = base64.b64decode((payload.get("file_base64") or "").strip())
            query = (payload.get("query") or "").strip()
            query2 = (payload.get("query2") or "").strip()
            mode = (payload.get("mode") or "substance").strip()
        else:
            return jsonify({"error": "Datei und Suchwort erforderlich."}), 400

        if not blob:
            raise ValueError("Leere Datei.")
        if len(blob) > MAX_GPM_UPLOAD_BYTES:
            raise ValueError("Datei zu groß (max. 50 MB).")

        if is_encrypted_gpm_blob(blob):
            raise ValueError(
                "Verschlüsselte .gpm — Suche erst nach Entschlüsselung (Lesen mit Schlüssel)."
            )

        document = read_gpm(blob)
        if mode == "lcm":
            if not query or not query2:
                raise ValueError("Zwei Suchwörter für kgV-Filter erforderlich.")
            result = _serialize_lcm_result(search_by_lcm(document, query, query2))
        elif mode == "gcd":
            if not query:
                raise ValueError("Suchwort erforderlich.")
            result = search_by_gcd(document, query)
            result["query_substance"] = _int_json(result["query_substance"])
            for row in result.get("matches", []):
                row["substance"] = _int_json(row["substance"])
                row["gcd_value"] = _int_json(row["gcd_value"])
        else:
            if not query:
                raise ValueError("Suchwort erforderlich.")
            result = search_by_word(document, query)
            result["query_substance"] = _int_json(result["query_substance"])
            for row in result.get("header_matches", []):
                row["substance"] = _int_json(row["substance"])
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except GpmFormatError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"mode": mode, "result": result})


def register(app, repo) -> None:
    @app.route("/api/gpm/compile", methods=["POST"])
    def api_gpm_compile():
        return handle_gpm_compile(request)

    @app.route("/api/gpm/read", methods=["POST"])
    def api_gpm_read():
        return handle_gpm_read(request)

    @app.route("/api/gpm/search", methods=["POST"])
    def api_gpm_search():
        return handle_gpm_search(request)
