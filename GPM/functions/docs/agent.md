# GPM — Agent-Hinweise (Phase 2)

Alles unter `GPM/functions/` — **keine** Änderungen in `Ge-Prime-Matrix OG/`.

## Ordner-Karte

```
functions/
  alphabets/          # Schicht 0 — je Schrift eigener Ordner
    og/               # frozen Referenz (Parität)
    roman/            # Latin aktiv (map + normalize)
    greek/
    cyrillic/
  perm/               # Permutations-Mathematik + LUT (nicht stdlib math!)
  gpm_types/          # Schicht 1 — I/O-Typen (nicht stdlib types!)
    classify.py       # S|N|D|H — einzige Klassifikations-Wahrheit
    si/               # Schriftsatz S(I)
    ni/               # Ganzzahl N(I)
    di/               # Dezimal D(I) aus N-Komponenten
    hi/               # Gemischt H(I)
  db/
  tools/
  tests/
    alphabets/
    types/
    boundary/
    parity/           # OG-Imports nur hier
```

## Typ-Tabelle (User ↔ Code)

| User | Typ | Modul |
|------|-----|-------|
| Schriftsatz, S, encode/decode | **S(I)** | `gpm_types/si/` |
| Ganzzahl | **N(I)** | `gpm_types/ni/` |
| Dezimal (3 N-Werte) | **D(I)** | `gpm_types/di/` |
| Gemischt String+Zahl | **H(I)** | `gpm_types/hi/` |
| Permutationsraum | `perm_space()` / `N_perm` | `gpm_types/si/codec.py` — **nicht** N(I)! |

## D(I) — drei N-Werte

Dezimal `4,16` → `(whole=4, den_reduced=25, ggt=4)` — alle Felder sind N(I)-Integer.

## H-Kanonisierungs-Garantie (`gpm_types/hi/codec.py`)

Da H(I) eine Liste typisierter Segmente ist (z.B. `[(S, "ABC"), (N, "123")]`), muss die Segment-Reihenfolge im Code **exakt der physikalischen Lese-Reihenfolge** des Eingabestrings entsprechen. **Keine nachträgliche Sortierung nach Typ** — sonst kollidieren `"ABC123"` und `"123ABC"` und die relationale Struktur des gemischten Wertes geht verloren.

## Eindeutigkeit

- Klassifikation nur über `gpm_types/classify.py`
- Reines S, N oder D darf nicht als H kodiert werden
- OG-Parität nur Roman/OG: `encode()` / `decode()`

## Compatibility-Shims

Flache Dateien (`alpha_roman.py`, `si.py`, …) re-exportieren neue Pfade — bitte neue Imports verwenden.

## Tests

```bash
python GPM/functions/run_tests.py
```
