"""Mongolian Buchstabenfrequenz — häufig→selten.

Source: Traditionelle mongolische Textverteilung (Basis-Grapheme, isolierte Form).
"""

from __future__ import annotations

from typing import Final

_MN = tuple(chr(0x1820 + i) for i in range(35))

MONGOLIAN_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    _MN[0], _MN[4], _MN[8], _MN[1], _MN[2], _MN[3], _MN[5], _MN[6], _MN[7], _MN[9],
    _MN[10], _MN[11], _MN[12], _MN[13], _MN[14], _MN[15], _MN[16], _MN[17], _MN[18],
    _MN[19], _MN[20], _MN[21], _MN[22], _MN[23], _MN[24], _MN[25], _MN[26], _MN[27],
    _MN[28], _MN[29], _MN[30], _MN[31], _MN[32], _MN[33], _MN[34],
)
