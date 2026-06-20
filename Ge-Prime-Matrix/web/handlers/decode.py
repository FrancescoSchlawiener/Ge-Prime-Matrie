"""POST /api/decode — S und I → Wort."""

from flask import Flask, jsonify, request

from web.handlers._steps import build_decode_steps


def register(app: Flask, repo) -> None:
    @app.route("/api/decode", methods=["POST"])
    def api_decode():
        data = request.get_json(silent=True) or {}
        substance_raw = data.get("substance")
        index_raw = data.get("perm_index")

        try:
            substance = int(str(substance_raw).strip().replace(".", "").replace(",", ""))
            perm_index = int(str(index_raw).strip().replace(".", "").replace(",", ""))
        except (TypeError, ValueError, AttributeError):
            return jsonify({"error": "S und I müssen ganze Zahlen sein."}), 400

        if substance < 1 or perm_index < 1:
            return jsonify({"error": "S und I müssen größer als 0 sein."}), 400

        result = build_decode_steps(substance, perm_index)
        if result is None:
            return jsonify({"error": "S und I passen nicht zu einem gültigen Wort."}), 400

        return jsonify(result)
