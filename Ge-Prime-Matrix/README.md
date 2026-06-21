# Ge-Prime-Matrix

Web-App und Bibliothek zur **Substanz-Codierung** von Wörtern und Texten: jedes Wort wird als Paar **S(I)** gespeichert — **S** (Substanz) ist das Primzahlprodukt der Buchstaben, **I** (Index) die Position im Permutationsraum.

Darauf aufbauend:

- **`.gpm` v5** — verlustfreies Binärformat mit Zell-Geometrie (I_Satz) und v4-Genom/Separator
- **I-Kurve & Meta-Genom** — Stil-Analyse, Sprache/Domäne, Plagiats-Heuristik
- **S(I)-Verschlüsselung** — symmetrische Obfuskation mit Wort-/Primzahl-Schlüsseln
- **GPC** — verschlüsselte `.gpm`-Hülle für den Editor (ohne Schlüssel kein lesbares Genom)

**Build:** `2026.06-gpm-v49` · **GPM-Format:** v7 (v1–v6 lesbar) · **GPC-Cipher:** v1

---

## Inhalt

1. [Konzept](#konzept)
2. [Normalisierung & Buchstaben](#normalisierung--buchstaben)
3. [Das .gpm-Format v5](#das-gpm-format-v5)
4. [Verschlüsselte .gpm (GPC)](#verschlüsselte-gpm-gpc)
5. [Schnellstart](#schnellstart)
6. [Python einrichten (Windows)](#python-einrichten-windows)
7. [Server starten & stoppen](#server-starten--stoppen)
8. [Web-Oberfläche](#web-oberfläche)
9. [HTTP-API](#http-api)
10. [CLI-Werkzeuge](#cli-werkzeuge)
11. [Projektstruktur & Module](#projektstruktur--module)
12. [Repository & GitHub](#repository--github)
13. [Deployment (Render)](#deployment-render)
14. [Tests](#tests)
15. [Umgebungsvariablen](#umgebungsvariablen)
16. [Fehlerbehebung](#fehlerbehebung)

---

## Konzept

### Substanz S

Jeder Buchstabe (A–Z und **ß**) hat eine feste Primzahl. Die **Substanz** eines Wortes ist das Produkt aller Primzahlen — unabhängig von der Buchstabenreihenfolge.

Beispiel: `HALLO` → H·A·L·L·O → `47 × 3 × 23 × 23 × 5`

### Index I

Bei gleicher Buchstabenmenge gibt es viele Anordnungen. **I** ist der lexikographische Rang im Permutationsraum (fraktale Intervallschachtelung). Zusammen mit **S** ist das Wort eindeutig rekonstruierbar.

### ggT- und kgV-Vergleich

| Operation | Formel | Bedeutung |
|-----------|--------|-----------|
| **ggT** | `gcd(S₁, S₂)` | Schnittmenge — gemeinsame Buchstaben |
| **kgV** | `lcm(S₁, S₂)` | Vereinigung — minimale Substanz für beide Wörter |

Der ggT eignet sich für Ähnlichkeitssuche (gemeinsame Primfaktoren). Der kgV liefert die synthetische Vereinigungsmenge: In `.gpm`-Genomen findet man passende Wörter mit **`S_Genom % kgV == 0`** — ein Modulo statt Regex-Kaskaden.

Implementierung: [`ge_prime/compare.py`](Ge-Prime-Matrix/ge_prime/compare.py) (`substance_lcm`, `substance_covers`, `union_letters`).

### Arithmetische Differenz

| Operation | Formel | Bedeutung |
|-----------|--------|-----------|
| **Rest** | `S_rest = S₁ ÷ ggT(S₁, S₂)` | Buchstaben in Wort 1 nach Abzug gemeinsamer Primfaktoren |
| **Teilmenge** | `S_rest == 1` und `S₁ ≠ S₂` | Echte Buchstaben-Teilmenge (nicht nur Gleichheit) |
| **Anagramm** | `S₁ = S₂` und `I₁ ≠ I₂` | Gleiche Buchstaben, andere Anordnung |

Implementierung: [`ge_prime/diff.py`](Ge-Prime-Matrix/ge_prime/diff.py).

### Index-Vektoren (I-Kurve) & Meta-Genom

Über die Token-Reihenfolge entsteht pro Text eine **I-Kurve** — der rhythmische Fingerabdruck der Satzgeometrie.

| Feld | Bedeutung |
|------|-----------|
| **i_ratio** | `I / N` — topologische Position im Permutationsraum (0–1) |
| **delta_ratio** | Sprung zwischen aufeinanderfolgenden Token |
| **Geometrie-Score** | Mittel aus Ratio- und Delta-Ähnlichkeit zweier Kurven |
| **Literal-Match** | Anteil gleicher Wörter an gleicher Position (Kontrast) |
| **suspicious_parallel** | Hohe Geometrie + niedriger Literal-Match bei gleicher Länge |

**Meta-Genom:** Aus dem Header-Genom wird ein Dokumenten-Vektor **V = ∏ S^Häufigkeit** gebildet (effizient als Primzahl-Profil). Damit lassen sich ohne Öffnen der Datei:

- **Sprache** schätzen (Referenz-Genome de/en, ß-Signal für Deutsch)
- **Domäne** clustern (ggT von V₁ und V₂ — Medizin vs. Recht als Demo-Referenzen)
- **DB-Sprachaudit** — unique Token gegen die Wort-Datenbank (auch bei „Unklar“ über de/en-Scores)
- **Spektroskopie** — Text markieren in I-Kurve (A/B) oder GPM-Editor: Teal/Amber/Kreuzfeuer
- **Plagiats-Signale** kombinieren (I-Kurve + Meta-ggT → Kombi-Score)

**Hierarchie-Ebenen (I-Kurve-Tab):** Wort, Sinn (Phrase/Satz/Absatz), Raum (Zeile). Formfeed-Seitenumbrüche (`\f`) sind keine Laufzeit-Ebene — nur für Export/PDF (`build_page_nodes_for_export`).

**Sprache & DB-Abdeckung (I-Kurve-Tab):**

| Anzeige | Bedeutung |
|---------|-----------|
| **Deutsch / Englisch** | Sprache mit ausreichender Konfidenz erkannt |
| **Unklar (hybrid/patterns/db)** | Konfidenz zu niedrig — Label bleibt „Unklar“, Erkennungsmethode in Klammern |
| **DB-Audit gegen DE/EN** | Audit-Sprache aus Score-Tendenz (bei unsicherer Erkennung) |
| **X % bestätigt** | Anteil unique Token, die in der Audit-Sprache in der DB stehen |
| **Fremdkörper** | Wörter eher der anderen Sprache (Modus de↔en) |
| **DB-Sprachaudit deaktiviert** | Dropdown „Aus“ gewählt |

Audit-Modi im Formular: **de ↔ en** (Standard), **Alle DB-Sprachen**, **Aus**.

Implementierung: [`ge_prime/i_curve.py`](Ge-Prime-Matrix/ge_prime/i_curve.py), [`ge_prime/meta_genome.py`](Ge-Prime-Matrix/ge_prime/meta_genome.py).
API: **POST `/api/i-curve`** (Freitext oder `.gpm` pro Seite, max. 10.000 Token).

> **Abgrenzung:** Heuristische Demo — kein Ersatz für juristische Plagiatsgutachten oder NLP-Klassifikatoren.

### S(I)-Verschlüsselung

Text wird kompiliert; **S**, **I** und die Separator-Schicht werden schlüsselabhängig transformiert.

| Modus | Schlüssel | Sicherheit (ehrlich) |
|-------|-----------|----------------------|
| **word** | Buchstabenwort → Substanz S | niedrig — Lernen/Demo |
| **prime** | `prime:N` (z. B. `prime:17`) | niedrig — kurze Schlüssel erratbar |
| **si** | Wort mit getrennter S/I-Mischung | mittel |
| **hardcore** | Kommagetrennt: Wörter und `prime:N` wechseln pro Token | hoch — gemischte Sequenz |

API: **POST `/api/cipher/encrypt`**, **POST `/api/cipher/decrypt`**.  
Implementierung: [`ge_prime/cipher.py`](Ge-Prime-Matrix/ge_prime/cipher.py).

> **Abgrenzung:** Symmetrisch — wer `PRIME_MAP` und den Schlüssel kennt, kann entschlüsseln. Kein Ersatz für AES/GPG.

---

## Normalisierung & Buchstaben

Vor dem Encodieren werden Wörter vereinheitlicht. Diese Regeln gelten überall gleich (Web, DB, `.gpm`, CLI).

| Regel | Verhalten |
|-------|-----------|
| **Umlaute** | ä/Ä → AE, ö/Ö → OE, ü/Ü → UE |
| **Eszett ß** | Eigener Buchstabe mit Primzahl **103** — **kein** ß→ss mehr |
| **Groß/Klein** | Nach Normalisierung: Großbuchstaben + ß; Python-`.upper()` würde ß→SS zerstören → eigene ß-bewusste Logik |
| **Original** | In der DB bleibt die Originalschreibweise erhalten |
| **Satzzeichen** | Beim **Encodieren einzelner Wörter** ignoriert; in **`.gpm`** verbatim in der Separator-Schicht |

### Primzahl-Mapping (27 Buchstaben)

| Buchstabe | Prim | Buchstabe | Prim | Buchstabe | Prim |
|-----------|------|-----------|------|-----------|------|
| E | 2 | N | 13 | X | 83 |
| A | 3 | R | 17 | Y | 67 |
| O | 5 | S | 19 | Z | 89 |
| I | 7 | T | 11 | ß | **103** |
| … | … | … | … | | |

Vollständige Map: `ge_prime/core.py` → `PRIME_MAP`

### Schreibweise-Schicht (.gpm)

Für die **exakte Rekonstruktion** des Originaltextes:

| Code | Bedeutung |
|------|-----------|
| 0 | alles klein |
| 1 | Erster groß, Rest klein |
| 2 | ALLES GROSS (ß → ẞ) |
| 3 | **Explicit** — Mischfall (z. B. `McDonald`), exakte Form im Overflow gespeichert |

---

## Das .gpm-Format v5

Statt Buchstabenketten speichert `.gpm` **reine Ganzzahlen** plus Schreibweise- und Separator-Schichten — **zeichengenaue Rekonstruktion** möglich. **v5** ergänzt die fraktale **Zell-Geometrie** (I_Satz): Wörter werden zu Atomen einer Zelle, der Body ist eine Kette von Zellen (max. 50 Token pro Zelle). **v1–v4** bleiben lesbar.

```
[GPM\x05 + Header 29 Byte + Flag BODY_CELL/BODY_FLAT]
  → Genom (v4): jedes Wort einmal (Original, Normalisiert, S als 2/4/8/16-Byte-Ganzzahl)
  → Body v5 (CELL): zellen_anzahl × [Skelett, I_Satz, k × (Word-ID, Case, I_Wort)]
  → Body FLAT (Fallback): wie v4 — [Word-ID, Case, I] pro Token
  → Separator-Blob + Perm-Code (Z/S/E/U-Bits)
  → Explicit-Overflow: Mischschreibweisen (CASE_EXPLICIT → eigene Kategorie pro Vorkommen)
  → CRC32-Trailer
```

**Zell-Teilung:** Gap-Split an `.!?`, Ziel ~30 Token, hart max. 50 — damit N_Satz in 64/128-Bit-Stufen bleibt (bereits 21 eindeutige Kategorien → N > 2⁶⁴).

### Speicherbreite von S und I

S und I werden **nicht als Dezimaltext**, sondern als **Binär-Ganzzahlen** mit fester Byte-Länge gespeichert. Die Länge wählt sich automatisch:

| Stufe | Bytes | Gültig wenn Wert ≤ |
|-------|-------|---------------------|
| 0 | 2 | 65535 |
| 1 | 4 | 2³²−1 |
| 2 | 8 | 2⁶⁴−1 |
| 3 | 16 | sehr große Wörter |

- **S (Genom):** 1 Byte Stufen-Info + 2/4/8/16 Byte Wert (`s_class` in 2 Bit).
- **I (Wort-Geometrie):** 2/4/8/16 Byte — Breite aus Wort-N.
- **I_Satz (Zell-Geometrie, v5):** 2/4/8/16 Byte — Breite aus Zell-N; pro Zelle ein Skelett + ein I_Satz.

### Separator-Layer & Perm-Code

Beim Kompilieren scannt der Compiler alle Zwischenräume zwischen Wörtern und setzt einen **Perm-Code** (Ganzzahl-Bitmask):

| Bit | Klasse | Bedeutung |
|-----|--------|-----------|
| — | BASE | Leerzeichen, Zeilenumbrüche, Satzzeichen inkl. `_` (literal, Perm 0) |
| Z = 1 | Ziffern | 0–9 per Escape-Sequenz |
| S = 2 | Symbole | @, €, §, … per feste Tabelle |
| E = 4 | Emoji | häufige Emoji per feste Tabelle |
| U = 8 | Unicode | Fallback für Symbole/Emoji außerhalb der Tabellen |

Symbole und Emoji liegen **nicht in der Datei**, sondern im Code (`gpm/separator_codec.py`). Beim Perm-Scan wird **U** automatisch gesetzt, wenn ein Zeichen nicht in der festen Tabelle steht (z. B. seltene Unicode-Sonderzeichen). Neu kompiliert wird **v5**; v1–v4 werden weiter gelesen.

**Module:**

| Datei | Aufgabe |
|-------|---------|
| `gpm/compiler.py` | Text → `.gpm` v5 (Zell-Kette + Perm-Scan) |
| `gpm/cell_geom.py` | Zell-Teilung, I_Satz, Kategorie-Schlüssel |
| `ge_prime/multiset_geom.py` | Gemeinsame Multiset-Engine (Wort + Zelle) |
| `gpm/reader.py` | Lesen, Rekonstruktion, Suche |
| `gpm/format.py` | Binär lesen/schreiben, CRC, v1–v4-Kompat |
| `gpm/int_codec.py` | Festbreiten 2/4/8/16 Byte für S und I |
| `gpm/separator_codec.py` | Perm-Code, Encode/Decode Separator-Blob |
| `gpm/cipher_wrap.py` | GPC-Hülle: verschlüsselte `.gpm` (Magic `GPC`) |
| `gpm/model.py` | Datenklassen |

---

## Verschlüsselte .gpm (GPC)

Normale `.gpm`-Dateien beginnen mit **`GPM`**. Verschlüsselte Dateien beginnen mit **`GPC`** — der Inhalt ist ein S(I)-Cipher-Paket; **`read_gpm` liefert ohne Schlüssel kein Genom**.

```
[GPC\x01]
  → JSON-Metadaten (Cipher-Version, Modus — kein Schlüssel)
  → S(I)-Cipher-Nutzlast (Base64-Payload aus ge_prime.cipher)
```

| Aktion | Verhalten |
|--------|-----------|
| **Kompilieren + Verschlüsseln** | Editor-Checkbox → `POST /api/gpm/compile` mit `encrypt: true` |
| **Lesen ohne Schlüssel** | HTTP 400, `needs_keys: true`, Modus sichtbar |
| **Lesen mit Schlüssel** | Entschlüsselung → Rekonstruktion → normale `.gpm` im Speicher für Suche/I-Kurve |
| **Suche** | Blockiert auf verschlüsselten Blobs |

Schlüssel und Modus müssen beim Entschlüsseln **identisch** zum Kompilieren sein (Hardcore: kommagetrennte Liste).

---

## Schnellstart

### Windows

```batch
cd Ge-Prime-Matrix
setup.bat      REM einmalig: Python registrieren, Abhängigkeiten
start.bat      REM Server starten → http://127.0.0.1:5000
```

Stoppen: `stop.bat` oder **Strg+C** im Server-Fenster.

### Linux / macOS

```bash
cd Ge-Prime-Matrix
chmod +x start.sh
./start.sh
```

### Abhängigkeiten

- Python **3.9+**
- Pakete: `flask`, `requests` (siehe `requirements.txt`)

---

## Python einrichten (Windows)

Auf vielen Systemen zeigt `python` nur auf den **Windows-Store-Alias** (funktioniert nicht). Dieses Projekt löst das **projekt-lokal**:

| Datei | Zweck |
|-------|--------|
| **`setup.bat`** | Findet Python, schreibt `.python-path`, erzeugt lokale `.vscode/settings.json` (gitignored), installiert Pakete |
| **`dev.bat`** | Führt Befehle mit dem Projekt-Python aus — **ohne** System-PATH |
| **`.python-path`** | Gespeicherter Pfad zum Python-Interpreter (gitignored) |
| **`.venv/`** | Optionale virtuelle Umgebung (wenn `venv`-Modul verfügbar) |

### Terminal-Befehle ohne PATH

```batch
dev.bat run_tests.py
dev.bat main.py
dev.bat scripts\gpm_tool.py compile -i text.txt -o out.gpm
```

### Cursor / VS Code

Nach `setup.bat` zeigt die lokale `.vscode/settings.json` (gitignored) auf den richtigen Interpreter. Vorlage: `.vscode/settings.json.example`. Cursor-Terminal: **`dev.bat`** verwenden, wenn `python` nicht gefunden wird.

### Empfehlung langfristig

Python von [python.org](https://www.python.org/downloads/) installieren mit **„Add Python to PATH“**. Alternativ Windows-Store-Alias deaktivieren: *Einstellungen → Apps → App-Ausführungsaliase → python.exe AUS*.

---

## Server starten & stoppen

### Lokale Entwicklung

| Skript | Aktion |
|--------|--------|
| `start.bat` / `start.sh` | Beendet alte **Ge-Prime**-Instanz auf Port 5000, startet neu |
| `stop.bat` | Beendet nur Prozesse mit `run_server.py` (keine fremden Dienste) |
| `scripts/run_server.py` | Flask-Server mit Preflight-Checks |

**Mehrere Laufzeiten:** `start.bat` und `run_server.py` räumen vor dem Start alte Instanzen auf (`scripts/server_control.py`). Eine Lock-Datei `data/.server.lock` hilft bei verwaisten Prozessen.

### Produktion (Render / Cloud)

In Produktion (`RENDER=true` oder `GE_PRIME_ENV=production`):

- **Kein** automatisches Beenden anderer Prozesse
- **Kein** Browser-Auto-Open
- **Keine** Lock-Datei relevant (ephemeres Dateisystem)
- Bindung an **`0.0.0.0:$PORT`** (Render-Vorgabe)

→ Mehrfach-Instanz-Probleme betreffen **nur lokale Entwicklung**, nicht Server-Deployment.

---

## Web-Oberfläche

URL nach Start: **http://127.0.0.1:5000**

| Tab | Funktion |
|-----|----------|
| **Konzept** | Erklärung S(I), Primzahl-Map, Normalisierung |
| **Encodieren** | Bis zu 50 Wörter → DB (Random/unsortiert) |
| **Decodieren** | S + I → normalisiertes Wort |
| **Wortpaar** | Vergleichen (ggT/kgV) und Differenz (Teilmenge, Anagramm) — gemeinsame Wortfelder |
| **I-Kurve** | Index-Vektoren, Meta-Genom, Sprache/Domäne, DB-Sprachaudit, Plagiats-Heuristik |
| **GPM Datei** | Editor, S(I)-Verschlüsselung, kompilieren, lesen, rekonstruieren, Substanz-/ggT-/kgV-Suche; optional **GPC** beim Kompilieren |
| **Datenbank** | Statistik nach Sprache |

Der GPM-Editor zeigt **volle Rekonstruktion**, Lossless-Indikator, scrollbare Tabellen und Copy-Button. Verschlüsselte Dateien (Magic **GPC**) erfordern beim Lesen dieselben Schlüssel wie beim Kompilieren; Suche auf verschlüsselten Blobs ist blockiert.

---

## HTTP-API

Alle API-Antworten: `Cache-Control: no-store`.

### System

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/health` | Status, Version, GPM-Version, DB-Pfad, Route-Checks |
| GET | `/api/version` | Build-Info, GPM-Version, GPM-Tab-Check |
| GET | `/api/db/stats` | Wortanzahl pro Sprache |

### Encodierung

| Methode | Pfad | Body | Beschreibung |
|---------|------|------|--------------|
| POST | `/api/encode` | `{ "text": "…" }` | Encodiert bis 50 Wörter, speichert in DB |
| POST | `/api/decode` | `{ "substance", "perm_index" }` | S,I → Wort + Schritte |
| POST | `/api/compare` | `{ "word1", "word2" }` | ggT + kgV-Vergleich |
| POST | `/api/diff` | `{ "word1", "word2" }` | Arithmetische Differenz, Teilmenge, Anagramm |
| POST | `/api/i-curve` | Freitext oder `.gpm` pro Seite (multipart `file_a`/`file_b` oder JSON), optional `db_audit_mode`: `de_en` (Standard), `all_db`, `off` | I-Kurven, Meta-Genom, DB-Audit, Plagiats-Heuristik |
| POST | `/api/cipher/encrypt` | `{ "text", "mode", "keys" }` | S(I)-Verschlüsselung (word/prime/si/hardcore) |
| POST | `/api/cipher/decrypt` | `{ "ciphertext", "keys" }` | Entschlüsselung (Modus im Paket) |

**`/api/i-curve` — Antwort (Auszug):** `curve_a`, `curve_b` (`sparkline_points`, `point_count`, Vorschau-Tabellen), `comparison`, `meta_a` / `meta_b` (`language` inkl. `db_coverage`, Domäne, Top-Wörter), `meta_comparison`, `plagiarism_assessment` (`db_coverage_a`/`b`, `db_audit_mode`).

### .gpm

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| POST | `/api/gpm/compile` | JSON `{ "text", optional "encrypt", "cipher_mode", "cipher_keys" }` → Base64-`.gpm` v5 oder verschlüsselte GPC-Hülle |
| POST | `/api/gpm/read` | Upload oder `{ "file_base64", optional "cipher_keys" }` → Analyse (v1–v4); GPC-Dateien brauchen Schlüssel |
| POST | `/api/gpm/search` | `{ "file_base64", "query", "mode", "query2"? }` — `substance`, `gcd` oder `lcm` (kgV braucht `query2`) |

---

## CLI-Werkzeuge

Alle über `dev.bat` (Windows) oder `python` (Linux):

```batch
dev.bat main.py                          REM Encode/Decode/DB-Demo
dev.bat scrape.py --help                 REM Wortlisten scrapen
dev.bat scripts\bootstrap.py             REM Leere DB anlegen
dev.bat scripts\reset_db.py              REM DB zurücksetzen
dev.bat scripts\server_control.py        REM Server auf Port 5000 stoppen
dev.bat scripts\gpm_tool.py compile -i in.txt -o doc.gpm
dev.bat scripts\gpm_tool.py read -i doc.gpm
dev.bat scripts\gpm_tool.py search -i doc.gpm -q Straße
dev.bat scripts\gpm_tool.py search -i doc.gpm MUT WUT --mode lcm
```

---

## Projektstruktur & Module

```
Ge-Prime-Matrix/
├── ge_prime/              # Domain-Paket: S/I, Analyse, Cipher, Linguistik, Config
├── main.py                # CLI-Demos (Encode, Compare, I-Kurve, Cipher, DB)
├── scrape.py              # Wortlisten-Import (ruft scrapers/ auf)
├── run_tests.py           # Test-Runner (unittest)
├── start.bat / start.sh   # Server starten
├── stop.bat               # Server stoppen (Windows)
├── setup.bat / dev.bat    # Setup bzw. Python-Wrapper
├── .env.example           # Vorlage für lokale Umgebungsvariablen (committet)
├── .gitignore             # DB, .env, Logs, venv, IDE-Settings — siehe unten
├── render.yaml            # Render.com Deployment
├── requirements.txt
├── data/                  # SQLite (gitignored), sample_words_de.txt, .gitkeep
├── db/                    # SQLite: Repository, Schema, Sprachen
├── gpm/                   # .gpm v4: Compiler, Reader, Separator, GPC-Hülle
├── pipeline/              # Text → S/I: Normalisierung, Token, Hilfetexte
│   └── size_compare.py    # Speichergrößen-Vergleich (UTF-8, JSON, .gpm, …)
├── scrapers/              # Wortquellen: Leipzig, Aspell, GitHub, …
├── scripts/               # Betrieb: Server, Port-Steuerung, Bootstrap, gpm_tool
├── web/                   # Flask-UI + JSON-API
│   ├── app.py             # Flask-Setup + register_routes()
│   ├── handlers/          # API nach Bereichen (system, encode, gpm, …)
│   │   └── _steps.py      # Schritt-für-Schritt-Erklärungen für Encode/Decode
│   ├── templates/         # index.html, Partials
│   └── static/            # app.js, style.css
└── tests/                 # unittest-Suite
```

### Python-Module (`ge_prime/` und `gpm/`)

| Modul | Aufgabe |
|-------|---------|
| `ge_prime/core.py` | PRIME_MAP, CHAR_MAP, Permutationsraum N |
| `ge_prime/encode.py` | Wort → S, I |
| `ge_prime/decode.py` | S, I → Wort; Faktorisierung |
| `ge_prime/compare.py` | ggT, kgV, Ähnlichkeit zweier Substanzen |
| `ge_prime/diff.py` | S_rest, Teilmenge, Anagramm |
| `ge_prime/i_curve.py` | I-Kurve extrahieren, Paarvergleich, `analyze_pair` |
| `ge_prime/meta_genome.py` | Dokumenten-Vektor V, Sprache/Domäne, Plagiats-Kombi |
| `ge_prime/cipher.py` | S(I)-Verschlüsselung (word/prime/si/hardcore) |
| `ge_prime/config.py` | APP_VERSION, REQUIRED_API_ROUTES, ROOT, db_path |
| `ge_prime/linguistics/` | Sprach-/Domänenerkennung (Hybrid, DB-Tier) |
| `gpm/compiler.py` | Text → `.gpm` v4 |
| `gpm/reader.py` | `.gpm` lesen, Rekonstruktion, `genome_payload_bytes` |
| `gpm/separator_codec.py` | Separator-Layer, Perm-Code, `_` in BASE |
| `gpm/cipher_wrap.py` | GPC: verschlüsselte `.gpm`-Hülle |
| `pipeline/normalize.py` | Normalisierung + UI-Hilfetexte (INDEX_HELP, CIPHER_HELP, …) |
| `web/handlers/` | Flask-Routen: system, encode, decode, compare, diff, icurve, cipher, gpm, size |

### Schichten (Namenskonvention)

| Präfix/Ordner | Rolle |
|---------------|--------|
| `ge_prime/` | Mathematik, Analyse, Cipher, Linguistik, Konfiguration |
| `pipeline/` | Textverarbeitung vor/nach Encode |
| `gpm/` | Binärformat `.gpm` und Dokument-Logik |
| `web/handlers/` | HTTP-API nach Funktionsbereichen |
| `web/` | Flask-App, Templates, Static |
| `scripts/` | Start, Stop, Setup — nicht importieren in Produktionscode |
| `db/` | Persistente Wort-Speicherung (Web + Scraper) |

Root-CLI (`main.py`, `scrape.py`, `run_tests.py`) liegen bewusst im Projektroot — kurze Aufrufe via `dev.bat main.py` bzw. Doppelklick auf Batch-Dateien.

**Import-Konvention:** `ge_prime.*`, `gpm.*`, `web.handlers.*`, `pipeline.*`, `db.*` — keine Root-Duplikate.

**Web-API:** [`web/app.py`](Ge-Prime-Matrix/web/app.py) registriert alle Routen über `register_routes()` in [`web/handlers/__init__.py`](Ge-Prime-Matrix/web/handlers/__init__.py) — ein Handler-Modul pro API-Bereich.

---

## Repository & GitHub

**Öffentliches Repo:** [github.com/FrancescoSchlawiener/Ge-Prime-Matrie](https://github.com/FrancescoSchlawiener/Ge-Prime-Matrie)

Das Repository ist für GitHub vorbereitet: Quellcode, Tests und Vorlagen sind versioniert; Laufzeitdaten und maschinenspezifische Pfade bleiben lokal.

### Clone

```batch
git clone https://github.com/FrancescoSchlawiener/Ge-Prime-Matrie.git
cd Ge-Prime-Matrie\Ge-Prime-Matrix
setup.bat
dev.bat scripts\bootstrap.py
start.bat
```

Unter Linux/macOS: `./start.sh` statt `start.bat`; Python-Pfad ggf. manuell setzen.

### Was **nicht** im Repo liegt (`.gitignore`)

| Kategorie | Beispiele | Grund |
|-----------|-----------|--------|
| **Datenbank** | `data/ge_prime.db`, `*.db`, SQLite-WAL/SHM | Lokal gepflegt (~ Millionen Wörter), zu groß für Git |
| **Umgebung** | `.env`, `.env.local` | Secrets und lokale Overrides |
| **Python-Laufzeit** | `.venv/`, `__pycache__/`, `.pytest_cache/` | Reproduzierbar per `setup.bat` / `pip install` |
| **Server-Lock** | `data/.server.lock` | Prozess-Artefakt beim lokalen Start |
| **Interpreter-Pfad** | `.python-path` | Maschinenspezifisch (Windows pgAdmin/Python) |
| **IDE** | `.vscode/settings.json` | Wird von `setup.bat` / `find_python.py` lokal erzeugt |
| **Logs & Scraper** | `*.log`, `scrapers/logs/*.tsv` | Laufzeit-Ausgaben |
| **Test-Artefakte** | `test_result*.txt`, `test_out.txt` | Temporäre Test-Outputs |
| **OS** | `.DS_Store`, `Thumbs.db` | Systemdateien |

Committet bleiben u. a. [`data/sample_words_de.txt`](Ge-Prime-Matrix/data/sample_words_de.txt), [`data/.gitkeep`](Ge-Prime-Matrix/data/.gitkeep) und [`.env.example`](Ge-Prime-Matrix/.env.example).

Ignore-Regeln: [`.gitignore`](.gitignore) (Repo-Root) und [`Ge-Prime-Matrix/.gitignore`](Ge-Prime-Matrix/.gitignore) (App).

### Lokale Konfiguration

**Umgebungsvariablen:** Vorlage [`.env.example`](Ge-Prime-Matrix/.env.example) nach `.env` kopieren (optional — alle Werte haben Defaults im Code):

```batch
copy .env.example .env
```

**IDE:** Vorlage [`.vscode/settings.json.example`](Ge-Prime-Matrix/.vscode/settings.json.example). Nach `setup.bat` zeigt die gitignored `settings.json` auf den gefundenen Interpreter (pgAdmin, `.venv` oder System-Python).

**Datenbank-Pfad:** Standard `data/ge_prime.db`; Override via `GE_PRIME_DB` (siehe [`db/paths.py`](Ge-Prime-Matrix/db/paths.py)).

### Vor dem Push prüfen

```powershell
git status
git ls-files | Select-String -Pattern '\.(db|sqlite|env)$|settings\.json|\.python-path'
cd Ge-Prime-Matrix
dev.bat run_tests.py
```

Keine `.db`, `.env` oder `settings.json` im Index — dann ist das Repo sicher öffentlich sichtbar.

---

## Deployment (Render)

`render.yaml` ist vorkonfiguriert:

- **Build:** `pip install -r requirements.txt`
- **Start:** `python scripts/run_server.py`
- **Env:** `GE_PRIME_ENV=production`, `OPEN_BROWSER=0`
- Render setzt automatisch `RENDER=true` und `PORT`

**Hinweise:**

- Dateisystem ist **ephemeral** — SQLite unter `data/` geht bei Redeploy verloren. Für Persistenz: Render Postgres oder externes Storage.
- Bindung erfolgt an `0.0.0.0:$PORT` (automatisch in Produktion).
- Free Tier: Spin-down nach Inaktivität (siehe [Render-Docs](https://render.com/docs/free)).

Manuell deployen: Repository verbinden, Root Directory `Ge-Prime-Matrix`, Blueprint aus `render.yaml` oder gleiche Werte manuell setzen.

---

## Tests

```batch
dev.bat run_tests.py
```

Oder:

```bash
python run_tests.py
```

Abdeckung (Auswahl):

| Testdatei | Inhalt |
|-----------|--------|
| `test_letters.py`, `test_normalize_case.py` | Buchstaben, ß, Umlaute, Groß-/Kleinschreibung |
| `test_gpm.py`, `test_int_codec.py`, `test_separator_codec.py` | GPM v4 Roundtrip, S/I-Stufen, Separator, `_` |
| `test_i_curve.py`, `test_meta_genome.py` | I-Kurve, Meta-Genom, Plagiats-Heuristik |
| `test_cipher.py` | S(I)-Verschlüsselung aller Modi |
| `test_compare.py`, `test_diff.py` | ggT/kgV, arithmetische Differenz |
| `test_web.py`, `test_static_ui.py` | API-Routen, Tab-Markup, Hilfetexte |
| `test_run_server.py`, `test_server_control.py` | Preflight, Port-Steuerung, Produktion |
| `test_size_compare.py`, `test_tokenize.py`, `test_packages.py` | Speichervergleich, Tokenizer, Paket-Layout |

---

## Umgebungsvariablen

Alle Variablen sind optional — der Server startet ohne `.env` mit den Defaults unten. Vorlage zum Kopieren: [`.env.example`](Ge-Prime-Matrix/.env.example) (committet); echte `.env`-Dateien sind gitignored.

| Variable | Standard | Beschreibung |
|----------|----------|--------------|
| `PORT` | `5000` | HTTP-Port |
| `HOST` | `127.0.0.1` (lokal) / `0.0.0.0` (Prod) | Bind-Adresse |
| `OPEN_BROWSER` | `1` (lokal) / `0` (Prod) | Chrome beim Start |
| `FLASK_DEBUG` | `0` | Flask-Debug-Modus |
| `GE_PRIME_DB` | `data/ge_prime.db` | SQLite-Pfad |
| `GE_PRIME_ENV` | — | `production` → Cloud-Modus |
| `RENDER` | — | Von Render gesetzt → Produktion |
| `PYTHONIOENCODING` | `utf-8` | Konsolen-Encoding |

---

## Fehlerbehebung

### `Python wurde nicht gefunden` (Windows)

1. `setup.bat` ausführen  
2. Danach `dev.bat` statt `python` nutzen  
3. Oder echten Python installieren / Store-Alias deaktivieren (siehe oben)

### Port 5000 belegt / alte UI

```batch
stop.bat
start.bat
```

Im Browser: **Strg+F5** (Hard Reload).

### `/api/health` liefert falsche Version

Alter Server-Prozess läuft noch → `stop.bat`, dann `start.bat`.

### GPM: „Payload-Länge inkonsistent“ / CRC-Fehler

Datei beschädigt oder von alter/incompatibler Version. Neu kompilieren mit aktuellem Build (`2026.06-gpm-v49` / GPM v7).

### GPC: „Schlüssel erforderlich“ / `needs_keys`

Die Datei beginnt mit **GPC** — normales Lesen liefert nur Metadaten (Modus). Gleiche Schlüssel und Modus wie beim Kompilieren in den Editor-Feldern angeben.

### I-Kurve: „Symbol nicht in Tabelle“

Unbekanze Zeichen werden beim Kompilieren über Perm **U** (Unicode-Fallback) abgebildet. Aktuellen Build verwenden; `_` (Unterstrich) ist seit v4 in BASE enthalten (`hello_world`).

### Cursor-Terminal: Befehle ohne Ausgabe

Sandbox ohne Python im PATH — `dev.bat` verwenden oder Terminal mit vollem Systemzugriff.

### venv schlägt fehl (pgAdmin-Python)

Normal — pgAdmin-Python hat oft kein `venv`-Modul. `setup.bat` nutzt dann pgAdmin-Python **direkt** (`.python-path`).

---

## Lizenz & Version

Projektversion: **`2026.06-gpm-v49`** · GPM-Format: **v7** · Quellcode: [GitHub](https://github.com/FrancescoSchlawiener/Ge-Prime-Matrie)

Bei Fragen oder Bugs: Tests laufen lassen (`dev.bat run_tests.py`) und `/api/health` prüfen.
