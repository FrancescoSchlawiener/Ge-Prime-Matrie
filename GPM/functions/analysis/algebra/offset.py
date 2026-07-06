"""Strukturelle Offset-Klassifikatoren und Twin-Keys."""

from __future__ import annotations

RIGID_MAE_THRESHOLD = 0.75
ELASTIC_MAE_THRESHOLD = 0.45
DTW_HIGH_THRESHOLD = 0.75


def classify_structural_offset(
    mae: float,
    dtw: float,
    *,
    literal: float | None = None,
) -> str:
    """Klassifikator rigid | elastic | hybrid | none aus MAE+DTW."""
    if dtw >= DTW_HIGH_THRESHOLD and mae >= RIGID_MAE_THRESHOLD:
        return "rigid"
    if dtw >= DTW_HIGH_THRESHOLD and mae <= ELASTIC_MAE_THRESHOLD:
        return "elastic"
    if ELASTIC_MAE_THRESHOLD < mae < RIGID_MAE_THRESHOLD and dtw >= 0.5:
        return "hybrid"
    if literal is not None and literal >= 0.999 and dtw >= 0.999:
        return "none"
    return "none"


def structural_twin_key(
    skeleton: tuple[int, ...],
    perm_index: int,
    perm_space: int,
) -> tuple[tuple[int, ...], int, int]:
    return (skeleton, perm_index, perm_space)
