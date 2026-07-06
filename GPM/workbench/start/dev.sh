#!/usr/bin/env sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
START="$(dirname "$0")"
cd "$ROOT"

PY_PATH_FILE="${ROOT}/.python-path"
VENV_PY="${ROOT}/.venv/bin/python"

if [ -x "$VENV_PY" ]; then
  exec "$VENV_PY" "${START}/run_dev.py" "$@"
fi

if [ -f "$PY_PATH_FILE" ]; then
  PY_CANDIDATE="$(cat "$PY_PATH_FILE")"
  if [ -x "$PY_CANDIDATE" ]; then
    PY="$PY_CANDIDATE"
  fi
fi

if [ -z "${PY:-}" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PY="$(python3 "${START}/find_python.py" --print-path-only)"
  else
    echo "[FATAL ERROR] Kein Python 3.10+ gefunden."
    exit 1
  fi
fi

if [ ! -x "$VENV_PY" ]; then
  echo "[INFO] Virtuelle Umgebung fehlt. Starte Bootstrap..."
  "$PY" "${START}/bootstrap.py"
fi

exec "$VENV_PY" "${START}/run_dev.py" "$@"
