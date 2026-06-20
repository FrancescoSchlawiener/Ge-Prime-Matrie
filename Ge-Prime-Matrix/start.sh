#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"
PYTHON=""

echo
echo "=== Ge-Prime-Matrix Setup ==="
echo

find_python() {
  if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    if python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
      PYTHON="python"
      return 0
    fi
  fi
  return 1
}

if ! find_python; then
  echo "[FEHLER] Python 3.9+ nicht gefunden."
  echo "Debian/Ubuntu: sudo apt install python3 python3-venv python3-pip"
  echo "Fedora:        sudo dnf install python3 python3-pip"
  exit 1
fi

echo "Python: $("$PYTHON" --version)"

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Erstelle virtuelle Umgebung..."
  "$PYTHON" -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "Aktualisiere pip..."
python -m pip install --upgrade pip -q

echo "Installiere Abhaengigkeiten..."
python -m pip install -r "$ROOT/requirements.txt"

echo "Initialisiere Datenbank..."
python "$ROOT/scripts/bootstrap.py"

echo
python "$ROOT/scripts/run_server.py" --verify-ui
if [[ $? -ne 0 ]]; then
  echo "[FEHLER] UI-Vorab-Check fehlgeschlagen"
  exit 1
fi

echo
echo "=== Starte Web-Server ==="
echo "URL: http://127.0.0.1:5000"
echo "Beenden mit Strg+C"
echo

export FLASK_DEBUG=0
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1
export PORT=5000
export HOST=127.0.0.1
export OPEN_BROWSER=1

python "$ROOT/scripts/server_control.py" --port "$PORT" 2>/dev/null || true

exec python "$ROOT/scripts/run_server.py"
