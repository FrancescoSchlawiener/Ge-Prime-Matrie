---
title: Case & Explicit
---

# Case-Code und Explicit-Einträge

GPM trennt **kanonische Wortform** (für S und Perm-Raum) von der **Original-Schreibweise** (Groß/Klein, Ausnahmen). Dafür gibt es `case_code` pro Token und optional `explicit[]` im Dokument.

## Kernidee

Nach Normalisierung ist `listen` die Basis für Substanz und Index. Die Anzeige `Listen` oder `LISTEN` wird über **Case-Kodierung** und **Explicit-Overrides** rekonstruiert — ohne den Perm-Raum zu vergrößern.

## Formal

### case_code (pro Token)

| Feld | Bedeutung |
|------|-----------|
| `word_id` | Verweis auf Header-Eintrag |
| `perm_index` | I im Perm-Raum des **normalisierten** Worts |
| `case_code` | Bitmaske / Policy-Code für Groß-Klein pro Zeichen |

Die Case-Policy ist profilabhängig (`DEFAULT_CASE_POLICY`).

### explicit[] (Dokument-Ebene)

Liste von `(token_index, override_text)`:

- Nur wo die Case-Policy **nicht** ausreicht
- Bitgenaue Rekonstruktion seltener Schreibweisen
- Explizit gespeichert, nicht abgeleitet

## Ablauf — Rekonstruktion

1. Token `word_id` → Header `word_normalized`
2. `perm_decode` mit `perm_index` → Zeichenfolge in Normalform
3. `case_code` anwenden → Ziel-Groß/Klein
4. Falls `explicit[i]` existiert → Override-Text statt abgeleiteter Form
5. Mit Gaps verketten → Volltext

## Ablauf — Kompilierung

1. Rohtext tokenisieren
2. Pro Wort: canonical (Anzeige) vs. normalized (Perm)
3. Case-Diff berechnen → `case_code`
4. Nicht darstellbare Fälle → `explicit`-Eintrag



## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Normalisierung](/erklaerungen/07-normalisierung)
- [Tokens](/erklaerungen/16-tokens)
- [GPM Binary](/erklaerungen/13-gpm-binary)
- [Profile](/erklaerungen/08-profile)
