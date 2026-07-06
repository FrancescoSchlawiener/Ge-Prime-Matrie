---
title: Redundanz
---

# Redundanz — gleitende Fenster und Struktur-Scan

Der **Redundanz-Scan** findet wiederkehrende Substanz-Muster in Dokumenten — mit adaptiven Fenstern und optionaler Trennung von **inhaltlicher** vs. **struktureller** Redundanz.

## Kernidee

Lange Texte enthalten oft wiederholte Wortfolgen oder Bausteine. GPM gleitet Fenster über Token-/Substanz-Ketten und meldet Überlappungen. Pointer mit `structural_only` zählen nur zur Struktur — [Payload-Kinds](/erklaerungen/17-payload-kinds).

## Formal

| Parameter | Wert |
|-----------|------|
| Fenstergrößen | adaptiv [8, 12, 16, 20, 24, 28] Token |
| Scan-Modus | index-only (ohne Voll-Rekompilierung) |
| Ausgabe | Treffer mit Position, Länge, Substanz-Hash |

## Ablauf

1. Dokument (oder Index-Signatur) laden
2. Job starten: `POST /api/jobs/redundancy`
3. Runner gleitet Fenster, vergleicht Substanz-Sequenzen
4. Ergebnis-Tabelle im UI

## API & Jobs

Redundanz ist **job-basiert** (lange Läufe):

- Job anlegen → Status pollen
- `index_only`-Modus für schnelle Voranalyse
- Fehler als strukturierte `error.code`


## Bezug zum Korpus

Korpus-Signaturen und Redundanz-Scan teilen **Basis-Layer**-Ideen (Postings, Substanz-Ketten), aber unterschiedliche Ziele: Korpus = Dokument-Dokument-Ähnlichkeit; Redundanz = intra-dokumentale Wiederholung.

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Korpus](/erklaerungen/21-corpus)
- [Substanz S](/erklaerungen/01-substanz-s)
- [Tokens](/erklaerungen/16-tokens)
