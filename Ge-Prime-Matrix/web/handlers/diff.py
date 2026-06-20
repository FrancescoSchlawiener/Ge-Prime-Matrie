"""POST /api/diff — arithmetische Differenz zweier Wörter."""

from flask import Flask, jsonify, request

from ge_prime.diff import classify_word_pair
from pipeline.normalize import DIFF_HELP, NORMALIZATION_HELP
from pipeline.process import process_token
from web.handlers.payloads import word_payload


def _diff_notes(p1, p2, diff_result: dict) -> list[str]:
    notes: list[str] = [DIFF_HELP["multiset_note"]]
    if diff_result.get("is_anagram"):
        notes.append(DIFF_HELP["example_anagram"])
    elif diff_result.get("is_subset_1_in_2") or diff_result.get("is_subset_2_in_1"):
        notes.append(DIFF_HELP["example_subset"])
    n1, n2 = p1.word_normalized, p2.word_normalized
    if n1 != n2 and ("ß" in n1) != ("ß" in n2):
        notes.append(NORMALIZATION_HELP["eszett_compare"])
    return notes


def register(app: Flask, repo) -> None:
    @app.route("/api/diff", methods=["POST"])
    def api_diff():
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

        diff_result = classify_word_pair(
            p1.substance,
            p2.substance,
            p1.perm_index,
            p2.perm_index,
            norm_len1=len(p1.word_normalized),
            norm_len2=len(p2.word_normalized),
        )
        notes = _diff_notes(p1, p2, diff_result)

        return jsonify(
            {
                "word1": word_payload(p1),
                "word2": word_payload(p2),
                "diff": {**diff_result, "notes": notes},
            }
        )
