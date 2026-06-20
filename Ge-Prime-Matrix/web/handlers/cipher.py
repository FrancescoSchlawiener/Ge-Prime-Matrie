"""POST /api/cipher/* — S(I)-Verschlüsselung."""

from flask import Flask, jsonify, request

from ge_prime.cipher import VALID_MODES, decrypt_ciphertext, encrypt_text


def register(app: Flask, repo) -> None:
    @app.route("/api/cipher/encrypt", methods=["POST"])
    def api_cipher_encrypt():
        data = request.get_json(silent=True) or {}
        text = (data.get("text") or "").strip()
        mode = (data.get("mode") or "word").strip().lower()
        keys = data.get("keys") if data.get("keys") is not None else data.get("key", "")
        if not text:
            return jsonify({"error": "Text erforderlich."}), 400
        if mode not in VALID_MODES:
            return jsonify({"error": f"Modus muss einer von {', '.join(VALID_MODES)} sein."}), 400
        try:
            return jsonify(encrypt_text(text, mode=mode, keys_raw=keys))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.route("/api/cipher/decrypt", methods=["POST"])
    def api_cipher_decrypt():
        data = request.get_json(silent=True) or {}
        ciphertext = (data.get("ciphertext") or "").strip()
        keys = data.get("keys") if data.get("keys") is not None else data.get("key", "")
        if not ciphertext:
            return jsonify({"error": "Chiffretext erforderlich."}), 400
        try:
            return jsonify(decrypt_ciphertext(ciphertext, keys_raw=keys))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
