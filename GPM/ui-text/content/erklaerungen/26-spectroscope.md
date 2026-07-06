---
title: Spectroscope
---

# Spectroscope — Token-Span-Analyse

Der **Spectroscope** analysiert **Token-Spans** in einem Dokument: welche Zeichenbereiche gehören zu welchem Token, wie verteilen sich Substanz und Index visuell über den Text?

## Kernidee

Die I-Kurve zeigt den **globalen Verlauf**. Der Spectroscope zoomt auf **lokale Spans** — hilfreich beim Debuggen von Kompilierung, Case-Code und Zell-Grenzen.

## Formal

Eingabe: `GpmDocument` (oder kompilierter Payload)

Ausgabe:

| Feld | Bedeutung |
|------|-----------|
| `spans` | Liste (start, end, token_index) |
| `token_meta` | word_id, perm_index, substance |
| `char_map` | Token → Zeichenoffset |

## Ablauf

1. Dokument im Editor kompilieren
2. `POST /api/editor/spectroscope` mit Dokument-JSON
3. Spans über Rohtext legen
4. Hover/Klick: Token-Details


## Bezug zur I-Kurve

| Tool | Skala |
|------|-------|
| I-Kurve | ganzes Dokument, ≤512 Punkte |
| Spectroscope | char-genaue Token-Spannen |

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [I-Kurve](/erklaerungen/20-i-curve)
- [Tokens](/erklaerungen/16-tokens)
- [Cells](/erklaerungen/19-cells)
