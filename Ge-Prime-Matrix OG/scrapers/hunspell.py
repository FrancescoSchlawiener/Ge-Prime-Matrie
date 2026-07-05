"""Hunspell-.dic-Wortlisten (wooorm/dictionaries) — beliebiger Sprachcode."""

from __future__ import annotations

import re
from typing import Iterable

import requests

from scrapers.base import WordListScraper
from scrapers.latin_fold import fold_latin

_WOOORM = "https://raw.githubusercontent.com/wooorm/dictionaries/main/dictionaries"

# Explizit verifizierte Codes (Rest nutzt gleiches URL-Muster)
_HUNSPELL_URLS: dict[str, str] = {}


def wooorm_dic_url(code: str) -> str:
    return f"{_WOOORM}/{code.strip().lower()}/index.dic"


_FLAG_RE = re.compile(r"/.*$")


class HunspellScraper(WordListScraper):
    """Einzelne Hunspell-.dic-Datei."""

    def __init__(
        self,
        language: str,
        *,
        download_url: str | None = None,
        name: str | None = None,
        fold_diacritics: bool = True,
    ):
        code = language.strip().lower()
        self.language = code
        self.download_url = download_url or _HUNSPELL_URLS.get(code) or wooorm_dic_url(code)
        self.name = name or f"hunspell_{code}"
        self.url = self.download_url
        self.fold_diacritics = fold_diacritics

    def _clean_token(self, token: str) -> str | None:
        token = _FLAG_RE.sub("", token.strip())
        if not token or token.startswith("#"):
            return None
        if self.fold_diacritics:
            token = fold_latin(token)
        return token or None

    def fetch_lines(self) -> Iterable[tuple[str, str | None]]:
        resp = requests.get(self.download_url, timeout=180)
        resp.raise_for_status()
        for i, line in enumerate(resp.text.splitlines()):
            if i == 0 and line.split() and line.split()[0].isdigit():
                continue
            word = self._clean_token(line)
            if word:
                yield word, self.language
