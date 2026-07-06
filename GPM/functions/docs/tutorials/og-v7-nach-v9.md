# Tutorial: OG v7 lesen

Best-effort Lesen älterer `.gpm`-Dateien aus Ge-Prime-Matrix OG.

## Hintergrund

| | OG Web-App | GPM/functions |
|---|------------|---------------|
| Schreib-Standard | v7 | v9 |
| Lesen | v1–v7 | v4, v8, v9 + v7 best-effort |

## Schritt 1 — Version erkennen

```python
data = open("legacy.gpm", "rb").read()
assert data[:3] == b"GPM"
version = data[3]
print("Version:", version)
```

## Schritt 2 — Mit compat lesen

```python
from analysis.binary.compat import read_gpm_any
from analysis.compile.reconstruct import reconstruct_text

doc = read_gpm_any(data)
text = reconstruct_text(doc)
```

`read_gpm_any` routet:

- v4, v8, v9 → natives `read_gpm`
- v7 → best-effort Lift (flaches Token-Body wie v4)

## Schritt 3 — Neu als v9 schreiben

```python
from analysis.binary.format import write_gpm, VERSION

blob9 = write_gpm(doc, version=VERSION)
```

**Hinweis:** OG-Hierarchie/GAP-RLE aus v7 wird nicht immer vollständig in v9-Geometrie überführt — NL-Text-Rekonstruktion ist das Ziel.

## Was fehlt bei v7-Lesen?

- Volle Meta-Genom-Daten (OG-only)
- Manche OG-spezifischen Hierarchy-Felder

Siehe [../og/og-vs-gpm.md](../og/og-vs-gpm.md).

## Weiter

- [../referenz/binary-format.md](../referenz/binary-format.md)
- [../og/roadmap.md](../og/roadmap.md)
