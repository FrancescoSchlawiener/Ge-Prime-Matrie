from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable

from db.repository import WordRepository
from pipeline.process import ProcessResult, process_word
from scrapers.log import get_logger, log_scrape_summary
from scrapers.skipped_log import SkippedLog

_BATCH_SIZE = 1000
_SQLITE_INT_MAX = 2**63 - 1
_SQLITE_INT_MIN = -(2**63)


@dataclass
class ScrapeResult:
    source: str
    fetched: int = 0
    accepted: int = 0
    skipped: int = 0
    inserted: int = 0
    duplicates: int = 0
    errors: list[str] = field(default_factory=list)
    skipped_log: str | None = None


class WordListScraper(ABC):
    name: str
    url: str | None = None

    @abstractmethod
    def fetch_lines(self) -> Iterable[tuple[str, str | None]]:
        """Yield (word, language|None) tuples from the source."""

    def _record_skip(
        self,
        result: ScrapeResult,
        skipped: SkippedLog,
        raw: str,
        lang: str | None,
        reason: str,
    ) -> None:
        result.skipped += 1
        skipped.write(raw, lang, reason)

    def _flush_batch(
        self,
        repo: WordRepository,
        batch: list[ProcessResult],
        source_id: int,
        result: ScrapeResult,
    ) -> None:
        if not batch:
            return
        logger = get_logger(self.name)
        try:
            stats = repo.insert_words_batch(batch, source_id, batch_size=_BATCH_SIZE)
            result.inserted += stats.inserted
            result.duplicates += stats.duplicates
        except Exception as exc:
            msg = f"DB insert failed ({len(batch)} words): {exc}"
            logger.error(msg)
            result.errors.append(msg)
        finally:
            batch.clear()

    def _accept_entry(
        self,
        entry: ProcessResult,
        result: ScrapeResult,
        skipped: SkippedLog,
        raw: str,
        lang: str | None,
    ) -> bool:
        if _SQLITE_INT_MIN <= entry.perm_index <= _SQLITE_INT_MAX:
            return True
        self._record_skip(
            result,
            skipped,
            raw,
            lang,
            f"perm_index_overflow (I={entry.perm_index})",
        )
        return False

    def scrape_to_db(self, repo: WordRepository) -> ScrapeResult:
        result = ScrapeResult(source=self.name)
        logger = get_logger(self.name)
        skipped = SkippedLog(self.name)
        result.skipped_log = str(skipped.path)
        batch: list[ProcessResult] = []
        source_id: int | None = None

        try:
            for raw, lang in self.fetch_lines():
                result.fetched += 1
                try:
                    entry = process_word(raw, language=lang, source=self.name)
                except Exception as exc:
                    self._record_skip(result, skipped, raw, lang, f"exception: {exc}")
                    logger.error("process_word failed for %r: %s", raw, exc)
                    continue

                if entry is None:
                    self._record_skip(result, skipped, raw, lang, "invalid")
                elif self._accept_entry(entry, result, skipped, raw, lang):
                    result.accepted += 1
                    if source_id is None:
                        source_id = repo.get_or_create_source(self.name, self.url)
                    batch.append(entry)
                    if len(batch) >= _BATCH_SIZE:
                        self._flush_batch(repo, batch, source_id, result)
        except Exception as exc:
            msg = str(exc)
            logger.error("fetch_lines failed: %s", msg)
            result.errors.append(msg)
        finally:
            skipped.close()

        if source_id is not None:
            self._flush_batch(repo, batch, source_id, result)

        log_scrape_summary(self.name, result)
        return result
