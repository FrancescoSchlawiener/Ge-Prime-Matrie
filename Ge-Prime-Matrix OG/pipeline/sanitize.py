import string

_PUNCT = set(string.punctuation) | {"\t", "\r"}


def sanitize_line(line: str) -> str | None:
    """Trim line; reject empty, digit, or punctuation-containing lines."""
    word = line.strip()
    if not word:
        return None
    if any(ch.isdigit() for ch in word):
        return None
    if any(ch in _PUNCT for ch in word):
        return None
    return word
