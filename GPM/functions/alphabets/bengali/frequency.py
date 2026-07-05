"""Bengali Buchstabenfrequenz — häufig→selten.

Source: modern Bengali corpus (Wikipedia/News frequency estimate).
"""

from __future__ import annotations

from typing import Final

BENGALI_FREQUENCY_DESC: Final[tuple[str, ...]] = (
    "ষ", "ত", "র", "ক", "ন", "ম", "ল", "স", "প", "ব", "দ", "য", "হ", "গ",
    "জ", "চ", "ট", "ড", "ভ", "ফ", "থ", "ধ", "শ", "খ", "ঘ", "ছ", "ঝ", "ঠ",
    "ঢ", "ণ", "ঞ", "ঙ", "ড়", "ঢ়", "য়",
)
