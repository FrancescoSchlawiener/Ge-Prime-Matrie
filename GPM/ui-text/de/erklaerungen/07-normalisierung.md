---
title: Normalisierung
---

# Normalisierung vor der Kodierung

Bevor **S** und **I** berechnet werden, durchläuft jeder Rohtext eine **profilabhängige Normalisierung**. Ohne diesen Schritt wären Roundtrips instabil und Vergleiche zwischen Eingaben undefiniert.

## Kernidee

Zwei Nutzer können dasselbe Wort unterschiedlich tippen (`straße`, `STRASSE`, `Strasse`). Die Normalisierung mappt auf **eine** kanonische Form pro Profil — erst dann wird kodiert.

## Schritte (typisch OG-Profil)

1. **Unicode NFC** — kanonische Zusammensetzung (z. B. é vs e+◌́)
2. **Groß-/Kleinschreibung** — OG: Großbuchstaben
3. **Sonderzeichen** — ß → SS, Umlaute → AE/OE/UE
4. **Whitelist** — nur Buchstaben des Profils zählen für S/I

## OG vs Roman

| Aspekt | OG (Original-German) | Roman-Alpha |
|--------|----------------------|-------------|
| Zeichensatz | erweitert DE | lateinisch |
| Anagramm-Korpus | allgemein | Roman-Alpha-DB |
| Primzuordnung | Profil `og` | Profil `roman` |

Wechsle das Profil im Editor — Substanz und Index ändern sich. Details: [Profile](/erklaerungen/08-profile).

## Hybrid & Code

In **Hybrid-Dokumenten** wird Fließtext normalisiert, **Code-Fences** (` ``` `) separat behandelt:

- Fences erscheinen **nicht** in der Registry (Invariante A)
- NL-Gaps enthalten keinen Fence-Inhalt

Siehe [Hybrid-Fences](/erklaerungen/23-hybrid-fences).


## Warum wichtig?

| Ohne Normalisierung | Mit Normalisierung |
|---------------------|-------------------|
| gleiches Wort, verschiedenes S | stabiles S |
| Decode-Ambiguität | eindeutiger Roundtrip |
| Profil-Mix beim Vergleich | Vergleich nur im selben Profil |

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [Einstieg](/erklaerungen/00-einstieg)
- [Substanz S](/erklaerungen/01-substanz-s)
- [Profile](/erklaerungen/08-profile)
