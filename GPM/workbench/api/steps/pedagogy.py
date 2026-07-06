"""OG-Pädagogik-Schritte für Encode/Decode — Port von web/handlers/_steps.py."""

from __future__ import annotations

from collections import Counter

from alphabets.lex import lex_order_for_profile
from alphabets.normalize import is_valid_substrate, prepare_substrate
from alphabets.profiles import AlphabetProfile
from alphabets.registry import prime_map_for_profile
from api.cache.word_compile import compile_word_cached, word_entry_from_cache
from api.helpers.encode_words import MAX_ENCODE_WORDS, extract_encode_words, letters_only
from api.schemas.common import Step
from gpm_types.si.codec import decode_si, encode_si_with_trace
from gpm_types.si.substance import ingredients_for_profile
from perm.multiset import calc_total_perms

_NORMALIZATION_HELP = {
    "letters": "Nur Buchstaben bleiben erhalten; Ziffern und Satzzeichen werden ignoriert.",
    "umlauts": "Umlaute werden in AE/OE/UE aufgelöst und großgeschrieben.",
    "eszett": "ß bleibt erhalten und wird nicht in SS umgewandelt.",
    "decode_result": "Das rekonstruierte Wort entspricht der normalisierten Form.",
    "original": "Die Originalschreibweise kann sich durch Normalisierung unterscheiden.",
}


def _eszett_lines(cleaned: str, normalized: str) -> list[str]:
    if "ß" in cleaned or "ß" in normalized:
        return ["ß bleibt als eigenes Symbol erhalten."]
    return []


def _og_step_to_api(step: dict, index: int, *, prefix: str) -> Step:
    return Step(
        id=f"{prefix}_{index}",
        title=step["title"],
        detail=step["detail"],
        lines=list(step.get("lines") or []),
        formula=step.get("formula"),
        extra=step.get("extra"),
        values={},
    )


def build_encode_steps(token: str, profile: AlphabetProfile | str) -> dict | None:
    cleaned = letters_only(token)
    if not cleaned:
        return None

    if isinstance(profile, str):
        profile = AlphabetProfile(profile)

    try:
        seq = prepare_substrate(cleaned, profile)
    except ValueError:
        return None

    if not is_valid_substrate(seq, profile):
        return None

    steps: list[dict] = []
    norm_lines = [f"Eingabe: {cleaned}", f"Normalisiert: {seq}"]
    norm_lines.extend(_eszett_lines(cleaned, seq))

    if cleaned != seq:
        steps.append(
            {
                "title": "1. Normalisierung",
                "detail": f"{_NORMALIZATION_HELP['umlauts']} {_NORMALIZATION_HELP['eszett']}",
                "lines": norm_lines,
            }
        )
    elif "ß" in seq:
        steps.append(
            {
                "title": "1. Normalisierung",
                "detail": _NORMALIZATION_HELP["eszett"],
                "lines": norm_lines,
            }
        )
    else:
        steps.append(
            {
                "title": "1. Normalisierung",
                "detail": _NORMALIZATION_HELP["letters"],
                "lines": norm_lines if len(norm_lines) > 1 else [f"Form: {seq}"],
            }
        )

    prime_map = prime_map_for_profile(profile)
    factors: list[str] = []
    product_parts: list[str] = []
    running = 1
    for char in seq:
        prime = prime_map[char]
        running *= prime
        factors.append(f"{char}→{prime}")
        product_parts.append(str(prime))

    steps.append(
        {
            "title": "2. Substanz S — Primzahlprodukt",
            "detail": (
                "Jeder Buchstabe wird zu seiner festen Primzahl. "
                "Alle Primzahlen werden multipliziert. Die Reihenfolge spielt keine Rolle."
            ),
            "lines": factors,
            "formula": " × ".join(product_parts) + f" = {running}",
        }
    )

    substance, perm_index, _trace = encode_si_with_trace(cleaned, profile)
    total_perms = calc_total_perms(Counter(seq))
    decoded_check = decode_si(substance, perm_index, profile)

    steps.append(
        {
            "title": "3. Index I — Permutations-Rang",
            "detail": (
                f"Für die Buchstaben-Menge gibt es {total_perms:,} mögliche Anordnungen "
                "(lexikographisch sortiert). I ist die exakte Position dieses Wortes."
            ),
            "lines": [
                f"Permutations-Raum: N = {total_perms:,}",
                f"Index I = {perm_index:,}",
            ],
        }
    )

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

    api_steps = [_og_step_to_api(s, i, prefix="encode") for i, s in enumerate(steps, start=1)]

    cache_entry, _cache_hit = compile_word_cached(cleaned, profile)
    cached = word_entry_from_cache(cache_entry)

    return {
        "original": cleaned,
        "normalized": cached["normalized"],
        "display": cleaned,
        "word": cleaned,
        "substance": cached["substance"],
        "index": cached["perm_index"],
        "perm_index": cached["perm_index"],
        "content_hash": cached["content_hash"],
        "decoded": decoded_check,
        "steps": api_steps,
        "og_steps": steps,
    }


def build_encode_batch(
    text: str,
    profile: AlphabetProfile | str,
    *,
    max_words: int = MAX_ENCODE_WORDS,
) -> dict:
    tokens, skipped, truncated = extract_encode_words(text, max_words=max_words)
    results: list[dict] = []
    failed: list[str] = []

    for token in tokens:
        entry = build_encode_steps(token, profile)
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


def build_decode_steps(
    substance: int,
    perm_index: int,
    profile: AlphabetProfile | str,
) -> dict | None:
    if substance < 1 or perm_index < 1:
        return None

    if isinstance(profile, str):
        profile = AlphabetProfile(profile)

    try:
        ingredients = ingredients_for_profile(substance, profile)
    except (ValueError, TypeError):
        return None

    if not ingredients:
        return None

    total_len = sum(ingredients.values())
    total_perms = calc_total_perms(ingredients.copy())

    if perm_index < 1 or perm_index > total_perms:
        return None

    prime_map = prime_map_for_profile(profile)
    steps: list[dict] = []

    factor_lines = []
    for char in sorted(ingredients.keys()):
        prime = prime_map[char]
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

    decoded = decode_si(substance, perm_index, profile)
    rebuild_lines: list[str] = []
    counts = ingredients.copy()
    index = perm_index
    position = 1
    lex = lex_order_for_profile(profile)

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
                _NORMALIZATION_HELP["decode_result"]
                + " "
                + _NORMALIZATION_HELP["original"]
            ),
            "lines": [f"Rekonstruiert: {decoded}"],
        }
    )

    api_steps = [_og_step_to_api(s, i, prefix="decode") for i, s in enumerate(steps, start=1)]

    cache_entry, _cache_hit = compile_word_cached(decoded, profile)
    cached = word_entry_from_cache(cache_entry)

    return {
        "substance": cached["substance"],
        "index": cached["perm_index"],
        "perm_index": cached["perm_index"],
        "ingredients": dict(ingredients),
        "total_permutations": total_perms,
        "word": decoded,
        "normalized": cached["normalized"],
        "content_hash": cached["content_hash"],
        "steps": api_steps,
        "og_steps": steps,
    }


def map_encode_steps_from_entry(entry: dict) -> list[Step]:
    return list(entry.get("steps") or [])


def map_decode_steps_from_entry(entry: dict) -> list[Step]:
    return list(entry.get("steps") or [])
