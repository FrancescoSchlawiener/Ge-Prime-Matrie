# Entfernte Duplikate (library-first)

| Datei | Grund | Ersatz |
|-------|-------|--------|
| `lib/tensorraum/normalize.ts` | Duplikat von `analysis/code/canonicalize.py` | API `normalized_code` |
| `lib/tensorraum/detectLanguage.ts` | Duplikat von `analysis/code/languages.py` | `lib/code/languages.ts` + `GET /api/code/languages` |
| `constants.ts` → `SUPPORTED_LANGUAGES` | Drift gegen Python | API languages |
| `constants.ts` → `TOKENIZER_REGEX`, `TAG_REGEX` | Tot, nie genutzt | — |
| `decompiler.ts` Rekonstruktionskern auf Compile-Pfad | Duplikat `decompile.py` | API `reconstructed` |

Neue Schicht: `lib/code/` — API-Client + Manifest-Filter. Wire-Decode bleibt in `lib/tensorraum/codeWire.ts` bis vollständige Umbenennung.
