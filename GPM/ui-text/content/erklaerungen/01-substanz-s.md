---
title: Substanz S
---

# Substanz S — das kommutative Primprodukt

Die **Substanz** eines Wortes fasst die **Buchstabenmenge** als eine einzige Ganzzahl zusammen — unabhängig von der Reihenfolge.

## Formal

```
S = ∏ pᵢ^aᵢ
```

Jeder Buchstabe des Profils ist einer Primzahl `pᵢ` zugeordnet. Der Exponent `aᵢ` ist die Häufigkeit in der normalisierten Multimenge.

## Kernidee

Substanz ist **kommutativ**: Permutationen der Buchstaben ändern S nicht. Deshalb haben Anagramme dieselbe Substanz.

| Wort | Substanz (konzeptionell) |
|------|--------------------------|
| LISTEN | S |
| SILENT | **dieselbe** S |
| TINSEL | **dieselbe** S |

Die **Reihenfolge** steckt im **Index I** — siehe [Index I](/erklaerungen/02-index-i).

## Ablauf in der Pipeline

1. Rohtext → [Normalisierung](/erklaerungen/07-normalisierung)
2. Multimenge zählen (wie oft jedes Zeichen vorkommt)
3. Primzahlen aus dem Profil multiplizieren
4. Ergebnis: Ganzzahl S

## Profilabhängigkeit

Jedes `AlphabetProfile` (33 Schriftsätze) definiert eine eigene Primzuordnung. Dasselbe Wort in Profil `og` und `roman` kann **verschiedene** Substanzen haben — Vergleiche nur innerhalb eines Profils.

## Algebraische Nutzung

| Operation | Bedeutung |
|-----------|-----------|
| **ggT(S₁, S₂)** | gemeinsame Primteiler → gemeinsame Buchstabenbasis |
| **kgV(S₁, S₂)** | Vereinigung der Multimengen |

Im Tab **Vergleichen → Wortpaar** siehst du ggT und kgV direkt — [ggT / kgV](/erklaerungen/09-ggt-kgv).


## Registry-Bezug

In einem Dokument speichert die **Registry** pro distinct Wort: normalisierter Text, Substanz S, Index I (als Referenz). Token verweisen nur auf `word_id` — [Registry](/erklaerungen/15-registry).


## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Index I](/erklaerungen/02-index-i) — Reihenfolge
- [Decode](/erklaerungen/03-decode) — S zerlegen in Multimenge
- [Normalisierung](/erklaerungen/07-normalisierung) — Voraussetzung
