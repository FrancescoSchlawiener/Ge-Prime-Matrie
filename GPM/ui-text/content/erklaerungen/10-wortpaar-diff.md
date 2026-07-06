---
title: Wortpaar-Diff
---

# Wortpaar-Differenz und Klassifikation

`analyze_word_pair` klassifiziert ein Wortpaar (A, B) anhand von Substanz, Index und kanonischem Text — ohne bloßen String-Vergleich.

## Kernidee

Zwei Wörter können gleich aussehen, Anagramm sein, Teilmenge oder völlig disjoint sein. GPM liefert eine **algebraische Klassifikation** plus Metriken (ggT, kgV, I-Differenz).

## Formal — Klassen

| Klasse | Bedingung (vereinfacht) |
|--------|------------------------|
| **identisch** | gleicher kanonischer Text (gleiches S und I) |
| **anagramm** | gleiches S, verschiedenes I |
| **teilmenge** | Substanz-Teilmenge (ein ggT deckt kleineres S) |
| **disjoint** | kein gemeinsamer Primteiler (ggT = 1) |
| **overlap** | gemeinsame Teiler, aber weder Teilmenge noch Anagramm |

## Ablauf

1. Wörter A, B mit Profil normalisieren
2. S₁, S₂, I₁, I₂ berechnen
3. `classify_word_pair` → Klasse
4. `compare_substances` → ggT, kgV, Ratio
5. Optional: Erklärungs-Links für Workbench-UI

## API

`POST /api/compare/word-pair` mit `mode: "diff"`:

```json
{
  "word_a": "LISTEN",
  "word_b": "SILENT",
  "profile": "og"
}
```

Antwort: `classification`, Substanz-Felder, `explain_links` zu Erklärungs-Kapiteln.


## Beispiele

| A | B | Klasse |
|---|---|--------|
| LISTEN | SILENT | anagramm |
| LISTEN | LISTEN | identisch |
| CAT | CATS | teilmenge (typisch) |
| ABC | XYZ | disjoint |

## Bezug zu S(I)

- **Anagramm** = Perm-Invariante: gleiches S, verschiedenes I
- **Identisch** = gleiches S **und** gleiches I
- Nur S vergleichen reicht für Anagramm-Erkennung; I für Eindeutigkeit

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [ggT / kgV](/erklaerungen/09-ggt-kgv)
- [Substanz S](/erklaerungen/01-substanz-s)
- [Index I](/erklaerungen/02-index-i)
- [Wortpaar-Anagramm](/erklaerungen/11-wortpaar-anagramm)
