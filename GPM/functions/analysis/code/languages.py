"""Sprach-Spezifikationen für C(I) Code-Parsing."""

from __future__ import annotations

import os
from dataclasses import dataclass

KEYWORDS_PY = frozenset(
    {
        "def",
        "class",
        "if",
        "elif",
        "else",
        "for",
        "while",
        "return",
        "import",
        "from",
        "pass",
        "break",
        "continue",
        "try",
        "except",
        "finally",
        "with",
        "as",
        "raise",
        "yield",
        "lambda",
        "async",
        "await",
        "global",
        "nonlocal",
        "assert",
        "del",
        "in",
        "is",
        "not",
        "and",
        "or",
    }
)

KEYWORDS_JS = frozenset(
    {
        "function",
        "class",
        "if",
        "else",
        "for",
        "while",
        "do",
        "switch",
        "return",
        "import",
        "export",
        "let",
        "var",
        "const",
        "new",
        "try",
        "catch",
        "finally",
        "throw",
        "typeof",
        "instanceof",
        "default",
        "case",
        "break",
        "continue",
        "async",
        "await",
        "this",
        "super",
        "delete",
        "void",
        "in",
        "of",
        "from",
        "as",
    }
)


@dataclass(frozen=True)
class LanguageSpec:
    id: str
    name: str
    extensions: tuple[str, ...]
    block_style: str  # brace | indent | tag | keyword | flat
    comment_style: str  # c | hash | sql | none
    keywords: frozenset[str] = frozenset()
    block_pairs: tuple[tuple[str, str], ...] = ()


LANGUAGES: dict[str, LanguageSpec] = {
    "py": LanguageSpec(
        "py",
        "Python",
        (".py", ".pyw"),
        "indent",
        "hash",
        KEYWORDS_PY,
    ),
    "js": LanguageSpec(
        "js",
        "JavaScript/TS",
        (".js", ".ts", ".jsx", ".tsx"),
        "brace",
        "c",
        KEYWORDS_JS,
    ),
    "html": LanguageSpec(
        "html",
        "HTML",
        (".html", ".htm"),
        "tag",
        "none",
        frozenset(),
    ),
}

VOID_HTML_TAGS = frozenset(
    {"BR", "IMG", "INPUT", "HR", "META", "LINK", "AREA", "BASE", "COL", "EMBED", "SOURCE", "TRACK", "WBR"}
)

_EXT_TO_LANG: dict[str, str] = {}
for _spec in LANGUAGES.values():
    for _ext in _spec.extensions:
        _EXT_TO_LANG[_ext.lower()] = _spec.id


def language_for_id(language_id: str) -> LanguageSpec:
    if language_id not in LANGUAGES:
        raise ValueError(f"Unbekannte Sprache: {language_id}")
    return LANGUAGES[language_id]


def language_for_extension(path: str) -> LanguageSpec | None:
    _, ext = os.path.splitext(path)
    lang_id = _EXT_TO_LANG.get(ext.lower())
    if lang_id is None:
        return None
    return LANGUAGES[lang_id]
