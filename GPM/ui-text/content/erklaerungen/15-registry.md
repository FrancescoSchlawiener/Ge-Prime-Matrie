---
title: Registry
---

# Registry — Header und DocumentRegistry

GPM nutzt **zwei Registry-Ebenen**: den **Header** für NL-Wörter (S(I)) und die **DocumentRegistry** für Code-Literale, Geometrie und weitere Pointer-Typen.

## Kernidee

Wörter und Literale werden **einmal** mit voller Identität gespeichert; der Body referenziert nur IDs. Das spart Platz und macht Vergleiche auf Registry-Ebene möglich.

## Formal — GpmHeaderEntry (NL)

| Feld | Bedeutung |
|------|-----------|
| `word_id` | Index in `header[]` |
| `word_canonical` | Original-Schreibweise |
| `word_normalized` | Normalisiert für Perm-Raum |
| `substance` | Primzahlprodukt S |
| `perm_index` | Header-eigener I (selten direkt genutzt) |

Der Body-Token trägt den **eigenen** `perm_index` pro Vorkommen — gleiches Wort, verschiedene Anordnungen → gleiche `word_id`, verschiedenes I.

## Formal — DocumentRegistry (Code/Geometrie)

| Tabelle | PointerKind | Inhalt |
|---------|-------------|--------|
| `s_entries` | S | Code-Identifier, Strings |
| `n_entries` | N | Ganzzahlen — [N(I)](/erklaerungen/04-ni-ganzzahl) |
| `d_entries` | D | Dezimalbrüche — [D(I)](/erklaerungen/05-di-dezimal) |
| `h_entries` | H | Hybrid-Segmente — [H(I)](/erklaerungen/06-hi-hybrid-identitaet) |
| `c_entries` | C | Geometrie-/Code-Keys (Registry-C in v9) |

C-Einträge unterscheiden **Origin**: `CODE` vs. `GEOM`.

## Ablauf — NL-Kompilierung

1. Wörter extrahieren
2. Pro neues Wort: S berechnen, Header-Eintrag anlegen
3. Pro Token-Vorkommen: `word_id` + `perm_index` + `case_code`

## Ablauf — Code-Kompilierung

1. Lexer/Parser → Literale und Identifier
2. `encode_ni`, `encode_di`, `parse_hi_segments` etc.
3. Einträge in `DocumentRegistry`
4. `BlockNode.sequence` mit `PointerRef` (kind + ptr_id)


## Beispiel LISTEN / SILENT

Beide Wörter → **ein** Header-Eintrag pro kanonischer Form, wenn normalisiert identisch; oder zwei Einträge mit **gleichem S**, verschiedenem I im Body.

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Tokens](/erklaerungen/16-tokens)
- [Payload-Kinds](/erklaerungen/17-payload-kinds)
- [Gaps & Dokument](/erklaerungen/12-gaps-dokument)
- [Blocks](/erklaerungen/18-blocks)
