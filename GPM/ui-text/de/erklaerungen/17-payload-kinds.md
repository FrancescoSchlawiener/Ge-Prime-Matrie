---
title: Payload-Kinds
---

# Payload-Kinds — Zeiger-Typen S, N, D, H, C

Jeder Verweis in einem GPM-Dokument trägt einen **Payload-Kind**: er sagt, welche Registry-Tabelle und welcher Codec gilt.

## Kernidee

Nicht alles ist ein „Wort“ im S(I)-Sinne. Ganzzahlen, Dezimalbrüche, Hybrid-Ketten und Geometrie-Keys haben eigene Identitätstypen — einheitlich als Pointer mit `kind` + `ptr_id`.

## Formal — Übersicht

| Kind | Name | Codec / Modul | Typisches Vorkommen |
|------|------|---------------|---------------------|
| **S** | Substanz-Identität | `encode_si` / `decode_si` | NL-Wörter, Code-Strings |
| **N** | Ganzzahl | `encode_ni` / `decode_ni` | Code-Literale `42` |
| **D** | Dezimal | `encode_di` / `decode_di` | Code-Literale `3.14` |
| **H** | Hybrid | `parse_hi_segments` | `abc123` |
| **C** | Code/Geometrie | Registry-C | Block-Keys, Zell-Origin |

Zusätzlich existieren System-Pointer (`SYS`, …) für strukturelle Knoten.

## structural_only

Bei Redundanz-Analysen können Pointer als **structural_only** markiert werden — sie zählen zur Struktur, nicht zur inhaltlichen Substanz-Kette. Siehe [Redundanz](/erklaerungen/22-redundanz).

## Ablauf — PointerRef in Blöcken

1. Code- oder Geometrie-Block parst Literale
2. Passenden Kind wählen (Lexer-Regel)
3. Registry-Eintrag anlegen → `ptr_id`
4. `PointerRef(kind, ptr_id)` in `BlockNode.sequence`

## Ablauf — NL-Token

1. Standard: `payload_kind = S`
2. `word_id` verweist auf Header (S + normalized)
3. `perm_index` im Body-Token


## Beispiel (Code-Zeile)

```python
x = abc123 + 42
```

| Fragment | Kind |
|----------|------|
| `abc123` | H |
| `42` | N |
| `+` | C (Operator-Key) |

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Registry](/erklaerungen/15-registry)
- [Blocks](/erklaerungen/18-blocks)
- [Code-Blöcke](/erklaerungen/24-code-blocks)
- [Einstieg](/erklaerungen/00-einstieg)
