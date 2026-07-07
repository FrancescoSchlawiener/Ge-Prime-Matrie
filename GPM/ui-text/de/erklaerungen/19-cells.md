---
title: Cells
---

# Cells — Zell-Geometrie und I-Kurve

**Cells** partitionieren ein Dokument in Satz- und Wort-Zellen mit Geometrie-Metadaten. Sie sind die Grundlage für **I-Kurven** und dokumentweite Vergleiche auf Zell-Ebene.

## Kernidee

Nach der flachen Token+Gap-Repräsentation kann GPM eine **visuelle und metrische Struktur** materialisieren: welches Token gehört zu welcher Zelle, wie lang ist der Perm-Raum pro Zelle, wie verläuft I entlang des Dokuments?

## Formal — CellGeometry

| Konzept | Bedeutung |
|---------|-----------|
| Zell-Grenzen | Token-Indizes pro Satz/Wort-Zelle |
| `perm_space` | Größe des Perm-Raums in der Zelle |
| `perm_index` | I-Wert pro Token innerhalb der Zelle |
| Hierarchie | Satz → Absatz → Linie → Seite (`DocumentHierarchy`) |

Materialisierung: `materialize_geometry(doc)` füllt `doc.cells` und `doc.hierarchy`.

## Ablauf

1. Dokument kompilieren (NL oder Hybrid)
2. `materialize_geometry` aufrufen
3. `cells[]` und optional `hierarchy` befüllen
4. I-Kurve extrahieren: `perm_index` / `perm_space` entlang der Zellen — [I-Kurve](/erklaerungen/20-i-curve)
5. Bei Export v9: `FLAG_BODY_CELL` / `FLAG_FRACTAL`

## Bezug zur I-Kurve

Die **I-Kurve** ist keine separate Datenstruktur, sondern eine **Projektion** der Zell- und Token-Metriken auf eine Zeitreihe:

```
Punkte_i = perm_index_i / perm_space_i   (vereinfacht)
```

Maximal 512 Punkte in der Workbench-Sparkline (Downsampling-Invariante).



## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [I-Kurve](/erklaerungen/20-i-curve)
- [Blocks](/erklaerungen/18-blocks)
- [Index I](/erklaerungen/02-index-i)
- [Wortpaar-Diff](/erklaerungen/10-wortpaar-diff)
