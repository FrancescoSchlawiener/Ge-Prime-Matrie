---
title: GPM Binary
---

# GPM Binary — das .gpm-Containerformat

Die **.gpm**-Datei ist der binäre Container für kompilierte GPM-Dokumente. Sie vereint Header-Registry, Token-Stream, Gap-Payloads und optional Geometrie, Block-Baum und Verschlüsselung.

## Kernidee

Ein `GpmDocument` im Speicher wird deterministisch in Bytes serialisiert und zurückgelesen. Der Roundtrip `write_gpm` → `read_gpm` → `reconstruct_text` muss den Originaltext (bzw. Hybrid-Quelle) bitgenau wiederherstellen.

## Formal — Datei-Header (29 Byte)

| Offset | Inhalt |
|--------|--------|
| 0–2 | Magic `GPM` |
| 3 | Versionsbyte |
| 4 | Flags (Bitmask) |
| 5–8 | Anzahl Header-Einträge (Wörter) |
| 9–12 | Anzahl Body-Tokens |
| 13–16 | Separator-Perm / reserviert |
| 17–20 | Explicit-Anzahl |
| 21–24 | Middle-Block-Länge (Gaps) |
| 25–28 | Payload-Länge |

**Magic-Prüfung:** Die ersten drei Bytes müssen `GPM` sein. Verschlüsselte Dateien beginnen mit `GPC\x01` — siehe [GPC-Hülle](/erklaerungen/28-cipher-gpc).

## Versionen

| Version | Status | Besonderheiten |
|---------|--------|----------------|
| **4** | Legacy | Flaches Layout, OG-lesbar |
| **8** | Profil | + `AlphabetProfile` im Header |
| **9** | **Standard** | Fraktal-Geometrie, Registry-C, GAP-RLE, Block-Tree |

Die Workbench schreibt standardmäßig **Version 9**.

## Flags (Auswahl)

| Flag | Bedeutung |
|------|-----------|
| `FLAG_PROFILE` | Profilname im Payload |
| `FLAG_GAP_RLE` | GAP run-length-kodiert |
| `FLAG_FRACTAL` | Registry-C + Geometrie |
| `FLAG_BLOCK_TREE` | Code-/Block-Baum eingebettet |
| `FLAG_BODY_CELL` | Zell-Geometrie aktiv |

## Ablauf — Speichern

1. Text/Code/Hybrid kompilieren → `GpmDocument`
2. `write_gpm(doc, version=9)` → `bytes`
3. Bytes als `.gpm` ablegen oder Base64 an API senden

## Ablauf — Laden

1. Datei lesen oder Drag&Drop im Editor
2. `read_gpm(bytes)` → `GpmDocument`
3. Bei verschlüsselter Datei: Schlüssel + `decrypt_gpm_file`
4. `reconstruct_text(doc)` oder Hybrid-Rekonstruktion

## Payload-Reihenfolge (v9)

Profil → Registry-C → Block-Tree (optional) → Genom (Header) → Token-Body → GAP Middle → Explicit


## Beispiel (konzeptionell)

```
"Hallo Welt."  →  compile  →  GPM\x09…  →  read  →  "Hallo Welt."
```

Drei Wörter im Header (`Hallo`, `Welt`, `.` je nach Tokenisierung), `n` Tokens, `n+1` Gaps — siehe [Gaps](/erklaerungen/12-gaps-dokument).

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Tokens](/erklaerungen/16-tokens)
- [Registry](/erklaerungen/15-registry)
- [Case & Explicit](/erklaerungen/14-case-explicit)
- [Cells](/erklaerungen/19-cells)
- [GPC-Hülle](/erklaerungen/28-cipher-gpc)
