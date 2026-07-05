"""PointerKind — shared ohne Zirkelimport."""

from __future__ import annotations

from enum import Enum


class PointerKind(str, Enum):
    S = "S"
    N = "N"
    D = "D"
    C = "C"
    H = "H"
    SYS = "SYS"
