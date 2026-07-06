"""In-memory job runner — Langoperationen ohne Client-Abbruch."""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class JobProgress:
    phase: str = "pending"
    percent: int = 0
    message: str = ""
    elapsed_ms: int = 0


@dataclass
class JobRecord:
    job_id: str
    kind: str
    status: str = "pending"
    progress: JobProgress = field(default_factory=JobProgress)
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    finished_at: float | None = None


class JobRunner:
    def __init__(self, ttl_seconds: int = 600) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.RLock()
        self._ttl = ttl_seconds

    def _gc(self) -> None:
        cutoff = time.time() - self._ttl
        stale = [jid for jid, j in self._jobs.items() if (j.finished_at or j.created_at) < cutoff]
        for jid in stale:
            self._jobs.pop(jid, None)

    def create(self, kind: str) -> str:
        job_id = uuid.uuid4().hex
        with self._lock:
            self._gc()
            self._jobs[job_id] = JobRecord(job_id=job_id, kind=kind)
        return job_id

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def run_async(
        self,
        job_id: str,
        worker: Callable[[Callable[[str, int, str], None]], dict[str, Any]],
    ) -> None:
        def _progress(phase: str, percent: int, message: str) -> None:
            with self._lock:
                rec = self._jobs.get(job_id)
                if rec is None:
                    return
                rec.status = "running"
                rec.progress = JobProgress(
                    phase=phase,
                    percent=min(100, max(0, percent)),
                    message=message,
                    elapsed_ms=int((time.time() - rec.created_at) * 1000),
                )

        def _thread() -> None:
            with self._lock:
                rec = self._jobs[job_id]
                rec.status = "running"
                rec.progress = JobProgress(phase="start", percent=0, message="Starte …")
            try:
                result = worker(_progress)
                with self._lock:
                    rec = self._jobs[job_id]
                    rec.status = "done"
                    rec.result = result
                    rec.progress = JobProgress(
                        phase="done",
                        percent=100,
                        message="Fertig",
                        elapsed_ms=int((time.time() - rec.created_at) * 1000),
                    )
                    rec.finished_at = time.time()
            except Exception as exc:
                with self._lock:
                    rec = self._jobs[job_id]
                    rec.status = "failed"
                    rec.error = str(exc)
                    rec.progress = JobProgress(
                        phase="failed",
                        percent=rec.progress.percent,
                        message=str(exc),
                        elapsed_ms=int((time.time() - rec.created_at) * 1000),
                    )
                    rec.finished_at = time.time()

        threading.Thread(target=_thread, daemon=True).start()


job_runner = JobRunner()


def job_to_dict(rec: JobRecord) -> dict[str, Any]:
    return {
        "job_id": rec.job_id,
        "kind": rec.kind,
        "status": rec.status,
        "progress": {
            "phase": rec.progress.phase,
            "percent": rec.progress.percent,
            "message": rec.progress.message,
            "elapsed_ms": rec.progress.elapsed_ms,
        },
        "result": rec.result,
        "error": rec.error,
    }
