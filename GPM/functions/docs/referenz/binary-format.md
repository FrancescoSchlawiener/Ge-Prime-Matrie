# .gpm Binärformat

Speicherung kompilierter Dokumente. Modul: `analysis/binary/format.py`, `compat.py`, `reader.py`.

```mermaid
flowchart TB
  doc[GpmDocument] --> write[write_gpm]
  write --> bytes[.gpm bytes]
  bytes --> read[read_gpm / read_gpm_any]
  read --> doc2[GpmDocument]
```

## Versionen

| Version | Standard | Besonderheiten |
|---------|----------|----------------|
| **4** | Legacy | Flaches Layout, OG-lesbar |
| **8** | Profil | + `AlphabetProfile` im Header |
| **9** | Lesen | Fraktal-Geometrie, Registry-C, GAP-RLE, Block-Tree (Schreiben: `version=9`) |
| **10** | **Default** | SI-Genom (nur S+I), kompakter Body, optional Canonical-Override, Code-Registry-Wire |

Konstante: `analysis.binary.format.VERSION` (= 10).

## Datei-Header (29 Byte)

| Offset | Inhalt |
|--------|--------|
| 0–2 | Magic `GPM` |
| 3 | Version |
| 4 | Flags (Bitmask) |
| 5–8 | Header-Einträge (Wörter) |
| 9–12 | Body-Tokens |
| 13–16 | Separator-Perm / reserviert |
| 17–20 | Explicit-Anzahl |
| 21–24 | Middle-Block-Länge (Gaps) |
| 25–28 | Payload-Länge |

## Flags

| Flag | Wert | Bedeutung |
|------|------|-----------|
| `FLAG_BODY_CELL` | 0x01 | Zell-Geometrie aktiv |
| `FLAG_BODY_HIER` | 0x02 | Hierarchie aktiv |
| `FLAG_STRUCT` | 0x04 | Struktur-Layer |
| `FLAG_GAP_RLE` | 0x08 | GAP run-length-kodiert |
| `FLAG_PROFILE` | 0x10 | Profilname im Payload |
| `FLAG_FRACTAL` | 0x20 | Registry-C + Geometrie |
| `FLAG_BLOCK_TREE` | 0x40 | Code-/Block-Baum eingebettet |
| `FLAG_GENOME_SI` | 0x80 | Genom nur S+I (v10), Body ohne per-Token-I |

## Payload-Reihenfolge (v9)

```mermaid
flowchart LR
  prof[Profil-Block]
  reg[Registry-C]
  tree[Block-Tree optional]
  gen[Genom Header-Einträge]
  body[Token-Body]
  mid[GAP Middle]
  exp[Explicit]
  prof --> reg --> tree --> gen --> body --> mid --> exp
```

## Payload-Reihenfolge (v10)

Profil → Registry (leer / C-SI / Code-Wire) → Block-Tree (optional, nur Code/Hybrid) → Genom (S+I [+ optional Canonical]) → Token-Body (word_id + case_code) → GAP Middle → Explicit

**v10 Genom-Eintrag:** Substanz S + Index I (binär). Wenn die Schreibweise von S/I abweicht (z. B. Umlaute `ö` vs. `oe`), folgt ein optionaler Canonical-Override (UTF-8).

**Registry v10:** NL-only → leer (count=0). Kurze Code-Symbole → C-Einträge nur mit S+I. Hybrid/Code → Code-Registry-Wire (`count=0xFFFF` + Länge + `encode_code_registry`).

## I/O-API

| Funktion | Parameter | Rückgabe | Beschreibung |
|----------|-----------|----------|--------------|
| `write_gpm` | `document`, optional `version`, `use_gap_rle` | `bytes` | Serialisieren |
| `read_gpm` | `bytes` | `GpmDocument` | v4/v8/v9 |
| `read_gpm_any` | `bytes` | `GpmDocument` | inkl. v7 best-effort |
| `load_gpm` | `path` | `GpmDocument` | Datei lesen |
| `analyze_gpm` | `path` oder bytes | `GpmAnalysis` | Metadaten |

## GAP-RLE

Standard-Hierarchie liefert **ableitbare** Gaps; Abweichungen werden kompakt als RLE-Map gespeichert. Rekonstruktion: `derive_gaps` + `merge_gaps`. Siehe [geometrie.md](geometrie.md).

## Registry-C (v9)

Code- und Geometrie-Literale (PointerKind C) mit Substanz, Perm-Raum, Origin-Byte. Wird bei `FLAG_FRACTAL` geschrieben.

## Beispiel

```python
from alphabets import AlphabetProfile
from analysis.compile.compiler import compile_text_to_gpm
from analysis.binary.format import read_gpm, VERSION, write_gpm
from analysis.binary.compat import read_gpm_any
from analysis.compile.reconstruct import reconstruct_text

doc, blob, _ = compile_text_to_gpm("Hallo.", AlphabetProfile.OG, version=VERSION)
assert blob[3] == VERSION

loaded = read_gpm(blob)
assert reconstruct_text(loaded) == "Hallo."

# OG v7 (best-effort):
# doc7 = read_gpm_any(open("legacy.gpm","rb").read())
```

## Hybrid → v9

```python
from analysis.code.compile import compile_hybrid_to_gpm

text = "# Titel\n\n```py\nx = 1\n```\n"
doc, blob = compile_hybrid_to_gpm(text)
# doc.root_block = Code-Modul; doc.registry = Code-Registry
```

## Grenzen

- Maximale String-Länge pro Feld: 1 MiB
- Middle-Block max. 16 MiB
- v7-Lesen ist best-effort — volle OG-Hierarchie ggf. nicht rekonstruiert
- Gelesener Block-Tree ersetzt nicht automatisch neu berechneten NL-Baum

## Siehe auch

- [datenmodell.md](datenmodell.md)
- [geometrie.md](geometrie.md)
- [code/compile-hybrid.md](code/compile-hybrid.md)
- [tutorials/og-v7-nach-v9.md](../tutorials/og-v7-nach-v9.md)
- [og/og-vs-gpm.md](../og/og-vs-gpm.md)
- Tests: `tests/analysis/test_binary.py`, `test_v9_binary.py`, `test_v9_hybrid.py`
