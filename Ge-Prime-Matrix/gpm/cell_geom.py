"""Zell-Geometrie (I_Satz) — Wort-Atome als Buchstaben einer Zelle."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from ge_prime.multiset_geom import perm_decode, perm_fits_width, perm_index, perm_space
from gpm.model import GpmDocument, GpmHeaderEntry, GpmToken
from pipeline.normalize import CASE_EXPLICIT

MAX_CELL_TOKENS = 50
PREFERRED_CELL_TOKENS = 30

_SENTENCE_END = frozenset(".!?")


def gap_ends_segment(gap: str) -> bool:
    """True wenn Gap mit Satzzeichen endet (Segmentierung, nicht Geometrie-Definition)."""
    stripped = gap.rstrip()
    return bool(stripped) and stripped[-1] in _SENTENCE_END


@dataclass(frozen=True)
class CellCategory:
    category_id: int
    word_id: int
    case_code: int
    perm_index: int
    explicit_index: int | None = None


@dataclass(frozen=True)
class CellGeometry:
    token_start: int
    token_count: int
    categories: list[CellCategory]
    category_sequence: list[int]
    frequencies: list[int]
    perm_space: int
    perm_index: int


@dataclass(frozen=True)
class CellSlice:
    token_start: int
    token_end: int  # exklusiv


def _category_key(
    token: GpmToken,
    token_index: int,
    explicit_map: dict[int, str],
) -> tuple[int, int, int | None]:
    explicit_idx = token_index if token.case_code == CASE_EXPLICIT else None
    if token.case_code == CASE_EXPLICIT and token_index not in explicit_map:
        explicit_idx = token_index
    return (token.word_id, token.case_code, explicit_idx)


def build_cell_geometry(
    tokens: list[GpmToken],
    *,
    token_start: int,
    explicit_map: dict[int, str],
) -> CellGeometry:
    """Baut Geometrie für ein Token-Segment [token_start, token_start+len(tokens))."""
    if not tokens:
        raise ValueError("Leere Zelle.")
    if len(tokens) > MAX_CELL_TOKENS:
        raise ValueError(
            f"Zelle hat {len(tokens)} Token — Maximum ist {MAX_CELL_TOKENS}."
        )

    key_to_cat: dict[tuple[int, int, int | None], int] = {}
    categories: list[CellCategory] = []
    category_sequence: list[int] = []

    for offset, token in enumerate(tokens):
        global_idx = token_start + offset
        key = _category_key(token, global_idx, explicit_map)
        if key not in key_to_cat:
            cat_id = len(categories)
            key_to_cat[key] = cat_id
            categories.append(
                CellCategory(
                    category_id=cat_id,
                    word_id=token.word_id,
                    case_code=token.case_code,
                    perm_index=token.perm_index,
                    explicit_index=key[2],
                )
            )
        category_sequence.append(key_to_cat[key])

    counts = Counter(category_sequence)
    frequencies = [counts[i] for i in range(len(categories))]
    n = perm_space(counts)
    i_satz = perm_index(category_sequence, counts)

    return CellGeometry(
        token_start=token_start,
        token_count=len(tokens),
        categories=categories,
        category_sequence=category_sequence,
        frequencies=frequencies,
        perm_space=n,
        perm_index=i_satz,
    )


def cell_geometry_encodable(geometry: CellGeometry, *, max_bytes: int = 16) -> bool:
    """True wenn N und I_Satz in die Integer-Stufen passen."""
    return perm_fits_width(geometry.perm_space, max_bytes=max_bytes)


def split_into_slices(
    token_count: int,
    gaps: list[str],
) -> list[CellSlice]:
    """
    Teilt Token-Indizes 0..token_count-1 in Zell-Segmente.
    Regeln: Gap-Split (.!?), bevorzugt 30 Token, hart max 50.
    """
    if token_count == 0:
        return []

    slices: list[CellSlice] = []
    start = 0
    i = 0

    while i < token_count:
        cell_len = i - start + 1
        gap_after = gaps[i + 1] if i + 1 < len(gaps) else ""
        at_hard = cell_len >= MAX_CELL_TOKENS
        at_preferred = cell_len >= PREFERRED_CELL_TOKENS
        at_gap = gap_ends_segment(gap_after)

        if at_hard or at_preferred or at_gap:
            slices.append(CellSlice(token_start=start, token_end=i + 1))
            start = i + 1
        i += 1

    if start < token_count:
        slices.append(CellSlice(token_start=start, token_end=token_count))

    return _ensure_encodable_slices(token_count, gaps, slices)


def _ensure_encodable_slices(
    token_count: int,
    gaps: list[str],
    slices: list[CellSlice],
) -> list[CellSlice]:
    """Teilt Zellen weiter, wenn sie MAX_CELL_TOKENS verletzen (sollte selten nötig sein)."""
    result: list[CellSlice] = []
    for sl in slices:
        length = sl.token_end - sl.token_start
        if length <= MAX_CELL_TOKENS:
            result.append(sl)
            continue
        mid = sl.token_start + length // 2
        result.extend(
            _ensure_encodable_slices(
                token_count,
                gaps,
                [
                    CellSlice(sl.token_start, mid),
                    CellSlice(mid, sl.token_end),
                ],
            )
        )
    return result


def split_for_perm_overflow(
    tokens: list[GpmToken],
    *,
    token_start: int,
    explicit_map: dict[int, str],
) -> list[CellGeometry]:
    """
    Baut Zell-Geometrie(n) für ein Slice; teilt rekursiv bei zu großem N.
    """
    if not tokens:
        return []
    try:
        geom = build_cell_geometry(
            tokens, token_start=token_start, explicit_map=explicit_map
        )
    except ValueError:
        if len(tokens) <= 1:
            raise
        mid = len(tokens) // 2
        return split_for_perm_overflow(
            tokens[:mid],
            token_start=token_start,
            explicit_map=explicit_map,
        ) + split_for_perm_overflow(
            tokens[mid:],
            token_start=token_start + mid,
            explicit_map=explicit_map,
        )

    if cell_geometry_encodable(geom):
        return [geom]

    if len(tokens) <= 1:
        return [geom]

    mid = len(tokens) // 2
    return split_for_perm_overflow(
        tokens[:mid],
        token_start=token_start,
        explicit_map=explicit_map,
    ) + split_for_perm_overflow(
        tokens[mid:],
        token_start=token_start + mid,
        explicit_map=explicit_map,
    )


def build_document_cells(document: GpmDocument) -> list[CellGeometry]:
    """Zell-Kette für ein vollständiges Dokument."""
    explicit_map = dict(document.explicit)
    slices = split_into_slices(len(document.tokens), document.gaps)
    cells: list[CellGeometry] = []
    for sl in slices:
        chunk = document.tokens[sl.token_start : sl.token_end]
        cells.extend(
            split_for_perm_overflow(
                chunk,
                token_start=sl.token_start,
                explicit_map=explicit_map,
            )
        )
    return cells


def expand_cell_to_tokens(cell: CellGeometry) -> list[GpmToken]:
    """Entrollt eine Zelle zu flachen GpmToken-Einträgen."""
    counts = Counter({i: cell.frequencies[i] for i in range(len(cell.frequencies))})
    path = perm_decode(counts, cell.perm_index)
    if len(path) != cell.token_count:
        raise ValueError("Entrollter Pfad passt nicht zur Zelllänge.")
    cat_map = {c.category_id: c for c in cell.categories}
    return [
        GpmToken(
            word_id=cat_map[cat_id].word_id,
            perm_index=cat_map[cat_id].perm_index,
            case_code=cat_map[cat_id].case_code,
        )
        for cat_id in path
    ]


def expand_cells_to_tokens(cells: list[CellGeometry]) -> list[GpmToken]:
    """Konkateniert alle Zellen zu einer Token-Liste."""
    tokens: list[GpmToken] = []
    for cell in cells:
        tokens.extend(expand_cell_to_tokens(cell))
    return tokens


def cells_cover_document(document: GpmDocument, cells: list[CellGeometry]) -> bool:
    """Prüft ob Zellen exakt alle Tokens abdecken."""
    if sum(c.token_count for c in cells) != len(document.tokens):
        return False
    expanded = expand_cells_to_tokens(cells)
    if len(expanded) != len(document.tokens):
        return False
    for orig, new in zip(document.tokens, expanded):
        if (
            orig.word_id != new.word_id
            or orig.perm_index != new.perm_index
            or orig.case_code != new.case_code
        ):
            return False
    return True
