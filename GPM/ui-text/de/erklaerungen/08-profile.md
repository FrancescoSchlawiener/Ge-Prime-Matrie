---
title: Profile
---

# Alphabet-Profile

GPM unterstützt **33 Schriftsätze** als `AlphabetProfile` (`alphabets.profiles.AlphabetProfile`):

- `og` — Original-German (Standard)
- `latin_extended`, `cyrillic`, …
- `aesthetic_hieroglyphs` — experimentelle Ästhetik

Jedes Profil definiert:

- Zeichen → Primzahl-Zuordnung
- Normalisierungsregeln
- Erlaubte Token-Zeichen

## API

`GET /api/profiles` liefert `{ id, label }` für den Workbench-**ProfilePicker**.

## Auswirkungen

| Bereich | Profil wirkt auf |
|---------|------------------|
| Encode/Decode | Primzuordnung, Normalisierung |
| Dokument | `GpmDocument.profile` |
| Korpus-Index | Partitionierung nach Profil (`analysis.basis.index`) |

Wechsle das Profil im Editor und kompiliere dasselbe Wort — Substanz und Index ändern sich entsprechend der Zuordnung.
