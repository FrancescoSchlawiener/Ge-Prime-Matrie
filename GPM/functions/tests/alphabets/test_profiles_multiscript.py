"""Shared alphabet profile tests."""

from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphabets.lex import lex_order_for_profile
from alphabets.normalize import prepare_substrate
from alphabets.profiles import AlphabetProfile
from gpm_types.si.codec import decode_si, encode_si
from gpm_types.si.substance import substance_for_profile
from perm.lut import get_permutation_lut, lut_index_of_sequence
from perm.multiset import perm_decode, perm_index


def _profile_test(
    cls: type[unittest.TestCase],
    profile: AlphabetProfile,
    raw: str,
    expected_size: int,
    freq_desc_first: str,
) -> None:
    def test_map_size(self: unittest.TestCase) -> None:
        from alphabets.registry import prime_map_for_profile

        self.assertEqual(len(prime_map_for_profile(profile)), expected_size)

    def test_lex_most_frequent_bottom(self: unittest.TestCase) -> None:
        lex = lex_order_for_profile(profile)
        self.assertEqual(lex[-1], freq_desc_first)

    def test_substance(self: unittest.TestCase) -> None:
        seq = prepare_substrate(raw, profile)
        s = substance_for_profile(seq, profile)
        self.assertGreater(s, 1)

    def test_perm_roundtrip(self: unittest.TestCase) -> None:
        seq = prepare_substrate(raw, profile)
        lex = lex_order_for_profile(profile)
        counts = Counter(seq)
        idx = perm_index(list(seq), counts, lex_order=lex)
        decoded = "".join(perm_decode(counts, idx, lex_order=lex))
        self.assertEqual(decoded, seq)

    def test_encode_decode_roundtrip(self: unittest.TestCase) -> None:
        s, idx = encode_si(raw, profile)
        self.assertEqual(decode_si(s, idx, profile), prepare_substrate(raw, profile))

    def test_lut_matches_perm_index(self: unittest.TestCase) -> None:
        seq = prepare_substrate(raw, profile)
        if len(seq) > 12:
            return
        lut = get_permutation_lut(Counter(seq), profile)
        lex = lex_order_for_profile(profile)
        expected = perm_index(list(seq), Counter(seq), lex_order=lex)
        self.assertEqual(lut_index_of_sequence(lut, seq), expected)

    setattr(cls, f"test_{profile.value}_map_size", test_map_size)
    setattr(cls, f"test_{profile.value}_lex_bottom", test_lex_most_frequent_bottom)
    setattr(cls, f"test_{profile.value}_substance", test_substance)
    setattr(cls, f"test_{profile.value}_perm_roundtrip", test_perm_roundtrip)
    setattr(cls, f"test_{profile.value}_encode_decode", test_encode_decode_roundtrip)
    setattr(cls, f"test_{profile.value}_lut", test_lut_matches_perm_index)


class TestArabic(unittest.TestCase):
    pass


_profile_test(TestArabic, AlphabetProfile.ARABIC, "مرحبا", 28, "ا")


class TestHebrew(unittest.TestCase):
    pass


_profile_test(TestHebrew, AlphabetProfile.HEBREW, "שלום", 22, "י")


class TestDevanagari(unittest.TestCase):
    pass


_profile_test(TestDevanagari, AlphabetProfile.DEVANAGARI, "कमल", 46, "क")


class TestThai(unittest.TestCase):
    pass


_profile_test(TestThai, AlphabetProfile.THAI, "กขคง", 48, "า")


class TestHangul(unittest.TestCase):
    pass


_profile_test(TestHangul, AlphabetProfile.HANGUL, "안녕", 51, "ᄋ")


class TestHiragana(unittest.TestCase):
    pass


_profile_test(TestHiragana, AlphabetProfile.HIRAGANA, "こんにちは", 46, "の")


class TestKatakana(unittest.TestCase):
    pass


_profile_test(TestKatakana, AlphabetProfile.KATAKANA, "コンニチハ", 46, "ア")


class TestArmenian(unittest.TestCase):
    pass


_profile_test(TestArmenian, AlphabetProfile.ARMENIAN, "բարև", 38, "Ա")


class TestGeorgian(unittest.TestCase):
    pass


_profile_test(TestGeorgian, AlphabetProfile.GEORGIAN, "გამარჯობა", 33, "ა")


class TestGurmukhi(unittest.TestCase):
    pass


_profile_test(TestGurmukhi, AlphabetProfile.GURMUKHI, "ਪੰਜਾਬ", 35, "ਕ")


class TestTamilProfile(unittest.TestCase):
    pass


_profile_test(TestTamilProfile, AlphabetProfile.TAMIL, "கமல", 30, "க")


class TestAmharic(unittest.TestCase):
    pass


_profile_test(TestAmharic, AlphabetProfile.AMHARIC, "ሰላም", 34, "አ")


class TestCoptic(unittest.TestCase):
    pass


_profile_test(TestCoptic, AlphabetProfile.COPTIC, "ⲁⲛⲟⲕ", 32, "Ⲁ")


