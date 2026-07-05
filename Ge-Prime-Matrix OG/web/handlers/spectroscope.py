"""POST /api/spectroscope — Token-Sliding-Window + Kreuzfeuer."""

from __future__ import annotations

from flask import Flask, jsonify, request

from ge_prime.payload_codec import compress_spectro_matches
from ge_prime.spectroscope import spectroscope_analyze, spectroscope_from_text
from gpm.cipher_wrap import is_encrypted_gpm_blob
from gpm.compiler import compile_text
from gpm.format import GpmFormatError, read_gpm
from pipeline.normalize import normalize_text_nfc
from web.handlers.gpm import MAX_GPM_UPLOAD_BYTES, _decode_gpm_blob


def register(app: Flask, repo) -> None:
    @app.route("/api/spectroscope", methods=["POST"])
    def api_spectroscope():
        data = request.get_json(silent=True) or {}
        modes = data.get("modes")
        if isinstance(modes, str):
            modes = [m.strip() for m in modes.split(",") if m.strip()]
        source = (data.get("source") or "text").strip().lower()
        try:
            if source == "gpm":
                blob = _decode_gpm_blob(data)
                if len(blob) > MAX_GPM_UPLOAD_BYTES:
                    raise ValueError("Datei zu groß (max. 50 MB).")
                if is_encrypted_gpm_blob(blob):
                    raise ValueError("Verschlüsselte .gpm — zuerst entschlüsseln.")
                document = read_gpm(blob)
                token_start = int(data.get("token_start", 0))
                token_end = int(data.get("token_end", len(document.tokens)))
                result = spectroscope_analyze(
                    document,
                    token_start=token_start,
                    token_end=token_end,
                    modes=modes,
                )
            else:
                text = normalize_text_nfc((data.get("text") or "").strip())
                if not text:
                    raise ValueError("text erforderlich.")
                selection_start = int(data.get("selection_start", 0))
                selection_end = int(data.get("selection_end", len(text)))
                result = spectroscope_from_text(
                    text,
                    selection_start=selection_start,
                    selection_end=selection_end,
                    modes=modes,
                )
            result["matches"] = compress_spectro_matches(result.get("matches") or [])
            return jsonify(result)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except GpmFormatError as exc:
            return jsonify({"error": str(exc)}), 400
