"""DocumentRegistry — Write-once S/C/N/D/H Layer."""

from __future__ import annotations

from dataclasses import dataclass, field

from alphabets import AlphabetProfile
from analysis.blocks.context import COrigin, NL_CONTEXT, ParseContext, ParseDomain
from analysis.blocks.kinds import PointerKind
from analysis.document.model import GpmHeaderEntry
from gpm_types.hi.codec import decode_hi
from gpm_types.hi.segments import HiPayload, parse_hi_segments


@dataclass
class StructureEntry:
    entry_id: int
    key_bytes: bytes
    substance: int
    perm_index: int
    perm_space: int
    origin: COrigin = COrigin.GEOM
    frequencies: list[int] = field(default_factory=list)


@dataclass
class DocumentRegistry:
    profile: AlphabetProfile
    s_entries: list[GpmHeaderEntry] = field(default_factory=list)
    c_entries: list[StructureEntry] = field(default_factory=list)
    n_entries: list[int] = field(default_factory=list)
    d_entries: list[str] = field(default_factory=list)
    h_entries: list[HiPayload] = field(default_factory=list)
    _s_reverse: dict[str, int] = field(default_factory=dict, repr=False)
    _c_reverse: dict[tuple[COrigin, bytes], int] = field(default_factory=dict, repr=False)
    _n_reverse: dict[int, int] = field(default_factory=dict, repr=False)
    _d_reverse: dict[str, int] = field(default_factory=dict, repr=False)
    _h_reverse: dict[str, int] = field(default_factory=dict, repr=False)

    def intern_s_header(self, entry: GpmHeaderEntry) -> int:
        key = entry.word_canonical
        if key in self._s_reverse:
            return self._s_reverse[key]
        entry = GpmHeaderEntry(
            word_id=len(self.s_entries),
            word_canonical=entry.word_canonical,
            word_normalized=entry.word_normalized,
            substance=entry.substance,
            perm_index=entry.perm_index,
        )
        self.s_entries.append(entry)
        self._s_reverse[key] = entry.word_id
        return entry.word_id

    def intern(
        self,
        kind: PointerKind,
        value: str | int,
        *,
        context: ParseContext = NL_CONTEXT,
        origin: COrigin = COrigin.GEOM,
        substance: int = 1,
        perm_index: int = 1,
        perm_space: int = 1,
        frequencies: list[int] | None = None,
    ) -> int:
        if kind in (PointerKind.C, PointerKind.SYS) and context.domain is ParseDomain.NL:
            if origin is COrigin.CODE:
                raise ValueError(f"{kind} nicht erlaubt im NL-Kontext: {value!r}")
            if kind is PointerKind.C and isinstance(value, str):
                raise ValueError(f"{kind} nicht erlaubt im NL-Kontext: {value!r}")

        if kind is PointerKind.S:
            if not isinstance(value, str):
                raise TypeError("S-Wert muss str sein.")
            if not value.strip():
                raise ValueError("Whitespace-only S-Eintrag verboten.")
            existing = self._s_reverse.get(value)
            if existing is not None:
                return existing
            if context.domain is ParseDomain.CODE:
                from gpm_types.si import encode_si

                try:
                    substance, perm_index = encode_si(value, self.profile)
                    word_normalized = value.upper()
                except ValueError:
                    substance, perm_index = 1, 1
                    word_normalized = value.upper()
                entry = GpmHeaderEntry(
                    word_id=len(self.s_entries),
                    word_canonical=value,
                    word_normalized=word_normalized,
                    substance=substance,
                    perm_index=perm_index,
                )
                self.s_entries.append(entry)
                self._s_reverse[value] = entry.word_id
                return entry.word_id
            raise ValueError(f"S-Eintrag {value!r} nicht im Genom — zuerst intern_s_header.")

        if kind is PointerKind.SYS:
            if context.domain is ParseDomain.NL:
                raise ValueError("SYS nicht erlaubt im NL-Kontext.")
            key = str(value).encode("utf-8")
            rev_key = (origin, key)
            if rev_key in self._c_reverse:
                return self._c_reverse[rev_key]
            entry_id = len(self.c_entries)
            self.c_entries.append(
                StructureEntry(
                    entry_id=entry_id,
                    key_bytes=key,
                    substance=1,
                    perm_index=1,
                    perm_space=1,
                    origin=origin,
                )
            )
            self._c_reverse[rev_key] = entry_id
            return entry_id

        if kind is PointerKind.C:
            if not isinstance(value, (str, bytes)):
                raise TypeError("C-Key muss str oder bytes sein.")
            key = value.encode("utf-8") if isinstance(value, str) else value
            rev_key = (origin, key)
            if rev_key in self._c_reverse:
                return self._c_reverse[rev_key]
            entry_id = len(self.c_entries)
            self.c_entries.append(
                StructureEntry(
                    entry_id=entry_id,
                    key_bytes=key,
                    substance=substance,
                    perm_index=perm_index,
                    perm_space=perm_space,
                    origin=origin,
                    frequencies=list(frequencies or []),
                )
            )
            self._c_reverse[rev_key] = entry_id
            return entry_id

        if kind is PointerKind.N:
            if not isinstance(value, int):
                raise TypeError("N-Wert muss int sein.")
            if value in self._n_reverse:
                return self._n_reverse[value]
            entry_id = len(self.n_entries)
            self.n_entries.append(value)
            self._n_reverse[value] = entry_id
            return entry_id

        if kind is PointerKind.D:
            if not isinstance(value, str):
                raise TypeError("D-Wert muss str sein.")
            if value in self._d_reverse:
                return self._d_reverse[value]
            entry_id = len(self.d_entries)
            self.d_entries.append(value)
            self._d_reverse[value] = entry_id
            return entry_id

        if kind is PointerKind.H:
            if not isinstance(value, str):
                raise TypeError("H-Wert muss str sein.")
            payload = parse_hi_segments(value)
            raw_key = decode_hi(payload)
            existing = self._h_reverse.get(raw_key)
            if existing is not None:
                return existing
            for seg in payload.segments:
                if seg.tag == "N":
                    self.intern(PointerKind.N, int(seg.value), context=context)
                else:
                    self.intern(PointerKind.S, seg.value, context=context)
            entry_id = len(self.h_entries)
            self.h_entries.append(payload)
            self._h_reverse[raw_key] = entry_id
            return entry_id

        raise ValueError(f"PointerKind {kind} nicht unterstützt für intern().")
