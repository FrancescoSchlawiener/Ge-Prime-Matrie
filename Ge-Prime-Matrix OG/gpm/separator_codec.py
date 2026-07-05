"""Kompakter Separator-Layer für .gpm v3/v4.

Perm-Code (Z/S/E/U) + minimaler Blob. BASE enthält Leerzeichen, Satzzeichen und
Unterstrich ``_``. Unbekannte Symbole/Emoji → Perm U (Unicode-Fallback).
"""

from __future__ import annotations

# Permutations-Bits (OR beim Kompilieren)
SEP_PERM_Z = 1  # Ziffern
SEP_PERM_S = 2  # Symbole
SEP_PERM_E = 4  # Emoji
SEP_PERM_U = 8  # Unicode-Fallback

ESC = 0x1E
GAP_SEP = 0x1F

BASE_WHITESPACE = frozenset(" \n\r\t")
BASE_PUNCTUATION = frozenset('.,;:!?…"\'-–—()[]{} /_')

# Fest sortierte Symbol-Tabelle (Perm-Code 1 / hardcoded)
SYMBOL_TABLE: tuple[str, ...] = (
    "@", "#", "$", "%", "&", "*", "+", "=", "<", ">", "|", "\\", "^", "~",
    "§", "€", "£", "¥", "¢", "©", "®", "™", "°", "±", "×", "÷", "µ", "¶",
    "·", "•", "†", "‡", "‰", "‹", "›", "«", "»", "„", "‚", "`", "´",
    "½", "¼", "¾", "¿", "¡", "¤", "¦", "¨", "¯", "´", "¸", "¸",
    "←", "→", "↑", "↓", "↔", "↕", "∞", "∑", "∏", "√", "∫", "≈", "≠", "≤", "≥",
    "∀", "∃", "∂", "∇", "∈", "∉", "∩", "∪", "⊂", "⊃", "⊆", "⊇",
    "♠", "♣", "♥", "♦", "♪", "♫", "✓", "✗", "✔", "✘", "★", "☆", "☀", "☁", "☂",
    "☎", "☐", "☑", "☒", "☕", "⚠", "⚡", "⬆", "⬇", "⬅", "➡",
)

_SYMBOL_INDEX: dict[str, int] = {ch: i for i, ch in enumerate(SYMBOL_TABLE)}

# Häufige Emoji (fest sortiert)
EMOJI_TABLE: tuple[str, ...] = (
    "😀", "😃", "😄", "😁", "😆", "😅", "🤣", "😂", "🙂", "🙃", "😉", "😊",
    "😇", "🥰", "😍", "🤩", "😘", "😗", "😚", "😙", "😋", "😛", "😜", "🤪",
    "😝", "🤑", "🤗", "🤭", "🤫", "🤔", "🤐", "🤨", "😐", "😑", "😶", "😏",
    "😒", "🙄", "😬", "🤥", "😌", "😔", "😪", "🤤", "😴", "😷", "🤒", "🤕",
    "🤢", "🤮", "🤧", "🥵", "🥶", "🥴", "😵", "🤯", "🤠", "🥳", "😎", "🤓",
    "🧐", "😕", "😟", "🙁", "☹", "😮", "😯", "😲", "😳", "🥺", "😦", "😧",
    "😨", "😰", "😥", "😢", "😭", "😱", "😖", "😣", "😞", "😓", "😩", "😫",
    "🥱", "😤", "😡", "😠", "🤬", "👍", "👎", "👏", "🙌", "🤝", "🙏", "💪",
    "❤", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❣", "💕",
    "💖", "💗", "💘", "💝", "💞", "💟", "☮", "✝", "☪", "🕉", "☸", "✡",
    "🔥", "⭐", "🌟", "✨", "⚡", "💥", "💫", "💦", "💨", "🎉", "🎊", "🎁",
    "🎈", "🎀", "🏆", "🥇", "🥈", "🥉", "⚽", "🏀", "🎮", "🎯", "🎲", "🎵",
    "🎶", "🎤", "🎧", "📱", "💻", "⌨", "🖥", "🖨", "📷", "📹", "🔋", "🔌",
    "💡", "🔦", "📚", "📖", "✏", "📝", "📌", "📎", "✂️", "🔑", "🔒", "🔓",
    "🌍", "🌎", "🌏", "🌐", "🗺", "🧭", "🏠", "🏢", "🚀", "✈", "🚗", "🚕",
    "🚌", "🚎", "🚲", "🛴", "☕", "🍵", "🍺", "🍷", "🍕", "🍔", "🍟", "🌭",
    "🥗", "🍎", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🥐", "🍞", "🧀", "🥚",
)

