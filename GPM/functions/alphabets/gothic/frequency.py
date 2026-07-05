"""Gothic Buchstabenfrequenz — häufig→selten.

Source: Wulfila-Bibel-Korpus-Frequenz-Schätzung (Nähe zu GREEK/ROMAN).
"""

from __future__ import annotations

from typing import Final

_GOTH = tuple(chr(0x10330 + i) for i in range(27))

GOTHIC_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    _GOTH[0], _GOTH[8], _GOTH[9], _GOTH[1], _GOTH[2], _GOTH[3], _GOTH[4], _GOTH[5],
    _GOTH[6], _GOTH[7], _GOTH[10], _GOTH[11], _GOTH[12], _GOTH[13], _GOTH[14],
    _GOTH[15], _GOTH[16], _GOTH[17], _GOTH[18], _GOTH[19], _GOTH[20], _GOTH[21],
    _GOTH[22], _GOTH[23], _GOTH[24], _GOTH[25], _GOTH[26],
)
