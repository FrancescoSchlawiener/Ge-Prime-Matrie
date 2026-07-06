# GPM Workbench — Start

Der Ordner `start/` enthält alle Startskripte. Kurzwege im Workbench-Root:

| Root | Ziel |
|------|------|
| `setup.bat` | → `start\setup.bat` |
| `dev.bat` | → `start\dev.bat` |
| `start\doctor.bat` | Python-Diagnose (bei Setup-Problemen) |

## Einmal-Setup

**Windows:** Doppelklick auf `setup.bat` (Root) oder `start\setup.bat`  
**Linux/macOS:** `chmod +x start/setup.sh && ./start/setup.sh`

Legt `.venv` an, installiert `requirements.txt` und `web/node_modules`.

Falls Setup „Kein Python gefunden“ meldet:

1. **`start\doctor.bat`** ausführen — zeigt alle Kandidaten und Ablehnungsgründe
2. [Python 3.10+](https://www.python.org/downloads/) installieren (Haken: **Add python.exe to PATH**)
3. **Neues CMD-Fenster** öffnen nach der Installation (Explorer/Doppelklick sieht sonst den alten PATH)
4. Windows-Store-Alias deaktivieren: Einstellungen → Apps → App-Ausführungsaliase → `python.exe` **Aus**
5. Oder Pfad manuell in `GPM/workbench/.python-path` eintragen (eine Zeile, voller Pfad zu `python.exe`)

Bei seltsamen CMD-Fehlern (`Der Befehl "t" ...`, `cho` nicht gefunden): neues CMD-Fenster öffnen und `start\doctor.bat` ausführen — oft veralteter PATH oder Store-Stub.

**Hinweis:** Python aus pgAdmin oder PostgreSQL (`C:\Program Files\pgAdmin 4\python\`) ist **nicht geeignet** — dort fehlt oft das `venv`-Modul. Verwenden Sie eine Standard-Installation von python.org.

## Entwicklung starten

**Windows:** `dev.bat` (Root) oder `start\dev.bat`  
**Linux/macOS:** `./start/dev.sh`

- API: http://127.0.0.1:8000/api/health  
- UI: http://127.0.0.1:5173  

## Stoppen

`Ctrl+C` im Dev-Terminal oder `start\stop.bat` (Windows Ports freigeben).

Alternativ: `npm run dev` im Workbench-Root (ruft ebenfalls `start/run_dev.py` auf).
