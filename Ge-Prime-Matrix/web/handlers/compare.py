"""POST /api/compare — ggT und kgV zweier Wörter."""

from flask import Flask, jsonify, request

from ge_prime.compare import compare_substances
from ge_prime.core import PRIME_MAP
from pipeline.normalize import NORMALIZATION_HELP
from pipeline.process import process_token
from web.handlers.payloads import word_payload


def _compare_notes(p1, p2) -> list[str]:
    notes: list[str] = []
    n1, n2 = p1.word_normalized, p2.word_normalized
    eszett_in_1 = "ß" in n1
    eszett_in_2 = "ß" in n2

    if n1 != n2 and eszett_in_1 != eszett_in_2:
        notes.append(NORMALIZATION_HELP["eszett_compare"])
    elif eszett_in_1 and eszett_in_2:
        notes.append(
            f"Beide Wörter enthalten ß (Primzahl {PRIME_MAP['ß']}) — gemeinsame Buchstaben im ggT "
            f"können ß und S getrennt ausweisen."
        )
    if n1 == n2 and p1.word_original != p2.word_original:
        notes.append(
            "Gleiche Substanz S — unterschiedliche Originalschreibweise (z. B. Umlaut vs. AE) "
            "ändert den ggT nicht."
        )
    if not notes:
        notes.append(NORMALIZATION_HELP["compare"])
    return notes


def register(app: Flask, repo) -> None:
    @app.route("/api/compare", methods=["POST"])
    def api_compare():
        data = request.get_json(silent=True) or {}
        w1 = (data.get("word1") or "").strip()
        w2 = (data.get("word2") or "").strip()

        if not w1 or not w2:
            return jsonify({"error": "Zwei Wörter erforderlich."}), 400

        p1 = process_token(w1, source="web")
        p2 = process_token(w2, source="web")
        if p1 is None:
            return jsonify({"error": f"Wort 1 ungültig: {w1}"}), 400
        if p2 is None:
            return jsonify({"error": f"Wort 2 ungültig: {w2}"}), 400

        cmp_result = compare_substances(p1.substance, p2.substance)
        notes = _compare_notes(p1, p2)

        return jsonify(
            {
                "word1": word_payload(p1),
                "word2": word_payload(p2),
                "comparison": {
                    "gcd_value": cmp_result["gcd_value"],
                    "lcm_value": cmp_result["lcm_value"],
                    "shared_letters": cmp_result["shared_letters"],
                    "union_letters": cmp_result["union_letters"],
                    "unique_to_first": cmp_result["unique_to_first"],
                    "unique_to_second": cmp_result["unique_to_second"],
                    "similarity_ratio": cmp_result["similarity_ratio"],
                    "notes": notes,
                },
            }
        )
