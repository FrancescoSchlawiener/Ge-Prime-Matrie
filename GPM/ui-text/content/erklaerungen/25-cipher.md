---
title: S(I)-Cipher
---

# S(I)-Cipher — Verschlüsselungsmodi im GPM-Tab

Die **S(I)-Cipher** verschlüsselt Klartext mit schlüsselabhängigen Modi, bevor er in ein Dokument oder einen Export einfließt. Sie ist **nicht** dasselbe wie die GPC-Dateihülle — siehe [GPC-Hülle](/erklaerungen/28-cipher-gpc).

## Kernidee

Workbench bietet im GPM-Tab einen **Cipher-Dialog**: Text oder Payload mit Passwort schützen. Verschiedene Modi mappen den Schlüssel unterschiedlich auf die S(I)-Algebra — von didaktisch einfach bis „hardcore“.

## Formal — Modi

| Modus | Beschreibung |
|-------|--------------|
| **word** | Wort-basierte Schlüsselableitung (Standard) |
| **prime** | Primzahl-Raum als Schlüsselraum |
| **si** | Direkte S(I)-Kopplung |
| **hardcore** | Maximale Härtung, alle Invarianten aktiv |

Gültige Modi: `VALID_MODES` in der Cipher-Implementierung.

## Ablauf — Verschlüsseln

1. Klartext + Passwort im Dialog eingeben
2. Modus wählen (word / prime / si / hardcore)
3. `encrypt_text` → Base64-Ciphertext
4. Optional: in Export-Pipeline einbetten

## Ablauf — Entschlüsseln

1. Ciphertext + gleicher Schlüssel
2. `decrypt_ciphertext`
3. Klartext zurück in Editor

## API

| Route | Funktion |
|-------|----------|
| `POST /api/cipher/encrypt` | Verschlüsseln |
| `POST /api/cipher/decrypt` | Entschlüsseln |

Editor-Route kann bei Export `wrap_cipher_payload` mit `mode="word"` aufrufen — dann entsteht eine **GPC-Datei**, nicht nur Roh-Ciphertext.



## Typische Fehler

- Workbench-Schritte und Beispiele stehen in den Karten **oberhalb** der Verknüpfungen.
- Alte Lesezeichen mit früheren Kapitelnummern werden automatisch weitergeleitet.

## Verknüpfungen

- [GPC-Hülle](/erklaerungen/28-cipher-gpc) — verschlüsselte .gpm-Datei
- [Substanz S](/erklaerungen/01-substanz-s)
- [GPM Binary](/erklaerungen/13-gpm-binary)
