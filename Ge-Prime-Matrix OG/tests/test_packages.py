import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import db
import ge_prime
import gpm
from ge_prime.config import REQUIRED_API_ROUTES
from ge_prime.encode import encode_word
from web.app import app

HANDLER_MODULES = (
    "web.handlers.system",
    "web.handlers.encode",
    "web.handlers.decode",
    "web.handlers.compare",
    "web.handlers.diff",
    "web.handlers.icurve",
    "web.handlers.cipher",
    "web.handlers.gpm",
    "web.handlers.size",
)

LEGACY_ROOT_SHIMS = (
    "ge_prime_config",
    "ge_prime_core",
    "ge_prime_encode",
    "ge_prime_decode",
    "ge_prime_compare",
    "ge_prime_diff",
    "ge_prime_cipher",
    "ge_prime_i_curve",
    "ge_prime_meta_genome",
)


class TestPackageExports(unittest.TestCase):
    def test_ge_prime_lazy_exports(self):
        self.assertEqual(ge_prime.APP_VERSION, "2026.06-gpm-v49")
        self.assertEqual(ge_prime.GPM_VERSION, 7)
        self.assertTrue(callable(ge_prime.encode_word))
        self.assertTrue(callable(ge_prime.compare_substances))
        self.assertTrue(callable(ge_prime.analyze_pair))
        self.assertTrue(callable(ge_prime.db_path))

    def test_no_legacy_root_shim_modules(self):
        for name in LEGACY_ROOT_SHIMS:
            self.assertFalse(
                (ROOT / f"{name}.py").exists(),
                msg=f"Legacy-Shim {name}.py soll entfernt sein — ge_prime.* nutzen",
            )

    def test_handler_modules_expose_register(self):
        for name in HANDLER_MODULES:
            mod = importlib.import_module(name)
            self.assertTrue(callable(getattr(mod, "register", None)), name)

    def test_required_api_routes_registered(self):
        rules = {r.rule for r in app.url_map.iter_rules()}
        for route in REQUIRED_API_ROUTES:
            self.assertIn(route, rules, route)

    def test_gpm_public_byte_helpers(self):
        self.assertTrue(callable(gpm.genome_payload_bytes))
        self.assertTrue(callable(gpm.body_payload_bytes))

    def test_linguistics_exports(self):
        from ge_prime.linguistics import (
            classify_domain,
            classify_language,
            infer_text_language_code,
            register_domain,
            register_language,
            resolve_linguistics_repo,
        )

        self.assertTrue(callable(classify_language))
        self.assertTrue(callable(infer_text_language_code))
        self.assertTrue(callable(classify_domain))
        self.assertTrue(callable(register_language))
        self.assertTrue(callable(register_domain))
        self.assertTrue(callable(resolve_linguistics_repo))

    def test_gpm_lazy_exports(self):
        self.assertTrue(callable(gpm.compile_text))
        self.assertTrue(callable(gpm.read_gpm))
        self.assertTrue(callable(gpm.reconstruct_text))
        self.assertTrue(callable(gpm.search_by_gcd))
        self.assertTrue(callable(gpm.search_by_lcm))

        substance, perm_index = encode_word("TEST")
        blob = gpm.write_gpm(
            gpm.GpmDocument(
                header=[
                    gpm.GpmHeaderEntry(0, "test", "TEST", substance),
                ],
                tokens=[gpm.GpmToken(0, perm_index, 0)],
                gaps=["", ""],
                explicit=[],
            )
        )
        doc = gpm.read_gpm(blob)
        self.assertEqual(blob[:4], b"GPM\x07")
        self.assertEqual(gpm.reconstruct_text(doc), "test")

        s_mut, pi_mut = encode_word("MUT")
        s_wut, pi_wut = encode_word("WUT")
        s_mutwut, pi_mutwut = encode_word("MUTWUT")
        lcm_blob = gpm.write_gpm(
            gpm.GpmDocument(
                header=[
                    gpm.GpmHeaderEntry(0, "mut", "MUT", s_mut),
                    gpm.GpmHeaderEntry(1, "wut", "WUT", s_wut),
                    gpm.GpmHeaderEntry(2, "mutwut", "MUTWUT", s_mutwut),
                ],
                tokens=[
                    gpm.GpmToken(2, pi_mutwut, 0),
                    gpm.GpmToken(0, pi_mut, 0),
                    gpm.GpmToken(1, pi_wut, 0),
                ],
                gaps=["", "", "", ""],
                explicit=[],
            )
        )
        lcm_doc = gpm.read_gpm(lcm_blob)
        lcm_result = gpm.search_by_lcm(lcm_doc, "MUT", "WUT")
        originals = {m["original"] for m in lcm_result["matches"]}
        self.assertIn("mutwut", originals)
        self.assertNotIn("mut", originals)
        self.assertTrue(all(m["covers_lcm"] for m in lcm_result["matches"]))

    def test_db_lazy_exports(self):
        self.assertTrue(callable(db.resolve_language))
        self.assertTrue(callable(db.default_db_path))
        self.assertEqual(db.language_label("random"), "Random / unsortiert")
        repo = db.WordRepository()
        self.assertTrue(callable(repo.init_db))

    def test_single_canonical_db_path(self):
        from db.paths import default_db_path
        from ge_prime.config import db_path

        self.assertEqual(db_path(), default_db_path())
        self.assertEqual(default_db_path().name, "ge_prime.db")
        self.assertEqual(default_db_path().parent.name, "data")

    def test_scraper_modules_use_canonical_db(self):
        """Regression: kein separates gpm_words.db in Scraper-Skripten."""
        root = Path(__file__).resolve().parent.parent
        for rel in ("scrapers/__main__.py", "scrape.py"):
            text = (root / rel).read_text(encoding="utf-8")
            self.assertNotIn("gpm_words.db", text, msg=f"{rel} darf gpm_words.db nicht hardcoden")
        main_src = (root / "scrapers/__main__.py").read_text(encoding="utf-8")
        self.assertIn("WordRepository()", main_src)

    def test_scrapers_package_imports(self):
        import scrapers

        self.assertIn("spanish", scrapers.ROMANCE_SCRAPERS)
        self.assertTrue(callable(scrapers.ROMANCE_SCRAPERS["spanish"]))
        self.assertIn("spanish", scrapers.ROMANCE_SOURCE_NAMES)
        self.assertIn("hunspell_fur", scrapers.ROMANCE_SCRAPERS)


if __name__ == "__main__":
    unittest.main()
