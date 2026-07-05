"""Token-Klassifikation — einzige Wahrheit für S|N|D|H."""

from __future__ import annotations

import re
from enum import Enum

_DECIMAL_RE = re.compile(r"^[+-]?\d+([.,]\d+)?$")
_INTEGER_RE = re.compile(r"^[+-]?\d+$")


class PayloadKind(str, Enum):
    S = "S"
    N = "N"
    D = "D"
    H = "H"


def classify_token(raw: str) -> PayloadKind:
    text = (raw or "").strip()
    if not text:
        raise ValueError("Leerer Token.")
    if _DECIMAL_RE.match(text) and ("," in text or "." in text):
        return PayloadKind.D
    if _INTEGER_RE.match(text):
        return PayloadKind.N
    has_digit = any(ch.isdigit() for ch in text)
    has_alpha = any(ch.isalpha() for ch in text)
    if has_digit and has_alpha:
        return PayloadKind.H
    if has_alpha:
        return PayloadKind.S
    raise ValueError(f"Token {raw!r} nicht klassifizierbar.")
