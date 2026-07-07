# Fraktaler Code-Vertrag (C(I) / CHILD mit Regeln)

GPM/functions ist die **einzige Logikquelle** für Kanonisierung. Die Workbench-UI dekodiert nur Wire und zeigt an.

## Registry (Write-once Header)

- Substanzwerte (S, N, D, C, H) werden **einmal** in `DocumentRegistry` interniert.
- Blöcke und Sequenzen speichern nur `PointerRef` (Kind + ptr_id + nl/col_prefix + meta).
- Keine Inline-Strings in `BlockNode.sequence`.

## Typisierte Block-Umschließer (kein String-Vergleich)

| Enum | Modul | Rolle |
|------|-------|-------|
| `BlockEnvelope` | `analysis/code/envelope.py` | BRACE, BRACKET, TAG, KEYWORD, INDENT |
| `CloseRole` | `analysis/code/envelope.py` | Schließ-Event für Stack-Matching |
| `BlockRuleContext` | `analysis/code/rules.py` | Sprachregeln aus `languages.py` |

Close-Matching: `rules.closes_matching_block(node, token)` — **kein** `visual_style == "tag"`, **kein** `len(stack)==2`.

Jeder `BlockNode` trägt:
- `rule_language` — unveränderlicher Parser-Kontext (Datei oder `embedded_language`)
- `envelope` — typisierter Umschließer
- `open_syntax` — Eröffner auf dem Knoten (nicht nur auf C-PointerRef)

## Fraktale Blöcke

```
Module (Datei)
  sequence: [ SYS→CHILD, … ]
  children: [ BlockNode, … ]

BlockNode (Teilraum)
  meta: envelope, rule_language, open_syntax, embedded_language?, prefix_nl/col
  sequence: [ C|S|N|D|H PointerRefs, SYS→CHILD, SYS close ]
  children: [ verschachtelte BlockNodes ]
```

## Ziffer-N(I) — fraktal mit eigenem Pointer

- Atomare Ziffern `0`–`9` in `n_entries` als `int` (werden wiederverwendet → max. 10 Atome)
- Mehrstellige Literale (`11`, `112`) als **eigener** `PointerRef` in der Sequenz
- Registry-Wert: `NComposite` (`literal`, `digit_ptrs`, `substance`, `checksum`)
  - `digit_ptrs`: Ziffer-ptr_ids als fraktale Innenstruktur (z. B. `11` → `(ptr_1, ptr_1)`)
  - `substance` = `substance_n(literal)` (Primprodukt über Ziffern) — dokumentübergreifende Äquivalenz
  - `checksum` = `checksum_n(literal)`; `pointer_id` = `N_<checksum>` (native `gpm_types/ni`-Adresse)
  - `literal` bleibt **roh** (führende Nullen) für verlustfreien Roundtrip
- Komposite wachsen linear mit eindeutigen Zahlenräumen; Dedup über `digit_ptrs`-Struktur
- `registry.n_display(ptr_id)` liefert das Literal; `n_substance`/`n_checksum` die Identität
- `intern.intern_n_digits` liefert **einen** Ref
- Kein `lstrip` / `canonical_n` auf dem gespeicherten Literal (Roundtrip `11` ≠ `1 1` über nl/col-Gap); `substance_n`/`checksum_n` nutzen intern `canonical_n` nur für die Identität
- `42n`: `meta.bigint` am N-Ref

## D(I) — DRelation-Dedup (pointer-first)

- `intern.intern_d_decimal` → `parse_decimal`; `DCodeEntry` in Registry
- `whole_ptr`, `den_reduced_ptr`, `ggt_ptr`, `frac_red_ptr` verweisen auf fraktale N(I)-Pointer
- **Dedup über Pointer-Triple** `(whole_ptr, den_reduced_ptr, ggt_ptr)` (`_d_by_triple`), nicht über String-`==`; `relation_key` bleibt nur sekundärer Index (Anzeige/Wire)
- `registry.d_relation(ptr_id)` rekonstruiert die `DRelation` aus den N-Pointern
- `registry.d_display(ptr_id)` rekonstruiert die Ziffern aus den N-Pointern (pointer-first) und erhält nur das originale Dezimaltrennzeichen (`.` vs `,`) aus dem Display
- Gleichwertige Dezimalen teilen ptr_id (nicht String-`==`)

## H(I) — fraktal im Code-Pfad

- `parse_hi_segments_code`: N-Runs als Ganzes (`abc123` → S + N123)
- `HiSegment.ptr_id` verweist auf S- bzw. N-Registry-Eintrag
- `registry.intern_h_code` interniert N-Segmente über `intern_n_literal`

## Sprachtrennung vs. crossLanguageAnalysis

- **C-Blöcke:** pro CHILD eigene `rule_language` (HTML ≠ JS in `<script>`)
- **S/N/D/H:** sprachübergreifend in einer Registry — Vergleich nur wenn Workspace `crossLanguageAnalysis` aktiv

## CHILD mit Sprachregeln (pro Datei)

| Kontext | Regel (block_style) | Beispiel |
|---------|---------------------|----------|
| Datei-Root | `html` → tag | `<div>`, `<script>` |
| `<script>` CHILD | `js` → brace | `function`, `{`, Ziffer-N |
| `<style>` CHILD | `css` → brace | `.class`, `{`, Farben als S-Chunk |

Eingebettete Re-Lex: `tokenize_html` → `_merge_rawtext_body` innerhalb des Tag-CHILD.

Eingebetteter Close: `}` in `<script>` schließt **nicht** das HTML-Tag (`absorb_close_into_embedded_tag`).

## language_manifest

Filter-Gate: `manifest.all ⊆ activeLanguageIds` (Primary + Embedded).

## Wire v2 Block-Tree Meta

| Flag | Inhalt |
|------|--------|
| 1 | `envelope` u8 |
| 2 | `open_syntax` utf32 |
| 4 | prefix_nl/col |
| 8 | `rule_language` utf32 |
| 16 | `embedded_language` utf32 |

Code-Wire Version 3 (Registry D mit relation_key).

## CSS-Hex-Guard

`#RRGGBB` bleibt ein S-Token — kein isolierter Hex-String in der Registry.

## Abgrenzung NL

NL-Zell-C(I) (`COrigin.GEOM`) ≠ Code-C(I) (`COrigin.CODE`).

## Toy v35

UI-Referenz — **keine** Spezifikation für eingebettete Re-Lex.
