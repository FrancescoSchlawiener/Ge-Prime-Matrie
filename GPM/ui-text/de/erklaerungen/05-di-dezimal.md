---
title: D(I) — Dezimal-Identität
---

# D(I) — Dezimal-Identität

**D(I)** speichert **Dezimalbrüche** als kanonische Relation — Ganzzahlanteil, gekürzter Nenner und ggT — statt als fragile Gleitkomma-Bits.

## Kernidee

Dezimalzahlen im Text (z. B. `3.14` oder `3,14` je nach Locale) werden in eine **exakte Bruchdarstellung** überführt. Der Roundtrip bleibt **bitgenau** im rationalen Sinne: kein `0.1 + 0.2`-Problem.

## Formal

| Funktion | Beschreibung |
|----------|--------------|
| `parse_decimal(raw)` | Rohtext → `DRelation` (Zähler/Nenner) |
| `encode_di(raw)` | → `(whole, den_reduced, ggt)` |
| `decode_di(whole, den, ggt)` | → Dezimal-Anzeigestring |
| `relation_key(raw)` | Kanonischer Registry-Schlüssel |

- **whole** — Ganzzahlanteil vor dem Dezimaltrennzeichen
- **den_reduced** — gekürzter Nenner der Nachkommastelle
- **ggt** — gemeinsamer Teiler für die volle Darstellung

## Ablauf (Encode)

1. String parsen (`3.14`, Nachkommastellen zählen)
2. Bruchrelation `DRelation` bilden (Zähler = whole × Nenner + Nachkomma)
3. Mit ggT kürzen
4. Triple `(whole, den_reduced, ggt)` in Registry speichern
5. Pointer `PointerKind.D` verweist auf Registry-ID

## Ablauf (Decode)

1. Triple aus Registry lesen
2. Relation rekonstruieren
3. Anzeigestring mit korrekter Nachkommastellenlänge erzeugen

## Warum nicht einfach float?

| Float (IEEE) | D(I) |
|--------------|------|
| Rundungsfehler bei jeder Operation | exakte Rationaldarstellung |
| `0.1` ist nicht exakt speicherbar | `0.1` als 1/10 exakt |
| schlecht für Vergleich/Registry | stabiler, deterministischer Schlüssel |
| verliert führende Nullen in Nachkomma | Nachkommalänge explizit |

Für **Sprach- und Code-Dokumente** ist deterministischer Roundtrip wichtiger als Hardware-Gleitkomma.

## Code-Modus

Dezimal-Literale in Code-Blöcken werden als **D(I)-Pointer** in der Registry geführt — analog zu N(I) für Ganzzahlen:

```python
pi = 3.14   # D(I)-Literal im Code-AST
count = 42  # N(I)-Literal
name = hi   # S(I)-Literal (Identifier)
```


## Beispiele

| Eingabe (konzeptionell) | Gespeichert | Decode |
|-------------------------|-------------|--------|
| `3.14` | whole=3, gekürzter Bruchteil | `3.14` |
| `2.0` | whole=2, Nenner 1 | `2.0` oder `2` (Anzeigeregel) |
| `0.5` | whole=0, 1/2 | `0.5` |

## Bezug zu ggT

D(I) nutzt denselben **ggT-Gedanken** wie die Substanz-Vergleiche bei S(I) — nur auf Bruchrelationen statt Primprodukten. Siehe [ggT / kgV](/erklaerungen/09-ggt-kgv).

## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [N(I) — Ganzzahl](/erklaerungen/04-ni-ganzzahl)
- [Payload-Kinds](/erklaerungen/17-payload-kinds)
- [Registry](/erklaerungen/15-registry)
- [Code-Blöcke](/erklaerungen/24-code-blocks)
