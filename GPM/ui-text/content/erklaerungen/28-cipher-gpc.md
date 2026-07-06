---
title: GPC-Hülle
---

# GPC-Hülle — verschlüsselte .gpm-Dateien

**GPC** (Ge-Prime-Cipher) ist die **Dateihülle** um eine verschlüsselte GPM-Nutzlast. Magic-Bytes: `GPC\x01` — nicht zu verwechseln mit `GPM` (Klartext-Container).

## Kernidee

Eine normale `.gpm` beginnt mit `GPM`. Eine verschlüsselte Datei beginnt mit `GPC\x01` + JSON-Metadaten + Ciphertext. Ohne Schlüssel liefert `read_gpm` einen strukturierten Fehler `cipher_key_required`.

## Formal — Dateiaufbau

```
GPC\x01 | meta_len (4 BE) | meta JSON | payload_len (4 BE) | ciphertext (ASCII/base64)
```

Meta-Felder:

| Feld | Bedeutung |
|------|-----------|
| `gpc_version` | GPC-Formatversion |
| `cipher_version` | Cipher-Algorithmus-Version |
| `mode` | word / prime / si / hardcore |

## Ablauf — Erzeugen

1. Dokument kompilieren → `write_gpm` → Klartext-Bytes
2. `encrypt_text` mit Passwort und Modus
3. `wrap_cipher_payload(ciphertext, mode=…)` → GPC-Blob
4. Als `.gpm` speichern (Dateiendung gleich, Magic unterscheidet)

## Ablauf — Lesen

1. Datei laden; Magic prüfen
2. Wenn `GPC\x01`: Schlüssel erforderlich
3. `decrypt_gpm_file(blob, key)` → innere GPM-Bytes
4. `read_gpm` → `GpmDocument`

## API-Fehlervertrag

`POST /api/editor/gpm/read` ohne Schlüssel bei GPC-Datei:

```json
{
  "error": {
    "code": "cipher_key_required",
    "message": "…"
  }
}
```

Fast-fail im RAM — keine teure Parsing-Pipeline auf verschlüsselten Blobs.

## Abgrenzung zu S(I)-Cipher

| Thema | S(I)-Cipher | GPC-Hülle |
|-------|-------------|-----------|
| Kapitel | [21-cipher](/erklaerungen/25-cipher) | dieses Kapitel |
| Ebene | Algorithmus / Dialog | Datei-Container |
| Magic | — | `GPC\x01` |
| Typischer Weg | `/api/cipher/*` | Export im GPM-Tab |


## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [S(I)-Cipher](/erklaerungen/25-cipher)
- [GPM Binary](/erklaerungen/13-gpm-binary)

**Zurück zum Einstieg:** [00-einstieg](/erklaerungen/00-einstieg)
