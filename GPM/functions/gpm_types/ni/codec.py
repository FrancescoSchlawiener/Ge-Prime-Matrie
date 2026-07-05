"""N(I) Codec."""

from __future__ import annotations

from gpm_types.ni.canonical import canonical_n
from gpm_types.ni.registry import NRegistry, pointer_id_n, checksum_n
from gpm_types.ni.substance import substance_n


def encode_ni(raw: str) -> tuple[int, str]:
    canon = canonical_n(raw)
    return substance_n(canon), pointer_id_n(canon)


def decode_ni(pointer_id: str, registry: NRegistry) -> str:
    return registry.resolve(pointer_id)
