import gzip
import io
import tarfile
from typing import Iterable

import requests

from scrapers.base import WordListScraper

# Leipzig-Korpus: Tab-Format in *_words.txt (Wort_ID \\t Wort \\t Häufigkeit)
# URL vom Portal wählen: https://wortschatz.informatik.uni-leipzig.de/de/download/deu
DEFAULT_URL = (
    "https://downloads.wortschatz-leipzig.de/corpora/"
    "deu_wikipedia_2021_300K.tar.gz"
)


class LeipzigScraper(WordListScraper):
    name = "leipzig"
    url = "https://wortschatz.informatik.uni-leipzig.de/de/download/deu"

    def __init__(self, download_url: str | None = None):
        self.download_url = download_url or DEFAULT_URL

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
            # rank word freq  OR  word freq  OR  single word
            if len(parts) >= 3 and parts[0].isdigit():
                yield parts[1], "de"
            elif len(parts) >= 2 and parts[-1].isdigit():
                yield parts[0], "de"
            else:
                yield parts[0], "de"

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
                        yield parts[1], "de"
                    elif parts and parts[0] and not parts[0].isdigit():
                        yield parts[0], "de"
