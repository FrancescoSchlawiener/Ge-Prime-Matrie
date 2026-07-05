# GPM functions — Phase 2

## Modi

| Aufruf | Bedeutung |
|--------|-----------|
| `S(seq)` | Substanz (Default OG-Parität) |
| `encode()` / `decode()` | S(I) OG-Pfad |
| `encode_ni()` / `encode_di()` / `encode_hi()` | N(I), D(I), H(I) |
| `perm_space()` | Permutationsraum (≠ N(I)!) |
| `Lut()`, `Sk()`, `Sp()` | Reihenfolge-Modus |

## Struktur

Siehe [agent.md](agent.md) — Ordner-Karte.

## Tests

```bash
python GPM/functions/run_tests.py
```

72+ Tests inkl. Grenzwerte und Typ-Trennung.
