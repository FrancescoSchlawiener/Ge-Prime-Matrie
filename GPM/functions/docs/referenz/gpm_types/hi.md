# H(I) — Hybrid-Identität

Segmentierte Identität (S- und N-Segmente in einer Zeichenkette). Modul: `gpm_types/hi/`.

| Funktion | Beschreibung |
|----------|--------------|
| `parse_hi_segments(raw)` | → `HiPayload` mit typisierten Segmenten |
| Segment-Typen | `S`, `N`, … in Lesereihenfolge |

## Beispiel

```python
from gpm_types.hi.segments import parse_hi_segments

payload = parse_hi_segments("abc123def")
# Segmente nach Typ getrennt
```

## Siehe auch

- [si.md](si.md), [ni.md](ni.md)
- Tests: `tests/types/hi/test_hi.py`
