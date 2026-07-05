# GPM — Agent-Hinweise (Phase 3d)

Alles unter `GPM/functions/` — **keine** Änderungen in `Ge-Prime-Matrix OG/`.

**Dokumentation:** [docs/README.md](README.md) — Grundfunktionen, Profile, Benchmark (jeweils eigene README).

## Ordner-Karte

```
functions/
  alphabets/
    og/ roman/ greek/ cyrillic/
    arabic/ hebrew/ devanagari/ thai/
    hangul/ hiragana/ katakana/
    armenian/ georgian/
    gurmukhi/ tamil/ amharic/ coptic/ runic/
    phoenician/ ugaritic/ ogham/ glagolitic/ gothic/
    mongolian/ thaana/ tifinagh/
    bengali/ telugu/ javanese/
    old_persian/ aesthetic_hieroglyphs/ old_italic/ old_turkic/
    unicode_utils.py
    registry.py  normalize.py  lex.py  primes.py
  perm/  gpm_types/  tests/
```

## Alphabet-Profile (33)

| Profil | Zeichen | Normalisierung |
|--------|---------|----------------|
| OG / ROMAN | 27 | OG frozen; ROMAN frequenz-LEX |
| GREEK | 24 | NFC + upper |
| CYRILLIC | 33 | NFC + upper |
| ARABIC | 28 | NFC, Alef-Vereinheitlichung |
| HEBREW | 22 | NFC, Niqqud strip |
| DEVANAGARI | 46 | NFC, virama strip |
| THAI | 48 | NFC |
| HANGUL | 51 Jamo | NFKD → Jamo |
| HIRAGANA / KATAKANA | je 46 | NFC, Dakuten→Basis |
| ARMENIAN | 38 | NFC + upper |
| GEORGIAN | 33 | NFC |
| GURMUKHI | 35 | NFC → Matra-Map → Mn-Strip → Whitelist |
| TAMIL | 30 | NFC → Matra/Pulli-Map → Mn-Strip → Whitelist |
| AMHARIC | 34 | NFKD, Silbe→Ge'ez-Basis |
| COPTIC | 32 | NFC + upper |
| RUNIC | 24 | NFC, Rundata-LEX |
| PHOENICIAN / UGARITIC / GOTHIC | 22/30/27 | SMP-sichere Whitelist |
| OGHAM | 20 | NFC, Whitelist |
| GLAGOLITIC | 41 | NFC + upper |
| MONGOLIAN | 35 | Positionsform→Basis, FVS-Strip |
| THAANA | 24 | NFC, Whitelist |
| TIFINAGH | 33 | NFC, Whitelist (IRCAM) |
| BENGALI | 35 | NFC → Matra-Strip → Mn-Strip → Whitelist (Konsonanten) |
| TELUGU | 35 | NFC → Matra-Strip → Mn-Strip → Whitelist (Konsonanten) |
| JAVANESE | 20 | Pasangan/Diakritika-Strip → Hanacaraka-Whitelist |
| OLD_PERSIAN | 36 | SMP-sichere Whitelist |
| AESTHETIC_HIEROGLYPHS | 24 | Gardiner-Map → hermetischer Endfilter |
| OLD_ITALIC | 26 | SMP + upper |
| OLD_TURKIC | 38 | SMP-sichere Whitelist |

Prime-Blöcke sind disjunkt (OG/Roman teilen 2–103; ab GREEK fortlaufend via `primes.py`).

## GPM-Reduktionsphilosophie

- **Indisch (Bengali/Telugu):** Nur 35 Basis-Konsonanten — Matras/Vokale/Mn restlos entfernt (Gurmukhi-Pipeline)
- **Javanese:** Hanacaraka-Kern (20 Aksara) — Pasangan und Wyanjana verworfen
- **Ägyptisch (Aesthetic Hieroglyphs):** 800+ Gardiner-Glyphen → 24 Uniliterale via `gardiner_map.py`

## Logogramm-Leak-Verbot (Aesthetic Hieroglyphs)

Ideogramme, Götterfiguren, Gebäude und unbekannte Glyphen werden **silent discarded** — kein `raise`, kein Pass-Through. Nur Zeichen in `CHAR_AESTHETIC_HIEROGLYPHS_SET` oder gültige Gardiner-Map-Ziele landen im Substrat. `len(normalized)` bleibt 1:1 paritätisch mit den 24 Primzahlen.

## SMP-Codepoints

Old Persian, Aesthetic Hieroglyphs, Old Italic, Old Turkic (+ Phoenician, Ugaritic, Gothic): `unicode_utils.py` verbindlich.

## Epigraphische LEX-Quellen

| Profil | Quelle |
|--------|--------|
| OLD_PERSIAN | Behistun-Inschrift |
| AESTHETIC_HIEROGLYPHS | Sinuhe / Mittelägyptisch (Uniliterale) |
| OLD_ITALIC | Etruskische Inschriften |
| OLD_TURKIC | Orkhon-Inschriften |
| BENGALI / TELUGU | Wikipedia/News-Korpus-Schätzung |

## Verbotene Zeichensätze

Architekturverbindlich — **niemals** als `AlphabetProfile`:

- **Volles Gardiner-Set** (800+ Hieroglyphen als Profil) — nur 24-Uniliteral-Reduktion erlaubt
- **CJK / Kanji** — Prime-Allocator-Explosion
- **Tibetan / Khmer** — Ligatur-Cluster ohne Rendering-Engine
- **Burmese / Sinhala** — kombinatorische Sonderformen

## S(I) Codec

- `encode_si(raw, profile)` / `decode_si(substance, index, profile)` für alle 33 Profile
- `encode()` / `decode()` bleiben OG-only (Parität)

## Perm-Invarianten

Siehe [grundfunktionen/README.md](grundfunktionen/README.md#perm-invariante-anagramm-regel).

```bash
cd GPM/functions
python -m tools.perm_audit   # → 33/33 OK
```

Tests: `tests/alphabets/test_perm_identity_all_profiles.py`

## Tests

```bash
python GPM/functions/run_tests.py
```

327 Tests inkl. Perm-Identity, Multiscript, Smoke.

## Performance-Grenzen (Benchmark)

Siehe [benchmark/README.md](benchmark/README.md) — Tiefenanalyse, Width-Gate, Befehle.

```bash
cd GPM/functions
python -m tools.profile_benchmark
```

Output: `docs/benchmark/PROFILE_LIMITS.md`, `benchmark_results.json`

