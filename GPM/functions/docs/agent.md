# Entwickler-Kurzreferenz

Kompakte Karte für **Contributors** am Repo — Ordnerstruktur, Befehle, Regeln.

**Neue Leser ohne Codebase-Kenntnis:** starte bei [docs/README.md](README.md) und den thematischen READMEs (Grundfunktionen, Profile, Analyse, Benchmark).

**API-Nachschlagen:** [referenz/index.md](referenz/index.md) — vollständiger Funktions-Index mit Links zu Detailseiten.

Alles unter `GPM/functions/`. Die Web-App liegt separat in `Ge-Prime-Matrix OG/`.

## Ordner-Karte

```
functions/
  alphabets/          33 Schriftprofile (siehe profile/README.md)
  perm/               Permutations-Index, LUT
  gpm_types/          S/I-Codec, N(I), D(I), H(I)
  analysis/           Textanalyse, Code, Binary I/O
    algebra/          Schicht 0 — Gates, Fusion, substance_kernel, window_fold
                      Doku: docs/analysis/algebra-layer.md, docs/analysis/basis-layer.md
    basis/            Signaturen, Index, Tiered Compare, Korpus-API
  tests/              Unit-Tests (siehe referenz/tests.md)
  tools/              perm_audit, profile_benchmark
  docs/               Diese Dokumentation
    referenz/         API-Detailseiten
    tutorials/        Geführte Walkthroughs
    og/               OG-Brücke & Roadmap
```

Vollständige Profil-Liste und Normalisierungsregeln: [profile/README.md](profile/README.md).

## S(I) Codec

- `encode_si(raw, profile)` / `decode_si(substance, index, profile)` — alle 33 Profile
- `encode()` / `decode()` — nur `AlphabetProfile.OG` (Legacy-Parität)

Detail: [referenz/gpm_types/si.md](referenz/gpm_types/si.md)

Perm-Invariante (Anagramm-Regel): gleiches S, verschiedenes I — [grundfunktionen/README.md](grundfunktionen/README.md).

## Reduktions- & Design-Regeln

- **Indisch / Javanese / Hieroglyphen:** siehe [profile/normalisierung.md](profile/normalisierung.md)
- **Logogramm-Leak-Verbot:** Aesthetic Hieroglyphs — unbekannte Glyphen silent discard
- **SMP-Codepoints:** `alphabets/unicode_utils.py` für epigraphische Profile
- **Verbotene Zeichensätze:** CJK, Tibetan, Khmer, Burmese, Sinhala — siehe Profile-Doku

## Tests & Benchmark

```bash
cd GPM/functions

python run_tests.py
python -m tools.perm_audit
python -m tools.profile_benchmark
```

Test-Landschaft: [referenz/tests.md](referenz/tests.md)  
Benchmark-Output: [benchmark/PROFILE_LIMITS.md](benchmark/PROFILE_LIMITS.md)

## Analyse-Schicht (Kurz)

- NL: `compile_text` / `reconstruct_text` — [referenz/compile.md](referenz/compile.md)
- Code: `compile_source` / `reconstruct_source` — [referenz/code/index.md](referenz/code/index.md)
- Hybrid: `compile_hybrid` / `reconstruct_hybrid` — [referenz/code/compile-hybrid.md](referenz/code/compile-hybrid.md)
- Binary: `write_gpm` / `read_gpm` — [referenz/binary-format.md](referenz/binary-format.md)

Überblick: [analyse/README.md](analyse/README.md) · Navigation: [analyse/index.md](analyse/index.md)

### Algebra / Basis — Contributor-Regeln (Phase F)

- **F-1:** Substanz-Vergleich importieren über `analysis.algebra.substance_kernel` — nicht direkt aus `analysis/substance/` in neuem Code
- **F-A:** Fenster-LCM nur via `exponent_window_to_substance` in `window_fold.py`
- **F-B:** Gewichts-Literale nur in `algebra/fusion.py` — Blends über `log_jaccard_basis_blend`, `fuse_structure_tier`, `fuse_curve_tier`
- Tiered Compare: Default `max_tier=CompareTier.BASIS` für Korpus; Voll-DTW nur explizit (Tier 4)
- Doku: [analysis/algebra-layer.md](analysis/algebra-layer.md), [analysis/basis-layer.md](analysis/basis-layer.md)

## OG-Bezug

Was portiert ist vs. Roadmap: [og/portiert.md](og/portiert.md), [og/roadmap.md](og/roadmap.md)

## Siehe auch

- [Doku-Hub](README.md)
- [Referenz-Index](referenz/index.md)
- [Grundfunktionen](grundfunktionen/README.md)
- [Benchmark](benchmark/README.md)
