---
title: Einstieg S(I)
---

# Einstieg: Die Ge-Prime-Matrix

Die **Ge-Prime-Matrix (GPM)** speichert Sprache und strukturierte Daten als **Identitätspakete** — nicht als bloße Zeichenketten. Das zentrale Datenobjekt für Wörter heißt **S(I)**:

- **S (Substanz)** — kommutatives Primprodukt über die Buchstaben-Multimenge
- **I (Index)** — ordnungssensitiver Permutations-Rang im Raum N

Zusammen sind S und I **eindeutig**: Aus dem Paar lässt sich der normalisierte Text rekonstruieren. Anagramme teilen dieselbe Substanz, unterscheiden sich im Index.

## Warum zwei Komponenten?

| Eigenschaft | Substanz S | Index I |
|-------------|------------|---------|
| Reihenfolge | irrelevant | entscheidend |
| Algebra | Multiplikation (Primzahlen) | Fakultäts-Rang |
| Vergleich | ggT, kgV | I-Kurven, DTW |
| Anagramm | gleiches S | verschiedenes I |

Ohne S wäre die Buchstabenmenge nicht kompakt vergleichbar. Ohne I ginge die Reihenfolge verloren.

## Pipeline (Wort → S(I) → Text)

1. **Normalisierung** — Profil, NFC, Zeichen-Whitelist
2. **Substanz** — Primzahlprodukt der Multimenge
3. **Index** — Rang der Zeichenfolge im Permutationsraum
4. **Speichern** — Registry + Token im Dokument
5. **Decode** — Substanz zerlegen, Index entpacken, Text rekonstruieren

## Weitere Identitätstypen

Nicht alles ist ein „Wort“ im S(I)-Sinne. GPM kennt weitere Pointer:

| Symbol | Name | Typischer Inhalt |
|--------|------|------------------|
| **S(I)** | Substanz + Index | Wörter, Token |
| **N(I)** | Ganzzahl-Identität | Literale `42`, `0042` |
| **D(I)** | Dezimal-Identität | Brüche `3,14` kanonisch |
| **H(I)** | Hybrid-Identität | Gemischte Läufe `abc123def` |

Details: [N(I)](/erklaerungen/04-ni-ganzzahl), [D(I)](/erklaerungen/05-di-dezimal), [H(I)](/erklaerungen/06-hi-hybrid-identitaet).

Nach jeder Berechnung liefert die API **Rechenschritte** (`steps[]`) — Säule 4 der Workbench-Pädagogik.

## Typische Fehler

- S und I verwechseln: gleiches S heißt nicht gleicher Text.
- Profil ignorieren: og vs. Roman liefert andere S/I-Werte.
- Nur Rohtext vergleichen statt Substanz oder I-Kurve.

## Verknüpfungen

- [Substanz S](/erklaerungen/01-substanz-s)
- [Index I](/erklaerungen/02-index-i)
- [Decode](/erklaerungen/03-decode)
- [Gaps & Dokument](/erklaerungen/12-gaps-dokument)