class TestRunic(unittest.TestCase):
    pass


_profile_test(TestRunic, AlphabetProfile.RUNIC, "ᚠᚢᚦᚨᚱ", 24, "ᚦ")


class TestPhoenician(unittest.TestCase):
    pass


_profile_test(
    TestPhoenician,
    AlphabetProfile.PHOENICIAN,
    "\U00010901\U00010913\U00010914",
    22,
    "\U0001090D",
)


class TestUgaritic(unittest.TestCase):
    pass


_profile_test(
    TestUgaritic,
    AlphabetProfile.UGARITIC,
    "\U00010381\U00010393\U00010394",
    30,
    "\U00010393",
)


class TestOgham(unittest.TestCase):
    pass


_profile_test(TestOgham, AlphabetProfile.OGHAM, "\u1694\u1693\u1690", 20, "\u1694")


class TestGlagolitic(unittest.TestCase):
    pass


_profile_test(TestGlagolitic, AlphabetProfile.GLAGOLITIC, "\u2C00\u2C01\u2C02", 41, "\u2C00")


class TestGothic(unittest.TestCase):
    pass


_profile_test(
    TestGothic,
    AlphabetProfile.GOTHIC,
    "\U00010331\U00010342\U00010343",
    27,
    "\U00010330",
)


class TestMongolian(unittest.TestCase):
    pass


_profile_test(
    TestMongolian,
    AlphabetProfile.MONGOLIAN,
    "\u1820\u1821\u1828",
    35,
    "\u1820",
)


class TestThaana(unittest.TestCase):
    pass


_profile_test(
    TestThaana,
    AlphabetProfile.THAANA,
    "\u0787\u0788\u0789",
    24,
    "\u0797",
)


class TestTifinagh(unittest.TestCase):
    pass


_profile_test(
    TestTifinagh,
    AlphabetProfile.TIFINAGH,
    "\u2D30\u2D54\u2D5C",
    33,
    "\u2D5C",
)


class TestBengali(unittest.TestCase):
    pass


_profile_test(TestBengali, AlphabetProfile.BENGALI, "বাংলা", 35, "ষ")


class TestTelugu(unittest.TestCase):
    pass


_profile_test(TestTelugu, AlphabetProfile.TELUGU, "తెలుగు", 35, "క")


class TestJavaneseProfile(unittest.TestCase):
    pass


_profile_test(
    TestJavaneseProfile,
    AlphabetProfile.JAVANESE,
    "\uA992\uA993\uA994",
    20,
    "\uA992",
)


class TestOldPersian(unittest.TestCase):
    pass


_profile_test(
    TestOldPersian,
    AlphabetProfile.OLD_PERSIAN,
    "\U000103A0\U000103A1\U000103A2",
    36,
    "\U000103A0",
)


class TestAestheticHieroglyphs(unittest.TestCase):
    pass


_profile_test(
    TestAestheticHieroglyphs,
    AlphabetProfile.AESTHETIC_HIEROGLYPHS,
    "\U00013196\U0001308B\U0001313F",
    24,
    "\U00013196",
)


class TestOldItalic(unittest.TestCase):
    pass


_profile_test(
    TestOldItalic,
    AlphabetProfile.OLD_ITALIC,
    "\U00010300\U00010301\U00010302",
    26,
    "\U00010300",
)


class TestOldTurkic(unittest.TestCase):
    pass


_profile_test(
    TestOldTurkic,
    AlphabetProfile.OLD_TURKIC,
    "\U00010C00\U00010C01\U00010C02",
    38,
    "\U00010C00",
)


class TestOg(unittest.TestCase):
    pass


_profile_test(TestOg, AlphabetProfile.OG, "HALLO", 27, "ß")


class TestRomanProfile(unittest.TestCase):
    pass


_profile_test(TestRomanProfile, AlphabetProfile.ROMAN, "HALLO", 27, "E")


class TestGreekProfile(unittest.TestCase):
    pass


_profile_test(TestGreekProfile, AlphabetProfile.GREEK, "ΑΘΗΝΑ", 24, "Α")


class TestCyrillicProfile(unittest.TestCase):
    pass


_profile_test(TestCyrillicProfile, AlphabetProfile.CYRILLIC, "ЁЖИК", 33, "О")


class TestGreekExtended(unittest.TestCase):
    def test_encode_decode(self) -> None:
        s, idx = encode_si("ΑΘΗΝΑ", AlphabetProfile.GREEK)
        self.assertEqual(decode_si(s, idx, AlphabetProfile.GREEK), "ΑΘΗΝΑ")


class TestCyrillicExtended(unittest.TestCase):
    def test_encode_decode_with_yo(self) -> None:
        s, idx = encode_si("ЁЖИК", AlphabetProfile.CYRILLIC)
        self.assertEqual(decode_si(s, idx, AlphabetProfile.CYRILLIC), "ЁЖИК")


if __name__ == "__main__":
    unittest.main()
