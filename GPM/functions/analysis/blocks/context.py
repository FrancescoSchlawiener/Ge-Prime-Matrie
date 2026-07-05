"""Parse-Kontext — hermetische NL/Code-Isolation (Absicherung A)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ParseDomain(str, Enum):
    NL = "nl"
    CODE = "code"


class COrigin(str, Enum):
    GEOM = "geom"
    CODE = "code"


@dataclass(frozen=True)
class ParseContext:
    domain: ParseDomain
    language_id: str | None = None
    fence_depth: int = 0

    def is_code(self) -> bool:
        return self.domain is ParseDomain.CODE

    def is_nl(self) -> bool:
        return self.domain is ParseDomain.NL


NL_CONTEXT = ParseContext(domain=ParseDomain.NL)
