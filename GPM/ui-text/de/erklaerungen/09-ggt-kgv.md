---
title: ggT / kgV
---

# ggT und kgV auf Substanzen

Für zwei Wörter mit Substanzen S₁ und S₂ berechnet GPM den **größten gemeinsamen Teiler** und das **kleinste gemeinsame Vielfache** auf der Primfaktor-Ebene — nicht auf Rohtext.

## Kernidee

Substanz S ist ein Primzahlprodukt. Gemeinsame Buchstaben = gemeinsame Primfaktoren. Der ggT misst die **Überlappung**; das kgV die **vereinigte Buchstabenmenge** (mit Multiplizitäten).

## Formal

```
ggT(S₁, S₂) = ∏ pᵢ^min(aᵢ, bᵢ)
kgV(S₁, S₂) = ∏ pᵢ^max(aᵢ, bᵢ)
```

wobei S₁ = ∏ pᵢ^aᵢ und S₂ = ∏ pᵢ^bᵢ in der Primfaktorzerlegung.

| Maß | Interpretation |
|-----|----------------|
| Hoher ggT-Anteil | Viele gemeinsame Buchstaben-Multiplizitäten |
| kgV >> ggT | Unterschiedliche oder asymmetrische Buchstabenmengen |
| ggT = S₁ = S₂ | Identische Multimenge (Anagramm-Kandidaten) |

## Ablauf — Wortpaar

1. Beide Wörter normalisieren und S berechnen
2. `compare_substances(S₁, S₂)` → ggT, kgV, Ratio
3. Klassifikation ableiten — [Wortpaar-Diff](/erklaerungen/10-wortpaar-diff)

## Ablauf — Dokument (Tiered)

1. Zwei Dokumente kompilieren
2. Substanz-Ketten extrahieren
3. `compare_documents_tiered` Tier 0–4
4. Frühe Tiers: Signatur/Jaccard; tiefe Tiers: mehr Token-Detail


## Beispiel LISTEN / SILENT

| Wort | S | ggT mit LISTEN |
|------|---|----------------|
| LISTEN | S* | S* |
| SILENT | **S*** (gleich) | S* |

→ Klassifikation **anagramm**; I-Werte unterscheiden sich.

LISTEN / LISTEN: ggT = kgV = S; Klassifikation **identisch**.

## Bezug zur I-Kurve

ggT/kgV arbeiten auf **S-Achse**; I-Kurven auf **Index-Achse**. Anagramm-Dokumente: parallele S-Kette, divergierende I-Spur — [I-Kurve](/erklaerungen/20-i-curve).

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Substanz S](/erklaerungen/01-substanz-s)
- [Wortpaar-Diff](/erklaerungen/10-wortpaar-diff)
- [Wortpaar-Anagramm](/erklaerungen/11-wortpaar-anagramm)
- [Korpus](/erklaerungen/21-corpus)
