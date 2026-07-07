# GPM Workbench — Maintainer Notes

Pedagogical web UI over `GPM/functions`. The Workbench does **not** duplicate math — all encoding, comparison, and document logic lives in the library; the API is a thin FastAPI wrapper.

## Layout

| Path | Role |
|------|------|
| `api/` | FastAPI routes, session store, pedagogical `steps[]` |
| `web/` | Vite + React + TypeScript SPA (hash router) |
| `start/` | Dev/bootstrap scripts (`run_dev.py`, `dev.bat`, `setup.bat`) |
| `scripts/` | Production (`run_prod.py`) and CI (`export_openapi.py`) |
| `render.yaml` | Render.com deploy blueprint |

Explain chapters live in **`GPM/ui-text/de/erklaerungen/`** (markdown, bundled via Vite `import.meta.glob` in `web/src/content/index.ts`). Chapter metadata: `GPM/ui-text/de/articles-data.ts`.

## Architecture pillars

1. **Library-first** — `api/main.py` inserts `GPM/functions` on `sys.path`; no forked algorithms.
2. **Pedagogy** — Every calc/compare response includes `steps[]` with titles, detail, and values (Säule 4).
3. **Explain links** — Routes return `explain_links` pointing to `/erklaerungen/…` chapters.
4. **Hermetic UI state** — `editorStore` and `compareStore` are isolated; only `openInCompare()` bridges Editor → Vergleichen with a frozen clone.

## Invariants

- **A (Hybrid):** Fences appear only in `fence_boundaries`, never in `registry_entries` or NL gaps. UI: `LivePanel` shows fences separately; gaps filtered in hybrid mode.
- **B (Sparkline):** I-curve endpoints downsample via `analysis.ui.sparkline.downsample_curve_points(..., limit=512)`.

### Runtime calibration (Phase 1 — P1-A..E)

| ID | Rule |
|----|------|
| P1-A | Never invoke `.py` in `for /f` without an explicit interpreter |
| P1-B | Reject `WindowsApps` paths and 0-byte Python stubs |
| P1-C | Python `major==3` and `minor>=10` |
| P1-D | Virtualenv only at `GPM/workbench/.venv` |
| P1-E | Successful discovery writes `GPM/workbench/.python-path` |

Start scripts: `start/dev.bat` (Windows), `start/dev.sh` (Unix). `dev.bat` always runs API via `.venv\Scripts\python.exe` after `bootstrap.py` if needed.

### UI text (Phase 2 — I2-A..C)

- UI chrome strings: `GPM/ui-text/de/` (`shell`, `encode`, `decode`, `wortpaar`, `ikurve`, `gpm`, `datenbank`, `explain`, `feedback`, `result`).
- Explain markdown: `GPM/ui-text/de/erklaerungen/`; metadata in `GPM/ui-text/de/articles-data.ts`.
- Frontend entry: `web/src/i18n/t.ts` → `createTranslationEngine(uiTextDe)`.
- Technical terms stay English (Registry, Gaps, Tier, Token, Roundtrip, Steps, Spectroscope).
- Do **not** move API `steps[]` or substance values into ui-text.

## Frontend conventions

- Max **300 lines** per `.ts`/`.tsx` (ESLint `max-lines`).
- **`fetch` only under** `web/src/api/` (`request.ts` + `endpoints/*`, assembled in `client.ts`).
- Hash routes: `#/codec/encodieren`, `#/codec/decodieren`, `#/vergleichen/wortpaar`, `#/vergleichen/ikurve`, `#/gpm`, `#/datenbank`, `#/erklaerungen/:chapter`
- OpenAPI codegen: `cd web && npm run codegen` (reads `openapi.snapshot.json`).

### Feature-page folder pattern (reference: `web/src/pages/GpmPage/`)

Every main tab uses the same layout:

```
FeatureView/
  FeatureView.tsx    # orchestrator only — wire hooks + child components (<80 lines)
  useFeature.ts      # useState, api calls, handlers
  FeatureForm.tsx    # inputs + submit
  FeatureResults.tsx # result display (when applicable)
```

Shell routes (`CodecPage.tsx`, `VergleichenPage.tsx`) stay thin: `SubTabNav` + `<Outlet />`.

## Local dev

```bash
cd GPM/workbench
pip install -r requirements.txt
cd web && npm install && cd ..
python start/run_dev.py
```

Or: `npm run dev` (same entry). Windows: `dev.bat` or `start/dev.bat`.

Open `http://127.0.0.1:5173` — API proxied to `:8000`.

## Tests

```bash
cd GPM/workbench
PYTHONPATH=../functions pytest api/tests -q
```

```bash
cd GPM/functions
python -m pytest tests/analysis/test_corpus_batch_gate.py -q
```

```bash
cd GPM/workbench/web
npm run lint && npm run build
```

## Backend-Härtung (Phase 0c+)

| Endpoint | OG-Falle | Lösung |
|----------|----------|--------|
| `/api/editor/compile` | Wiederholtes Tokenisieren | CAS-LRU via SHA-256 (`api/cache/document_cache.py`) |
| `/api/calc/*` | Doppelte Formeln für UI | `InferenceTrace` + Steps nur Mapping (`analysis/inference/trace.py`) |
| `/api/compare/corpus/*` | O(n) Tiered-Loops | `batch_gate_candidates` + lazy `doc_loader` |
| `/api/editor/gpm/read` | Korrupte Streams im RAM | Pydantic `Base64Bytes` + GPC fast-fail 401 |
| `/api/compare/redundancy/scan` | String-Duplikate in JSON | Index-only `registry_ids` / `hit_positions` |

**Weitere Guards:** Compile warm-up (`api/cache/warmup.py`), Session-LRU (`max_refs=500`), Single-Flight bei parallelen Compiles, `include_steps` Flag auf Calc-Requests.

**Fehlerformat:** `{"error": {"code": "...", "message": "...", "details": {...}}}` via `WorkbenchError`.

## Code-Werkzeug (library-first)

| Endpoint | Rolle |
|----------|--------|
| `GET /api/code/languages` | Sprachen aus `analysis/code/languages.py` |
| `POST /api/code/manifest` | Primary + eingebettete Sprachen (HTML script/style) |
| `POST /api/code/canonicalize` | normalize → compile → wire_b64 + reconstructed |
| `POST /api/tensorraum/canonicalize` | Deprecated Alias |

Client: `web/src/lib/code/` — API-Client + Manifest-Filter. Wire-Decode: `web/src/lib/tensorraum/codeWire.ts`. Entfernte Duplikate: `web/src/lib/code/REMOVED.md`.

Vertrag: `GPM/functions/docs/analyse/fractal-code-contract.md`.

## Deploy (Render)

See `render.yaml` — bind `0.0.0.0:$PORT`, ephemeral filesystem (in-memory session store only).

## Key API surfaces

| Area | Prefix | Used by |
|------|--------|---------|
| System | `/api/health`, `/api/profiles` | Shell, ProfilePicker |
| Calc | `/api/calc/*` | Erklärungen Mini-Rechner |
| Editor | `/api/editor/*` | Editor (compile, reconstruct, gpm, spectroscope) |
| Compare | `/api/compare/*` | Vergleichen (wortpaar, dokumente, korpus, redundanz) |

## Related docs

- Chapters: `GPM/ui-text/de/erklaerungen/00-einstieg.md` … `29-tensorraum.md`
- OG tree (`Ge-Prime-Matrix OG/`) is **not** part of the Workbench — stay under `GPM/`.
