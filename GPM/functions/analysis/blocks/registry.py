"""DocumentRegistry — Write-once S/C/N/D/H Layer."""

from __future__ import annotations

from dataclasses import dataclass, field

from alphabets import AlphabetProfile
from analysis.blocks.context import COrigin, NL_CONTEXT, ParseContext, ParseDomain
from analysis.blocks.kinds import PointerKind
from analysis.document.model import GpmHeaderEntry
from gpm_types.ci.registry import checksum_c
from gpm_types.ci.substance import perm_index_c, perm_space_c, substance_c
from gpm_types.di.relation import DRelation
from gpm_types.hi.codec import decode_hi
from gpm_types.hi.segments import HiPayload, HiSegment, parse_hi_segments, parse_hi_segments_code
from gpm_types.hi.substance import substance_hi
from gpm_types.ni.registry import checksum_n, pointer_id_n
from gpm_types.ni.substance import substance_n


# Exakter Multiset-Permutations-Rang ist O(n*k) mit Fakultaeten — nur fuer
# kurze Struktur-Token (Operatoren/Klammern) sinnvoll und billig. Fuer laengere
# Token (Keywords, Kommentare, lange Symbole) ist der exakte Rang weder guenstig
# noch nuetzlich; dort dient die reihenfolgesensitive checksum_c als Index.
_CODE_PERM_MAX_LEN = 12


def _code_geometry(text: str) -> tuple[int, int, int]:
    """(substance, perm_index, perm_space) fuer ein Code-Struktur-Token.

    Leere Werte fallen auf die neutrale Identitaet (1,1,1) zurueck. Substanz ist
    immer das exakte Primprodukt (billig). Der Reihenfolge-Index ist fuer kurze
    Token der exakte Permutations-Rang, fuer lange Token die reihenfolge-
    sensitive checksum_c (beschraenkt Laufzeit, bleibt kollisionsarm).
    """
    if not text:
        return 1, 1, 1
    substance = substance_c(text)
    if len(text) <= _CODE_PERM_MAX_LEN:
        return substance, perm_index_c(text), perm_space_c(text)
    return substance, checksum_c(text), 1


@dataclass(frozen=True)
class NComposite:
    """Mehrstelliges N(I)-Literal als adressierbarer Kompositionsknoten.

    Das Ganze bleibt ein einziger Pointer (fraktal: innen Ziffern-Komposition
    über ``digit_ptrs``), trägt aber echte GPM-Identität: ``substance`` als
    Primprodukt über die Ziffern und ``checksum`` als N_<hash>-Adresse. Der
    rohe ``literal`` bleibt für den verlustfreien Roundtrip erhalten
    (führende Nullen), während substance/checksum dokumentübergreifende
    Äquivalenz erlauben.
    """

    literal: str
    digit_ptrs: tuple[int, ...]
    substance: int
    checksum: int

    @property
    def pointer_id(self) -> str:
        return pointer_id_n(self.literal)


# Atomare Ziffern 0–9 bleiben ``int``; mehrstellige Literale werden NComposite.
NEntry = int | NComposite