_EMOJI_INDEX: dict[str, int] = {ch: i for i, ch in enumerate(EMOJI_TABLE)}


class SeparatorCodecError(ValueError):
    """Ungültiger Separator-Stream."""


def _is_emoji(ch: str) -> bool:
    if ch in _EMOJI_INDEX:
        return True
    o = ord(ch)
    return (
        0x1F300 <= o <= 0x1FAFF
        or 0x2600 <= o <= 0x26FF
        or 0x2700 <= o <= 0x27BF
        or 0x1F600 <= o <= 0x1F64F
        or 0x1F900 <= o <= 0x1F9FF
    )


def _char_class(ch: str) -> str:
    if ch in BASE_WHITESPACE or ch in BASE_PUNCTUATION:
        return "base"
    if ch.isdigit():
        return "z"
    if ch in _EMOJI_INDEX or _is_emoji(ch):
        return "e"
    if ch in _SYMBOL_INDEX:
        return "s"
    cat = __import__("unicodedata").category(ch)
    if cat.startswith("S") or cat.startswith("P") and ch not in BASE_PUNCTUATION:
        return "s"
    if cat.startswith("N") and not ch.isdigit():
        return "s"
    return "u"


def scan_perm_code(gaps: list[str]) -> int:
    """Ermittelt Perm-Bitmask aus allen Gap-Strings."""
    perm = 0
    for gap in gaps:
        i = 0
        while i < len(gap):
            ch = gap[i]
            if ch.isdigit():
                perm |= SEP_PERM_Z
                while i < len(gap) and gap[i].isdigit():
                    i += 1
                continue
            cls = _char_class(ch)
            if cls == "z":
                perm |= SEP_PERM_Z
            elif cls == "s":
                if ch in _SYMBOL_INDEX:
                    perm |= SEP_PERM_S
                else:
                    perm |= SEP_PERM_U
            elif cls == "e":
                if ch in _EMOJI_INDEX:
                    perm |= SEP_PERM_E
                else:
                    perm |= SEP_PERM_U
            elif cls == "u":
                perm |= SEP_PERM_U
            i += 1
    return perm


def perm_code_label(perm: int) -> str:
    """Lesbare Beschreibung für UI."""
    if perm == 0:
        return "BASE (Leerzeichen & Satzzeichen)"
    parts = ["BASE"]
    if perm & SEP_PERM_Z:
        parts.append("Ziffern")
    if perm & SEP_PERM_S:
        parts.append("Symbole")
    if perm & SEP_PERM_E:
        parts.append("Emoji")
    if perm & SEP_PERM_U:
        parts.append("Unicode")
    return " + ".join(parts)


def _pack_varint(value: int) -> bytes:
    if value < 0:
        raise SeparatorCodecError("Varint darf nicht negativ sein.")
    out = bytearray()
    while value > 0x7F:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value & 0x7F)
    return bytes(out) if out else b"\x00"


def _unpack_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while offset < len(data):
        b = data[offset]
        offset += 1
        value |= (b & 0x7F) << shift
        if not (b & 0x80):
            return value, offset
        shift += 7
        if shift > 35:
            raise SeparatorCodecError("Varint zu lang.")
    raise SeparatorCodecError("Varint unvollständig.")


def _encode_literal_byte(b: int, out: bytearray) -> None:
    if b in (ESC, GAP_SEP):
        out.append(ESC)
        out.append(b)
    else:
        out.append(b)


