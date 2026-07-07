---
title: Wortpaar-Anagramm
---

# Anagramm-Suche im Roman-Alpha-Korpus

Die Anagramm-Suche nutzt die geklonte Datenbank `ge_prime_roman_alpha_alt`: Wörter mit **gleicher Substanz S**, aber **verschiedenem Index I**.

## Kernidee

Ein Anagramm teilt die Buchstabenmenge (gleiches S), nicht die Anordnung (verschiedenes I). Die Korpus-Suche findet alle registrierten Wörter mit gleichem S — ohne alle Paare brute-force zu vergleichen.

## Formal

Suchbedingung für Query-Wort mit (S_q, I_q):

```
words.substance = S_q  AND  words.perm_index ≠ I_q  AND  normalized ≠ query_normalized
```

## Ablauf

1. Suchwort normalisieren und kodieren → (S, I)
2. SQLite-Abfrage auf `words.substance`
3. Treffer filtern: kein identisches Wort, verschiedenes I
4. Limit (1–500) anwenden

## API

`POST /api/compare/anagram-search`:

```json
{
  "word": "LISTEN",
  "profile": "og",
  "limit": 50
}
```



## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Substanz S](/erklaerungen/01-substanz-s)
- [Index I](/erklaerungen/02-index-i)
- [ggT / kgV](/erklaerungen/09-ggt-kgv)
- [Korpus](/erklaerungen/21-corpus)
