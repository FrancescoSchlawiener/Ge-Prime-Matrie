---
title: Korpus
---

# Korpus — Basis-Index und Dokument-Suche

Der **Korpus** ist ein invertierter Index über kompilierte Dokument-Signaturen. Er ermöglicht „ähnliche Dokumente finden“ ohne paarweisen Vollvergleich aller Dateien.

## Kernidee

Jedes Dokument erhält eine **Basis-Signatur** (Log-Profil, Jaccard-ähnliche Merkmale, Substanz-Postings). Der Index speichert, welche Dokumente welche Merkmale teilen — Kandidaten werden vorgefiltert, dann tiered verglichen.

## Formal

| Funktion | Beschreibung |
|----------|--------------|
| `build_basis_signature` | Signatur aus Dokument |
| `build_basis_index` | Invertierter Index |
| `extend_basis_index` | Inkrementell erweitern |
| `query_candidates` | Postings + MinHash-Vorfilter |
| `find_similar_documents` | Zwei-Stufen-Korpus-Suche |

## Ablauf — Index aufbauen

1. Dokumente kompilieren
2. Pro Dokument Signatur berechnen
3. Postings in SQLite/Index schreiben
4. Optional: Roman-Alpha-Korpus (Wörter-Tabelle) für Anagramm-Suche

## Ablauf — Ähnlichkeitssuche

1. Query-Dokument signieren
2. `query_candidates` → kurze Kandidatenliste
3. `compare_documents_tiered` Tier 0–4 auf Kandidaten
4. Rangliste zurückgeben



## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Redundanz](/erklaerungen/22-redundanz)
- [ggT / kgV](/erklaerungen/09-ggt-kgv)
- [Wortpaar-Anagramm](/erklaerungen/11-wortpaar-anagramm)
