"""Thaana Buchstabenfrequenz — häufig→selten.

Source: Dhivehi-Korpus-Frequenz (historische Ableitung aus arabisch-indischen Ziffern).
"""

from __future__ import annotations

from typing import Final

_TH = tuple(chr(0x0780 + i) for i in range(24))

THAANA_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    _TH[23], _TH[22], _TH[21], _TH[0], _TH[1], _TH[2], _TH[3], _TH[4], _TH[5], _TH[6],
    _TH[7], _TH[8], _TH[9], _TH[10], _TH[11], _TH[12], _TH[13], _TH[14], _TH[15],
    _TH[16], _TH[17], _TH[18], _TH[19], _TH[20],
)
