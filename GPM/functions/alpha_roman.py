"""Compatibility shim — use alphabets.registry + alphabets.roman."""
from alphabets.profiles import AlphabetProfile
from alphabets.registry import char_map_for_profile, lex_order_for_profile, prime_map_for_profile
from alphabets.roman.map import *  # noqa: F403
