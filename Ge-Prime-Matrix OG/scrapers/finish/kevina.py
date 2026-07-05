from typing import Iterable

import requests

from scrapers.base import WordListScraper

# en-wl/wordlist (Nachfolger von kevina/wordlist) — englische Alpha-Wörter
DEFAULT_URL = (
    "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
)


class KevinaScraper(WordListScraper):
    name = "kevina"
    url = "https://github.com/en-wl/wordlist"

    def __init__(self, download_url: str = DEFAULT_URL):
        self.download_url = download_url

    def fetch_lines(self) -> Iterable[tuple[str, str | None]]:
        resp = requests.get(self.download_url, timeout=180)
        resp.raise_for_status()
        for line in resp.text.splitlines():
            word = line.strip()
            if word and not word.startswith("#"):
                yield word, "en"
