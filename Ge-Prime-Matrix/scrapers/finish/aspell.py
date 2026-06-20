import io
import zipfile
from pathlib import PurePosixPath
from typing import Iterable

import requests

from scrapers.base import WordListScraper

# Aspell / 12dicts — englische Wortlisten
ASPELL_INDEX = "http://wordlist.aspell.net/dicts/"
DEFAULT_URL = (
    "https://downloads.sourceforge.net/project/wordlist/12Dicts/6.0/12dicts-6.0.2.zip"
)

# 12dicts-6.0.2.zip: alle Listen sind Englisch (American / International / …)
_DEFAULT_LANG = "en"

_PATH_LANG: tuple[tuple[str, str], ...] = (
    ("american/", "en"),
    ("international/", "en"),
    ("lemmatized/", "en"),
    ("special/", "en"),
)

_LANG_FROM_NAME: dict[str, str] = {
    "american": "en",
    "british": "en",
    "english": "en",
    "german": "de",
    "deutsch": "de",
    "french": "fr",
    "spanish": "es",
}

# Keine Wortlisten — Metadaten / Inflektions-DB
_SKIP_BASENAMES = frozenset({"agid.txt", "infl.txt", "readme.txt"})


class AspellScraper(WordListScraper):
    name = "aspell"
    url = ASPELL_INDEX

    def __init__(self, download_url: str = DEFAULT_URL, language: str | None = None):
        self.download_url = download_url
        self.language = language

    def _skip_file(self, filename: str) -> bool:
        base = PurePosixPath(filename).name.lower()
        return base in _SKIP_BASENAMES or base.startswith("readme")

    def _guess_language(self, filename: str) -> str:
        if self.language:
            return self.language
        norm = filename.replace("\\", "/").lower()
        for prefix, code in _PATH_LANG:
            if f"/{prefix}" in norm or norm.startswith(prefix):
                return code
        lower = norm
        for key, code in _LANG_FROM_NAME.items():
            if key in lower:
                return code
        return _DEFAULT_LANG

    def fetch_lines(self) -> Iterable[tuple[str, str | None]]:
        resp = requests.get(self.download_url, timeout=180, allow_redirects=True)
        resp.raise_for_status()

        if self.download_url.endswith(".txt") or "text/plain" in resp.headers.get(
            "Content-Type", ""
        ):
            lang = self.language or _DEFAULT_LANG
            for line in resp.text.splitlines():
                word = line.strip()
                if word and not word.startswith("#"):
                    yield word, lang
            return

        data = io.BytesIO(resp.content)
        if self.download_url.lower().endswith(".zip") or zipfile.is_zipfile(data):
            data.seek(0)
            yield from self._read_zip(data)
        else:
            data.seek(0)
            yield from self._read_tar_gz(data)

    def _read_zip(self, data: io.BytesIO) -> Iterable[tuple[str, str | None]]:
        with zipfile.ZipFile(data) as zf:
            for name in zf.namelist():
                if not name.endswith((".txt", ".words", ".dic")):
                    continue
                if self._skip_file(name):
                    continue
                lang = self._guess_language(name)
                with zf.open(name) as fh:
                    for raw in io.TextIOWrapper(fh, encoding="utf-8", errors="replace"):
                        word = raw.strip()
                        if word and not word.startswith("#"):
                            yield word, lang

    def _read_tar_gz(self, data: io.BytesIO) -> Iterable[tuple[str, str | None]]:
        import tarfile

        with tarfile.open(fileobj=data, mode="r:*") as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                if not member.name.endswith((".txt", ".words", ".dic")):
                    continue
                if self._skip_file(member.name):
                    continue
                lang = self._guess_language(member.name)
                fh = tf.extractfile(member)
                if fh is None:
                    continue
                for raw in io.TextIOWrapper(fh, encoding="utf-8", errors="replace"):
                    word = raw.strip()
                    if word and not word.startswith("#"):
                        yield word, lang
