# GPM functions — Dokumentation

Alles unter `GPM/functions/`. Keine Änderungen in `Ge-Prime-Matrix OG/`.

## Dokumentations-Index

| Thema | README | Inhalt |
|-------|--------|--------|
| **Grundfunktionen** | [grundfunktionen/README.md](grundfunktionen/README.md) | SI/Perm-Pipeline, API, Module, Tests |
| **Profile** | [profile/README.md](profile/README.md) | 33 AlphabetProfile, Normalisierung, Prime-Blöcke |
| **Benchmark** | [benchmark/README.md](benchmark/README.md) | Performance-Grenzen, Width-Gate, Tiefenanalyse |
| **Analyse (Phase 4a)** | [analyse/README.md](analyse/README.md) | ggT/kgV, DTW, Case, Compile, Gap-Symmetrie |
| **Agent-Kurzreferenz** | [agent.md](agent.md) | Ordner-Karte, CI-Befehle für Agents |

## Schnellbefehle

```bash
cd GPM/functions

python run_tests.py                  # alle Unit-Tests
python -m tools.perm_audit           # Perm-Invarianten 33/33
python -m tools.profile_benchmark    # Voll-Sweep ~54 s
```

## Benchmark-Artefakte (generiert)

- [benchmark/PROFILE_LIMITS.md](benchmark/PROFILE_LIMITS.md) — Tabellen-Report
- [benchmark/benchmark_results.json](benchmark/benchmark_results.json) — JSON-Rohdaten

## Phase

Phase 4a — Analyse-Schicht (Compare, DTW, Compile, Gap-Symmetrie). Phase 3d: 33 Profile, Perm-Audit, Benchmark.
