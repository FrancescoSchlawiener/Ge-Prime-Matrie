"""Old Italic Buchstabenfrequenz — häufig→selten.

Source: Etruscan inscription corpus estimate (GREEK→ROMAN bridge).
"""

from __future__ import annotations

from typing import Final

_OI = tuple(chr(0x10300 + i) for i in range(26))

OLD_ITALIC_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    _OI[0], _OI[1], _OI[2], _OI[3], _OI[4], _OI[5], _OI[6], _OI[7], _OI[8], _OI[9],
    _OI[10], _OI[11], _OI[12], _OI[13], _OI[14], _OI[15], _OI[16], _OI[17], _OI[18],
    _OI[19], _OI[20], _OI[21], _OI[22], _OI[23], _OI[24], _OI[25],
)
