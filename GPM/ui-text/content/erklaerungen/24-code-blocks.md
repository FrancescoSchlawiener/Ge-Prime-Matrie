---
title: Code-Blöcke
---

# Code-Blöcke — compile_source und Decompile

**Code-Blöcke** sind die AST-Repräsentation von Quellcode in GPM: `compile_source` erzeugt `root_block` und DocumentRegistry; `reconstruct_source` führt den Roundtrip zurück.

## Kernidee

Code ist nicht „ein langer NL-String“. Der Lexer erkennt Identifier, Literale (N, D, H), Operatoren und Struktur — alles wird als **Pointer-Sequenz** in einem Block-Baum gespeichert.

## Formal

| Funktion | Richtung |
|----------|----------|
| `compile_source(text)` | Quelltext → `GpmDocument` + `root_block` |
| `reconstruct_source(doc)` | Dokument → Quelltext |
| `compile_hybrid(text)` | NL + Fences — [Hybrid-Fences](/erklaerungen/23-hybrid-fences) |

## Ablauf — Kompilieren

1. Tokenize (Code-Lexer)
2. Literale → N(I), D(I), H(I) in Registry
3. Identifier → S(I) oder C-Keys
4. AST als `BlockNode`-Hierarchie
5. `PointerRef`-Sequenzen pro Block

## Ablauf — Dekompilieren

1. `root_block` traversieren
2. Pro `PointerRef`: Registry nachschlagen, Textfragment emitieren
3. `nl` / `col_prefix` für Formatierung
4. `meta.open_syntax` / `close_syntax` für Klammern



## Typische Fehler

- Code als NL-Fließtext kompilieren — dann fehlt der Block-Baum.
- Fence-Inhalt in der NL-Registry suchen — Invariante A verbietet das.
- Hybrid ohne Steps-Panel prüfen — Segment-Grenzen bleiben unsichtbar.

## Verknüpfungen

- [Payload-Kinds](/erklaerungen/17-payload-kinds)
- [N(I)](/erklaerungen/04-ni-ganzzahl)
- [Blocks](/erklaerungen/18-blocks)
- [Hybrid-Fences](/erklaerungen/23-hybrid-fences)
