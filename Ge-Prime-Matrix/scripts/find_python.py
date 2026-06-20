"""Projekt-Python finden und optional .venv anlegen."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PY = ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / (
    "python.exe" if sys.platform == "win32" else "python"
)
PYTHON_PATH_FILE = ROOT / ".python-path"

CANDIDATES = [
    Path(r"C:\Program Files\pgAdmin 4\python\python.exe"),
    Path(r"C:\Program Files\PostgreSQL\18\pgAdmin 4\python\python.exe"),
    Path(r"C:\Program Files\PostgreSQL\17\pgAdmin 4\python\python.exe"),
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Python/Python313/python.exe",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Python/Python312/python.exe",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Python/Python311/python.exe",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Python/Python310/python.exe",
]


def _works(path: Path) -> bool:
    if not path.is_file():
        return False
    if "windowsapps" in str(path).lower():
        return False
    try:
        r = subprocess.run(
            [str(path), "-c", "import sys"],
            capture_output=True,
            check=False,
        )
        return r.returncode == 0
    except OSError:
        return False


def find_system_python() -> Path | None:
    if _works(VENV_PY):
        return VENV_PY
    for candidate in CANDIDATES:
        if _works(candidate):
            return candidate
    if sys.platform == "win32":
        try:
            r = subprocess.run(
                ["py", "-3", "-c", "import sys; print(sys.executable)"],
                capture_output=True,
                text=True,
                check=False,
            )
            if r.returncode == 0:
                path = Path(r.stdout.strip())
                if _works(path):
                    return path
        except OSError:
            pass
    for name in ("python3", "python"):
        try:
            r = subprocess.run(
                [name, "-c", "import sys; print(sys.executable)"],
                capture_output=True,
                text=True,
                check=False,
            )
            if r.returncode == 0:
                path = Path(r.stdout.strip())
                if _works(path):
                    return path
        except OSError:
            pass
    return None


def ensure_venv(base: Path | None = None) -> Path:
    """Bevorzugt .venv; falls venv fehlt (z. B. pgAdmin-Python), Basis-Python direkt nutzen."""
    if _works(VENV_PY):
        _write_python_path(VENV_PY)
        _write_vscode_settings(VENV_PY)
        return VENV_PY

    base = base or find_system_python()
    if base is None:
        raise SystemExit(
            "[FEHLER] Kein Python 3 gefunden.\n"
            "Installiere Python von https://www.python.org/downloads/ "
            '(Haken "Add Python to PATH") oder nutze pgAdmin-Python.'
        )

    try:
        subprocess.run(
            [str(base), "-m", "venv", str(ROOT / ".venv")],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, OSError):
        _write_python_path(base)
        _write_vscode_settings(base)
        return base

    if _works(VENV_PY):
        _write_python_path(VENV_PY)
        _write_vscode_settings(VENV_PY)
        return VENV_PY

    _write_python_path(base)
    _write_vscode_settings(base)
    return base


def resolve_python() -> Path:
    path = find_system_python()
    if path is not None:
        return path
    if PYTHON_PATH_FILE.is_file():
        stored = Path(PYTHON_PATH_FILE.read_text(encoding="utf-8").strip())
        if _works(stored):
            return stored
    raise SystemExit(1)


def _write_vscode_settings(path: Path) -> None:
    escaped = str(path.resolve()).replace("\\", "/")
    content = (
        "{\n"
        f'  "python.defaultInterpreterPath": "{escaped}",\n'
        '  "python.terminal.activateEnvironment": true\n'
        "}\n"
    )
    for vscode_dir in (ROOT / ".vscode", ROOT.parent / ".vscode"):
        try:
            vscode_dir.mkdir(exist_ok=True)
            (vscode_dir / "settings.json").write_text(content, encoding="utf-8")
        except OSError:
            pass


def _write_python_path(path: Path) -> None:
    try:
        PYTHON_PATH_FILE.write_text(str(path.resolve()), encoding="utf-8")
    except OSError:
        pass


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--ensure-venv", action="store_true")
    parser.add_argument("--print", action="store_true", dest="do_print")
    args = parser.parse_args()
    if args.ensure_venv:
        path = ensure_venv()
    else:
        path = resolve_python()
    if args.do_print:
        print(path)


if __name__ == "__main__":
    main()
