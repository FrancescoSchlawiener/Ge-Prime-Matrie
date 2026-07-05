import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from preparation import prepare_substrate


class TestPreparation(unittest.TestCase):
    def test_umlaut(self):
        self.assertEqual(prepare_substrate("Straße"), "STRAßE")

    def test_default_roman(self):
        self.assertEqual(prepare_substrate("HALLO"), "HALLO")

    def test_eszett_not_expanded_to_ss(self):
        self.assertEqual(prepare_substrate("Straße"), "STRAßE")
        self.assertEqual(prepare_substrate("Strasse"), "STRASSE")
        self.assertNotEqual(prepare_substrate("Straße"), prepare_substrate("Strasse"))

    def test_capital_eszett_normalized(self):
        self.assertEqual(prepare_substrate("ẞpaß"), "ßPAß")

    def test_größe_umlaut_and_eszett(self):
        self.assertEqual(prepare_substrate("Größe"), "GROEßE")


if __name__ == "__main__":
    unittest.main()
