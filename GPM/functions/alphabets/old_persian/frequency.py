"""Old Persian Buchstabenfrequenz — häufig→selten.

Source: Behistun inscription frequency estimate.
"""

from __future__ import annotations

from typing import Final

_OP = tuple(chr(0x103A0 + i) for i in range(36))

OLD_PERSIAN_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    _OP[0], _OP[1], _OP[2], _OP[3], _OP[4], _OP[5], _OP[6], _OP[7], _OP[8], _OP[9],
    _OP[10], _OP[11], _OP[12], _OP[13], _OP[14], _OP[15], _OP[16], _OP[17], _OP[18],
    _OP[19], _OP[20], _OP[21], _OP[22], _OP[23], _OP[24], _OP[25], _OP[26], _OP[27],
    _OP[28], _OP[29], _OP[30], _OP[31], _OP[32], _OP[33], _OP[34], _OP[35],
)
