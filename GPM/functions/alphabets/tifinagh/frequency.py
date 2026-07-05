"""Tifinagh Buchstabenfrequenz — häufig→selten.

Source: Berber-Korpus-Frequenz-Schätzung (IRCAM Neo-Tifinagh, 33 Zeichen).
"""

from __future__ import annotations

from typing import Final

# IRCAM Neo-Tifinagh — 33 Standardzeichen
_TIFINAGH_IRCAM: Final[str] = (
    "\u2D30\u2D31\u2D33\u2D37\u2D39\u2D3B\u2D3C\u2D3D\u2D40\u2D43\u2D44\u2D45"
    "\u2D47\u2D49\u2D4A\u2D4D\u2D4E\u2D4F\u2D53\u2D54\u2D55\u2D56\u2D57\u2D59"
    "\u2D5A\u2D5B\u2D5C\u2D5D\u2D5F\u2D61\u2D62\u2D63\u2D64"
)

TIFINAGH_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    "\u2D5C", "\u2D4F", "\u2D30", "\u2D54", "\u2D53", "\u2D49", "\u2D31", "\u2D33",
    "\u2D37", "\u2D39", "\u2D3B", "\u2D3C", "\u2D3D", "\u2D40", "\u2D43", "\u2D44",
    "\u2D45", "\u2D47", "\u2D4A", "\u2D4D", "\u2D4E", "\u2D55", "\u2D56", "\u2D57",
    "\u2D59", "\u2D5A", "\u2D5B", "\u2D5D", "\u2D5F", "\u2D61", "\u2D62", "\u2D63",
    "\u2D64",
)
