---
title: Inference-Trace
---

# Inference-Trace — Schritt-Protokoll für Encode/Decode

Der **Inference-Trace** protokolliert jeden Zwischenschritt von Encode und Decode — für **Pedagogik** und Debugging, ohne doppelte Encodes in der Pipeline.

## Kernidee

Wenn ein Nutzer fragt „wie kam diese Substanz zustande?“, liefert der Trace die Kette: Normalisierung → Multimenge → Primprodukt → perm_index → Ergebnis. Gleiches für Decode rückwärts.

## Formal

`InferenceTrace` sammelt strukturierte Schritte:

| Schritt-Typ | Beispiel-Inhalt |
|-------------|-----------------|
| `normalize` | raw → prepared substrate |
| `substance` | Zeichen → Primfaktoren |
| `perm_index` | Rang-Berechnung |
| `decode_ingredients` | S → Multimenge |
| `perm_decode` | I → Zeichenfolge |

**Invariante:** Pedagogik-API encodiert **einmal** — der Trace liest Zwischenwerte, ruft nicht erneut `encode_si` auf (Test: `test_pedagogy_no_double_encode`).

## Ablauf — Encode-Trace

1. Rohtext + Profil
2. `prepare_substrate` → Trace-Eintrag
3. `substance_for_profile` → Trace
4. `perm_index` → Trace
5. Finales (S, I)

## Ablauf — Decode-Trace

1. (S, I) + Profil
2. `ingredients_for_profile` → Multimenge
3. `perm_decode` → Zeichenfolge
4. Case-Anwendung


## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Substanz S](/erklaerungen/01-substanz-s)
- [Index I](/erklaerungen/02-index-i)
- [Decode](/erklaerungen/03-decode)
