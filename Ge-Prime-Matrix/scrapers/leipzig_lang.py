"""Leipzig-Korpus-Scraper — gleiches Tab-Format wie deu, beliebige Sprache."""

from __future__ import annotations

import gzip
import io
import tarfile
from typing import Iterable

import requests

from scrapers.base import WordListScraper
from scrapers.latin_fold import fold_latin

LEIPZIG_BASE = "https://downloads.wortschatz-leipzig.de/corpora/"
LEIPZIG_PORTAL = "https://wortschatz-leipzig.de/en/download/"


class LeipzigLanguageScraper(WordListScraper):
    """Wortliste aus Leipzig *-words.txt (Wort_ID \\t Wort \\t Häufigkeit)."""

    def __init__(
        self,
        *,
        name: str,
        language: str,
        download_url: str,
        portal_lang: str,
        fold_diacritics: bool = True,
    ):
        self.name = name
        self.language = language
        self.download_url = download_url
        self.url = f"{LEIPZIG_PORTAL}{portal_lang}"
        self.fold_diacritics = fold_diacritics

    def _emit_word(self, word: str) -> str | None:
        word = word.strip()
        if not word or word.startswith("#"):
            return None
        if self.fold_diacritics:
            word = fold_latin(word)
        return word or None

    def fetch_lines(self) -> Iterable[tuple[str, str | None]]:
        resp = requests.get(self.download_url, timeout=300)
        resp.raise_for_status()
        content = resp.content
        url_lower = self.download_url.lower()

        if url_lower.endswith(".gz") and not url_lower.endswith(".tar.gz"):
            text = gzip.decompress(content).decode("utf-8", errors="replace")
            yield from self._parse_plain_lines(text)
        elif url_lower.endswith((".tar.gz", ".tgz", ".tar")):
            yield from self._parse_tar(content)
        else:
            text = content.decode("utf-8", errors="replace")
            yield from self._parse_plain_lines(text)

    def _parse_plain_lines(self, text: str) -> Iterable[tuple[str, str | None]]:
        for line in text.splitlines():
            parts = line.strip().split()
            if not parts:
                continue
            if len(parts) >= 3 and parts[0].isdigit():
                raw = parts[1]
            elif len(parts) >= 2 and parts[-1].isdigit():
                raw = parts[0]
            else:
                raw = parts[0]
            word = self._emit_word(raw)
            if word:
                yield word, self.language

    def _parse_tar(self, data: bytes) -> Iterable[tuple[str, str | None]]:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                if "words" not in member.name.lower():
                    continue
                fh = tf.extractfile(member)
                if fh is None:
                    continue
                for raw in io.TextIOWrapper(fh, encoding="utf-8", errors="replace"):
                    parts = raw.strip().split("\t")
                    if len(parts) >= 2 and parts[1]:
                        candidate = parts[1]
                    elif parts and parts[0] and not parts[0].isdigit():
                        candidate = parts[0]
                    else:
                        continue
                    word = self._emit_word(candidate)
                    if word:
                        yield word, self.language
