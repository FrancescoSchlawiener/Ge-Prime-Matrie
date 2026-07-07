"""Code-Kanonisierung — compile_source + GPM Code-Wire (library-first)."""

from __future__ import annotations

import base64
from typing import Any

from alphabets import AlphabetProfile
from analysis.blocks.registry import DocumentRegistry
from analysis.code.canonicalize import normalize_for_tensorraum
from analysis.code.compile import compile_source
from analysis.code.decompile import reconstruct_source
from analysis.code.languages import LANGUAGES, IGNORED_SUFFIXES, language_for_extension, language_for_id
from analysis.code.manifest import language_manifest
from analysis.code.wire import encode_code_module


def languages_payload() -> dict[str, Any]:
    langs = []
    for spec in LANGUAGES.values():
        langs.append(
            {
                "id": spec.id,
                "name": spec.name,
                "extensions": list(spec.extensions),
                "block_style": spec.block_style,
                "comment_style": spec.comment_style,
                "block_pairs": [list(p) for p in spec.block_pairs],
                "case_insensitive": spec.case_insensitive,
            }
        )
    langs.sort(key=lambda x: x["id"])
    return {"languages": langs, "ignored_suffixes": sorted(IGNORED_SUFFIXES)}


def canonicalize_for_code(
    source: str,
    filename: str,
    *,
    profile: AlphabetProfile | str = AlphabetProfile.OG,
) -> dict[str, Any]:
    prof = profile if isinstance(profile, AlphabetProfile) else AlphabetProfile(profile)
    spec = language_for_extension(filename)
    if spec is None:
        raise ValueError(f"Keine Sprache für Datei: {filename!r}")
    language_id = spec.id
    language_for_id(language_id)
    manifest = language_manifest(source, filename)
    reg = DocumentRegistry(profile=prof)
    normalized = normalize_for_tensorraum(source, language_id)
    module = compile_source(normalized, language_id, reg)
    reconstructed = reconstruct_source(module, reg)
    roundtrip_ok = reconstructed == normalized
    wire = encode_code_module(module, reg)
    return {
        "filename": filename,
        "language_id": language_id,
        "language_name": spec.name,
        "language_manifest": manifest,
        "normalized_code": normalized,
        "reconstructed": reconstructed,
        "roundtrip_ok": roundtrip_ok,
        "trailing_whitespace": module.meta.get("trailing_whitespace", ""),
        "wire_b64": base64.b64encode(wire).decode("ascii"),
    }


# Deprecated alias — Tensorraum war Toy-Name, Logik lebt hier.
canonicalize_for_tensorraum = canonicalize_for_code
