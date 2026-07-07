---
title: Hybrid-Fences
---

# Hybrid-Fences — Invariante A

Hybrid-Dokumente mischen **NL-Prosa** und **Code-Fences** (Markdown `` ``` ``). **Invariante A** garantiert: Fence-Inhalt liegt nie in der NL-Registry oder in NL-Gaps.

## Kernidee

Ohne diese Regel würde Code doppelt gespeichert — einmal als Fence-Block, einmal als „Wörter“ im NL-Header. Invariante A trennt die Domänen sauber.

## Formal — Invariante A

| Erlaubt | Verboten |
|---------|----------|
| Fence in `fence_boundaries` | Fence-Text in `header` / NL-`gaps` |
| Code in `root_block` / Code-Registry | Code-Literale in NL-Token-Stream |
| NL-Segmente mit S(I)-Tokens | Fence-Zeilen als NL-Wörter |

## Ablauf — Hybrid-Kompilierung

1. Quelltext in Segmente scannen (NL vs. Fence)
2. NL-Segment → `compile_text` → eigenes Mini-Dokument
3. Fence-Segment → `compile_source` → `BlockNode` (CODE_BLOCK)
4. `fence_open` / `fence_close` in `HybridSegment` speichern
5. Gemeinsame `DocumentRegistry` für Code-Literale

## Ablauf — Rekonstruktion

1. Segmente in Quell-Reihenfolge
2. NL: `reconstruct_text(nl_document)`
3. Code: `reconstruct_source(code_module)` mit Fence-Markern
4. `source_trailing` anhängen



## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Gaps & Dokument](/erklaerungen/12-gaps-dokument)
- [Code-Blöcke](/erklaerungen/24-code-blocks)
- [Blocks](/erklaerungen/18-blocks)
- [H(I)](/erklaerungen/06-hi-hybrid-identitaet)
