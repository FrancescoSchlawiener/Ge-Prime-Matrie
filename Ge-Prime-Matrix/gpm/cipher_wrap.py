"""GPC — verschlüsselte .gpm-Hülle (Magic ``GPC\\x01``).

Normale .gpm beginnt mit ``GPM``; GPC wrappt ein S(I)-Cipher-Paket.
``read_gpm`` ohne Schlüssel liefert kein Genom — nur ``peek_gpc_meta`` (Modus).
"""

from __future__ import annotations

import json
import struct

from ge_prime.cipher import CIPHER_VERSION, VALID_MODES, decrypt_ciphertext, encrypt_text

GPC_MAGIC = b"GPC\x01"
GPC_VERSION = 1


class GpcFormatError(ValueError):
    """Ungültige oder beschädigte verschlüsselte GPM-Datei."""


def is_encrypted_gpm_blob(blob: bytes) -> bool:
    return len(blob) >= len(GPC_MAGIC) and blob[: len(GPC_MAGIC)] == GPC_MAGIC


def peek_gpc_meta(blob: bytes) -> dict:
    """Metadaten ohne Schlüssel (Modus für UI-Hinweis)."""
    if not is_encrypted_gpm_blob(blob):
        raise GpcFormatError("Keine verschlüsselte GPM-Datei.")
    offset = len(GPC_MAGIC)
    if len(blob) < offset + 4:
        raise GpcFormatError("GPC-Header unvollständig.")
    meta_len = struct.unpack(">I", blob[offset : offset + 4])[0]
    offset += 4
    if len(blob) < offset + meta_len:
        raise GpcFormatError("GPC-Metadaten beschädigt.")
    meta = json.loads(blob[offset : offset + meta_len].decode("utf-8"))
    offset += meta_len
    if len(blob) < offset + 4:
        raise GpcFormatError("GPC-Nutzlast-Header fehlt.")
    payload_len = struct.unpack(">I", blob[offset : offset + 4])[0]
    return {
        "gpc_version": meta.get("gpc_version", GPC_VERSION),
        "cipher_version": meta.get("cipher_version", CIPHER_VERSION),
        "mode": meta.get("mode", "word"),
        "payload_bytes": payload_len,
        "file_bytes": len(blob),
    }


def _unwrap_cipher_blob(blob: bytes) -> tuple[str, str]:
    if not is_encrypted_gpm_blob(blob):
        raise GpcFormatError("Keine verschlüsselte GPM-Datei (Magic GPC fehlt).")
    offset = len(GPC_MAGIC)
    meta_len = struct.unpack(">I", blob[offset : offset + 4])[0]
    offset += 4
    meta_raw = blob[offset : offset + meta_len]
    offset += meta_len
    payload_len = struct.unpack(">I", blob[offset : offset + 4])[0]
    offset += 4
    payload = blob[offset : offset + payload_len]
    if len(payload) != payload_len:
        raise GpcFormatError("GPC-Nutzlast beschädigt (Länge).")
    meta = json.loads(meta_raw.decode("utf-8"))
    mode = meta.get("mode", "word")
    if mode not in VALID_MODES:
        raise GpcFormatError(f"Unbekannter Cipher-Modus in Datei: {mode}")
    return mode, payload.decode("ascii")


def wrap_cipher_payload(ciphertext_b64: str, *, mode: str) -> bytes:
    if mode not in VALID_MODES:
        raise ValueError(f"Unbekannter Modus: {mode}")
    meta = json.dumps(
        {
            "gpc_version": GPC_VERSION,
            "cipher_version": CIPHER_VERSION,
            "mode": mode,
        },
        separators=(",", ":"),
    ).encode("utf-8")
    payload = ciphertext_b64.encode("ascii")
    return (
        GPC_MAGIC
        + struct.pack(">I", len(meta))
        + meta
        + struct.pack(">I", len(payload))
        + payload
    )


def encrypt_gpm_file(text: str, *, mode: str, keys_raw: str) -> tuple[bytes, dict]:
    """Text → S(I)-Cipher → GPC-Datei (nicht mit read_gpm lesbar)."""
    enc = encrypt_text(text, mode=mode, keys_raw=keys_raw)
    blob = wrap_cipher_payload(enc["ciphertext"], mode=mode)
    return blob, enc


def decrypt_gpm_file(blob: bytes, *, keys_raw: str) -> dict:
    """GPC-Datei → Klartext (danach normal kompilierbar)."""
    mode, ciphertext_b64 = _unwrap_cipher_blob(blob)
    dec = decrypt_ciphertext(ciphertext_b64, keys_raw=keys_raw)
    dec["cipher_mode"] = mode
    dec["gpc"] = True
    return dec
