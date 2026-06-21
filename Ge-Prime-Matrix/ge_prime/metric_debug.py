"""Optional stderr diagnostics for Meta-ggT and Literal metric intersections."""

from __future__ import annotations

import json
import os
import sys


def metric_debug_enabled() -> bool:
    return os.environ.get("GE_PRIME_METRIC_DEBUG", "").strip() == "1"


def emit_metric_debug(label: str, payload: dict) -> None:
    """Print raw intersection data before ratio normalization when debug is enabled."""
    if not metric_debug_enabled():
        return
    print(f"[GE_PRIME_METRIC_DEBUG] {label}: {json.dumps(payload, default=str)}", file=sys.stderr)
