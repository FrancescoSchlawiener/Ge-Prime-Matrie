#!/usr/bin/env python3
"""Rename Erklärungen markdown files and update internal links."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "ui-text" / "content" / "erklaerungen"

RENAME: dict[str, str] = {
    "25-ni-ganzzahl": "04-ni-ganzzahl",
    "26-di-dezimal": "05-di-dezimal",
    "27-hi-hybrid-identitaet": "06-hi-hybrid-identitaet",
    "04-normalisierung": "07-normalisierung",
    "05-profile": "08-profile",
    "06-ggt-kgv": "09-ggt-kgv",
    "07-wortpaar-diff": "10-wortpaar-diff",
    "08-wortpaar-anagramm": "11-wortpaar-anagramm",
    "08-gaps-dokument": "12-gaps-dokument",
    "09-gpm-binary": "13-gpm-binary",
    "10-case-explicit": "14-case-explicit",
    "11-registry": "15-registry",
    "12-tokens": "16-tokens",
    "13-payload-kinds": "17-payload-kinds",
    "14-blocks": "18-blocks",
    "15-cells": "19-cells",
    "16-i-curve": "20-i-curve",
    "17-corpus": "21-corpus",
    "18-redundanz": "22-redundanz",
    "19-hybrid-fences": "23-hybrid-fences",
    "20-code-blocks": "24-code-blocks",
    "21-cipher": "25-cipher",
    "22-spectroscope": "26-spectroscope",
    "23-inference-trace": "27-inference-trace",
    "24-cipher-gpc": "28-cipher-gpc",
}

# Phase 1: temp names
for old, new in RENAME.items():
    src = ROOT / f"{old}.md"
    if src.exists():
        src.rename(ROOT / f"__tmp__{new}.md")

# Phase 2: final names
for p in ROOT.glob("__tmp__*.md"):
    p.rename(ROOT / p.name.replace("__tmp__", ""))

# Update links in all md files
link_map = {f"/erklaerungen/{k}": f"/erklaerungen/{v}" for k, v in RENAME.items()}

SECTIONS_TO_STRIP = [
    re.compile(r"\n## Workbench\n[\s\S]*?(?=\n## |\n---|\Z)", re.MULTILINE),
    re.compile(r"\n## Beispiel\n[\s\S]*?(?=\n## |\n---|\Z)", re.MULTILINE),
    re.compile(r"\n\*\*Nächstes Kapitel:\*\*[^\n]*\n?", re.MULTILINE),
]

for path in sorted(ROOT.glob("*.md")):
    text = path.read_text(encoding="utf-8")
    for old, new in link_map.items():
        text = text.replace(old, new)
    for pat in SECTIONS_TO_STRIP:
        text = pat.sub("\n", text)
    if "## Typische Fehler" not in text and "## Verknüpfungen" in text:
        text = text.replace(
            "## Verknüpfungen",
            "## Typische Fehler\n\n- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.\n- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.\n\n## Verknüpfungen",
            1,
        )
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

print(f"Done. {len(list(ROOT.glob('*.md')))} files in {ROOT}")
