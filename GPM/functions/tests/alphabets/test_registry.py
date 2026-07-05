"""Querschnitt — Registry und disjunkte Prime-Blöcke."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.profiles import AlphabetProfile
from alphabets.registry import all_profiles, prime_map_for_profile


class TestRegistry(unittest.TestCase):
    def test_thirty_three_profiles(self) -> None:
        self.assertEqual(len(all_profiles()), 33)

    def test_disjoint_prime_blocks(self) -> None:
        seen: set[int] = set()
        for profile in all_profiles():
            if profile is AlphabetProfile.ROMAN:
                continue
            primes = set(prime_map_for_profile(profile).values())
            overlap = seen & primes
            self.assertFalse(overlap, f"Overlap for {profile}: {overlap}")
            seen |= primes

    def test_og_roman_share_primes(self) -> None:
        og = prime_map_for_profile(AlphabetProfile.OG)
        roman = prime_map_for_profile(AlphabetProfile.ROMAN)
        self.assertEqual(set(og.values()), set(roman.values()))


if __name__ == "__main__":
    unittest.main()
