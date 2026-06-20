"""POST /api/hierarchy/search — kgV-Pruning und Brücken-Queries."""

from __future__ import annotations

from flask import Flask, jsonify, request

from ge_prime.hierarchy_search import hierarchy_search, hierarchy_search_from_blob
from gpm.cipher_wrap import is_encrypted_gpm_blob
from gpm.compiler import compile_text
from gpm.format import GpmFormatError
from web.handlers.gpm import MAX_GPM_UPLOAD_BYTES, _decode_gpm_blob


def register(app: Flask, repo) -> None:
    @app.route("/api/hierarchy/search", methods=["POST"])
    def api_hierarchy_search():
        data = request.get_json(silent=True) or {}
        pattern_text = (data.get("pattern_text") or data.get("pattern") or "").strip()
        if not pattern_text:
            return jsonify({"error": "pattern_text erforderlich."}), 400
        level = (data.get("level") or "paragraph").strip().lower()
        zoom = bool(data.get("zoom", True))
        query = (data.get("query") or "").strip() or None
        source = (data.get("source") or "text").strip().lower()
        try:
            if source == "gpm":
                blob = _decode_gpm_blob(data)
                if len(blob) > MAX_GPM_UPLOAD_BYTES:
                    raise ValueError("Datei zu groß (max. 50 MB).")
                if is_encrypted_gpm_blob(blob):
                    raise ValueError("Verschlüsselte .gpm — zuerst entschlüsseln.")
                result = hierarchy_search_from_blob(
                    blob,
                    pattern_text=pattern_text,
                    level=level,
                    zoom=zoom,
                    query=query,
                )
            else:
                text = (data.get("text") or "").strip()
                if not text:
                    raise ValueError("text oder .gpm erforderlich.")
                document, _, _ = compile_text(text)
                result = hierarchy_search(
                    document,
                    pattern_text=pattern_text,
                    level=level,
                    zoom=zoom,
                    query=query,
                )
            return jsonify(result)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except GpmFormatError as exc:
            return jsonify({"error": str(exc)}), 400
