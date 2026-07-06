# Von OG portiert / in GPM angekommen

Selektive Übernahme in `GPM/functions/analysis/` — **ohne** Web-Handler.

| OG-Modul | GPM-Äquivalent | Status |
|----------|----------------|--------|
| `ge_prime/compare.py` ggT/kgV | `analysis/substance/compare.py` | portiert |
| `ge_prime/diff.py` | `analysis/substance/diff.py` | portiert |
| `ge_prime/dtw.py` | `analysis/geom/dtw.py` | portiert |
| `gpm/hierarchy_geom.py` build | `analysis/hierarchy/geom.py` | portiert |
| `split_page_spans` | `analysis/hierarchy/geom.py` | portiert |
| `gpm/cell` Geometrie | `analysis/cell/geom.py` | portiert |
| `gpm/format.py` v4/v7 Lesen | `analysis/binary/format.py`, `compat.py` | teilweise |
| `ge_prime/substance_align.py` | `analysis/align/substance_align.py` | portiert |
| `ge_prime/i_curve.py` | `analysis/curves/i_curve.py` | portiert (Literal/DTW) |
| `analyze_pair` / `analyze_pair_full` | `analysis/curves/compare.py` | 4-Achsen + Full-Preset |
| `ge_prime/spectroscope.py` | `analysis/search/spectroscope.py` | portiert |
| `ge_prime/hierarchy_search.py` | `analysis/search/hierarchy_search.py` | portiert |
| `ge_prime/cipher.py` + `gpm/cipher_wrap.py` | `analysis/security/cipher.py`, `analysis/binary/gpc.py` | portiert (opt-in) |
| `gpm/reader.py` search_by_* | `analysis/binary/search.py` | portiert (Invariante B) |
| `ge_prime/relation_profile.py` | `analysis/profile/relation.py` | portiert |
| `ge_prime/structure_validation.py` | `analysis/validation/structure.py` | portiert (meta_profile_audit) |
| `ge_prime/substance_span.py` | `analysis/span/substance_span.py` | portiert |
| `ge_prime/sparkline.py` | `analysis/ui/sparkline.py` | portiert |
| `ge_prime/linguistics/profiles.py` (Kern) | `analysis/profile/prime_profile.py` | profil-aware |
| Anagramm-Korpus-Protokoll | `analysis/corpus/protocol.py` | Stub |
| Algebra + Basis-Layer (Phase 4b+) | `analysis/algebra/`, `analysis/basis/` | portiert |
| Pipeline normalize/encode | `gpm_types/si`, `alphabets/` | portiert + erweitert |

## Netto-Neu in GPM (nicht aus OG)

| Feature | Modul |
|---------|-------|
| 33 AlphabetProfile | `alphabets/` |
| Code-Tokenizer 19 Sprachen | `analysis/code/` |
| Hybrid Markdown | `analysis/code/hybrid.py` |
| v9 Block-Tree | `analysis/binary/format.py` |
| N(I), D(I), H(I) | `gpm_types/` |

## Tests als Paritäts-Nachweis

- `tests/parity/test_si.py`
- `tests/parity/test_substrate_og.py`
- `tests/parity/test_alpha_og.py`

## Siehe auch

- [og-vs-gpm.md](og-vs-gpm.md)
- [roadmap.md](roadmap.md)
