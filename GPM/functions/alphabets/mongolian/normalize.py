"""Mongolian Normalisierung — Positionsform→Basis, FVS-Strip, Mn-Strip, Whitelist."""

from __future__ import annotations

import unicodedata

from alphabets.mongolian.map import CHAR_MONGOLIAN_SET, _MONGOLIAN_SYMBOLS
from alphabets.unicode_utils import assert_no_surrogates, iter_codepoints

_SKIP: frozenset[str] = frozenset({
    "\u180B", "\u180C", "\u180D",  # FVS1–3
    "\u180E",  # MVS
    "\u200C", "\u200D",  # ZWNJ/ZWJ
})

_FORM_SUFFIXES: tuple[str, ...] = (
    " ISOLATED FORM",
    " INITIAL FORM",
    " MEDIAL FORM",
    " FINAL FORM",
    " Suffix FORM",
)

_BASE_BY_STEM: dict[str, str] = {}
for _base in _MONGOLIAN_SYMBOLS:
    _name = unicodedata.name(_base)
    if _name.startswith("MONGOLIAN LETTER "):
        _BASE_BY_STEM[_name[18:]] = _base


def _mongolian_stem(name: str) -> str | None:
    if not name.startswith("MONGOLIAN LETTER "):
        return None
    stem = name[18:]
    for suffix in _FORM_SUFFIXES:
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def _positional_to_base(ch: str) -> str | None:
    try:
        name = unicodedata.name(ch)
    except ValueError:
        return None
    stem = _mongolian_stem(name)
    if stem is None:
        return None
    return _BASE_BY_STEM.get(stem)


def normalize_mongolian(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    assert_no_surrogates(text)
    result: list[str] = []
    for ch in iter_codepoints(text):
        if ch in _SKIP:
            continue
        if unicodedata.category(ch) == "Mn":
            continue
        if ch in CHAR_MONGOLIAN_SET:
            result.append(ch)
            continue
        base = _positional_to_base(ch)
        if base is not None and base in CHAR_MONGOLIAN_SET:
            result.append(base)
    return "".join(result)
