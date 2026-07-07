---
title: Tensorraum
---

# Tensorraum — Kanonisierung, Registry und Projektvergleich

Der **Tensorraum** ist ein browser-seitiges Werkzeug zur **Kanonisierung von Quellcode**, zur **Registry-Visualisierung** und zum **Vergleich von Resonanzmustern** zwischen mehreren Projekten. Er ergänzt den GPM-Tab der Workbench: Dort liegt der Fokus auf Dokumenten, Gaps und `.gpm`-Export — im Tensorraum liegt der Fokus auf **Codebasen**, **Pointer-Registries** und **Vergleichs-Workflows**.

## Tensorraum vs. GPM-Tab

| Aspekt | GPM-Tab | Tensorraum |
|--------|---------|------------|
| Eingabe | NL, Code, Hybrid als Dokument | Dateien, Ordner, interaktives Snippet |
| Ziel | GPM-Binary, Roundtrip eines Dokuments | Registry-Atlas, Resonanz, Multi-Projekt-Vergleich |
| Speicher | Session, Export `.gpm` | Browser-Ablage (Snapshots) + JSON-Import |
| Server | Kompilierung über API | Phase 6: **rein client-seitig** |

Der Tensorraum ist bewusst ein **Vergleichs- und Resonanz-Werkzeug**, kein Single-Project-Editor: In der Sidebar können mehrere **Live-Projekte** parallel existieren.

## Workspace — Code einlesen und kanonisieren

Im Tab **Workspace** wird Quellcode eingegeben oder per Drag&Drop geladen:

1. **Snippet** in die Textarea schreiben und **Kanonisieren & speichern** wählen
2. **Dateien** oder **Ordner** über die Sidebar laden (Sprache aus Dateiendung)
3. **Sprachfilter** in der Sidebar: nur aktive Sprachen werden verarbeitet
4. Optionen: **Sprachübergreifend vergleichen**, **Nur Struktur** (Pointer-Typen ohne konkrete Substanz-Inhalte)

Die Kanonisierung ruft intern `processCode` auf — dieselbe Pipeline wie beim Datei-Einlesen. Rohtext wird in eine **Sequenz von Pointer-Referenzen** übersetzt; Substanz-Werte landen in der **Root-Registry** (Header).

**Nicht gespeichert** in Snapshots: Pointer-IDs, Registry-Maps, Sequenz-IDs — diese werden beim Laden **deterministisch neu erzeugt** (OG-Invariante).

## Registry — S, N, D, C, H: Substanz statt Pointer-ID

Nach der Kanonisierung zeigt der Tab **Registry** die fünf Pointer-Klassen:

| Klasse | Bedeutung | Beispiele |
|--------|-----------|-----------|
| **C(I)** | Räume & Trenner | Teilräume, `{`, `}`, Operatoren |
| **S(I)** | Reine Identifier · Strings | `function`, `add` — keine Hybride |
| **N(I)** | Ganzzahlen | Literale `42`, kanonisch |
| **D(I)** | Dezimal-Relation | `3.14` als `(whole, den_reduced, ggt)` |
| **H(I)** | Hybrid | `abc123` → Segmente S + N |

Intern speichert die Registry jede Klasse als Map **Pointer-ID → Substanz**. In der Oberfläche steht die **Substanz** im Vordergrund; H(I) zeigt zusätzlich die **Segment-Zerlegung** (S- und N-Läufe).

Zwei Ansichten:

- **Registry** — Metriken und fünf Kategorie-Tabellen
- **Fraktal** — Baum der Module und Blöcke mit aufgelöster Sequenz-Vorschau

Details zu Pointer-Kinds: [Payload-Kinds](/erklaerungen/17-payload-kinds). Die Workbench-GPM-Registry: [Registry](/erklaerungen/15-registry).

## Resonanz — wiederkehrende Sequenzen

Der Tab **Resonanz** (intern Redundanz-Analyzer) sucht **wiederkehrende kanonische Ketten**:

- **Block-Ebene** — wiederholte Pointer-Sequenzen innerhalb von Blöcken
- **Satz-Ebene (S(I))** — satzübergreifende Muster mit gleitendem Fenster

**Fenster-Modi** (Sidebar):

| Modus | Verhalten |
|-------|---------|
| Fest | Ein Fenster (z. B. 12 Token), 50 % Überlappung |
| Adaptiv | Parallel [8, 12, 16, 20, 24, 28] Token |

Jeder Treffer zeigt Vorkommen, Kettenlänge und optional eine **I-Kurve** (Perm-Verlauf). Server-seitiger Redundanz-Job in der Workbench: [Redundanz](/erklaerungen/22-redundanz) — der Tensorraum führt den Scan **lokal** im Browser aus.

## Round-Trip — Rekonstruktion prüfen

Der Tab **Round-Trip** dekompiliert jede Datei zurück in Quelltext und vergleicht mit dem Original:

- **Original** vs. **Rekonstruiert** nebeneinander (mit Zeilennummern)
- Metriken: Zeilen, Token, Tiefe, Round-Trip-Status
- `verifyReversibility` prüft Byte-genauen oder strukturellen Abgleich

Damit lässt sich prüfen, ob die Kanonisierung **verlustfrei** für die gewählte Sprache ist.

## Ablage — Snapshots und Projektvergleich

Der Tab **Ablage** speichert **Snapshots** im Browser (`localStorage`):

**Gespeichert:** Rohcode (`rawCodeOriginal`), Dateiname, Einstellungen inkl. Resonanz-Fenster  
**Nicht gespeichert:** Registry, Pointer-IDs, Sequenz, normalisierter Code

### Vergleichs-Workflow

1. Projekt A kanonisieren → in Ablage **sichern**
2. Projekt B bearbeiten oder anderes Snippet laden → **sichern**
3. Snapshot B **als neues Projekt laden** → erscheint in der Sidebar (Badge „Ablage“)
4. Zwischen Projekt A und B wechseln → je Tab **Resonanz** scannen oder **Round-Trip** prüfen

**Laden überschreibt nie** das aktive Projekt — es wird immer ein **neues Live-Projekt** angelegt. JSON-Export/-Import dient als portabler Fallback, wenn die Browser-Ablage voll ist.

## Architektur — client-only (Phase 6)

In Phase 6 gibt es **keinen Tensorraum-API-Endpoint** und **keine OpenAPI-Erweiterung**:

- Kanonisierung, Registry, Resonanz, Decompiler und Ablage laufen vollständig in `web/src/lib/tensorraum/`
- Snapshots in `localStorage` — funktioniert auf Render ohne persistentes Server-Dateisystem
- **Große Repos** (Enterprise-Codebasen mit tausenden Dateien) sind für einen optionalen **Server-Job** vorgesehen (Worker + Objektspeicher) — bewusst nicht Teil von Phase 6

Code-Blöcke und Block-Bäume in der Workbench: [Code-Blöcke](/erklaerungen/24-code-blocks).

## Typische Fehler

- **Leere Registry** — zuerst im Workspace kanonisieren oder Dateien laden
- **Sprache übersprungen** — Dateiendung passt nicht zum aktiven Sprachfilter
- **Ablage voll** — alte Snapshots löschen oder als JSON exportieren
- **Gleicher Projektname nach Laden** — mehrere Live-Projekte können denselben Namen tragen; an `sourceSaveId`-Badge und Sidebar-Liste unterscheiden

## Verknüpfungen

- [Registry](/erklaerungen/15-registry)
- [Redundanz](/erklaerungen/22-redundanz)
- [Code-Blöcke](/erklaerungen/24-code-blocks)
- [Payload-Kinds](/erklaerungen/17-payload-kinds)
