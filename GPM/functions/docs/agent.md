# Entwickler-Kurzreferenz

Kompakte Karte für **Contributors** am Repo — Ordnerstruktur, Befehle, Regeln.

**Neue Leser ohne Codebase-Kenntnis:** starte bei [docs/README.md](README.md) und den thematischen READMEs (Grundfunktionen, Profile, Analyse, Benchmark).

Alles unter `GPM/functions/`. Die Web-App liegt separat in `Ge-Prime-Matrix OG/`.

## Ordner-Karte

```
functions/
  alphabets/          33 Schriftprofile (siehe profile/README.md)
  perm/               Permutations-Index, LUT
  gpm_types/          S/I-Codec, N(I), D(I), H(I)
  analysis/           Textanalyse, Code, Binary I/O
  tests/              Unit-Tests
  tools/              perm_audit, profile_benchmark
  docs/               Diese Dokumentation
```

Vollständige Profil-Liste und Normalisierungsregeln: [profile/README.md](profile/README.md).

## S(I) Codec

- `encode_si(raw, profile)` / `decode_si(substance, index, profile)` — alle 33 Profile
- `encode()` / `decode()` — nur `AlphabetProfile.OG` (Legacy-Parität)

Perm-Invariante (Anagramm-Regel): gleiches S, verschiedenes I — Details in [grundfunktionen/README.md](grundfunktionen/README.md).

## Reduktions- & Design-Regeln

- **Indisch / Javanese / Hieroglyphen:** siehe [profile/README.md](profile/README.md)
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

Benchmark-Output: [benchmark/PROFILE_LIMITS.md](benchmark/PROFILE_LIMITS.md), `benchmark/benchmark_results.json`

## Analyse-Schicht (Kurz)

- NL: `compile_text` / `reconstruct_text`
- Code: `compile_source` / `reconstruct_source` — py, js, html
- Hybrid: `compile_hybrid` / `reconstruct_hybrid`

Details: [analyse/README.md](analyse/README.md)

## Siehe auch

- [Doku-Hub](README.md)
- [Grundfunktionen](grundfunktionen/README.md)
- [Benchmark](benchmark/README.md)
