# AGENTS.md

## Cursor Cloud specific instructions

Per project direction, cloud-agent work here is scoped to the **`GPM/`** folder only. The
sibling `Ge-Prime-Matrix OG/` Flask app is out of scope and is not set up or run by the
cloud environment.

### What lives under `GPM/`

| Component | Path | Stack | Role |
|-----------|------|-------|------|
| **Workbench API** | `GPM/workbench/` (`api/`) | FastAPI + uvicorn (Python) | JSON API on port **8000** |
| **Workbench frontend** | `GPM/workbench/web/` | React 19 + Vite 6 + TypeScript | SPA dev server on port **5173** (proxies `/api` → `127.0.0.1:8000`) |
| **Functions library** | `GPM/functions/` | Pure-stdlib Python (no deps) | Core S/I encoding; imported by the API via `PYTHONPATH` |

The API imports `GPM/functions`, so `PYTHONPATH` must include it. The repo's launcher and
prod script already set this; only set it manually for ad-hoc commands.

### Environment (already applied by the update script)

The update script creates a venv at `GPM/workbench/.venv`, installs
`GPM/workbench/requirements.txt` plus `pytest`+`httpx` (test-only deps), and runs
`npm ci` in `GPM/workbench/web`. `GPM/functions` needs no install.

- Non-obvious: creating the venv requires the **`python3.12-venv`** system package. It is
  not in the update script (system packages are provisioned once into the VM snapshot). If
  `python3 -m venv` ever fails with an `ensurepip` error, install it with
  `sudo apt-get install -y python3.12-venv`.
- Always use the venv interpreter: `GPM/workbench/.venv/bin/python`.

### Run (development)

Start both API + Vite together (run with the venv python so the right interpreter is used):

```bash
cd GPM/workbench && .venv/bin/python start/run_dev.py
```

- `run_dev.py` launches uvicorn (`api.main:app --reload` on `127.0.0.1:8000`) and
  `npm run dev` (Vite on `5173`), and sets `PYTHONPATH` to `GPM/functions` itself.
- Non-obvious: the Vite dev server binds to **`localhost` only**, so reach the UI via
  `http://localhost:5173` (curling `127.0.0.1:5173` returns nothing). The API is reachable
  on both `127.0.0.1:8000` and through the Vite `/api` proxy at `localhost:5173/api`.
- Health checks: `curl http://127.0.0.1:8000/api/health` → `{"status":"ok"}`;
  `curl http://localhost:5173/`.

### Test / lint / build

- Library tests: `cd GPM/functions && python3 run_tests.py` (pure stdlib, no venv needed).
  - Known-failing, pre-existing and unrelated to setup: `tests/analysis/test_corpus_minhash_auto.py::test_large_corpus_enables_minhash` (its mocked `query_candidates` is never called, so `call_args` is `None`).
- API tests: `cd GPM/workbench && PYTHONPATH=../functions .venv/bin/python -m pytest api/tests -q`.
  - Known-failing, pre-existing (brittle mock/cache-count assertions that don't hold against the installed dependency versions): `api/tests/test_document_cache.py::test_compile_cache_hit`, `test_document_cache.py::test_compile_single_flight_cas_cache_invariant`, `api/tests/test_pedagogy_no_double_encode.py::test_encode_word_single_inference`.
- Frontend lint: `cd GPM/workbench/web && npm run lint` — currently reports pre-existing
  `prefer-const` / `max-lines` / `no-control-regex` errors in existing source; not caused by setup.
- Frontend build: `cd GPM/workbench/web && npm run build` (runs UI-text/gpm-utils/tensorraum
  validators + `tsc --noEmit` + `vite build`) — passes clean.

### Hello-world check

`curl -s -X POST http://127.0.0.1:8000/api/calc/encode-word -H 'Content-Type: application/json' -d '{"word":"HALLO","profile":"og"}'`
returns `substance: 372945, index: 13`.
