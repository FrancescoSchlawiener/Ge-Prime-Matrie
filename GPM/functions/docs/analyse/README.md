# Analyse-Schicht (Phase 4a)

Modulare Analyse in `GPM/functions/analysis/` — profil-aware Substanz-Vergleich, DTW, optionale Case-Schicht, Document-Compile und Wortpaar-Klassifikation.

**Regel:** Kein String-Vergleich für Ähnigkeit. Vergleiche laufen über **S, I, ggT, kgV und DTW auf Substanz-Ketten**.

## Modul-Karte

```
analysis/
  case/           Schreibweise (4 Modi), CaseStoragePolicy
  substance/      ggT/kgV, Diff, Wortpaar-Klassifikation
  geom/           DTW (generisch, substance_ggt_kgv_distance)
  document/       GpmDocument, Gap-Invarianten
  compile/        split_segments, compile_text, compile_text_to_gpm, reconstruct_text
  binary/         write_gpm, read_gpm, int_codec, separator_codec, gap_rle
  pair/           analyze_word_pair (Convenience)
```

## Binary-Writer (.gpm v8)

| Version | Beschreibung |
|---------|--------------|
| **8** (Standard) | v4-Genom/Body + `AlphabetProfile` im Payload + Separator oder GAP-RLE |
| **4** (Lesen/Schreiben) | OG-kompatibles flaches Layout, Profil default `OG` |

Layout: `[GPM][Header 29B][Profil?][Genom][Body][Gaps][Explicit][CRC32]`

```python
from analysis.compile.compiler import compile_text_to_gpm
from analysis.binary import write_gpm, read_gpm, analyze_gpm

doc, blob, stats = compile_text_to_gpm("Hallo Welt", AlphabetProfile.OG)
# stats.file_bytes, stats.genome_bytes, stats.body_bytes, …

loaded = read_gpm(blob)
# oder: analyze_gpm(blob) → version, counts, reconstructed text
```

Option `use_gap_rle=True` speichert alle Gaps verlustfrei im GAP-RLE-Block (für Emoji/Sonderzeichen-heavy Texte).

## Case-Schicht

| Code | Konstante | Verhalten |
|------|-----------|-----------|
| 0 | `CASE_LOWER` | alles klein |
| 1 | `CASE_TITLE` | Anfang groß |
| 2 | `CASE_UPPER` | alles groß |
| 3 | `CASE_EXPLICIT` | Mischfall → Eintrag in `explicit` |

`CaseStoragePolicy(store_case=False)` setzt alle Tokens auf `CASE_LOWER` und leert `explicit` — Rekonstruktion liefert kanonische Kleinschreibung.

## Gap-Symmetrie (kritisch)

**Invariante:** `len(gaps) == len(tokens) + 1`

Rekonstruktion: `gaps[0] + w0 + gaps[1] + w1 + … + gaps[n]`

Beispiel `"Hallo Welt"` → `gaps=["", " ", ""]`, 2 Tokens.

## API-Beispiele

```python
from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text
from analysis.compile.reconstruct import reconstruct_text
from analysis.substance.compare import compare_substances
from analysis.pair.analyze_word_pair import analyze_word_pair
from gpm_types.si import encode_si

# Satzbau
doc, stats = compile_text("Hallo Welt", AlphabetProfile.OG)
assert reconstruct_text(doc) == "Hallo Welt"

# Binary
doc, blob, stats = compile_text_to_gpm("Hallo Welt", AlphabetProfile.OG)
assert read_gpm(blob).profile == AlphabetProfile.OG

# Wortpaar
result = analyze_word_pair("LISTEN", "SILENT", AlphabetProfile.OG)
assert result["classification"]["is_anagram"]
assert result["comparison"]["ggt_kgv_similarity"] == 1.0

# Substanz-Vergleich
s1, _ = encode_si("LISTEN", AlphabetProfile.OG)
s2, _ = encode_si("SILENT", AlphabetProfile.OG)
compare_substances(s1, s2, AlphabetProfile.OG)
```

## Tests

```bash
cd GPM/functions
python run_tests.py
```

Neue Tests unter `tests/analysis/`.

## Roadmap

- **Phase 4b:** Kurven (`substance_curve`, `i_curve`), Align, Hierarchie
- **Phase 4c:** Morphem-Segmentierung (Graph-Suche, Toy-Audit)

Keine Abhängigkeit von `Ge-Prime-Matrix OG/` — OG-Logik ist portiert und generalisiert (`profile: AlphabetProfile`).
