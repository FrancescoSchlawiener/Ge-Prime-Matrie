"""H(I) Substanz — positionsabhängig über Segmentliste."""

from __future__ import annotations

from gpm_types.hi.segments import HiPayload, HiSegment
from gpm_types.ni.substance import substance_n


def substance_hi(payload: HiPayload) -> int:
    result = 1
    weights = (31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101)
    for i, seg in enumerate(payload.segments):
        w = weights[i % len(weights)]
        if seg.tag == "N":
            block = substance_n(seg.value)
        else:
            from gpm_types.si.substance import substance_roman
            block = substance_roman(seg.value)
        result *= block ** w
    return result


def fingerprint_hi(payload: HiPayload) -> tuple[tuple[str, str], ...]:
    return tuple((s.tag, s.value) for s in payload.segments)
