---
title: Gaps & Dokument
---

# Gaps, Token und die n+1-Invariante

Ein **GpmDocument** besteht aus Header (Wörterbuch), Token-Stream (Body) und **Gaps** — den Textfragmenten **zwischen** den Tokens inklusive Anfang und Ende.

## Kernidee

GPM speichert nicht den Volltext als eine Zeichenkette. Stattdessen:

```
Volltext = gap[0] + token[0] + gap[1] + token[1] + … + gap[n]
```

Die Gaps halten Leerzeichen, Satzzeichen und Formatierung, die nicht zum Wort-Token gehören.

## Formal — Invariante

```
len(gaps) == len(tokens) + 1
```

Verletzung → `assert_gap_symmetry` wirft. Rekonstruktion (`reconstruct_text`) verlässt sich auf diese Symmetrie.

## Formal — Dokumentfelder

| Feld | Bedeutung |
|------|-----------|
| `header` | Registry-Einträge (Wörter mit S, normalized) |
| `tokens[]` | word_id + perm_index + case_code |
| `gaps[]` | UTF-8-Strings zwischen Tokens |
| `explicit[]` | Case-Overrides — [Case & Explicit](/erklaerungen/14-case-explicit) |
| `registry` | Code-Literale (Hybrid/Code) — [Registry](/erklaerungen/15-registry) |

## Ablauf — Kompilieren

1. Rohtext tokenisieren
2. Header-Einträge für neue Wörter
3. Tokens mit perm_index anlegen
4. Gaps aus Zwischen-Text extrahieren
5. Invariante prüfen

## Ablauf — Rekonstruieren

1. Für i in 0…n: `gaps[i]` + dekodiertes Token i
2. `gaps[n]` anhängen
3. Ergebnis mit Original vergleichen (Roundtrip)

## Modi im Editor

| Modus | Kompilierung | Registry |
|-------|--------------|----------|
| NL | `compile_text` | Header-Einträge |
| Code | `compile_source` | `DocumentRegistry` |
| Hybrid | `compile_hybrid` | Registry ohne Fence-Inhalt |
| GPM | `read_gpm` / `write_gpm` | Binärserialisierung |

## Invariante A (Hybrid)

Code-Fences (`` ``` ``) erscheinen ausschließlich in `fence_boundaries`, **nie** in `registry_entries` oder NL-Gaps. Das Live-Panel zeigt Fences separat — [Hybrid-Fences](/erklaerungen/23-hybrid-fences).

## Workbench-Flow

1. Text eingeben → **Kompilieren**
2. Tabs **Gaps / Registry / Tokens / Steps** prüfen
3. **Rekonstruieren** → Roundtrip-Badge
4. **In Vergleichen öffnen** — eingefrorene Kopie via Session


## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Tokens](/erklaerungen/16-tokens)
- [Registry](/erklaerungen/15-registry)
- [GPM Binary](/erklaerungen/13-gpm-binary)
- [Hybrid-Fences](/erklaerungen/23-hybrid-fences)
