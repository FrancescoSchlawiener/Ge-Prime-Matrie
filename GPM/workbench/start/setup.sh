#!/usr/bin/env sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="$(python3 "$(dirname "$0")/find_python.py" --ensure-venv --print)"
"$PY" -m pip install --upgrade pip -q
"$PY" -m pip install -r requirements.txt
"$PY" "$(dirname "$0")/bootstrap.py"
echo "[OK] Setup fertig. Start: start/dev.sh"