@dataclass
class DCodeEntry:
    display: str
    relation_key: str
    whole_ptr: int
    den_reduced_ptr: int
    ggt_ptr: int
    # frac_red als N-Pointer: macht die D(I)-Rekonstruktion vollständig
    # pointer-first (DRelation aus N-Pointern statt display-String).
    frac_red_ptr: int | None = None


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
    n_entries: list[NEntry] = field(default_factory=list)
    d_entries: list[DCodeEntry | str] = field(default_factory=list)
    h_entries: list[HiPayload] = field(default_factory=list)
    _s_reverse: dict[str, int] = field(default_factory=dict, repr=False)
    _c_reverse: dict[tuple[COrigin, bytes], int] = field(default_factory=dict, repr=False)
    _n_reverse: dict[int | tuple[int, ...], int] = field(default_factory=dict, repr=False)
    _n_substance: dict[int, list[int]] = field(default_factory=dict, repr=False)
    _d_reverse: dict[str, int] = field(default_factory=dict, repr=False)
    _d_by_triple: dict[tuple[int, int, int], int] = field(default_factory=dict, repr=False)
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
                    # Nicht-OG-Token (Symbole, gemischte Identifier): echte
                    # Primzahl-Geometrie statt Entartung auf substance=1.
                    substance, perm_index, _ = _code_geometry(value)
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
            text = str(value)
            key = text.encode("utf-8")
            rev_key = (origin, key)
            if rev_key in self._c_reverse:
                return self._c_reverse[rev_key]
            geo_s, geo_i, geo_space = _code_geometry(text)
            entry_id = len(self.c_entries)
            self.c_entries.append(
                StructureEntry(
                    entry_id=entry_id,
                    key_bytes=key,
                    substance=geo_s,
                    perm_index=geo_i,
                    perm_space=geo_space,
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
            # Code-Struktur-Token (Keyword/Klammer/Operator) bekommen echte
            # Primzahl-Geometrie; NL-Zell-C (GEOM, pickled bytes) behaelt die
            # vom Aufrufer uebergebene Zell-Geometrie (perm_index/perm_space).
            if origin is COrigin.CODE and isinstance(value, str):
                substance, perm_index, perm_space = _code_geometry(value)
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
            if isinstance(value, tuple):
                if not value:
                    raise ValueError("Leeres N(I)-Tupel verboten.")
                # Fraktale Komposition: strukturelle Dedup über die Ziffern-ptrs.
                if value in self._n_reverse:
                    return self._n_reverse[value]
                literal = "".join(self.n_display(d) for d in value)
                composite = NComposite(
                    literal=literal,
                    digit_ptrs=value,
                    substance=substance_n(literal),
                    checksum=checksum_n(literal),
                )
                entry_id = len(self.n_entries)
                self.n_entries.append(composite)
                self._n_reverse[value] = entry_id
                self._n_substance.setdefault(composite.substance, []).append(entry_id)
                return entry_id
            if not isinstance(value, int):
                raise TypeError("N-Wert muss int oder tuple[int, ...] sein.")
            if context.domain is ParseDomain.CODE and not (0 <= value <= 9):
                raise ValueError(f"Code-N(I): atomare Ziffern nur 0–9, got {value}")
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
            if context.domain is ParseDomain.CODE:
                return self.intern_h_code(value, context=context)
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

    def n_display(self, ptr_id: int) -> str:
        entry = self.n_entries[ptr_id]
        if isinstance(entry, int):
            return str(entry)
        return entry.literal

    def n_val(self, ptr_id: int) -> int:
        return int(self.n_display(ptr_id))

    def n_substance(self, ptr_id: int) -> int:
        """Primprodukt-Substanz eines N(I)-Eintrags (Atom oder Komposit)."""
        entry = self.n_entries[ptr_id]
        if isinstance(entry, int):
            return substance_n(str(entry))
        return entry.substance

    def n_checksum(self, ptr_id: int) -> int:
        """Checksum-Identität (N_<checksum>) eines N(I)-Eintrags."""
        entry = self.n_entries[ptr_id]
        if isinstance(entry, int):
            return checksum_n(str(entry))
        return entry.checksum

    def c_display(self, ptr_id: int) -> str:
        """Klartext eines C(I)/SYS-Struktureintrags."""
        return self.c_entries[ptr_id].key_bytes.decode("utf-8", errors="replace")

    def c_substance(self, ptr_id: int) -> int:
        """Primprodukt-Substanz eines C(I)-Struktureintrags."""
        return self.c_entries[ptr_id].substance

    def c_perm_index(self, ptr_id: int) -> int:
        """Permutations-Rang (Reihenfolge) eines C(I)-Struktureintrags."""
        return self.c_entries[ptr_id].perm_index

    def c_checksum(self, ptr_id: int) -> int:
        """Checksum-Identität (C_<checksum>) eines C(I)-Struktureintrags."""
        return checksum_c(self.c_display(ptr_id))

    def h_substance(self, ptr_id: int) -> int:
        """Gewichtete Segment-Substanz eines H(I)-Eintrags."""
        return substance_hi(self.h_entries[ptr_id])

    def collision_report(self) -> dict[str, dict[str, int | bool]]:
        """Kollisionsfreiheit je Kategorie prüfen.

        Für jede Kategorie wird gezählt, ob zwei **unterschiedliche** Literale
        dieselbe geometrische Identität teilen. Kollisionsfrei heißt: Anzahl
        eindeutiger Identitäten == Anzahl eindeutiger Literale.
        """
        report: dict[str, dict[str, int | bool]] = {}

        def _bucket(literals: list[str], identity) -> dict[str, int | bool]:
            uniq_lit = set(literals)
            ids = {identity(lit) for lit in uniq_lit}
            return {
                "entries": len(uniq_lit),
                "identities": len(ids),
                "collisions": len(uniq_lit) - len(ids),
                "collision_free": len(uniq_lit) == len(ids),
            }

        # S: Identität = (substance, perm_index)
        s_lits = [e.word_canonical for e in self.s_entries]
        report["S"] = _bucket(
            s_lits,
            lambda lit: (
                self.s_entries[self._s_reverse[lit]].substance,
                self.s_entries[self._s_reverse[lit]].perm_index,
            ),
        )
        # N: Identität = substance_n (Atom/Komposit), Literal = n_display
        n_lits = [self.n_display(i) for i in range(len(self.n_entries))]
        report["N"] = _bucket(n_lits, substance_n)
        # C: Identität = (substance, order-index) mit gebundener Perm-Berechnung
        c_lits = [self.c_display(i) for i in range(len(self.c_entries))]
        report["C"] = _bucket(c_lits, lambda lit: _code_geometry(lit)[:2])
        # H: Identität = substance_hi, Literal = raw
        h_lits = [decode_hi(p) for p in self.h_entries]
        report["H"] = _bucket(
            h_lits,
            lambda lit, idx={decode_hi(p): i for i, p in enumerate(self.h_entries)}: self.h_substance(idx[lit]),
        )
        return report

    def intern_n_from_display(self, text: str, *, context: ParseContext) -> int:
        """Wire/Decode: Ziffernliteral → atomarer oder Tupel-N-Eintrag."""
        from analysis.code.intern import intern_n_literal

        return intern_n_literal(text, self, context)

    def intern_d_code(
        self,
        display: str,
        rel_key: str,
        rel: DRelation,
        *,
        context: ParseContext,
    ) -> int:
        from analysis.code.intern import intern_n_from_int

        # Zuerst die N-Pointer erzeugen — Identität kommt aus dem Pointer-Triple,
        # nicht aus dem rel_key-String.
        whole_ptr = intern_n_from_int(rel.whole, self, context)
        den_reduced_ptr = intern_n_from_int(rel.den_reduced, self, context)
        ggt_ptr = intern_n_from_int(rel.ggt, self, context)
        frac_red_ptr = intern_n_from_int(rel.frac_red, self, context)

        triple = (whole_ptr, den_reduced_ptr, ggt_ptr)
        existing = self._d_by_triple.get(triple)
        if existing is not None:
            return existing

        entry_id = len(self.d_entries)
        self.d_entries.append(
            DCodeEntry(
                display=display,
                relation_key=rel_key,
                whole_ptr=whole_ptr,
                den_reduced_ptr=den_reduced_ptr,
                ggt_ptr=ggt_ptr,
                frac_red_ptr=frac_red_ptr,
            )
        )
        self._d_by_triple[triple] = entry_id
        # rel_key bleibt als sekundärer Index (Wire-Decode nutzt ihn weiterhin).
        self._d_reverse[rel_key] = entry_id
        return entry_id

    def d_relation(self, ptr_id: int) -> DRelation | None:
        """DRelation aus den N-Pointern rekonstruieren (pointer-first)."""
        entry = self.d_entries[ptr_id]
        if not isinstance(entry, DCodeEntry) or entry.frac_red_ptr is None:
            return None
        return DRelation(
            whole=self.n_val(entry.whole_ptr),
            den_reduced=self.n_val(entry.den_reduced_ptr),
            ggt=self.n_val(entry.ggt_ptr),
            frac_red=self.n_val(entry.frac_red_ptr),
        )

    def intern_h_code(self, raw: str, *, context: ParseContext) -> int:
        from analysis.code.intern import intern_n_literal

        payload = parse_hi_segments_code(raw)
        raw_key = decode_hi(payload)
        existing = self._h_reverse.get(raw_key)
        if existing is not None:
            return existing
        resolved: list[HiSegment] = []
        for seg in payload.segments:
            if seg.tag == "N":
                ptr = intern_n_literal(seg.value, self, context)
            else:
                ptr = self.intern(PointerKind.S, seg.value, context=context)
            resolved.append(HiSegment(seg.tag, seg.value, ptr_id=ptr))
        entry_id = len(self.h_entries)
        self.h_entries.append(HiPayload(tuple(resolved)))
        self._h_reverse[raw_key] = entry_id
        return entry_id

    def reconstruct_h(self, ptr_id: int) -> str:
        """Pointer-first: H(I) aus S/N-Registry über ``seg.ptr_id`` rekonstruieren.

        Nutzt NICHT ``seg.value``, sondern rekonstruiert jedes Segment aus dem
        Registry-Eintrag, auf den ``ptr_id`` zeigt (S → Genom-Kanonform,
        N → N(I)-Literal). Fällt nur dann auf ``seg.value`` zurück, wenn ein
        Segment keinen ``ptr_id`` trägt (NL-Pfad-Payload).
        """
        payload = self.h_entries[ptr_id]
        parts: list[str] = []
        for seg in payload.segments:
            if seg.ptr_id is None:
                parts.append(seg.value)
            elif seg.tag == "N":
                parts.append(self.n_display(seg.ptr_id))
            else:
                parts.append(self.s_entries[seg.ptr_id].word_canonical)
        return "".join(parts)

    def d_display(self, ptr_id: int) -> str:
        entry = self.d_entries[ptr_id]
        if isinstance(entry, DCodeEntry):
            # Pointer-first: Ziffern aus dem N-Pointer-Triple (DRelation)
            # rekonstruieren; nur das originale Dezimaltrennzeichen aus dem
            # gespeicherten Display übernehmen (Roundtrip-Treue . vs ,).
            rel = self.d_relation(ptr_id)
            if rel is not None:
                from gpm_types.di.codec import decode_di_relation

                canonical = decode_di_relation(rel)
                if "," in canonical and "," not in entry.display and "." in entry.display:
                    return canonical.replace(",", ".")
                return canonical
            return entry.display
        return str(entry)
