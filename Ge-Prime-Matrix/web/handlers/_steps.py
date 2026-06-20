"""Schritt-für-Schritt-Erklärungen für Encode und Decode (Web-UI)."""

from collections import Counter

from ge_prime.core import PRIME_MAP, calc_total_perms
from ge_prime.decode import decode_word, get_ingredients
from ge_prime.encode import encode_word, get_index, get_substance
from pipeline.normalize import NORMALIZATION_HELP, denormalize_word, eszett_step_lines, normalize_word
from pipeline.tokenize import MAX_ENCODE_WORDS, extract_encode_words, letters_only
from pipeline.validate import is_valid_normalized


def build_encode_steps(token: str) -> dict | None:
    cleaned = letters_only(token)
    if not cleaned:
        return None

    normalized = normalize_word(cleaned)
    if not is_valid_normalized(normalized):
        return None

    steps: list[dict] = []

    norm_lines = [f"Eingabe: {cleaned}", f"Normalisiert: {normalized}"]
    norm_lines.extend(eszett_step_lines(cleaned, normalized))

    if cleaned != normalized:
        steps.append(
            {
                "title": "1. Normalisierung",
                "detail": f"{NORMALIZATION_HELP['umlauts']}. {NORMALIZATION_HELP['eszett']}",
                "lines": norm_lines,
            }
        )
    elif "ß" in normalized:
        steps.append(
            {
                "title": "1. Normalisierung",
                "detail": NORMALIZATION_HELP["eszett"],
                "lines": norm_lines,
            }
        )
    else:
        steps.append(
            {
                "title": "1. Normalisierung",
                "detail": NORMALIZATION_HELP["letters"],
                "lines": norm_lines if len(norm_lines) > 1 else [f"Form: {normalized}"],
            }
        )

    factors = []
    product_parts = []
    running = 1
    for char in normalized:
        prime = PRIME_MAP[char]
        running *= prime
        factors.append(f"{char}→{prime}")
        product_parts.append(str(prime))

    steps.append(
        {
            "title": "2. Substanz S — Primzahlprodukt",
            "detail": "Jeder Buchstabe wird zu seiner festen Primzahl. Alle Primzahlen werden multipliziert. Die Reihenfolge spielt keine Rolle.",
            "lines": factors,
            "formula": " × ".join(product_parts) + f" = {running}",
        }
    )

    substance = get_substance(normalized)
    perm_index = get_index(normalized)
    total_perms = calc_total_perms(Counter(normalized))

    steps.append(
        {
            "title": "3. Index I — Permutations-Rang",
            "detail": (
                f"Für die Buchstaben-Menge gibt es {total_perms:,} mögliche Anordnungen "
                "(lexikographisch sortiert). I ist die exakte Position dieses Wortes."
            ),
            "lines": [f"Permutations-Raum: N = {total_perms:,}", f"Index I = {perm_index:,}"],
        }
    )

    decoded_check = decode_word(substance, perm_index)

    steps.append(
        {
            "title": "4. Datenobjekt S(I)",
            "detail": "Substanz und Index zusammen speichern die Anordnung verlustfrei.",
            "lines": [
                f"S = {substance:,}",
                f"I = {perm_index:,}",
                f"Roundtrip-Check: {decoded_check}",
            ],
        }
    )

    return {
        "original": cleaned,
        "normalized": normalized,
        "display": denormalize_word(normalized, cleaned),
        "substance": substance,
        "perm_index": perm_index,
        "decoded": decoded_check,
        "steps": steps,
    }


def build_encode_batch(text: str, *, max_words: int = MAX_ENCODE_WORDS) -> dict:
    tokens, skipped, truncated = extract_encode_words(text, max_words=max_words)
    results: list[dict] = []
    failed: list[str] = []

    for token in tokens:
        entry = build_encode_steps(token)
        if entry is None:
            failed.append(token)
        else:
            results.append(entry)

    return {
        "words": results,
        "count": len(results),
        "skipped": skipped,
        "failed": failed,
        "truncated": truncated,
        "max_words": max_words,
    }


def build_decode_steps(substance: int, perm_index: int) -> dict | None:
    if substance < 1 or perm_index < 1:
        return None

    try:
        ingredients = get_ingredients(substance)
    except (ValueError, TypeError):
        return None

    if not ingredients:
        return None

    total_len = sum(ingredients.values())
    total_perms = calc_total_perms(ingredients.copy())

    if perm_index < 1 or perm_index > total_perms:
        return None

    steps: list[dict] = []

    factor_lines = []
    for char in sorted(ingredients.keys()):
        prime = PRIME_MAP[char]
        count = ingredients[char]
        factor_lines.append(f"{char} × {count}  (Primzahl {prime})")

    multiset = ", ".join(f"{c}×{n}" for c, n in sorted(ingredients.items()))
    steps.append(
        {
            "title": "1. Faktorisierung von S",
            "detail": "S wird in seine Primfaktoren zerlegt. Jeder Faktor entspricht einem Buchstaben.",
            "lines": factor_lines or ["Keine gültigen Primfaktoren gefunden."],
            "formula": f"Zutatenliste: {{{multiset}}}",
        }
    )

    steps.append(
        {
            "title": "2. Permutations-Raum öffnen",
            "detail": "Aus der Zutatenliste folgt die Anzahl aller möglichen Anordnungen.",
            "lines": [
                f"Wortlänge L = {total_len}",
                f"N = {total_perms:,} Permutationen",
                f"Gesuchter Index I = {perm_index:,}",
            ],
        }
    )

    decoded = decode_word(substance, perm_index)
    rebuild_lines = []
    counts = ingredients.copy()
    index = perm_index
    position = 1

    for _ in range(total_len):
        for char in sorted(counts.keys()):
            counts[char] -= 1
            block = calc_total_perms(counts)
            if index > block:
                index -= block
                counts[char] += 1
            else:
                rebuild_lines.append(
                    f"Position {position}: '{char}'  (Blockgröße {block:,}, Rest-Index {index:,})"
                )
                if counts[char] == 0:
                    del counts[char]
                position += 1
                break

    steps.append(
        {
            "title": "3. Intervallschachtelung — Wort rekonstruieren",
            "detail": "Position für Position wird der Index durch den Entscheidungsbaum geführt.",
            "lines": rebuild_lines[:12],
            "extra": f"... {len(rebuild_lines)} Positionen gesamt" if len(rebuild_lines) > 12 else None,
        }
    )

    steps.append(
        {
            "title": "4. Ergebnis",
            "detail": (
                NORMALIZATION_HELP["decode_result"]
                + " "
                + NORMALIZATION_HELP["original"]
            ),
            "lines": [f"Rekonstruiert: {decoded}"],
        }
    )

    return {
        "substance": substance,
        "perm_index": perm_index,
        "ingredients": dict(ingredients),
        "total_permutations": total_perms,
        "word": decoded,
        "steps": steps,
    }
