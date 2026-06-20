from ge_prime.core import PRIME_MAP


def is_valid_normalized(word: str) -> bool:
    """All characters must be in the 26 fixed prime-letter alphabet."""
    return len(word) >= 1 and all(ch in PRIME_MAP for ch in word)
