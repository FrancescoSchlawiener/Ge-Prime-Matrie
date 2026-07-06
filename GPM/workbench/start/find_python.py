"""Projekt-Python finden und optional .venv anlegen — GPM Workbench."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV_PY = ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / (
    "python.exe" if sys.platform == "win32" else "python"
)
PYTHON_PATH_FILE = ROOT / ".python-path"

STANDARD_CANDIDATES = [
    Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python313\python.exe")),
    Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python312\python.exe")),
    Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python311\python.exe")),
    Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python310\python.exe")),
    Path(os.path.expandvars(r"%APPDATA%\Python\Python313\python.exe")),
    Path(os.path.expandvars(r"%APPDATA%\Python\Python312\python.exe")),
    Path(os.path.expandvars(r"%APPDATA%\Python\Python311\python.exe")),
    Path(os.path.expandvars(r"%APPDATA%\Python\Python310\python.exe")),
    Path(r"C:\Python313\python.exe"),
    Path(r"C:\Python312\python.exe"),
    Path(r"C:\Python311\python.exe"),
    Path(r"C:\Python310\python.exe"),
]

BUNDLED_CANDIDATES = [
    Path(r"C:\Program Files\pgAdmin 4\python\python.exe"),
    Path(r"C:\Program Files\PostgreSQL\18\pgAdmin 4\python\python.exe"),
    Path(r"C:\Program Files\PostgreSQL\17\pgAdmin 4\python\python.exe"),
]


def scan_program_files() -> list[Path]:
    paths: list[Path] = []
    bases: list[Path] = []
    for env in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA", "APPDATA"):
        val = os.environ.get(env)
        if val:
            bases.append(Path(val))
    for base in bases:
        for child in base.glob("Python3*"):
            exe = child / "python.exe"
            if exe.is_file():
                paths.append(exe)
        nested = base / "Programs" / "Python"
        if nested.is_dir():
            for child in nested.glob("Python3*"):
                exe = child / "python.exe"
                if exe.is_file():
                    paths.append(exe)
    appdata = os.environ.get("APPDATA")
    if appdata:
        py_root = Path(appdata) / "Python"
        if py_root.is_dir():
            for child in py_root.glob("Python3*"):
                exe = child / "python.exe"
                if exe.is_file():
                    paths.append(exe)
    local = os.environ.get("LOCALAPPDATA")
    if local:
        py_local = Path(local) / "Python"
        if py_local.is_dir():
            for child in py_local.glob("pythoncore-*"):
                exe = child / "python.exe"
                if exe.is_file():
                    paths.append(exe)
            bin_exe = py_local / "bin" / "python.exe"
            if bin_exe.is_file():
                paths.append(bin_exe)
    return paths


def _is_bundled_python(path: Path) -> bool:
    lowered = str(path).lower()
    return "pgadmin" in lowered or "postgresql" in lowered


def _can_create_venv(path: Path) -> bool:
    try:
        res = subprocess.run(
            [str(path), "-m", "venv", "--help"],
            capture_output=True,
            timeout=5,
            check=False,
        )
        return res.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _is_valid_interpreter(path: Path, *, require_venv: bool = False) -> bool:
    """Invarianten P1-B und P1-C; optional venv capability (P1-D)."""
    try:
        if not path.exists() or not path.is_file():
            return False
        if "windowsapps" in str(path).lower() or path.stat().st_size == 0:
            return False
        cmd = [str(path), "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=2, check=False)
        if res.returncode != 0:
            return False
        major, minor = map(int, res.stdout.strip().split(".")[:2])
        if not (major == 3 and minor >= 10):
            return False
        if require_venv and not _can_create_venv(path):
            return False
        return True
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def scan_windows_registry() -> list[Path]:
    paths: list[Path] = []
    if sys.platform != "win32":
        return paths
    try:
        import winreg

        for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for sub in (
                r"Software\Microsoft\Windows\CurrentVersion\App Paths\python.exe",
                r"Software\Microsoft\Windows\CurrentVersion\App Paths\python3.exe",
            ):
                for bits in (0, winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
                    try:
                        with winreg.OpenKey(root, sub, 0, winreg.KEY_READ | bits) as key:
                            exe, _ = winreg.QueryValueEx(key, None)
                            if exe:
                                paths.append(Path(exe))
                    except OSError:
                        pass

        for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for bits in (0, winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY):
                try:
                    key_path = r"Software\Python\PythonCore"
                    with winreg.OpenKey(root, key_path, 0, winreg.KEY_READ | bits) as base_key:
                        i = 0
                        while True:
                            try:
                                v_name = winreg.EnumKey(base_key, i)
                            except OSError:
                                break
                            try:
                                major, minor = map(int, v_name.split(".")[:2])
                                if major == 3 and minor >= 10:
                                    ip_path = rf"{key_path}\{v_name}\InstallPath"
                                    with winreg.OpenKey(root, ip_path, 0, winreg.KEY_READ | bits) as ip_key:
                                        exe, _ = winreg.QueryValueEx(ip_key, "ExecutablePath")
                                        if exe:
                                            paths.append(Path(exe))
                            except (OSError, ValueError):
                                pass
                            i += 1
                except OSError:
                    pass
    except Exception:
        pass
    return paths


def _py_launcher_candidates() -> list[Path]:
    """Paths reported by Windows py launcher (py -0p)."""
    if sys.platform != "win32":
        return []
    paths: list[Path] = []
    try:
        r = subprocess.run(
            ["py", "-0p"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("-"):
                    continue
                # Format: "-V:3.13 *        C:\...\python.exe"
                parts = line.split()
                if parts:
                    candidate = Path(parts[-1])
                    if candidate.is_file():
                        paths.append(candidate)
    except (OSError, subprocess.TimeoutExpired):
        pass
    return paths


def _py_launcher_executable() -> Path | None:
    if sys.platform != "win32":
        return None
    try:
        r = subprocess.run(
            ["py", "-3", "-c", "import sys; print(sys.executable)"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if r.returncode == 0:
            path = Path(r.stdout.strip())
            if path.is_file():
                return path
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    out: list[Path] = []
    for path in paths:
        try:
            key = str(path.resolve()).lower()
        except OSError:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def iter_python_candidates() -> list[Path]:
    """Ordered discovery: standard installs first, bundled pgAdmin last."""
    ordered: list[Path] = []

    if PYTHON_PATH_FILE.is_file():
        stored = Path(PYTHON_PATH_FILE.read_text(encoding="utf-8").strip())
        ordered.append(stored)

    launcher = _py_launcher_executable()
    if launcher:
        ordered.append(launcher)

    ordered.extend(_py_launcher_candidates())
    ordered.extend(scan_windows_registry())
    ordered.extend(scan_program_files())
    ordered.extend(STANDARD_CANDIDATES)

    for cmd in ("python", "python3"):
        resolved = shutil.which(cmd)
        if resolved:
            ordered.append(Path(resolved))

    ordered.extend(BUNDLED_CANDIDATES)

    standard: list[Path] = []
    bundled: list[Path] = []
    for path in _dedupe_paths(ordered):
        if _is_bundled_python(path):
            bundled.append(path)
        else:
            standard.append(path)
    return standard + bundled


def resolve_python() -> Path:
    if _is_valid_interpreter(VENV_PY):
        return VENV_PY

    for path in iter_python_candidates():
        if _is_valid_interpreter(path, require_venv=True):
            _write_python_path(path)
            return path

    print(
        "[FATAL] Es konnte kein lauffähiger Python 3.10+ Interpreter mit venv ermittelt werden.",
        file=sys.stderr,
    )
    print(
        "[INFO] Installieren Sie Python von python.org (inkl. venv) oder tragen Sie den Pfad in .python-path ein.",
        file=sys.stderr,
    )
    print(
        "[INFO] pgAdmin/PostgreSQL-Python ist nicht geeignet — kein venv-Modul.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def ensure_venv(base: Path | None = None) -> Path:
    if _is_valid_interpreter(VENV_PY):
        _write_python_path(VENV_PY)
        return VENV_PY

    candidates: list[Path] = []
    if base is not None:
        candidates.append(base)
    candidates.extend(iter_python_candidates())

    tried: set[str] = set()
    for cand in _dedupe_paths(candidates):
        key = str(cand.resolve()).lower()
        if key in tried:
            continue
        tried.add(key)

        if not _is_valid_interpreter(cand):
            continue
        if not _can_create_venv(cand):
            print(
                f"[WARN] Interpreter ohne venv-Modul übersprungen: {cand}",
                file=sys.stderr,
            )
            continue

        try:
            subprocess.run(
                [str(cand), "-m", "venv", str(ROOT / ".venv")],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, OSError) as exc:
            err = getattr(exc, "stderr", "") or str(exc)
            print(f"[WARN] venv konnte nicht angelegt werden ({cand}): {err}", file=sys.stderr)
            continue

        if _is_valid_interpreter(VENV_PY):
            _write_python_path(VENV_PY)
            return VENV_PY

    print(
        "[FATAL] Virtuelle Umgebung (.venv) konnte mit keinem gefundenen Interpreter angelegt werden.",
        file=sys.stderr,
    )
    print(
        "[INFO] Installieren Sie Python 3.10+ von https://www.python.org/downloads/ "
        '(Haken: "Add python.exe to PATH").',
        file=sys.stderr,
    )
    raise SystemExit(1)


def _write_python_path(path: Path) -> None:
    try:
        PYTHON_PATH_FILE.write_text(str(path.resolve()), encoding="utf-8")
    except OSError:
        pass


def _diagnose_candidate(path: Path) -> str:
    reasons: list[str] = []
    if not path.exists():
        return "missing"
    if "windowsapps" in str(path).lower():
        reasons.append("WindowsApps stub")
    try:
        if path.stat().st_size == 0:
            reasons.append("0-byte stub")
    except OSError:
        reasons.append("stat failed")
    try:
        res = subprocess.run(
            [str(path), "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if res.returncode != 0:
            reasons.append("version check failed")
        else:
            major, minor = map(int, res.stdout.strip().split(".")[:2])
            if major != 3 or minor < 10:
                reasons.append(f"version {major}.{minor} < 3.10")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        reasons.append("version probe error")
    if _is_bundled_python(path):
        reasons.append("bundled pgAdmin/PostgreSQL")
    if not _can_create_venv(path):
        reasons.append("no venv module")
    if not reasons:
        return "OK (venv-capable)"
    return "; ".join(reasons)


def _say(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "backslashreplace").decode("ascii"), flush=True)


def run_doctor() -> int:
    _say("=== GPM Workbench Python Doctor ===\n")
    _say(f"ROOT: {ROOT}")
    _say(f".python-path exists: {PYTHON_PATH_FILE.is_file()}")
    if PYTHON_PATH_FILE.is_file():
        _say(f".python-path: {PYTHON_PATH_FILE.read_text(encoding='utf-8').strip()}")
    _say(f".venv python exists: {VENV_PY.is_file()}\n")

    _say("--- py launcher ---")
    try:
        r = subprocess.run(["py", "-0p"], capture_output=True, text=True, check=False, timeout=5)
        _say(r.stdout.strip() if r.stdout.strip() else "(py -0p unavailable)")
    except OSError as exc:
        _say(f"(py not found: {exc})")

    _say("\n--- candidates ---")
    found_ok = False
    for path in iter_python_candidates():
        status = _diagnose_candidate(path)
        mark = " [SELECT]" if status == "OK (venv-capable)" else ""
        if status == "OK (venv-capable)":
            found_ok = True
        _say(f"  {path}")
        _say(f"    -> {status}{mark}")

    _say("\n--- recommendation ---")
    if found_ok:
        _say("Run: start\\setup.bat")
    else:
        _say("Install Python 3.10+ from https://www.python.org/downloads/")
        _say('  - Check "Add python.exe to PATH"')
        _say("  - Disable Store alias: Settings > Apps > App execution aliases > python.exe OFF")
        _say("  - Open a NEW Command Prompt after install, then run start\\doctor.bat again")
        _say("  - pgAdmin/PostgreSQL Python cannot create .venv - use python.org")
    return 0 if found_ok else 1


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--ensure-venv", action="store_true")
    parser.add_argument("--print", action="store_true", dest="do_print")
    parser.add_argument("--print-path-only", action="store_true", dest="print_path_only")
    parser.add_argument("--doctor", action="store_true")
    args = parser.parse_args()
    if args.doctor:
        raise SystemExit(run_doctor())
    path = ensure_venv() if args.ensure_venv else resolve_python()
    if args.do_print or args.print_path_only:
        _say(path)


if __name__ == "__main__":
    main()
