---
title: I-Kurve
---

# I-Kurve — Perm-Verlauf im Dokument

Die **I-Kurve** zeigt, wie sich der Permutations-Index (I) relativ zum Perm-Raum entlang eines Dokuments entwickelt — Satz für Satz, Zelle für Zelle.

## Kernidee

Zwei Dokumente können ähnliche Substanz-Ketten haben, sich aber in der **Reihenfolge-Dynamik** unterscheiden. Die I-Kurve macht diese Dynamik sichtbar — zentral für Anagramm-ähnliche Texte (LISTEN vs. SILENT).

## Formal

Pro Token oder Zelle:

```
ratio_i = perm_index_i / perm_space_i   (normiert 0…1)
```

`perm_space` = Größe des Permutationsraums für das normalisierte Wort (n! / ∏ cᵢ!).

**Downsampling-Invariante B:** Die Workbench-Sparkline zeigt maximal **512 Punkte**; die Aggregation (min/max/mean pro Bucket) ist API-contracted, damit UI und Backend übereinstimmen.

## Vier Vergleichsachsen

Beim Dokumentpaar-Vergleich (`analyze_pair`):

| Achse | Quelle |
|-------|--------|
| **substance** | S-Kette, ggT/kgV |
| **token_i** | I-Ratio pro Token |
| **cell_i** | Zell-Geometrie — [Cells](/erklaerungen/19-cells) |
| **hierarchy** | Satz/Absatz-Struktur (optional) |

## Ablauf — Kurve extrahieren

1. Dokument kompilieren (+ optional Geometrie)
2. Token- oder Zell-Sequenz mit perm_index, perm_space lesen
3. Ratios bilden
4. Auf ≤512 Punkte downsamplen
5. Matrix für zwei Dokumente + DTW-Fusion


## Beispiel LISTEN vs. SILENT

| Dokument | S-Kurve | I-Kurve |
|----------|---------|---------|
| LISTEN-Text | Referenz | Referenz |
| SILENT-Text | **parallel** (Anagramm) | **divergiert** |

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Index I](/erklaerungen/02-index-i)
- [Cells](/erklaerungen/19-cells)
- [ggT / kgV](/erklaerungen/09-ggt-kgv)
- [Spectroscope](/erklaerungen/26-spectroscope)
