"""Stride-Downsampling für Sparklines — gemeinsame Spec für API und Preview."""

from __future__ import annotations


def dedupe_neighbors(points: list[dict]) -> list[dict]:
    if not points:
        return points
    out = [points[0]]
    for point in points[1:]:
        if point is not out[-1]:
            out.append(point)
    return out


def downsample_curve_points(points: list[dict], limit: int) -> list[dict]:
    """Stride-Downsampling — erster/letzter Punkt immer erhalten."""
    if len(points) <= limit:
        return points
    stride = max(1, len(points) // limit)
    out = [points[0]]
    for i in range(stride, len(points), stride):
        out.append(points[i])
    if out[-1] is not points[-1]:
        out.append(points[-1])
    out = dedupe_neighbors(out)
    assert out[0] is points[0]
    assert out[-1] is points[-1]
    return out


def build_preview_points(
    points: list[dict],
    *,
    preview_limit: int,
) -> tuple[list[dict], bool]:
    """Head-Slice + globaler Tail-Anker; dedupe_neighbors nach Push."""
    full_count = len(points)
    if full_count <= preview_limit:
        return list(points), False
    preview = list(points[:preview_limit])
    if preview[-1] is not points[-1]:
        preview.append(points[-1])
    preview = dedupe_neighbors(preview)
    return preview, True
