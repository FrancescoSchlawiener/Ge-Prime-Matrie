# GPM UI-Text (`GPM/ui-text/`)

Typsicheres UI-Vokabular und Erklär-Inhalte für die GPM Inferenz-Workbench. Kein Runtime-Parsing für Chrome-Strings — alle `t()`-Keys sind `as const` und werden zur Build-Zeit aufgelöst.

## Invarianten

| ID | Regel |
|----|-------|
| **I2-A** | Kein UI-Vokabular in `GPM/functions/`. Domain-Logik und Pedagogik-API bleiben sprachneutral; sichtbarer Text lebt unter `GPM/ui-text/` (Chrome + Markdown-Kapitel). |
| **I2-B** | Fachbegriffe Englisch: **Registry**, **Gaps**, **Tier**, **Token**, **Roundtrip**, **Steps**, **Spectroscope**. Diese Begriffe werden nicht übersetzt. |
| **I2-C** | Steuerelemente Deutsch (Buttons, Navigation, Hinweise, Fehlermeldungen). Module als `as const`; Lookup über `createTranslationEngine()` — kein JSON/YAML zur Laufzeit. |

## Struktur

```
GPM/ui-text/
  README.md
  de/                    # UI-Chrome (t()-Keys)
    shell.ts             — Brand, Navigation, Footer
    encode.ts            — Encodieren-Tab
    decode.ts            — Decodieren-Tab
    wortpaar.ts          — Wortpaar / Vergleichen
    ikurve.ts            — I-Kurve
    gpm.ts               — GPM-Datei
    datenbank.ts         — Datenbank
    explain.ts           — Erklärungen-Chrome (Sidebar, CTAs)
    feedback.ts          — Fortschritt, Fehler (snake_case = error.code)
    result.ts            — Gemeinsame Result-/Compare-Strings
    articles.ts          — Erklär-Kapitel-Metadaten (slug, title, summary, miniCalc)
    index.ts             — uiTextDe, createTranslationEngine
  content/
    erklaerungen/        — Markdown-Kapitel (kanonische Prosa)
      00-einstieg.md … 24-cipher-gpc.md
```

## Anbindung (Workbench Web)

- Vite-Alias: `@gpm/ui-text` → `GPM/ui-text/de`
- Vite-Alias: `@gpm/ui-text/articles` → `GPM/ui-text/de/articles.ts`
- Chrome: `GPM/workbench/web/src/i18n/t.ts`

```typescript
import { uiTextDe, createTranslationEngine } from "@gpm/ui-text";
export const t = createTranslationEngine(uiTextDe);
```

- Erklärungen: `web/src/content/index.ts` lädt Markdown via `import.meta.glob` aus `ui-text/content/erklaerungen/`

## Nicht migrieren

- API `steps[]`, `word_canonical`, Substanz-Werte (bleiben in Python, sprachneutral bzw. API-Pedagogik)
- `articles.ts` enthält nur Metadaten — der Artikeltext steht in `content/erklaerungen/*.md`
