---
title: H(I) — Hybrid-Identität
---

# H(I) — Hybrid-Identität

**H(I)** beschreibt **gemischte Zeichenketten**, in denen Buchstaben- und Ziffernläufe **in Lesereihenfolge** alternieren — ohne die Segmente nach Typ zu sortieren.

## Kernidee

Manche Werte sind weder reines Wort (S(I)) noch reine Zahl (N(I)):

```
abc123def  →  [S:abc] [N:123] [S:def]
```

H(I) parst links-nach-rechts und typisiert jeden **Run** — einen maximalen zusammenhängenden Block gleicher Zeichenklasse (Buchstaben vs. Ziffern).

## Formal

```
parse_hi_segments(raw) → HiPayload mit Segmenten (tag, value)
```

| Tag | Bedeutung | Normalisierung |
|-----|-----------|----------------|
| **S** | Buchstabenlauf | Latin-Profil, wie S(I)-Substrat |
| **N** | Ziffernlauf | `canonical_n` |

**Invariante:** Mindestens **zwei** Segmente und **mindestens zwei verschiedene Tags** — sonst kein echter H(I)-Wert (reines S oder reines N).

## Ablauf (Parse)

1. Eingabe von links nach rechts scannen
2. Ziffern → N-Segment (kanonisch, führende Nullen entfernt)
3. Buchstaben → S-Segment (normalisiert)
4. Sonderzeichen ohne gültigen Run → Fehler
5. `HiPayload` für Registry / Code-Pointer erzeugen

## Ablauf (Roundtrip)

1. Segmente in **Originalreihenfolge** aus Registry lesen
2. S-Segmente und N-Segmente konkatenieren
3. Ergebnis = exakte Hybrid-Zeichenkette

Die Reihenfolge der Segmente **ist** die Identität — im Gegensatz zu S(I), wo die Buchstabenmenge kommutativ ist.

## Hybrid-Dokumente

Im **Hybrid-Modus** des Editors:

- NL-Fließtext → S(I)-Token pro Wort
- Code-Fences → eigene Block-Struktur (`root_block`)
- Einzelne **gemischte Literale** innerhalb von Code → H(I)

**Invariante A:** Fences erscheinen nie in der NL-Registry — siehe [Hybrid-Fences](/erklaerungen/23-hybrid-fences).


## Beispiele

| Eingabe | Segmente | Gültig als H(I)? |
|---------|----------|------------------|
| `abc123def` | S, N, S | ja |
| `42` | nur N | nein → N(I) |
| `hello` | nur S | nein → S(I) |
| `a1b2` | S, N, S, N | ja |
| `x00y` | S, N, S | ja (`00` → `0`) |

## Vergleich der Identitätstypen

| Typ | Beispiel | Reihenfolge wichtig? |
|-----|----------|----------------------|
| S(I) | `listen` | ja (über I) |
| N(I) | `42` | nein (kanonisch) |
| D(I) | `3.14` | nein (Relation) |
| H(I) | `abc123` | ja (Segment-Reihenfolge) |

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [N(I)](/erklaerungen/04-ni-ganzzahl)
- [D(I)](/erklaerungen/05-di-dezimal)
- [Substanz S](/erklaerungen/01-substanz-s) — S-Anteile in Segmenten
- [Payload-Kinds](/erklaerungen/17-payload-kinds)
- [Hybrid-Fences](/erklaerungen/23-hybrid-fences)
- [Einstieg](/erklaerungen/00-einstieg) — Übersicht aller Typen
