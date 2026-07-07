"""Sprach-Manifest pro Datei — Primary + eingebettete Sprachen (HTML script/style)."""

from __future__ import annotations

import re

from analysis.code.languages import language_for_extension, language_for_id

_HTML_EMBEDDED: dict[str, str] = {"script": "js", "style": "css"}
_EMBEDDED_OPEN_RE = re.compile(r"<(script|style)\b", re.IGNORECASE)
_EMBEDDABLE_PRIMARIES = frozenset({"html", "xml"})


def scan_embedded_languages(source: str, primary: str) -> list[str]:
    """Leichtgewichtiger Scan — gleiche Tabelle wie tokenize_html rawtext."""
    if primary not in _EMBEDDABLE_PRIMARIES:
        return []
    found: set[str] = set()
    for m in _EMBEDDED_OPEN_RE.finditer(source):
        lang = _HTML_EMBEDDED.get(m.group(1).lower())
        if lang:
            found.add(lang)
    return sorted(found)


def language_manifest(source: str, filename: str) -> dict[str, str | list[str]]:
    spec = language_for_extension(filename)
    if spec is None:
        raise ValueError(f"Keine Sprache für Datei: {filename!r}")
    primary = spec.id
    language_for_id(primary)
    embedded = scan_embedded_languages(source, primary)
    all_langs = sorted({primary, *embedded})
    return {"primary": primary, "embedded": embedded, "all": all_langs}
