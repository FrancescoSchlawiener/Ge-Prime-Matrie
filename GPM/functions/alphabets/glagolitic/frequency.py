"""Glagolitic Buchstabenfrequenz — häufig→selten.

Source: Altslawische Textverteilung (historischer Gegenpol zu CYRILLIC).
"""

from __future__ import annotations

from typing import Final

_GLAG = tuple(chr(0x2C00 + i) for i in range(41))

GLAGOLITIC_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    _GLAG[0], _GLAG[1], _GLAG[2], _GLAG[3], _GLAG[4], _GLAG[5], _GLAG[6], _GLAG[7],
    _GLAG[8], _GLAG[9], _GLAG[10], _GLAG[11], _GLAG[12], _GLAG[13], _GLAG[14],
    _GLAG[15], _GLAG[16], _GLAG[17], _GLAG[18], _GLAG[19], _GLAG[20], _GLAG[21],
    _GLAG[22], _GLAG[23], _GLAG[24], _GLAG[25], _GLAG[26], _GLAG[27], _GLAG[28],
    _GLAG[29], _GLAG[30], _GLAG[31], _GLAG[32], _GLAG[33], _GLAG[34], _GLAG[35],
    _GLAG[36], _GLAG[37], _GLAG[38], _GLAG[39], _GLAG[40],
)
