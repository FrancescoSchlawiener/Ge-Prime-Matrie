"""Weitere lateinische Sprachen (nicht-Romanze) — Leipzig + Hunspell."""

from __future__ import annotations

from scrapers.hunspell import HunspellScraper
from scrapers.leipzig_lang import LEIPZIG_BASE, LeipzigLanguageScraper

# (name, ISO-639-1, Leipzig-Portal, corpus ohne .tar.gz)
LATIN_LEIPZIG: tuple[tuple[str, str, str, str], ...] = (
    ("dutch", "nl", "nld", "nld_wikipedia_2021_300K"),
    ("danish", "da", "dan", "dan_wikipedia_2021_300K"),
    ("swedish", "sv", "swe", "swe_wikipedia_2021_300K"),
    ("polish", "pl", "pol", "pol_wikipedia_2021_300K"),
    ("czech", "cs", "ces", "ces_wikipedia_2021_300K"),
    ("slovak", "sk", "slk", "slk_wikipedia_2021_300K"),
    ("hungarian", "hu", "hun", "hun_wikipedia_2021_300K"),
    ("finnish", "fi", "fin", "fin_wikipedia_2021_300K"),
    ("lithuanian", "lt", "lit", "lit_wikipedia_2021_300K"),
    ("basque", "eu", "eus", "eus_wikipedia_2021_300K"),
    ("indonesian", "id", "ind", "ind_wikipedia_2021_300K"),
    ("malay", "ms", "msa", "msa_wikipedia_2021_300K"),
    ("croatian", "hr", "hrv", "hrv_wikipedia_2021_300K"),
    ("slovenian", "sl", "slv", "slv_wikipedia_2021_300K"),
    ("turkish", "tr", "tur", "tur_wikipedia_2021_300K"),
    ("norwegian", "nn", "nno", "nno_wikipedia_2021_300K"),
    ("welsh", "cy", "cym", "cym_wikipedia_2021_100K"),
    ("icelandic", "is", "isl", "isl_wikipedia_2021_100K"),
    # Weitere lateinische Leipzig-Korpora (2026)
    ("afrikaans", "af", "afr", "afr_wikipedia_2021_300K"),
    ("asturian", "ast", "ast", "ast_wikipedia_2021_300K"),
    ("aragonese", "an", "arg", "arg_wikipedia_2021_10K"),
    ("bosnian", "bs", "bos", "bos_wikipedia_2021_300K"),
    ("breton", "br", "bre", "bre_wikipedia_2021_100K"),
    ("irish", "ga", "gle", "gle_wikipedia_2021_10K"),
    ("luxembourgish", "lb", "ltz", "ltz_wikipedia_2021_100K"),
    ("bokmal", "nb", "nor", "nor_wikipedia_2021_300K"),
    ("maltese", "mt", "mlt", "mlt_wikipedia_2021_10K"),
    ("sicilian", "scn", "scn", "scn_wikipedia_2021_10K"),
    ("sardinian", "srd", "srd", "srd_wikipedia_2021_10K"),
    ("swahili", "sw", "swa", "swa_wikipedia_2021_100K"),
    ("tagalog", "tl", "tgl", "tgl_wikipedia_2021_100K"),
    ("vietnamese", "vi", "vie", "vie_wikipedia_2021_300K"),
    ("uzbek", "uz", "uzb", "uzb_wikipedia_2021_100K"),
    ("azerbaijani", "az", "aze", "aze_wikipedia_2021_300K"),
)

# Nur Hunspell (wooorm) — kein passendes Leipzig-300K
LATIN_HUNSPELL: tuple[tuple[str, str], ...] = (
    ("hunspell_nl", "nl"),
    ("hunspell_da", "da"),
    ("hunspell_sv", "sv"),
    ("hunspell_nb", "nb"),
    ("hunspell_pl", "pl"),
    ("hunspell_cs", "cs"),
    ("hunspell_sk", "sk"),
    ("hunspell_hu", "hu"),
    ("hunspell_et", "et"),
    ("hunspell_lv", "lv"),
    ("hunspell_lt", "lt"),
    ("hunspell_eu", "eu"),
    ("hunspell_ga", "ga"),
    ("hunspell_gd", "gd"),
    ("hunspell_cy", "cy"),
    ("hunspell_br", "br"),
    ("hunspell_is", "is"),
    ("hunspell_lb", "lb"),
    ("hunspell_eo", "eo"),
    ("hunspell_ia", "ia"),
    ("hunspell_fy", "fy"),
    ("hunspell_nds", "nds"),
    ("hunspell_hr", "hr"),
    ("hunspell_sl", "sl"),
    ("hunspell_tr", "tr"),
    ("hunspell_vi", "vi"),
    ("hunspell_ie", "ie"),
    ("hunspell_mn", "mn"),
)


