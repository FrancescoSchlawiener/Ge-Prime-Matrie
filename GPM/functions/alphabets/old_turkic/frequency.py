"""Old Turkic Buchstabenfrequenz — häufig→selten.

Source: Orkhon inscription corpus estimate.
"""

from __future__ import annotations

from typing import Final

_OT = tuple(chr(0x10C00 + i) for i in range(38))

OLD_TURKIC_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    _OT[0], _OT[1], _OT[2], _OT[3], _OT[4], _OT[5], _OT[6], _OT[7], _OT[8], _OT[9],
    _OT[10], _OT[11], _OT[12], _OT[13], _OT[14], _OT[15], _OT[16], _OT[17], _OT[18],
    _OT[19], _OT[20], _OT[21], _OT[22], _OT[23], _OT[24], _OT[25], _OT[26], _OT[27],
    _OT[28], _OT[29], _OT[30], _OT[31], _OT[32], _OT[33], _OT[34], _OT[35], _OT[36],
    _OT[37],
)
