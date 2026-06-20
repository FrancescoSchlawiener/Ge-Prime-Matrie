import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts import server_control


class TestServerControl(unittest.TestCase):
    def test_production_on_render(self):
        with patch.dict(os.environ, {"RENDER": "true"}, clear=False):
            self.assertTrue(server_control.is_production())

    def test_production_local_default(self):
        env = {k: v for k, v in os.environ.items() if k not in ("RENDER", "GE_PRIME_ENV")}
        with patch.dict(os.environ, env, clear=True):
            self.assertFalse(server_control.is_production())

    def test_default_host_production(self):
        with patch.dict(os.environ, {"RENDER": "true", "HOST": ""}, clear=False):
            self.assertEqual(server_control.default_host(), "0.0.0.0")

    def test_default_host_local(self):
        with patch.dict(os.environ, {"RENDER": "", "HOST": "", "GE_PRIME_ENV": ""}, clear=False):
            self.assertEqual(server_control.default_host(), "127.0.0.1")

    def test_prepare_skipped_in_production(self):
        with patch.dict(os.environ, {"RENDER": "true"}, clear=False):
            with patch.object(server_control, "stop_local_servers") as mock_stop:
                killed = server_control.prepare_local_port(5000)
        self.assertEqual(killed, [])
        mock_stop.assert_not_called()

    def test_decode_output_cp1252(self):
        raw = b"TCP 127.0.0.1:5000 LISTENING 1234 \x99"
        text = server_control._decode_output(raw)
        self.assertIn("LISTENING", text)
        self.assertIn("1234", text)

    def test_run_text_handles_empty(self):
        with patch.object(server_control, "subprocess") as mock_sub:
            mock_sub.run.return_value = type("R", (), {"stdout": None, "returncode": 0})()
            self.assertEqual(server_control._run_text(["netstat", "-ano"]), "")

    def test_is_ge_prime_server_detects_run_server(self):
        with patch.object(
            server_control,
            "_command_line",
            return_value=r"C:\python.exe scripts\run_server.py",
        ):
            self.assertTrue(server_control.is_ge_prime_server(9999))


if __name__ == "__main__":
    unittest.main()
