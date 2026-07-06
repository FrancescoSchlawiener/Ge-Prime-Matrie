---
title: Decode
---

# Decode — von S(I) zurück zum Text

**Decode** ist die Umkehrung von Encode: Aus Substanz S und Index I wird der **kanonisch normalisierte** Text rekonstruiert.

## Formal

```
decode(S, I, profile) → Text
```

Voraussetzung: `(S, I)` muss zu einer gültigen Multimenge im gewählten Profil passen.

## Ablauf (konzeptionell)

1. **S zerlegen** — Primexponenten → Multimenge (welche Buchstaben, wie oft)
2. **I entpacken** — Permutations-Rang im Raum N_perm
3. **perm_decode** — Zeichenfolge in Lex-Ordnung des Profils
4. **Ausgabe** — normalisierter Text (Großbuchstaben bei OG)

## Fehlerfälle

| Situation | Folge |
|-----------|-------|
| S passt nicht zum Profil | Decode schlägt fehl |
| I ≥ N_perm | ungültiger Rang |
| I inkonsistent zu S | Rekonstruktion unmöglich |

Im Workbench erscheint eine klare Fehlermeldung über die Calc-API.

## Roundtrip

```
Text → encode → (S, I) → decode → Text'
```

Bei korrekter Pipeline gilt `Text' = normalize(Text)`. Im **GPM-Editor** zeigt die Rekonstruktion, ob Quelltext und Ergebnis übereinstimmen.


## Pädagogik (Säule 4)

Jede Decode-Antwort listet Rechenschritte: Substanz-Zerlegung, Multimenge, Permutationsdekodierung. So siehst du **warum** ein bestimmtes Wort herauskommt — nicht nur das Ergebnis.


## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Substanz S](/erklaerungen/01-substanz-s)
- [Index I](/erklaerungen/02-index-i)
- [Normalisierung](/erklaerungen/07-normalisierung)
- [N(I)](/erklaerungen/04-ni-ganzzahl) — Decode für Zahlenliteral, nicht S(I)
