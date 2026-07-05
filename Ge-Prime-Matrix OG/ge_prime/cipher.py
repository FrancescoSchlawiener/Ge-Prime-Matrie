"""S(I)-Verschlüsselung — symmetrische Obfuskation mit Wort- und Primzahl-Schlüsseln.

Modi: word, prime, si, hardcore. Kompiliert Text zu GPM-Geometrie, transformiert
S/I und Separator-Schicht. Wird auch von ``gpm/cipher_wrap`` (GPC) genutzt.
Kein Ersatz für AES — wer PRIME_MAP und Schlüssel kennt, kann entschlüsseln.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass

from ge_prime.encode import encode_word, get_substance
from gpm.compiler import compile_text
from gpm.int_codec import perm_space_size
from gpm.model import GpmDocument, GpmHeaderEntry, GpmToken
from gpm.reader import reconstruct_text
from pipeline.normalize import normalize_word

CIPHER_VERSION = 1
MAX_CIPHER_TOKENS = 2000

MODE_WORD = "word"
MODE_PRIME = "prime"
MODE_SI = "si"
MODE_HARDCORE = "hardcore"
VALID_MODES = (MODE_WORD, MODE_PRIME, MODE_SI, MODE_HARDCORE)


@dataclass(frozen=True)
class KeyEntry:
    kind: str  # "word" | "prime"
    value: str


def _is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def parse_key_token(raw: str) -> KeyEntry:
    """Einzelnen Schlüssel parsen: Wort oder ``prime:17`` / ``p:103``."""
    raw = raw.strip()
    if not raw:
        raise ValueError("Leerer Schlüssel-Eintrag.")
    lower = raw.lower()
    if lower.startswith("prime:") or lower.startswith("p:"):
        part = raw.split(":", 1)[1].strip()
        try:
            p = int(part)
        except ValueError as exc:
            raise ValueError(f"Ungültige Primzahl: {part!r}") from exc
        if p < 2:
            raise ValueError("Primzahl-Schlüssel muss ≥ 2 sein.")
        if not _is_probable_prime(p):
            raise ValueError(f"{p} ist keine Primzahl.")
        return KeyEntry("prime", str(p))
    normalized = normalize_word(raw)
    if not normalized or not any(ch.isalpha() for ch in normalized):
        raise ValueError(f"Ungültiges Schlüsselwort: {raw!r}")
    return KeyEntry("word", normalized)


def parse_keys(keys_raw: str | list[str], *, mode: str) -> list[KeyEntry]:
    if mode == MODE_HARDCORE:
        if isinstance(keys_raw, str):
            parts = [p.strip() for p in keys_raw.replace("\n", ",").split(",") if p.strip()]
        else:
            parts = [str(p).strip() for p in keys_raw if str(p).strip()]
        if len(parts) < 2:
            raise ValueError("Hardcore-Modus: mindestens zwei Schlüssel (Wort oder prime:N), kommagetrennt.")
        return [parse_key_token(p) for p in parts]

    if isinstance(keys_raw, list):
        keys_raw = keys_raw[0] if keys_raw else ""
    token = parse_key_token(str(keys_raw or "").strip())
    if mode == MODE_PRIME and token.kind != "prime":
        raise ValueError("Primzahl-Modus: Schlüssel als prime:N angeben (z. B. prime:17).")
    if mode in (MODE_WORD, MODE_SI) and token.kind != "word":
        raise ValueError("Wort-Modus: ein Buchstaben-Wort als Schlüssel (kein prime:).")
    return [token]


def _key_base_int(key: KeyEntry) -> int:
    if key.kind == "word":
        return get_substance(key.value)
    return int(key.value)


def _mix_int(key: KeyEntry, position: int, lane: str) -> int:
    base = _key_base_int(key)
    digest = hashlib.sha256(f"{key.kind}:{key.value}:{base}:{position}:{lane}".encode()).hexdigest()
    return int(digest[:16], 16) + 1


def _stream_byte(key: KeyEntry, index: int) -> int:
    digest = hashlib.sha256(f"gap:{key.kind}:{key.value}:{index}".encode()).digest()
    return digest[index % len(digest)]


def _encrypt_gap(gap: str, keys: list[KeyEntry], anchor: int) -> str:
    if not gap:
        return ""
    data = gap.encode("utf-8")
    enc = bytearray(len(data))
    for i, byte in enumerate(data):
        key = keys[(anchor + i) % len(keys)]
        enc[i] = byte ^ _stream_byte(key, anchor + i)
    return base64.b64encode(bytes(enc)).decode("ascii")


def _decrypt_gap(gap_enc: str, keys: list[KeyEntry], anchor: int) -> str:
    if not gap_enc:
        return ""
    data = base64.b64decode(gap_enc.encode("ascii"))
    out = bytearray(len(data))
    for i, byte in enumerate(data):
        key = keys[(anchor + i) % len(keys)]
        out[i] = byte ^ _stream_byte(key, anchor + i)
    return bytes(out).decode("utf-8")


def _encrypt_s(substance: int, key: KeyEntry, position: int, *, dual_lane: bool) -> int:
    k = _mix_int(key, position, "S")
    if dual_lane:
        k2 = _mix_int(key, position, "S2")
        return substance * k + k2
    return substance * k


def _decrypt_s(s_enc: int, key: KeyEntry, position: int, *, dual_lane: bool) -> int:
    k = _mix_int(key, position, "S")
    if dual_lane:
        k2 = _mix_int(key, position, "S2")
        if (s_enc - k2) % k != 0:
            raise ValueError("Entschlüsselung fehlgeschlagen — falscher Schlüssel oder beschädigte Daten.")
        return (s_enc - k2) // k
    if s_enc % k != 0:
        raise ValueError("Entschlüsselung fehlgeschlagen — falscher Schlüssel oder beschädigte Daten.")
    return s_enc // k


def _encrypt_i(perm_index: int, perm_space: int, key: KeyEntry, position: int, *, dual_lane: bool) -> int:
    if perm_space <= 1:
        return perm_index
    k = _mix_int(key, position, "I" if dual_lane else "i") % perm_space or 1
    return (perm_index + k - 1) % perm_space + 1


def _decrypt_i(i_enc: int, perm_space: int, key: KeyEntry, position: int, *, dual_lane: bool) -> int:
    if perm_space <= 1:
        return i_enc
    k = _mix_int(key, position, "I" if dual_lane else "i") % perm_space or 1
    return (i_enc - k - 1) % perm_space + 1


def assess_security(mode: str, keys: list[KeyEntry]) -> dict:
    """Ehrliche Sicherheitsbewertung für UI — kein Ersatz für AES."""
    warnings = [
        "Symmetrisch: wer PRIME_MAP und Schlüssel kennt, kann entschlüsseln.",
        "Kein Ersatz für AES/GPG — geeignet für Demonstration und Obfuskation.",
    ]
    base = {
        MODE_WORD: (32, "niedrig", "Einzelnes Wort → Substanz S als Schlüsselmaterial"),
        MODE_PRIME: (40, "niedrig", "Eine Primzahl als Schlüssel — kurze Schlüssel sind erratbar"),
        MODE_SI: (55, "mittel", "Getrennte S- und I-Mischung aus einem Wortschlüssel"),
        MODE_HARDCORE: (72, "hoch", "Wechselnde Wort- und Primzahl-Schlüssel pro Token"),
    }[mode]
    score, level, summary = base
    if mode == MODE_HARDCORE:
        score = min(92, score + max(0, len(keys) - 2) * 4)
        if len(keys) >= 4:
            level = "sehr hoch"
        mixed = len({k.kind for k in keys}) > 1
        if mixed:
            score = min(95, score + 3)
            summary += " · gemischte Wort/Primzahl-Sequenz"
    elif mode == MODE_SI:
        if keys and keys[0].kind == "word" and len(keys[0].value) >= 8:
            score = min(62, score + 5)
    confidence = "gering" if score < 45 else "moderat" if score < 65 else "erhöht"
    return {
        "level": level,
        "score": score,
        "confidence": confidence,
        "summary": summary,
        "key_count": len(keys),
        "warnings": warnings,
    }


def _dual_lane(mode: str) -> bool:
    return mode in (MODE_SI, MODE_HARDCORE)


def encrypt_text(text: str, *, mode: str, keys_raw: str | list[str]) -> dict:
    if mode not in VALID_MODES:
        raise ValueError(f"Unbekannter Modus: {mode}")
    if not text or not text.strip():
        raise ValueError("Leerer Text — nichts zu verschlüsseln.")

    keys = parse_keys(keys_raw, mode=mode)
    document, _, stats = compile_text(text)
    if stats.total_tokens > MAX_CIPHER_TOKENS:
        raise ValueError(f"Maximal {MAX_CIPHER_TOKENS:,} Token pro Verschlüsselung.")

    dual = _dual_lane(mode)
    header_out = []
    for entry in document.header:
        key = keys[entry.word_id % len(keys)]
        s_enc = _encrypt_s(entry.substance, key, entry.word_id, dual_lane=dual)
        header_out.append(
            {
                "word_id": entry.word_id,
                "word_original": entry.word_original,
                "word_normalized": entry.word_normalized,
                "s_enc": s_enc,
            }
        )

    tokens_out = []
    for pos, token in enumerate(document.tokens):
        key = keys[pos % len(keys)]
        entry = document.header[token.word_id]
        n = perm_space_size(entry.word_normalized)
        i_enc = _encrypt_i(token.perm_index, n, key, pos, dual_lane=dual)
        tokens_out.append(
            {
                "word_id": token.word_id,
                "i_enc": i_enc,
                "case_code": token.case_code,
                "perm_space": n,
            }
        )

    gaps_enc = []
    for i, gap in enumerate(document.gaps):
        gaps_enc.append(_encrypt_gap(gap, keys, i * 97))

    security = assess_security(mode, keys)
    payload = {
        "cipher_version": CIPHER_VERSION,
        "mode": mode,
        "security": security,
        "header": header_out,
        "tokens": tokens_out,
        "gaps_enc": gaps_enc,
        "explicit": document.explicit,
        "token_count": len(tokens_out),
        "unique_words": len(header_out),
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {
        "ciphertext": base64.b64encode(raw).decode("ascii"),
        "mode": mode,
        "security": security,
        "token_count": len(tokens_out),
        "unique_words": len(header_out),
        "preview": reconstruct_text(document)[:120],
    }


def _document_from_payload(payload: dict, keys: list[KeyEntry], *, mode: str) -> GpmDocument:
    dual = _dual_lane(mode)
    header = []
    for row in payload["header"]:
        key = keys[row["word_id"] % len(keys)]
        substance = _decrypt_s(row["s_enc"], key, row["word_id"], dual_lane=dual)
        header.append(
            GpmHeaderEntry(
                word_id=row["word_id"],
                word_original=row["word_original"],
                word_normalized=row["word_normalized"],
                substance=substance,
            )
        )

    tokens = []
    for pos, row in enumerate(payload["tokens"]):
        key = keys[pos % len(keys)]
        perm_index = _decrypt_i(
            row["i_enc"],
            row["perm_space"],
            key,
            pos,
            dual_lane=dual,
        )
        tokens.append(
            GpmToken(
                word_id=row["word_id"],
                perm_index=perm_index,
                case_code=row["case_code"],
            )
        )

    gaps = []
    for i, gap_enc in enumerate(payload["gaps_enc"]):
        gaps.append(_decrypt_gap(gap_enc, keys, i * 97))

    return GpmDocument(
        header=header,
        tokens=tokens,
        gaps=gaps,
        explicit=[tuple(x) for x in payload.get("explicit", [])],
    )


def decrypt_ciphertext(ciphertext: str, *, keys_raw: str | list[str]) -> dict:
    if not ciphertext or not str(ciphertext).strip():
        raise ValueError("Kein Chiffretext.")

    try:
        raw = base64.b64decode(ciphertext.strip().encode("ascii"))
        payload = json.loads(raw.decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Ungültiger Chiffretext (kein gültiges S(I)-Cipher-Paket).") from exc

    if payload.get("cipher_version") != CIPHER_VERSION:
        raise ValueError("Nicht unterstützte Cipher-Version.")

    mode = payload.get("mode")
    if mode not in VALID_MODES:
        raise ValueError(f"Unbekannter Modus im Paket: {mode}")

    keys = parse_keys(keys_raw, mode=mode)
    document = _document_from_payload(payload, keys, mode=mode)
    text = reconstruct_text(document)

    security = assess_security(mode, keys)
    return {
        "text": text,
        "mode": mode,
        "security": security,
        "token_count": payload.get("token_count", len(document.tokens)),
        "verified": True,
    }


def demo_roundtrip(word: str, key: str, mode: str = MODE_WORD) -> dict:
    """Kurztest für CLI."""
    enc = encrypt_text(word, mode=mode, keys_raw=key)
    dec = decrypt_ciphertext(enc["ciphertext"], keys_raw=key)
    s, i = encode_word(normalize_word(word)) if word.isalpha() else (0, 0)
    return {
        "mode": mode,
        "match": dec["text"] == word or dec["text"].upper() == word.upper(),
        "security_score": enc["security"]["score"],
        "substance": s,
        "perm_index": i,
    }
