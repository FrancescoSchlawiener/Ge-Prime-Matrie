from dataclasses import dataclass, field


@dataclass(frozen=True)
class GpmHeaderEntry:
    """Ein Eintrag im lokalen Genom — jede eindeutige Schreibweise genau einmal.

    word_original ist die kanonische Kleinform (mit Umlauten/ß); die konkrete
    Schreibweise pro Vorkommen liefert die Case-Schicht (token.case_code).
    """

    word_id: int
    word_original: str
    word_normalized: str
    substance: int
    s_width_class: int = 0


@dataclass(frozen=True)
class GpmToken:
    """Ein Wort-Vorkommen im Body: Zeiger + Permutations-Index + Schreibweise."""

    word_id: int
    perm_index: int
    case_code: int = 0


@dataclass
class GpmDocument:
    """Vollständiges, verlustfreies Dokumentmodell.

    Rekonstruktion: gaps[0] + wort[0] + gaps[1] + wort[1] + … + wort[n-1] + gaps[n]
    wobei wort[i] = apply_case(header[token.word_id].word_original, token.case_code)
    bzw. der Explicit-Overflow-Eintrag bei Mischschreibweise.
    """

    header: list[GpmHeaderEntry] = field(default_factory=list)
    tokens: list[GpmToken] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    explicit: list[tuple[int, str]] = field(default_factory=list)
    cells: list = field(default_factory=list)  # list[CellGeometry] nach v5-Kompilierung
    hierarchy: object | None = None  # DocumentHierarchy | None nach v6
    interval_index: object | None = None  # IntervalIndex | None nach v40
    substance_index: object | None = None  # SubstanceIndex | None nach v40
    gap_rle: dict | None = None  # dict[int, str] — v7 Rest-Whitespace


@dataclass
class GpmCompileStats:
    source_bytes: int
    file_bytes: int
    header_bytes: int
    body_bytes: int
    separator_bytes: int
    separator_perm: int
    unique_words: int
    total_tokens: int
    skipped_tokens: int
    compression_ratio: float
    lossless: bool
    zellen_anzahl: int = 0
    body_mode: str = "flat"
    cell_count_encodable: int = 0

    @property
    def gap_bytes(self) -> int:
        """Alias für ältere API/UI."""
        return self.separator_bytes


@dataclass
class GpmAnalysis:
    version: int
    unique_words: int
    total_tokens: int
    file_bytes: int
    header_bytes: int
    body_bytes: int
    separator_bytes: int
    separator_perm: int
    header: list[dict]
    body_preview: list[dict]
    reconstructed_text: str
    lossless: bool

    @property
    def gap_bytes(self) -> int:
        return self.separator_bytes
