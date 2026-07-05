"""H(I) Codec — H-Kanonisierungs-Garantie: Segment-Reihenfolge = Lese-Reihenfolge."""

from __future__ import annotations

from gpm_types.hi.segments import HiPayload, parse_hi_segments
from gpm_types.hi.substance import fingerprint_hi, substance_hi


def encode_hi(raw: str) -> tuple[HiPayload, int]:
    payload = parse_hi_segments(raw)
    return payload, substance_hi(payload)


def decode_hi(payload: HiPayload) -> str:
    parts: list[str] = []
    for seg in payload.segments:
        parts.append(seg.value)
    return "".join(parts)


def hi_fingerprint(raw: str) -> tuple[tuple[str, str], ...]:
    payload = parse_hi_segments(raw)
    return fingerprint_hi(payload)
