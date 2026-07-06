# Test-Landschaft

Unit-Tests unter `GPM/functions/tests/`. Befehl: `python run_tests.py`.

## Nach Schicht

| Ordner | Prüft | Wichtige Module |
|--------|-------|-----------------|
| `tests/alphabets/` | 33 Profile, Normalisierung, LUT | `alphabets/`, `perm/` |
| `tests/analysis/` | Compile, Binary, Code, Kurven | `analysis/` |
| `tests/parity/` | OG-Parität | `gpm_types/si` |
| `tests/benchmark/` | CI Smoke Width-Gate | `tools/profile_benchmark` |
| `tests/types/` | N(I), D(I), H(I) | `gpm_types/` |
| `tests/boundary/` | PayloadKind-Klassifikation | `gpm_types/classify` |

## Analyse — wichtige Testdateien

| Datei | Invariante |
|-------|------------|
| `test_compile.py` | Gap-Symmetrie, Rekonstruktion |
| `test_case.py` | Case/Explicit Roundtrip |
| `test_binary.py` | v4/v8 Roundtrip, CRC |
| `test_v9_binary.py` | v9 Geometrie |
| `test_v9_hybrid.py` | Hybrid → v9 Block-Tree |
| `test_code_tokenizer_guards.py` | Guards A/B |
| `test_code_hybrid_gaps.py` | Fence Gap-Invariante |
| `test_code_interference.py` | NL vs CODE Kontext |
| `test_curves_fusion.py` | LISTEN/SILENT, analyze_pair |
| `test_hierarchy.py` | Struktur-Partition |
| `test_cell_geom.py` | Zell-Abdeckung |

## Algebra / Basis — Blocker-Tests (Phase D–F)

Invarianten für Schicht 0 (`algebra/`) und Schicht 1 (`basis/`). Gesamtanzahl aller Tests: ~593 via `python run_tests.py`.

| Datei | Invariante |
|-------|------------|
| `test_substance_kernel_imports.py` | **F-1** — Produktionscode importiert `substance_kernel` |
| `test_exponent_window_lcm.py` | **F-A** — `exponent_window_to_substance` zentralisiert |
| `test_scan_windows_profile.py` | **F-A + E-A** — Log-Pfad bei profil-geflaggten Fenstern |
| `test_log_jaccard_blend.py` | **F-B** — `log_jaccard_basis_blend` kanonisch |
| `test_weight_literal_audit.py` | **F-B** — keine Inline-Gewichts-Literale in Blends |
| `test_tier_fusion_blends.py` | **F-B** — Structure/Curve-Tier über `fusion.py` |
| `test_fingerprint_log_invariant.py` | **E-A** — kein Integer-LCM bei Log-Fingerprint |
| `test_i_ratio_invariant.py` | **E-B** — `i_ratio_similarity` in [0, 1] |
| `test_typed_sketch_weight.py` | **E-C** — typed_sketch Default-Gewicht 0.0 |
| `test_sparse_counter_invariants.py` | **D-A** — O(k) Cosine/Jaccard |
| `test_coupled_invariants.py` | **D-B** — I×S-Kopplung |
| `test_guard_audit.py` | **D-C** — `profile_symmetry_guard` first |
| `test_basis_invariants.py` | Basis-Invarianten A/B |
| `test_compare_tiered.py` | Tiered Compare Tier 0–4 |
| `test_corpus_compare.py` | Korpus-Zwei-Stufen-Suche |
| `test_basis_corpus_smoke.py` | Korpus-Smoke @500 Docs (<150 ms) |
| `test_algebra_package_exports.py` | `analysis.algebra` Public API |
| `test_minhash.py` | Härtungs-Inv. A — `prime_minhash` |
| `test_basis_index.py` | Index + Postings |
| `test_basis_signature.py` | Signatur-Bau |

Doku: [analysis/algebra-layer.md](../analysis/algebra-layer.md), [analysis/basis-layer.md](../analysis/basis-layer.md).

## Parity

| Datei | OG-Abgleich |
|-------|-------------|
| `test_si.py` | encode/decode OG |
| `test_substrate_og.py` | Substanz-Berechnung |
| `test_alpha_og.py` | 27-Symbol-Alphabet |

## CI-Empfehlung

```bash
cd GPM/functions
python run_tests.py
python -m tools.perm_audit
python -m pytest tests/benchmark/ -q  # optional schneller Smoke
```

## Siehe auch

- [tools.md](tools.md)
- [../benchmark/README.md](../benchmark/README.md)
- [../agent.md](../agent.md)
