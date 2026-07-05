import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ge_prime.config import APP_VERSION, REQUIRED_API_ROUTES
from scripts import run_server
from web.app import app


class TestRunServerPreflight(unittest.TestCase):
    def test_verify_ui_files_accepts_jinja_build_tag(self):
        run_server._verify_ui_files()

    def test_verify_ui_cli_flag(self):
        import subprocess

        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "run_server.py"), "--verify-ui"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("[OK] UI:", result.stdout)

    def test_required_api_routes_registered(self):
        rules = {r.rule for r in app.url_map.iter_rules()}
        for route in REQUIRED_API_ROUTES:
            self.assertIn(route, rules, route)

    def test_verify_api_health(self):
        from db.repository import WordRepository

        run_server._verify_api_health(WordRepository())

    def test_app_version_in_rendered_homepage(self):
        with app.test_client() as client:
            html = client.get("/").data.decode("utf-8")
        self.assertIn(APP_VERSION, html)


if __name__ == "__main__":
    unittest.main()
