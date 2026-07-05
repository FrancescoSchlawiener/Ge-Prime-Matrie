"""Schnelle Invarianten für Profil-Benchmark (CI)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from alphabets.normalize import prepare_substrate
from alphabets.profiles import AlphabetProfile
from alphabets.registry import all_profiles
from gpm_types.si.codec import decode_si, encode_si
from perm.lut import MAX_LUT_BUILD_LENGTH
from perm.multiset import perm_fits_width
from tools.benchmark_patterns import (
    PATTERN_IDS,
    build_pattern,
    can_build_pattern,
)
from tools.profile_benchmark import run_sweep_point, width_gate_blocks


class TestProfileLimitsSmoke(unittest.TestCase):
    def test_all_profiles_count(self) -> None:
        self.assertEqual(len(all_profiles()), 33)

    def test_perm_fits_width_one(self) -> None:
        self.assertTrue(perm_fits_width(1))

    def test_l1_roundtrip_all_profiles(self) -> None:
        for profile in all_profiles():
            raw = build_pattern(profile, 1, "all_same")
            s, idx = encode_si(raw, profile)
            expected = prepare_substrate(raw, profile)
            self.assertEqual(decode_si(s, idx, profile), expected, profile.name)

    def test_lut_length_invariant(self) -> None:
        self.assertEqual(MAX_LUT_BUILD_LENGTH, 12)

    def test_pattern_builder_valid_strings(self) -> None:
        for profile in all_profiles():
            for pattern in PATTERN_IDS:
                if can_build_pattern(profile, 4, pattern):
                    raw = build_pattern(profile, 4, pattern)
                    self.assertEqual(len(raw), 4, f"{profile.name}/{pattern}")

    def test_width_gate_blocks_huge_n_perm(self) -> None:
        self.assertTrue(width_gate_blocks(1 << 129))
        self.assertTrue(width_gate_blocks(2_000_000))

    @patch("tools.profile_benchmark.perm_index")
    @patch("tools.profile_benchmark.encode_si")
    def test_width_gate_skips_expensive_steps(
        self,
        mock_encode: unittest.mock.MagicMock,
        mock_perm_index: unittest.mock.MagicMock,
    ) -> None:
        profile = AlphabetProfile.THAI
        raw = build_pattern(profile, 48, "max_multiplicity")
        row = run_sweep_point(
            profile,
            raw,
            length=48,
            pattern="max_multiplicity",
        )
        if row.get("failed_at") in ("width_limit", "perm_index_limit"):
            mock_perm_index.assert_not_called()
            mock_encode.assert_not_called()
            self.assertIn("perm_index", row.get("skipped_steps", []))
            self.assertIsNone(row.get("encode_si_ms"))
        else:
            mock_perm_index.assert_called()
            mock_encode.assert_called()

    def test_unique_l64_not_buildable_for_any_profile(self) -> None:
        for profile in all_profiles():
            self.assertFalse(
                can_build_pattern(profile, 64, "unique"),
                profile.name,
            )


if __name__ == "__main__":
    unittest.main()
