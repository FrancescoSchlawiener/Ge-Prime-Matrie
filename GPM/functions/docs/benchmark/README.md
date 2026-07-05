# GPM Profil-Performance-Benchmark

Empirische Grenzanalyse über alle **33 AlphabetProfile**. Der Benchmark misst Permutationsraum, Index-Breite, LUT-Eligibility, Roundtrip-Stabilität und Timing pro Pipeline-Schritt.

## Schnellstart

```bash
cd GPM/functions

# Voll-Sweep (~54 s, 3.691 Sweep-Punkte)
python -m tools.profile_benchmark

# CI-Smoke (in run_tests.py, <3 s)
python run_tests.py
```

## Output-Artefakte

| Datei | Inhalt |
|-------|--------|
| [PROFILE_LIMITS.md](PROFILE_LIMITS.md) | Auto-generierte Summary-Tabelle + Duplikat-Matrix + Timing @ L=32 |
| [benchmark_results.json](benchmark_results.json) | Maschinenlesbare Rohdaten aller Sweep-Punkte |

Nach Profil- oder Pipeline-Änderungen Benchmark neu laufen lassen und Artefakte committen.

---

## Tiefenanalyse (Referenzlauf 2026-07-05)

Der erfolgreiche Durchlauf über alle 33 implementierten Alphabete liefert empirisch untermauerte Erkenntnisse über die kombinatorischen Grenzen und die funktionale Skalierung des fraktalen Substrat-Raums.

| Kennzahl | Wert |
|----------|------|
| Sweep-Punkte | 3.691 |
| Gesamtlaufzeit | 53,83 s |
| Ø pro Sweep-Punkt | ~14,5 ms |
| Width-Skips | 167 |
| Roundtrip-Fehler | 0 |

---

## 1. Architektonische Validierung des Width-Gates

Das Kernproblem asymptotischer Fakultätsberechnungen

```
N_perm = n! / ∏(c_i!)
```

bei großen String-Längen wird durch ein **zweistufiges Schutzsystem** abgefangen:

```
[Kombinatorischer Input]  (z.B. L=48, unique)
            |
            v
+---------------------------+
| N_perm.bit_length() > 128 | --(Ja)--> failed_at=width_limit
+---------------------------+           (teure Schritte übersprungen)
            | (Nein)
            v
+---------------------------+
|     N_perm > 1_000_000    | --(Ja)--> failed_at=perm_index_limit
+---------------------------+           (perm_index-Explosion blockiert)
            | (Nein)
            v
     [Regulärer Inferenzpfad]
            |
            v
  perm_index → encode_si → decode_si
  (optional: build_permutation_lut wenn L≤12 und N_perm≤10.000)
```

Implementierung: [`tools/profile_benchmark.py`](../tools/profile_benchmark.py) — `width_gate_blocks()`, `width_gate_reason()`.

### Quantitativer Effekt

Von 3.691 Testkonfigurationen wurden **167 Punkte** durch den Schutzfilter abgefangen:

| Filter | Bedingung | Wirkung |
|--------|-----------|---------|
| `width_limit` | `N_perm.bit_length() > 128` (16-Byte-Index) | Verhindert Big-Int-Pfade jenseits der Registerbreite |
| `perm_index_limit` | `N_perm > 1_000_000` | Blockiert kombinatorisches Backtracking in `perm_index` **vor** Speicher-Overflow |

Bei Width-Skip werden **nicht** ausgeführt: `perm_index`, `build_permutation_lut`, `encode_si`, `decode_si`. Timing-Felder bleiben `null`.

Erlaubt bleiben: `prepare_substrate`, `substance_for_profile`, `calc_total_perms`, `perm_fits_*`-Flags.

---

## 2. Inferenz-Erkenntnisse & Grenz-Analyse

### `all_same` — totale Redundanz

Muster: ein Zeichen L-mal wiederholt (z.B. `AAAA…`).

```
N_perm = L! / L! = 1   →   I = 1
```

**Ergebnis:** Fehlerfreier Roundtrip bis **L = 64** für alle 33 Profile. Kein Permutationsindex muss aufgespannt werden; Komplexität **O(L)** (sequenzielle Prim-Multiplikation in `substance.py`).

### `unique` — volle Disjunktion

Muster: L verschiedene Zeichen → `N_perm = L!`.

| Länge L | N_perm | Status |
|---------|--------|--------|
| ≤ 8 | ≤ 8! = 40.320 | Roundtrip OK, Sub-ms |
| 10 | 10! = 3.628.800 | `perm_index_limit` (Schwellwert 1 Mio.) |
| 32, 48, 64 | astronomisch | Width-Gate / perm_index_limit |

**Roundtrip-Grenze im Sweep-Raster:** max **L = 8** für `unique` (nächster Sweep-Punkt L = 10 scheitert am Limit).

