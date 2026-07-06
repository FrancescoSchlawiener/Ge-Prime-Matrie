# Basis-Layer — gestaffelter Dokument-Vergleich

Optionaler Zusatzpfad für Korpus-Suche und Paar-Vergleich ohne O(n²)-Voll-DTW.

## Tiers

| Tier | Name | Inhalt |
|------|------|--------|
| 0 | GATE | `profile_symmetry_guard`, Prim-Disjunktion |
| 1 | BASIS | Log-Profil ggT/kgV, Jaccard, Relations-Sketch (renormiert) |
| 2 | STRUCTURE | Meta-Genom, Relations-Profil, shared_prime_count-Gate |
| 3 | CURVES | substance_align, i_curve |
| 4 | FULL | `analyze_pair_full` |

Default für Korpus: `max_tier=CompareTier.BASIS`. Voller Vergleich nur explizit (`Tier4`).

## Invarianten

**Basis-Invariante A (Algebra):** `profile_symmetry_guard` — kein Cross-Profile-Vergleich.

**Basis-Invariante B (Algebra):** `profile_log_norm` — O(k) Log-Summe, kein `profile_to_vector`.

**Härtungs-Invariante A (MinHash):** `prime_minhash` — Exponent $c_i$ als virtuelle Hash-Beiträge + profil-Salt.

**Härtungs-Invariante B (Renorm):** ohne `relation_sketch` → Gewichte 0.67/0.33 (Summe 1.0).

## API

```python
from analysis.basis import (
    build_basis_signature,
    build_basis_index,
    extend_basis_index,
    query_candidates,
    CandidateQueryResult,
    compare_documents_tiered,
    find_similar_documents,
    CorpusSearchResult,
    CompareTier,
)
```

### Korpus-Suche (zwei Stufen)

1. `query_candidates` — Postings + `compare_basis_signatures_only` (max `top_k * 5`)
2. `compare_documents_tiered` — nur für Survivors

Bulk-Index: `build_basis_index(..., include_relation_sketch=False)` für Performance.

### `analyze_pair` Prefilter

```python
analyze_pair(doc_a, doc_b, basis_prefilter=True)  # Tier 1 Gate
analyze_pair(doc_a, doc_b, basis_prefilter=query_sig)  # vorberechnete Signatur
```

## Module

- `analysis/algebra/` — Gates, Fold, Log-Metriken, MinHash, typed_bridge, substance_kernel, sparse_counter, window_fold, offset, tier_fusion
- `analysis/basis/` — Signature, Index, Scoring, Tiered Compare, Corpus-API

### Phase D — Algebra-Erweiterungen

- `minhash_band_distance` — optionaler Index-Vorfilter (`query_candidates(..., minhash_min_band=0.1)`)
- `substance_hint` — Anagramm-Bucket via `anagram_class_key`
- `typed_sketch_jaccard` — in Tier-1-Detail (Gewicht 0 im Default-Score)
- **Härtungs-Inv. D-A:** `sparse_counter` — O(k) Cosine/Jaccard
- **Härtungs-Inv. D-B:** `coupled_point_similarity` — i × s
- **Härtungs-Inv. D-C:** Guard an profil-geflaggten paarweisen APIs

## Phase E — Härtungs-Invarianten E-A / E-B / E-C

- **E-A (Log-LCM):** `fingerprint_similarity` und `scan_windows(..., profile=…)` nutzen den Log-Pfad — kein Integer-LCM bei großen Exponenten; Metadaten `window_lcm` via `exponent_window_to_substance`
- **E-B (I-Ratio):** `i_ratio_similarity` in `algebra/i_metrics.py` — Ergebnis immer in [0, 1]; Guard bei ungültigen Inputs
- **E-C (typed_sketch):** `typed_sketch_jaccard` — Default-Gewicht **0.0** im Tier-1-Score (opt-in über `include_relation_sketch=True`)

Blocker-Tests: `test_fingerprint_log_invariant.py`, `test_i_ratio_invariant.py`, `test_typed_sketch_weight.py`, `test_scan_windows_profile.py`.

Schicht-0-Detail: [algebra-layer.md](algebra-layer.md).

## Phase F — Härtungs-Invarianten F-1 / F-A / F-B

- **F-1:** Alle Analyse-Pfade → `analysis.algebra.substance_kernel`; `substance/` = Legacy-Hülle
- **F-A:** `exponent_window_to_substance` nur für `window_lcm`-Metadaten bei `scan_windows(..., profile=…)`
- **F-B:** Gewichts-Literale nur in `algebra/fusion.py` (`log_jaccard_basis_blend`, `WEIGHTS_*`)

### Tier-Fusion & Gates (Phase F5)

- `_run_signature_gates` in `compare_tiered.py` — gemeinsame Gate-Logik für Voll-Doc- und Signatur-only-Pfade
- Structure-Tier: `fuse_structure_tier` (Meta + Relations + Bitmask)
- Curve-Tier: `fuse_curve_tier` (i_curve + substance)
- Import-Matrix (Auszug): `binary/search`, `pair/analyze_word_pair`, `algebra/fold`, `algebra/multiset`, `curves/i_curve`, `align/substance_align` → `substance_kernel`

## Freigabe-Checkliste

- [x] `profile_symmetry_guard` an allen Einstiegspunkten
- [x] `profile_log_norm` ohne BigInt-V
- [x] `CandidateQueryResult` mit `zero_reason`
- [x] `structure_score=None` in Prefilter (Option A)
- [x] Härtungs-Inv. A/B implementiert
- [x] Zwei-Stufen-Korpus + extend_basis_index
- [x] Phase D: substance_kernel, sparse_counter, window_fold
- [x] Härtungs-Inv. D-A/B/C Blocker-Tests
- [x] Phase E: Log-LCM-Pfad (E-A), i_ratio-Guard (E-B), typed_sketch-Gewicht 0 (E-C)
- [x] Phase F: substance_kernel-Dispatcher (F-1), exponent_window zentral (F-A), fusion-Gewichte (F-B)
- [x] `_run_signature_gates` + Tier-Fusion über `fusion.py`
- [x] Korpus-Smoke @500 Docs (<150 ms)

## Siehe auch

- [Algebra-Layer — Schicht 0](algebra-layer.md)
- [Vergleich & Kurven](../referenz/vergleich.md)
- [Test-Landschaft — Blocker D–F](../referenz/tests.md)