def _encode_gap_text(gap: str, perm: int) -> bytes:
    out = bytearray()
    i = 0
    while i < len(gap):
        ch = gap[i]
        if ch.isdigit() and (perm & SEP_PERM_Z):
            out.append(ESC)
            out.append(ord("Z"))
            while i < len(gap) and gap[i].isdigit():
                out.append(ord(gap[i]))
                i += 1
            continue

        cls = _char_class(ch)

        if cls == "base":
            for b in ch.encode("utf-8"):
                _encode_literal_byte(b, out)
        elif cls == "z" and (perm & SEP_PERM_Z):
            out.append(ESC)
            out.append(ord("Z"))
            while i < len(gap) and gap[i].isdigit():
                out.append(ord(gap[i]))
                i += 1
            continue
        elif cls == "s" and (perm & SEP_PERM_S):
            idx = _SYMBOL_INDEX.get(ch)
            if idx is None:
                raw = ch.encode("utf-8")
                if perm & SEP_PERM_U:
                    out.append(ESC)
                    out.append(ord("U"))
                    out.extend(_pack_varint(len(raw)))
                    out.extend(raw)
                else:
                    raise SeparatorCodecError(f"Symbol nicht in Tabelle: {ch!r}")
            else:
                out.append(ESC)
                out.append(ord("S"))
                out.extend(_pack_varint(idx))
        elif cls == "e" and (perm & SEP_PERM_E):
            idx = _EMOJI_INDEX.get(ch)
            if idx is None:
                if perm & SEP_PERM_U:
                    raw = ch.encode("utf-8")
                    out.append(ESC)
                    out.append(ord("U"))
                    out.extend(_pack_varint(len(raw)))
                    out.extend(raw)
                else:
                    raise SeparatorCodecError(f"Emoji nicht in Tabelle: {ch!r}")
            else:
                out.append(ESC)
                out.append(ord("E"))
                out.extend(_pack_varint(idx))
        elif perm & SEP_PERM_U:
            raw = ch.encode("utf-8")
            out.append(ESC)
            out.append(ord("U"))
            out.extend(_pack_varint(len(raw)))
            out.extend(raw)
        else:
            raise SeparatorCodecError(
                f"Zeichen {ch!r} benötigt Perm-Bit, perm={perm} reicht nicht."
            )
        i += 1
    return bytes(out)


def encode_gaps(gaps: list[str], perm: int) -> bytes:
    """Alle Gaps in einen kompakten Blob (GAP_SEP zwischen Slots)."""
    if not gaps:
        return b""
    parts = [_encode_gap_text(g, perm) for g in gaps]
    return GAP_SEP.to_bytes(1, "big").join(parts)


def _decode_gap_text(data: bytes, perm: int) -> str:
    out: list[str] = []
    i = 0
    while i < len(data):
        b = data[i]
        if b == ESC:
            i += 1
            if i >= len(data):
                raise SeparatorCodecError("Escape am Ende.")
            tag = data[i]
            i += 1
            if tag == ord("Z"):
                if not (perm & SEP_PERM_Z):
                    raise SeparatorCodecError("Z-Sequenz ohne Z-Perm.")
                while i < len(data) and 0x30 <= data[i] <= 0x39:
                    out.append(chr(data[i]))
                    i += 1
            elif tag == ord("S"):
                if not (perm & SEP_PERM_S):
                    raise SeparatorCodecError("S-Sequenz ohne S-Perm.")
                idx, i = _unpack_varint(data, i)
                if idx >= len(SYMBOL_TABLE):
                    raise SeparatorCodecError(f"Symbol-Index {idx} ungültig.")
                out.append(SYMBOL_TABLE[idx])
            elif tag == ord("E"):
                if not (perm & SEP_PERM_E):
                    raise SeparatorCodecError("E-Sequenz ohne E-Perm.")
                idx, i = _unpack_varint(data, i)
                if idx >= len(EMOJI_TABLE):
                    raise SeparatorCodecError(f"Emoji-Index {idx} ungültig.")
                out.append(EMOJI_TABLE[idx])
            elif tag == ord("U"):
                if not (perm & SEP_PERM_U):
                    raise SeparatorCodecError("U-Sequenz ohne U-Perm.")
                length, i = _unpack_varint(data, i)
                if i + length > len(data):
                    raise SeparatorCodecError("U-Block abgeschnitten.")
                out.append(data[i : i + length].decode("utf-8"))
                i += length
            elif tag in (ESC, GAP_SEP):
                out.append(chr(tag))
            else:
                raise SeparatorCodecError(f"Unbekannter Escape-Tag: {tag}.")
        else:
            start = i
            while i < len(data):
                if data[i] == ESC:
                    break
                i += 1
            out.append(data[start:i].decode("utf-8"))
    return "".join(out)


def decode_gaps(blob: bytes, perm: int, gap_count: int) -> list[str]:
    """Blob → N Gap-Strings."""
    if gap_count < 1:
        raise SeparatorCodecError("gap_count muss ≥ 1 sein.")
    if gap_count == 1:
        return [_decode_gap_text(blob, perm)]

    parts = blob.split(bytes([GAP_SEP]))
    if len(parts) != gap_count:
        raise SeparatorCodecError(
            f"Gap-Anzahl {len(parts)} ≠ erwartet {gap_count}."
        )
    return [_decode_gap_text(p, perm) for p in parts]
