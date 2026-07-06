# OG → GPM Modul-Karte

| OG-Pfad | GPM/functions | Status |
|---------|---------------|--------|
| `ge_prime/compare.py` | `analysis/substance/compare.py` | ✅ |
| `ge_prime/diff.py` | `analysis/substance/diff.py` | ✅ |
| `ge_prime/dtw.py` | `analysis/geom/dtw.py` | ✅ |
| `ge_prime/substance_align.py` | `analysis/align/substance_align.py` | ✅ |
| `ge_prime/i_curve.py` | `analysis/curves/i_curve.py` | ✅ |
| `ge_prime/meta_genome.py` | `analysis/meta/` | ✅ |
| `ge_prime/structure_validation.py` | `analysis/validation/structure.py` | ✅ |
| `ge_prime/spectroscope.py` | `analysis/search/spectroscope.py` | ✅ |
| `ge_prime/hierarchy_search.py` | `analysis/search/hierarchy_search.py` | ✅ |
| `ge_prime/hierarchy.py` | `analysis/hierarchy/` | ✅ |
| `ge_prime/cipher.py` | `analysis/security/cipher.py` | ✅ opt-in |
| `ge_prime/relation_profile.py` | `analysis/profile/relation.py` | ✅ |
| `ge_prime/sparkline.py` | `analysis/ui/sparkline.py` | ✅ |
| `ge_prime/linguistics/` | — | ❌ Roadmap (DB) |
| `ge_prime/language_detect.py` | — | ❌ Roadmap |
| `gpm/format.py` | `analysis/binary/format.py` | ⚠️ v9 vs v7 |
| `gpm/reader.py` | `analysis/binary/reader.py` + `search.py` | ✅ |
| `gpm/hierarchy_geom.py` | `analysis/hierarchy/geom.py` | ✅ |
| `gpm/reconstruct_v7.py` | `analysis/reconstruct/derive_gaps.py` | ⚠️ anderer Ansatz |
| `gpm/cipher_wrap.py` | `analysis/binary/gpc.py` | ✅ opt-in |
| `pipeline/process.py` | `analysis/compile/compiler.py` | ⚠️ partial |
| `pipeline/size_compare.py` | — | ❌ |
| `db/repository.py` | — | ❌ |
| `web/handlers/*` | — | ❌ bewusst OG |
| — | `analysis/algebra/` | ✅ Phase 4b+ |
| — | `analysis/basis/` | ✅ Phase 4b+ |
| — | `analysis/code/*` | ✅ GPM-neu |
| — | `alphabets/*` (33 Profile) | ✅ GPM-neu |
| — | `gpm_types/ni,di,hi` | ✅ GPM-neu |

Legende: ✅ portiert · ⚠️ teilweise · ❌ fehlt

## Siehe auch

- [og-vs-gpm.md](og-vs-gpm.md)
- [roadmap.md](roadmap.md)
- [../analysis/basis-layer.md](../analysis/basis-layer.md)
- [../referenz/index.md](../referenz/index.md)
