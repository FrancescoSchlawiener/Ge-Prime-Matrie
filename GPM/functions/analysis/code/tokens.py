"""Code-Token-Zwischenrepräsentation — nl/col_prefix/EOF-Invariante."""

from __future__ import annotations

from dataclasses import dataclass, field

from analysis.code.envelope import BlockEnvelope, CloseRole

_FORMATTING_CHARS = frozenset("\n\r\t ")


def assert_formatting_chars_only(text: str) -> None:
    for ch in text:
        if ch not in _FORMATTING_CHARS:
            raise ValueError(f"Ungültiges Formatierungszeichen in Gap: {ch!r}")


def assert_horizontal_whitespace_only(text: str) -> None:
    for ch in text:
        if ch not in (" ", "\t"):
            raise ValueError(f"col_prefix darf nur Space/Tab enthalten: {ch!r}")


def split_leading_gap(source: str, start: int, end: int) -> tuple[int, str]:
    gap = source[start:end]
    nl = gap.count("\n")
    if "\n" in gap:
        col_prefix = gap.rsplit("\n", 1)[1]
    else:
        col_prefix = gap
    assert_formatting_chars_only(gap)
    assert_horizontal_whitespace_only(col_prefix)
    return nl, col_prefix


def extract_trailing_whitespace(source: str, last_end: int) -> str:
    trail = source[last_end:]
    assert_formatting_chars_only(trail)
    return trail


@dataclass
class CodeToken:
    nl: int = 0
    col_prefix: str = ""
    type: str | None = None
    value: str | None = None
    block: str | None = None
    visual_style: str | None = None
    envelope: BlockEnvelope | None = None
    close_role: CloseRole | None = None
    open_syntax: str | None = None
    close_syntax: str | None = None
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d: dict = {"nl": self.nl, "col_prefix": self.col_prefix}
        if self.block:
            d["block"] = self.block
        if self.type:
            d["type"] = self.type
        if self.value is not None:
            d["value"] = self.value
        if self.visual_style:
            d["visual_style"] = self.visual_style
        if self.open_syntax:
            d["open_syntax"] = self.open_syntax
        if self.close_syntax:
            d["close_syntax"] = self.close_syntax
        return d


@dataclass
class TokenizeResult:
    tokens: list[CodeToken]
    trailing_whitespace: str = ""

    def token_dicts(self) -> list[dict]:
        return [t.to_dict() for t in self.tokens]


def tokenize_results_equal(a: TokenizeResult, b: TokenizeResult) -> bool:
    if a.trailing_whitespace != b.trailing_whitespace:
        return False
    if len(a.tokens) != len(b.tokens):
        return False
    for ta, tb in zip(a.tokens, b.tokens):
        if ta.nl != tb.nl or ta.col_prefix != tb.col_prefix:
            return False
        if ta.block != tb.block or ta.type != tb.type or ta.value != tb.value:
            return False
    return True
