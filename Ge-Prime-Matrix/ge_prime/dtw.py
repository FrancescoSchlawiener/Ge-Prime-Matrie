"""Gemeinsame DTW-Implementierung mit adaptivem Sakoe-Chiba-Fenster."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ge_prime.config import DTW_SEQUENCE_LIMIT


@dataclass(frozen=True)
class DtwResult:
    cost: float
    similarity: float
    failed: bool
    window: int
    length_a: int
    length_b: int
    downsampled: bool = False


def downsample_sequence(seq: list, limit: int) -> list:
    """Stride-Downsampling — erster/letzter Eintrag bleibt erhalten."""
    if len(seq) <= limit:
        return seq
    stride = max(1, len(seq) // limit)
    out = [seq[0]]
    for i in range(stride, len(seq), stride):
        out.append(seq[i])
    if out[-1] is not seq[-1]:
        out.append(seq[-1])
    return out


def adaptive_window(n: int, m: int) -> int:
    """|i-j| <= abs(n-m) + slack — garantiert erreichbaren Pfad (n,m)."""
    return abs(n - m) + max(3, min(n, m) // 8)


def dtw_similarity(
    seq_a: list,
    seq_b: list,
    distance_fn: Callable,
    *,
    window_mode: str = "adaptive",
    sample_limit: int | None = DTW_SEQUENCE_LIMIT,
) -> DtwResult:
    """DTW-Kosten und Ähnlichkeit 0..1 (1 = identisch)."""
    downsampled = False
    if sample_limit and (len(seq_a) > sample_limit or len(seq_b) > sample_limit):
        seq_a = downsample_sequence(seq_a, sample_limit)
        seq_b = downsample_sequence(seq_b, sample_limit)
        downsampled = True

    n, m = len(seq_a), len(seq_b)
    if n == 0 or m == 0:
        return DtwResult(
            cost=float("inf"),
            similarity=0.0,
            failed=True,
            window=0,
            length_a=n,
            length_b=m,
            downsampled=downsampled,
        )
    if n == 1 and m == 1:
        d = float(distance_fn(seq_a[0], seq_b[0]))
        return DtwResult(
            cost=d,
            similarity=max(0.0, 1.0 - d),
            failed=False,
            window=1,
            length_a=n,
            length_b=m,
            downsampled=downsampled,
        )

    if window_mode == "adaptive":
        window = adaptive_window(n, m)
    elif window_mode == "full":
        window = max(n, m)
    else:
        window = max(3, max(n, m) // 4)

    inf = float("inf")
    prev = [inf] * (m + 1)
    prev[0] = 0.0
    for i in range(1, n + 1):
        curr = [inf] * (m + 1)
        j_start = max(1, i - window)
        j_end = min(m, i + window)
        for j in range(j_start, j_end + 1):
            cost = float(distance_fn(seq_a[i - 1], seq_b[j - 1]))
            best_prev = min(prev[j], curr[j - 1], prev[j - 1])
            curr[j] = cost + best_prev
        prev = curr

    total_cost = prev[m]
    failed = total_cost == inf
    max_cost = max(n, m) * 1.0
    similarity = 0.0 if failed else max(0.0, 1.0 - total_cost / max_cost)
    return DtwResult(
        cost=total_cost,
        similarity=similarity,
        failed=failed,
        window=window,
        length_a=n,
        length_b=m,
        downsampled=downsampled,
    )


def dtw_result_payload(result: DtwResult) -> dict:
    """Serialisierbare DTW-Diagnostik für API-Responses."""
    payload = {
        "dtw_cost": round(result.cost, 6) if result.cost != float("inf") else None,
        "dtw_failed": result.failed,
        "dtw_window": result.window,
        "geometry_score": round(result.similarity, 6),
    }
    if result.downsampled:
        payload["dtw_downsampled"] = True
    return payload
