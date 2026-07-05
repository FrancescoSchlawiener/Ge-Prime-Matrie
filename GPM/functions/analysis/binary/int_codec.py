"""Modellpassende Integer-Stufen (2/4/8/16 Byte) für .gpm."""

from __future__ import annotations

from collections import Counter

from perm.multiset import calc_total_perms

WIDTH_CLASSES = (2, 4, 8, 16)


def width_class_for_magnitude(value: int) -> int:
    if value < 1:
        raise ValueError("Wert muss >= 1 sein.")
    bits = value.bit_length()
    if bits <= 16:
        return 0
    if bits <= 32:
        return 1
    if bits <= 64:
        return 2
    return 3


def width_bytes_for_class(width_class: int) -> int:
    if not 0 <= width_class < len(WIDTH_CLASSES):
        raise ValueError(f"Ungültige Width-Klasse: {width_class}.")
    return WIDTH_CLASSES[width_class]


def substance_width_class(substance: int) -> int:
    if substance < 1:
        raise ValueError("Substanz muss >= 1 sein.")
    return width_class_for_magnitude(substance)


def perm_space_size(normalized: str) -> int:
    return calc_total_perms(Counter(normalized))


def perm_width_class(normalized: str) -> int:
    return width_class_for_magnitude(perm_space_size(normalized))


def perm_width_bytes(normalized: str) -> int:
    return width_bytes_for_class(perm_width_class(normalized))


def encode_fixed_int(value: int, width_bytes: int) -> bytes:
    if value < 0:
        raise ValueError("Ganzzahl darf nicht negativ sein.")
    max_val = (1 << (width_bytes * 8)) - 1
    if value > max_val:
        raise ValueError(f"Wert {value} passt nicht in {width_bytes} Byte (max {max_val}).")
    return value.to_bytes(width_bytes, "big")


def decode_fixed_int(data: bytes, width_bytes: int) -> int:
    if len(data) != width_bytes:
        raise ValueError(f"Erwartet {width_bytes} Byte, erhalten {len(data)}.")
    return int.from_bytes(data, "big")


def genome_substance_field_bytes(substance: int) -> int:
    return 1 + width_bytes_for_class(substance_width_class(substance))
