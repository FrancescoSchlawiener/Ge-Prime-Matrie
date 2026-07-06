---
title: N(I) — Ganzzahl-Identität
---

# N(I) — Ganzzahl-Identität

**N(I)** kodiert **numerische Literale** als eigener Pointer-Typ — getrennt von Wörtern im S(I)-Sinne. Im Code-Modus erkennt der Lexer Ziffernfolgen und erzeugt `PointerKind.N`.

## Kernidee

Eine Ganzzahl ist nicht sinnvoll „Buchstabe für Buchstabe“ als S(I) gespeichert. Stattdessen gilt:

- **Kanonische Form** — führende Nullen werden zusammengeführt (`0042` → `42`)
- **Pointer-ID** — stabiler Schlüssel in der N-Registry des Dokuments
- **Roundtrip** — Decode liefert immer den kanonischen Ziffernstring, nie die Roheingabe

Damit bleibt `42` und `0042` im gespeicherten Modell **dieselbe Identität**.

## Formal

| Schritt | Funktion | Ergebnis |
|---------|----------|----------|
| Normalisieren | `canonical_n(raw)` | Ziffernstring ohne führende Nullen |
| Als int | `canonical_n_int(raw)` | Python-int nach Normalisierung |
| Kodieren | `encode_ni(raw)` | `(pointer_id, canonical)` |
| Dekodieren | `decode_ni(ptr_id, registry)` | kanonischer Ziffernstring |

Die Substanz-Logik für N arbeitet auf dem **kanonischen** String, nicht auf der Roheingabe.

## Ablauf (Encode)

1. Rohtext `0042` einlesen (z. B. aus Code-Literal)
2. `canonical_n` → `42`
3. Registry-Eintrag mit kanonischem Wert anlegen
4. Token/Pointer verweist auf `pointer_id`

## Ablauf (Decode)

1. `pointer_id` aus Token oder Block-Sequenz lesen
2. Registry-Eintrag nachschlagen
3. Kanonischen Ziffernstring zurückgeben (`42`, nicht `0042`)

## Code-Modus vs. NL-Modus

| Kontext | Beispiel | Identitätstyp |
|---------|----------|---------------|
| NL-Fließtext | `Hallo` | S(I) pro Wort |
| Code-Literal | `42`, `0`, `12345` | N(I) |
| Gemischt | `abc123` | H(I) — siehe [H(I)](/erklaerungen/06-hi-hybrid-identitaet) |

Der Code-Lexer erzeugt für numerische Literale automatisch `PointerKind.N`. NL-Tokenisierung behandelt Ziffernfolgen **nicht** als N(I), solange sie Teil eines Wortes sind.


## Beispiele

| Eingabe | Kanonisch | Hinweis |
|---------|-----------|---------|
| `0042` | `42` | führende Nullen entfernt |
| `42` | `42` | bereits kanonisch |
| `000` | `0` | nur Nullen → eine Null |
| `-7` | (Parser-abhängig) | Vorzeichen je nach Lexer-Regel |

## Abgrenzung zu S(I) und D(I)

| | S(I) | N(I) | D(I) |
|---|------|------|------|
| Inhalt | Buchstaben-Wörter | Ganzzahlen | Dezimalbrüche |
| Kommutativität | S ja, I nein | kanonisch eindeutig | Bruch gekürzt |
| Typischer Ort | NL-Token | Code-Ganzzahl | Code-Dezimal |

## Abgrenzung zu H(I)

Reine Ganzzahl `42` → **N(I)**. Gemischte Kette `abc42` → **H(I)** mit Segmenten S + N. H(I) erfordert mindestens zwei Segmente mit verschiedenen Tags.

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [H(I) — Hybrid](/erklaerungen/06-hi-hybrid-identitaet)
- [D(I) — Dezimal](/erklaerungen/05-di-dezimal)
- [Payload-Kinds](/erklaerungen/17-payload-kinds)
- [Code-Blöcke](/erklaerungen/24-code-blocks)
- [Registry](/erklaerungen/15-registry)
