"""Sprach-Zuordnung: explizit, erkannt (de/en) oder Random/Unsortiert."""

LANGUAGE_RANDOM = "random"

STORED_LANGUAGE_CODES = frozenset({
    "de", "en",
    # Romanze
    "es", "fr", "it", "pt", "ro", "ca", "gl", "oc", "la", "rm", "fur",
    # Germanisch / Slawisch / Baltisch / Sonstige (lateinisch)
    "nl", "da", "sv", "nb", "nn", "pl", "cs", "sk", "hu", "fi", "et", "lv", "lt",
    "eu", "ga", "gd", "cy", "br", "is", "lb", "eo", "ia", "fy", "nds",
    "hr", "sl", "tr", "id", "ms",
    "af", "ast", "an", "bs", "mt", "scn", "srd", "sw", "tl", "vi", "uz", "az",
    "ie", "mn",
})

LANGUAGE_LABELS = {
    "random": "Random / unsortiert",
    "de": "Deutsch",
    "en": "Englisch",
    "es": "Spanisch",
    "fr": "Französisch",
    "it": "Italienisch",
    "pt": "Portugiesisch",
    "ro": "Rumänisch",
    "ca": "Katalanisch",
    "gl": "Galicisch",
    "oc": "Okzitanisch",
    "la": "Latein",
    "rm": "Rätoromanisch",
    "fur": "Friulanisch",
    "nl": "Niederländisch",
    "da": "Dänisch",
    "sv": "Schwedisch",
    "nb": "Norwegisch (Bokmål)",
    "nn": "Norwegisch (Nynorsk)",
    "pl": "Polnisch",
    "cs": "Tschechisch",
    "sk": "Slowakisch",
    "hu": "Ungarisch",
    "fi": "Finnisch",
    "et": "Estnisch",
    "lv": "Lettisch",
    "lt": "Litauisch",
    "eu": "Baskisch",
    "ga": "Irisch",
    "gd": "Schottisch-Gälisch",
    "cy": "Walisisch",
    "br": "Bretonisch",
    "is": "Isländisch",
    "lb": "Luxemburgisch",
    "eo": "Esperanto",
    "ia": "Interlingua",
    "fy": "Friesisch",
    "nds": "Niederdeutsch",
    "hr": "Kroatisch",
    "sl": "Slowenisch",
    "tr": "Türkisch",
    "id": "Indonesisch",
    "ms": "Malaiisch",
    "af": "Afrikaans",
    "ast": "Asturisch",
    "an": "Aragonesisch",
    "bs": "Bosnisch",
    "mt": "Maltesisch",
    "scn": "Sizilianisch",
    "srd": "Sardisch",
    "sw": "Suaheli",
    "tl": "Tagalog",
    "vi": "Vietnamesisch",
    "uz": "Usbekisch",
    "az": "Aserbaidschanisch",
    "ie": "Interlingue",
    "mn": "Mongolisch",
}


def resolve_language(language: str | None) -> str:
    if language and str(language).strip():
        return str(language).strip().lower()
    return LANGUAGE_RANDOM


def language_label(code: str | None) -> str:
    if not code:
        return LANGUAGE_LABELS[LANGUAGE_RANDOM]
    key = str(code).strip().lower()
    return LANGUAGE_LABELS.get(key, key)


def lang_stats_rows(raw_stats: list[tuple[str | None, int]]) -> list[tuple[str, int]]:
    """Sprachstatistik mit ausgeschriebenen Namen, absteigend nach Anzahl."""
    return sorted(
        [(language_label(code), cnt) for code, cnt in raw_stats],
        key=lambda row: (-row[1], row[0].lower()),
    )
