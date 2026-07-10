"""C(I) decode_ci Roundtrip."""

import unittest

from gpm_types.ci.substance import decode_ci, perm_index_c, substance_c


class TestCiDecode(unittest.TestCase):
    def test_short_operators_roundtrip(self):
        for token in ("=>", ">=", "[]", "function", "(", ")", "++", "==="):
            with self.subTest(token=token):
                s = substance_c(token)
                i = perm_index_c(token)
                self.assertEqual(decode_ci(s, i), token)

    def test_checksum_mode_not_decodable(self):
        from gpm_types.ci.registry import checksum_c

        long_token = "a" * 20
        s = substance_c(long_token)
        i = checksum_c(long_token)
        with self.assertRaises(ValueError):
            decode_ci(s, i)


if __name__ == "__main__":
    unittest.main()
