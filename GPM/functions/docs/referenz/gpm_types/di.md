# D(I) — Dezimal-Identität

Dezimalbrüche als Relation (Zähler/Nenner/ggT). Modul: `gpm_types/di/`.

| Funktion | Beschreibung |
|----------|--------------|
| `parse_decimal(raw)` | → `DRelation` |
| `encode_di(raw)` | → `(whole, den_reduced, ggt)` |
| `decode_di(...)` | → Dezimalstring |
| `relation_key(raw)` | Kanonischer Schlüssel |

## Beispiel

```python
from gpm_types.di.codec import encode_di, decode_di

whole, den, ggt = encode_di("3.14")
text = decode_di(whole, den, ggt)
```

## Siehe also

- Tests: `tests/types/di/test_di.py`
