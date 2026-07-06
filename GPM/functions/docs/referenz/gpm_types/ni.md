# N(I) — Ganzzahl-Identität

Ganzzahlen als eigener Pointer-Typ. Modul: `gpm_types/ni/`.

| Funktion | Beschreibung |
|----------|--------------|
| `canonical_n(raw)` | Normalisierte String-Form |
| `canonical_n_int(raw)` | int nach Normalisierung |
| `encode_ni(raw)` | → `(pointer_id, canonical)` |
| `decode_ni(ptr_id, registry)` | → Ziffernstring |

Code-Lexer erzeugt `PointerKind.N` für numerische Literale.

## Beispiel

```python
from gpm_types.ni.codec import encode_ni

ptr, canon = encode_ni("0042")
# canonical führt führende Nullen zusammen
```

## Siehe auch

- [si.md](si.md)
- Tests: `tests/types/ni/test_ni.py`
