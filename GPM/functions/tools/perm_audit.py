"""CLI — Perm-Invarianten-Audit für alle 33 Profile."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from alphabets.lex import lex_order_for_profile
from alphabets.normalize import prepare_substrate
from alphabets.profiles import AlphabetProfile
from alphabets.registry import all_profiles
from gpm_types.si.codec import permutation_index_for_profile
from gpm_types.si.order import Sk_lut, sequence_key_via_lut
from tools.benchmark_patterns import build_unique, can_build_pattern
from tools.perm_invariants import anagram_pair_for_profile, check_anagram_invariant


def audit_profile(profile: AlphabetProfile) -> str | None:
    pair = anagram_pair_for_profile(profile)
    if pair is None:
        return f"{profile.name}: kein Anagramm-Paar baubar"
    word_a, word_b = pair
    err = check_anagram_invariant(profile, word_a, word_b)
    if err:
        return f"{profile.name}: {err}"

    if can_build_pattern(profile, 3, "unique"):
        raw = build_unique(lex_order_for_profile(profile), 3)
        seq = prepare_substrate(raw, profile)
        if len(seq) <= 12:
            i_lut = sequence_key_via_lut(seq, profile)[1]
            i_perm = permutation_index_for_profile(seq, profile)
            if i_lut != i_perm:
                return f"{profile.name}: LUT-Index {i_lut} != perm_index {i_perm}"
            if Sk_lut(seq, profile) != tuple(seq):
                return f"{profile.name}: Sk_lut != Substrat-Tuple"

    return None


def main() -> int:
    profiles = all_profiles()
    failures: list[str] = []
    for i, profile in enumerate(profiles, start=1):
        err = audit_profile(profile)
        if err:
            failures.append(err)
            print(f"[{i}/{len(profiles)}] FAIL {err}", flush=True)
        else:
            print(f"[{i}/{len(profiles)}] OK {profile.name}", flush=True)

    if failures:
        print(f"\n{len(failures)}/{len(profiles)} Profile fehlgeschlagen.", flush=True)
        return 1
    print(f"\n{len(profiles)}/{len(profiles)} Profile OK.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
