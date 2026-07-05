import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from ge_prime.config import APP_VERSION, REQUIRED_API_ROUTES
from db.repository import WordRepository
from scripts.server_control import (
    clear_lock,
    default_host,
    is_production,
    prepare_local_port,
)
from web.app import app


def _console(msg: str) -> None:
    """Windows cp1252 kann Unicode-Pfade im Projektordner nicht ausgeben."""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"), flush=True)


def _port_is_free(host: str, port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
        return True
    except OSError:
        return False


def _find_chrome() -> str | None:
    candidates = [
        os.path.join(os.environ.get("PROGRAMFILES", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def _wait_for_port(host: str, port: int, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def _verify_ui_files() -> None:
    index_path = ROOT / "web" / "templates" / "index.html"
    if not index_path.exists():
        raise SystemExit("[FEHLER] index.html fehlt in web/templates/")
    content = index_path.read_text(encoding="utf-8")
    if 'data-tab="gpm"' not in content:
        raise SystemExit("[FEHLER] index.html ohne GPM-Tab — start.bat aus Ge-Prime-Matrix ausfuehren.")
    if "{{ app_version }}" not in content and APP_VERSION not in content:
        raise SystemExit(
            f"[FEHLER] index.html ohne Build-Tag ({{{{ app_version }}}} oder {APP_VERSION})."
        )
    _console(f"[OK] UI: {index_path.name} · Build {APP_VERSION}")


def _verify_api_routes() -> None:
    rules = {r.rule for r in app.url_map.iter_rules()}
    missing = [route for route in REQUIRED_API_ROUTES if route not in rules]
    if missing:
        raise SystemExit(f"[FEHLER] Fehlende API-Routen: {', '.join(missing)}")


def _verify_api_health(repo: WordRepository) -> None:
    with app.test_client() as client:
        resp = client.get("/api/health")
        if resp.status_code != 200:
            raise SystemExit(f"[FEHLER] /api/health antwortet mit {resp.status_code}")
        data = resp.get_json() or {}
        if not data.get("ok"):
            raise SystemExit("[FEHLER] /api/health meldet ok=false")
        routes = data.get("routes") or {}
        missing = sorted(key for key, ok in routes.items() if not ok)
        if missing:
            raise SystemExit(
                f"[FEHLER] Fehlende Routen in Health-Check: {', '.join(missing)}"
            )
        if not routes.get("db_stats") or not routes.get("encode"):
            raise SystemExit("[FEHLER] Encode/DB-Routen in Health-Check inaktiv")
        _console(f"[OK] DB: {data.get('db_words', 0)} Woerter · {Path(str(data.get('db_path', ''))).name}")


def _open_browser(url: str, host: str, port: int) -> None:
    if not _wait_for_port(host, port):
        _console(f"[WARNUNG] Server antwortet nicht rechtzeitig — Browser trotzdem oeffnen: {url}")

    if sys.platform == "win32":
        chrome = _find_chrome()
        if chrome:
            subprocess.Popen(
                [chrome, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
            )
            return
        os.startfile(url)
        return

    chrome = _find_chrome()
    if chrome:
        subprocess.Popen([chrome, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        webbrowser.open(url)


def main() -> None:
    port = int(os.environ.get("PORT", 5000))
    host = default_host()
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    url = f"http://{host if host != '0.0.0.0' else '127.0.0.1'}:{port}"

    if not is_production():
        killed = prepare_local_port(port)
        for pid in killed:
            _console(f"[INFO] Alter Ge-Prime-Server beendet (PID {pid}).")
        if not _port_is_free(host if host != "0.0.0.0" else "127.0.0.1", port):
            raise SystemExit(
                f"[FEHLER] Port {port} noch belegt — stop.bat ausfuehren oder anderen Dienst beenden."
            )
    elif not _port_is_free(host, port):
        raise SystemExit(f"[FEHLER] Port {port} nicht bindbar.")

    _verify_ui_files()
    _verify_api_routes()

    repo = WordRepository()
    repo.init_db()
    _verify_api_health(repo)

    open_browser = (
        not is_production()
        and os.environ.get("OPEN_BROWSER", "1") == "1"
        and host in ("127.0.0.1", "localhost")
    )
    if open_browser:
        threading.Thread(
            target=_open_browser,
            args=(f"{url}/#encodieren", "127.0.0.1", port),
            daemon=True,
        ).start()

    mode = "Produktion" if is_production() else "Lokal"
    _console(f"Ge-Prime-Matrix {APP_VERSION} ({mode}) auf {host}:{port}")
    _console(f"Health: {url}/api/health · DB-Stats: {url}/api/db/stats")

    try:
        app.run(host=host, port=port, debug=debug, use_reloader=False, threaded=True)
    finally:
        if not is_production():
            clear_lock()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ge-Prime-Matrix Web-Server")
    parser.add_argument(
        "--verify-ui",
        action="store_true",
        help="Nur UI-Dateien prüfen (für start.bat, Unicode-Pfade)",
    )
    args = parser.parse_args()
    if args.verify_ui:
        _verify_ui_files()
        raise SystemExit(0)
    main()
