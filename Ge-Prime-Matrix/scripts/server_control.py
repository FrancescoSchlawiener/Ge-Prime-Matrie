"""Lokale Server-Steuerung: Port freimachen, Lock-Datei, Produktions-Erkennung."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / "data" / ".server.lock"
SERVER_MARKER = "run_server.py"


def is_production() -> bool:
    """Cloud/Server: kein Port-Kill, kein Browser, kein Lock."""
    if os.environ.get("RENDER"):
        return True
    env = os.environ.get("GE_PRIME_ENV", "").strip().lower()
    return env in ("production", "prod", "render")


def default_host() -> str:
    raw = os.environ.get("HOST", "").strip()
    if raw:
        return raw
    return "0.0.0.0" if is_production() else "127.0.0.1"


def _decode_output(raw: bytes | None) -> str:
    if not raw:
        return ""
    if sys.platform == "win32":
        for enc in ("cp1252", "utf-8", "latin-1"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                continue
    return raw.decode("utf-8", errors="replace")


def _run_text(args: list[str]) -> str:
    try:
        result = subprocess.run(args, capture_output=True, check=False)
    except OSError:
        return ""
    return _decode_output(result.stdout)


def pids_on_port(port: int) -> set[int]:
    found: set[int] = set()
    if sys.platform == "win32":
        for line in _run_text(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue).OwningProcess",
            ]
        ).splitlines():
            line = line.strip()
            if line.isdigit():
                found.add(int(line))
        if found:
            return found
        suffix = f":{port}"
        for line in _run_text(["netstat", "-ano"]).splitlines():
            if "LISTENING" not in line:
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            local = parts[1]
            if local.endswith(suffix) and parts[-1].isdigit():
                found.add(int(parts[-1]))
        return found

    for cmd in (["lsof", "-ti", f":{port}"], ["fuser", f"{port}/tcp"]):
        try:
            result = subprocess.run(cmd, capture_output=True, check=False)
        except OSError:
            continue
        if result.returncode != 0:
            continue
        for token in _decode_output(result.stdout).replace("\n", " ").split():
            if token.isdigit():
                found.add(int(token))
        if found:
            break
    return found


def _command_line(pid: int) -> str:
    if sys.platform == "win32":
        return _run_text(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-CimInstance Win32_Process -Filter \"ProcessId={pid}\").CommandLine",
            ]
        ).strip()
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
        return raw.replace(b"\x00", b" ").decode("utf-8", errors="replace")
    except OSError:
        return ""


def is_ge_prime_server(pid: int) -> bool:
    if pid == os.getpid():
        return False
    cmd = _command_line(pid).lower()
    if not cmd:
        return False
    if SERVER_MARKER in cmd:
        return True
    if "ge-prime-matrix" in cmd and "flask" in cmd:
        return True
    return False


def stop_local_servers(port: int, *, include_foreign: bool = False) -> list[int]:
    """
    Beendet Ge-Prime-Server auf dem Port.

    include_foreign=False (Standard): nur run_server.py — sicher lokal & auf Shared Hosts.
    include_foreign=True: alles auf dem Port (nur fuer explizites stop.bat --force).
    """
    my_pid = os.getpid()
    killed: list[int] = []
    for pid in sorted(pids_on_port(port)):
        if pid == my_pid:
            continue
        if not include_foreign and not is_ge_prime_server(pid):
            continue
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
                check=False,
            )
        else:
            subprocess.run(["kill", "-9", str(pid)], capture_output=True, check=False)
        killed.append(pid)
    if killed:
        time.sleep(0.75)
    return killed


def read_lock_pid() -> int | None:
    try:
        raw = LOCK_PATH.read_text(encoding="utf-8").strip()
        return int(raw) if raw.isdigit() else None
    except OSError:
        return None


def write_lock(pid: int | None = None) -> None:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.write_text(str(pid or os.getpid()), encoding="utf-8")


def clear_lock() -> None:
    try:
        LOCK_PATH.unlink(missing_ok=True)
    except OSError:
        pass


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        ps = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"exit ([int](Get-Process -Id {pid} -ErrorAction SilentlyContinue) -ne $null)",
            ],
            capture_output=True,
            check=False,
        )
        return ps.returncode == 0
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def prepare_local_port(port: int) -> list[int]:
    """Vor lokalem Start: veraltete Locks + alte Ge-Prime-Instanzen entfernen."""
    if is_production():
        return []

    lock_pid = read_lock_pid()
    if lock_pid and not process_alive(lock_pid):
        clear_lock()
    elif lock_pid and lock_pid != os.getpid() and is_ge_prime_server(lock_pid):
        stop_local_servers(port)

    killed = stop_local_servers(port)
    write_lock()
    return killed


def stop_cli(port: int | None = None, *, force: bool = False) -> int:
    port = port or int(os.environ.get("PORT", 5000))
    killed = stop_local_servers(port, include_foreign=force)
    clear_lock()
    if killed:
        print(f"[OK] Beendet: {', '.join(str(p) for p in killed)}")
    else:
        print("[OK] Kein Ge-Prime-Server auf Port", port)
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ge-Prime lokaler Server-Stop")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 5000)))
    parser.add_argument(
        "--force",
        action="store_true",
        help="Alles auf dem Port beenden (nur manuell)",
    )
    args = parser.parse_args()
    raise SystemExit(stop_cli(args.port, force=args.force))
