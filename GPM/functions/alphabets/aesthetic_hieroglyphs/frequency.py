"""Aesthetic Hieroglyphs Buchstabenfrequenz — häufig→selten.

Source: Middle Egyptian corpus (Sinuhe), uniliteral phoneme frequency.
"""

from __future__ import annotations

from typing import Final

# 24 Gardiner-Uniliterale (transliteration: a i y aa b p f m n r h H x X s S q k g t T d D w)
_UNI = (
    "\U0001313F", "\U000131CB", "\U0001336D", "\U00013253", "\U000130C0", "\U000132EA",
    "\U00013191", "\U000130D4", "\U00013196", "\U0001308B", "\U00013250", "\U0001321B",
    "\U0001330D", "\U00013121", "\U000132F4", "\U000132BD", "\U000132C3", "\U000133A1",
    "\U000133BC", "\U000133CF", "\U0001337F", "\U000130A7", "\U0001336F", "\U00013037",
)

AESTHETIC_HIEROGLYPHS_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    _UNI[8], _UNI[9], _UNI[7], _UNI[0], _UNI[1], _UNI[4], _UNI[5], _UNI[6], _UNI[2],
    _UNI[3], _UNI[10], _UNI[11], _UNI[12], _UNI[13], _UNI[14], _UNI[15], _UNI[16],
    _UNI[17], _UNI[18], _UNI[19], _UNI[20], _UNI[21], _UNI[22], _UNI[23],
)
