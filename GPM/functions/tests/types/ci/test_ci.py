import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from gpm_types.ci.registry import checksum_c, pointer_id_c
from gpm_types.ci.substance import (
    CODE_CHAR_PRIMES,
    perm_index_c,
    perm_space_c,
    prime_for_char,
    substance_c,
)


class TestCi(unittest.TestCase):
    def test_char_primes_are_distinct(self):
        primes = list(CODE_CHAR_PRIMES.values())
        self.assertEqual(len(primes), len(set(primes)))
        # Alle druckbaren ASCII-Zeichen abgedeckt.
        for ch in "abcABC{}[]();=<>+-*/.,:":
            self.assertIn(ch, CODE_CHAR_PRIMES)

    def test_substance_is_commutative(self):
        # Gleiche Zeichenmenge → gleiche Substanz.
        self.assertEqual(substance_c("=>"), substance_c(">="))
        self.assertEqual(substance_c("[]"), substance_c("]["))

    def test_perm_index_distinguishes_order(self):
        # Reihenfolge → unterschiedlicher perm_index (kollisionsfrei).
        self.assertNotEqual(perm_index_c("=>"), perm_index_c(">="))
        self.assertNotEqual(perm_index_c("[]"), perm_index_c("]["))

    def test_identity_pair_is_collision_free(self):
        # (substance, perm_index) eindeutig pro Token.
        a = (substance_c("=>"), perm_index_c("=>"))
        b = (substance_c(">="), perm_index_c(">="))
        self.assertNotEqual(a, b)

    def test_substance_greater_than_one_for_symbols(self):
        for tok in ["{", "}", "(", ")", "=>", "function", "import", ";"]:
            self.assertGreater(substance_c(tok), 1)

    def test_perm_space_at_least_one(self):
        self.assertGreaterEqual(perm_space_c("=>"), 2)
        self.assertEqual(perm_space_c("("), 1)

    def test_checksum_order_sensitive(self):
        self.assertNotEqual(checksum_c("=>"), checksum_c(">="))
        self.assertTrue(pointer_id_c("{").startswith("C_"))

    def test_unicode_fallback_deterministic(self):
        p1 = prime_for_char("λ")
        p2 = prime_for_char("λ")
        self.assertEqual(p1, p2)
        self.assertGreater(substance_c("λx"), 1)

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            substance_c("")
        with self.assertRaises(ValueError):
            perm_index_c("")


if __name__ == "__main__":
    unittest.main()
