"""v7 read compat (best-effort)."""

import unittest

from analysis.binary.compat import VERSION_V7, read_gpm_any
from analysis.binary.format import GpmFormatError


class TestReadV7Compat(unittest.TestCase):
    def test_invalid_blob_raises(self):
        with self.assertRaises(GpmFormatError):
            read_gpm_any(b"GPM" + bytes([VERSION_V7]) + b"\x00" * 20)


if __name__ == "__main__":
    unittest.main()
