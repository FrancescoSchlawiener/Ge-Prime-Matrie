---
title: Index I
---

# Index I — Permutations-Rang

Während **Substanz S** die Buchstaben**menge** festhält, kodiert der **Index I** die **Reihenfolge** als Rang im Permutationsraum.

## Formal

```
I = rank(Sequenz | Multimenge)
N_perm = n! / ∏(cᵢ!)
```

`N_perm` ist die Anzahl gültiger Permutationen der Multimenge — **nicht** mit der Bitbreite von I verwechseln.

## Anagramm-Regel (Perm-Invariante)

Für zwei normalisierte Strings A, B mit gleicher Multimenge, aber unterschiedlicher Anordnung:

- `S(A) = S(B)`
- `I(A) ≠ I(B)`
- `decode(S(A), I(A)) = A`

## Warum ein Rang?

Ohne I wäre nur die Menge bekannt — `LISTEN` und `SILENT` wären identisch. I macht das Wort **eindeutig** bei gegebenem S.

## Ablauf

1. Multimenge aus S oder aus dem Wort
2. Lexikographische Ordnung im Profil
3. Lehmer-Code / Multiset-Rang → Ganzzahl I
4. Decode: `perm_decode` rekonstruiert die Zeichenfolge

## Sequenz-Identitäten (Sk, Sp, Lut)

Neben S(I) gibt es **positionsabhängige** Schlüssel — vor allem für Code und Analyse:

| Symbol | Bedeutung | Kommutativ? |
|--------|-----------|-------------|
| **Sk** | Rohes Zeichen-Tuple | nein |
| **Sk_lut** | Tuple via Permutations-LUT | nein |
| **Sp** | Positions-Substanz (Prim^Gewicht pro Stelle) | nein |
| **Lut** | Materialisierte Permutations-LUT | Hilfsstruktur |

`Sp(A) ≠ Sp(B)` bei Anagrammen — im Gegensatz zu S. Für reine Wort-Speicherung reicht **S(I)**.

## I-Kurven auf Dokumentebene

Für längere Texte: pro Token-Position ein I-Verhältnis (`perm_index / perm_space`). Im Tab **Vergleichen → I-Kurve** als Sparkline (max. 512 Punkte nach Downsampling).

Siehe [I-Kurve](/erklaerungen/20-i-curve).


## Beispiel LISTEN vs SILENT

| Wort | S | I |
|------|---|---|
| LISTEN | gleich | I₁ |
| SILENT | gleich | I₂, I₂ ≠ I₁ |

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Substanz S](/erklaerungen/01-substanz-s)
- [Decode](/erklaerungen/03-decode)
- [Tokens](/erklaerungen/16-tokens) — I pro Token-Position im Stream