Praktische Inferenz bei strikter Eindeutigkeit: kurze, hochdichte Token (Morpheme, IDs, komprimierte Wurzeln).

### LUT-Integrität

| Konstante | Wert | Benchmark-Bestätigung |
|-----------|------|----------------------|
| `MAX_LUT_BUILD_LENGTH` | 12 | LUT-Build bis L = 12 wenn N_perm ≤ 10.000 |
| `MAX_LUT_BENCHMARK_N` | 10.000 | Zusätzliche Cap im Benchmark (volle LUT würde bei 12! scheitern) |

Bei höherer kombinatorischer Dichte: tabellenfreier Codec-Pfad (`perm_index` / `perm_decode`).

---

## 3. Komplexitätsklassen & Hardware-Timing

Die Heuristik in [`tools/benchmark_report.py`](../tools/benchmark_report.py) klassifiziert alle 33 Profile im erfolgreichen Raum als **O(L)** — lineare Skalierung, keine algorithmischen Ausreißer.

### Mikrosekunden @ L = 32 (`unique`)

Bei L = 32 unter `unique` greift das Width-Gate; teure Perm-Schritte werden übersprungen (`—` in PROFILE_LIMITS.md). Messbar bleiben:

| Schritt | Typische Spanne |
|---------|-----------------|
| `normalize_ms` / `prepare_substrate_ms` | 0,001 – 0,009 ms |
| `substance_ms` | 0,001 – 0,009 ms |

Selbst komplexe Normalisierungen (Mongolian Positionsformen, Aesthetic Hieroglyphs Gardiner-Map) zeigen keinen nennenswerten Overhead.

---

## 4. Sweep-Konfiguration

### Dimensionen

| Dimension | Werte |
|-----------|-------|
| Profile | 33 (`registry.all_profiles()`) |
| Längen L | 1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 20, 24, 32, 48, 64 |
| Muster | `unique`, `all_same`, `pairs`, `triple`, `max_multiplicity` |
| Duplikat-Matrix | L ∈ {4, 8, 12, 16}, k ∈ {1…L} (`all_same_k`) |

Teststring-Generatoren: [`tools/benchmark_patterns.py`](../tools/benchmark_patterns.py).

### Abgeleitete Grenzwerte pro Profil

| Feld | Bedeutung |
|------|-----------|
| `max_L_roundtrip_unique` | Größtes L mit Roundtrip (`unique`) |
| `max_duplicate_count_all_same` | Größtes L mit Roundtrip (`all_same`) |
| `max_L_with_lut` | Größtes L ≤ 12 mit LUT-Build OK |
| `max_N_perm_fits_16` | Größtes N_perm innerhalb 16-Byte-Index |
| `first_fail` | Erster Fehlerpunkt im Sweep |
| `complexity_class` | O(L) / O(N_perm) Heuristik |

Referenztabelle: [PROFILE_LIMITS.md](PROFILE_LIMITS.md) (Summary).

---

## 5. CI-Sicherheit

| Test | Laufzeit | Prüft |
|------|----------|-------|
| `tests/benchmark/test_profile_limits_smoke.py` | < 3 s | L=1 Roundtrip, Width-Gate-Invariante, LUT-Länge |
| `tests/alphabets/test_perm_identity_all_profiles.py` | in run_tests | Anagramm S/I, LUT-Kaskade |
| `python -m tools.perm_audit` | ~1 s | 33/33 Perm-Invarianten (manuell) |

**327 Tests** in `run_tests.py` (Stand nach Perm-Audit).

---

## 6. Fazit & Systemstatus

Der Benchmark beweist: die mathematische Engine operiert **deterministisch, plattformunabhängig und stabil**. Grenzwerte sind reproduzierbare Hardwarerealität, keine Schätzungen.

| Aspekt | Status |
|--------|--------|
| Strukturelle Parität | 33 Profile, disjunkte Primblöcke, kollisionsfrei |
| RAM-Sicherheit | Width-Gate + Hieroglyphen-Endfilter (silent discard) |
| Perm-Invarianten | Anagramm-Regel verifiziert (`perm_audit` 33/33) |
| CI | Smoke + Perm-Identity bei jedem Commit |

### Nächste Härtungsstufe (optional)

- Feinere Sweep-Stufen zwischen L = 8 und L = 10 (L = 9 fehlt im Raster)
- Profil-spezifische Anagramm-Korpus-Paare statt generischer 3-Zeichen-Reversal
- Benchmark-Diff bei PRs (JSON-Vergleich)

---

## Siehe auch

- [Grundfunktionen](../grundfunktionen/README.md) — Pipeline, API, Perm-Invarianten
- [Profile](../profile/README.md) — alle 33 AlphabetProfile
- [agent.md](../agent.md) — kompakte Agent-Referenz
