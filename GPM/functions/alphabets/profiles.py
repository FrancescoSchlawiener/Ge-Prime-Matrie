"""AlphabetProfile — User: 'Schriftsatz' / welches Alpha-Profil."""

from __future__ import annotations

from enum import Enum


class AlphabetProfile(str, Enum):
    OG = "og"
    ROMAN = "roman"
    GREEK = "greek"
    CYRILLIC = "cyrillic"
