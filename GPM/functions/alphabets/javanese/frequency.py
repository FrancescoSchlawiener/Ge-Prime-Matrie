"""Javanese Buchstabenfrequenz — häufig→selten.

Source: Javanese text corpus frequency estimate (Hanacaraka core).
"""

from __future__ import annotations

from typing import Final

_JV = tuple(chr(0xA992 + i) for i in range(20))

JAVANESE_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    _JV[0], _JV[4], _JV[3], _JV[1], _JV[2], _JV[5], _JV[6], _JV[7], _JV[8], _JV[9],
    _JV[10], _JV[11], _JV[12], _JV[13], _JV[14], _JV[15], _JV[16], _JV[17], _JV[18],
    _JV[19],
)
