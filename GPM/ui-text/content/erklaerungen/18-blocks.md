---
title: Blocks
---

# Blocks — root_block und AST

Strukturierte Dokumente (Code, Hybrid, fraktale NL-Geometrie) nutzen einen **Block-Baum** (`root_block`): Module, Absätze, Sätze, Code-Fences und Zellen als verschachtelte Knoten.

## Kernidee

Statt nur einer flachen Token-Liste modelliert GPM **Hierarchie**: Wo beginnt ein Absatz? Wo ein Code-Fence? Welche Pointer-Sequenz gehört zu welchem Block? Der Baum ist die Antwort.

## Formal — BlockNode

| Feld | Bedeutung |
|------|-----------|
| `block_id` | Eindeutige ID im Dokument |
| `level` | `MODULE`, `CODE_BLOCK`, `PARAGRAPH`, `SENTENCE`, `CELL`, … |
| `sequence` | Geordnete `PointerRef`-Liste (Literale, Verweise) |
| `children` | Verschachtelte Unterblöcke |
| `meta` | z. B. `visual_style`, `trailing_whitespace` |

### PointerRef (in sequence)

| Feld | Bedeutung |
|------|-----------|
| `kind` | S, N, D, H, C, … |
| `ptr_id` | Index in DocumentRegistry |
| `nl`, `col_prefix` | Formatierung vor Literal (Code) |
| `meta` | `open_syntax`, `close_syntax` |

## Ablauf — NL-Fraktalbaum

1. `compile_text` → flaches Dokument
2. Optional `materialize_geometry` → Zellen/Sätze
3. `root_block` spiegelt Satz/Absatz-Struktur
4. In v9: `FLAG_BLOCK_TREE` + serialisierter Baum

## Ablauf — Code/Hybrid

1. `compile_source` oder `compile_hybrid`
2. Parser erzeugt `BlockNode`-AST pro Fence/Modul
3. `root_block` = oberstes Code-Modul oder Hybrid-Segment-Baum
4. Registry hält alle Literale


## Beispiel — Hybrid

```markdown
# Titel

```py
x = 1
```
```

- NL-Segment: Überschrift + Prosa → S(I)-Tokens
- CODE-Segment: ein `CODE_BLOCK` mit N-Literal `1`
- `root_block.children`: NL- und Code-Submodule

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Code-Blöcke](/erklaerungen/24-code-blocks)
- [Hybrid-Fences](/erklaerungen/23-hybrid-fences)
- [Cells](/erklaerungen/19-cells)
- [Payload-Kinds](/erklaerungen/17-payload-kinds)