def _make_leipzig(name: str, language: str, portal: str, corpus: str) -> type:
    url = f"{LEIPZIG_BASE}{corpus}.tar.gz"

    class _S(LeipzigLanguageScraper):
        def __init__(self, download_url: str | None = None):
            super().__init__(
                name=name,
                language=language,
                download_url=download_url or url,
                portal_lang=portal,
            )

    _S.__name__ = "".join(p.title() for p in name.split("_")) + "Scraper"
    return _S


def _make_hunspell(source: str, code: str) -> type:
    class _H(HunspellScraper):
        def __init__(self, download_url: str | None = None):
            super().__init__(code, download_url=download_url, name=source)

    return _H


LATIN_SCRAPERS: dict[str, type] = {}
for _n, _l, _p, _c in LATIN_LEIPZIG:
    LATIN_SCRAPERS[_n] = _make_leipzig(_n, _l, _p, _c)
for _s, _c in LATIN_HUNSPELL:
    LATIN_SCRAPERS[_s] = _make_hunspell(_s, _c)

LATIN_SOURCE_NAMES: tuple[str, ...] = tuple(n for n, _, _, _ in LATIN_LEIPZIG)

# Direktimporte
DutchScraper = LATIN_SCRAPERS["dutch"]
DanishScraper = LATIN_SCRAPERS["danish"]
SwedishScraper = LATIN_SCRAPERS["swedish"]
PolishScraper = LATIN_SCRAPERS["polish"]
CzechScraper = LATIN_SCRAPERS["czech"]
SlovakScraper = LATIN_SCRAPERS["slovak"]
HungarianScraper = LATIN_SCRAPERS["hungarian"]
FinnishScraper = LATIN_SCRAPERS["finnish"]
LithuanianScraper = LATIN_SCRAPERS["lithuanian"]
BasqueScraper = LATIN_SCRAPERS["basque"]
IndonesianScraper = LATIN_SCRAPERS["indonesian"]
MalayScraper = LATIN_SCRAPERS["malay"]
CroatianScraper = LATIN_SCRAPERS["croatian"]
SlovenianScraper = LATIN_SCRAPERS["slovenian"]
TurkishScraper = LATIN_SCRAPERS["turkish"]
NorwegianScraper = LATIN_SCRAPERS["norwegian"]
WelshScraper = LATIN_SCRAPERS["welsh"]
IcelandicScraper = LATIN_SCRAPERS["icelandic"]
AfrikaansScraper = LATIN_SCRAPERS["afrikaans"]
AsturianScraper = LATIN_SCRAPERS["asturian"]
AragoneseScraper = LATIN_SCRAPERS["aragonese"]
BosnianScraper = LATIN_SCRAPERS["bosnian"]
BretonScraper = LATIN_SCRAPERS["breton"]
IrishScraper = LATIN_SCRAPERS["irish"]
LuxembourgishScraper = LATIN_SCRAPERS["luxembourgish"]
BokmalScraper = LATIN_SCRAPERS["bokmal"]
MalteseScraper = LATIN_SCRAPERS["maltese"]
SicilianScraper = LATIN_SCRAPERS["sicilian"]
SardinianScraper = LATIN_SCRAPERS["sardinian"]
SwahiliScraper = LATIN_SCRAPERS["swahili"]
TagalogScraper = LATIN_SCRAPERS["tagalog"]
VietnameseScraper = LATIN_SCRAPERS["vietnamese"]
UzbekScraper = LATIN_SCRAPERS["uzbek"]
AzerbaijaniScraper = LATIN_SCRAPERS["azerbaijani"]
