---
title: Tokens
---

# Tokens — word_id und perm_index

Der **Body** eines GPM-Dokuments ist eine geordnete Liste von **Tokens**. Jedes Token ist eine Referenz auf einen Header-Eintrag plus den positionsabhängigen Permutations-Index I.

## Kernidee

Das Dokument speichert nicht den Volltext als eine Zeichenkette, sondern als **Abfolge von Wort-Identitäten** mit Gaps dazwischen. Ein Token = „dieses Wort, in dieser Anordnung, mit dieser Schreibweise“.

## Formal — GpmToken

| Feld | Bedeutung |
|------|-----------|
| `word_id` | Index in `header[word_id]` |
| `perm_index` | I im Perm-Raum von `header[word_id].word_normalized` |
| `case_code` | Groß/Klein-Kodierung |
| `payload_kind` | Standard `S` für NL-Wörter; `N`, `D`, `H` in Code-Kontext |

Rekonstruktion eines Tokens:

```
text = gaps[i] + decode(header[word_id].substance, perm_index) + case/explicit
```

## Ablauf — Body aufbauen

1. Quelltext tokenisieren (Wörter + Interpunktion je nach Modus)
2. Pro Token: `word_id` aus Header (oder neu anlegen)
3. `perm_index` = Rang der Zeichenfolge im Perm-Raum
4. `case_code` aus Original vs. Normalform
5. Token an `tokens[]` anhängen

## Ablauf — Body lesen

1. Für jedes Token: Header nachschlagen
2. `perm_decode(counts, perm_index)` → normalisierte Zeichen
3. Case/Explicit anwenden
4. Mit `gaps[0]…gaps[n]` verketten

## Binärformat

Im .gpm-Body (v4/v8/v9):

- `word_id` (uint16)
- `case_code` (uint8)
- `perm_index` (variable Breite je nach Wortlänge)

Die Perm-Breite hängt von `perm_space_size(word_normalized)` ab.



## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Registry](/erklaerungen/15-registry)
- [Index I](/erklaerungen/02-index-i)
- [Gaps & Dokument](/erklaerungen/12-gaps-dokument)
- [GPM Binary](/erklaerungen/13-gpm-binary)
