"""Ringside face selection (?face=<name>) and the Den face's data contract.

Faces are explicit-opt-in alternates to stock Ringside: stock serves at /,
a face only when the query names it, unknown/invalid names 404 (never a
silent fallback), and a face file's mere presence changes nothing.
The Den contract test locks the face to fields the real API fixtures carry.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
os.environ.setdefault("RINGER_NO_SELF_UPDATE", "1")

import ringer  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def get(port: int, path: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8", errors="replace")


class FaceSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.server = ringer.PersistentHudServer(
            state_dir=Path(cls.tmp.name), preferred_port=8931, open_viewer=False
        )
        cls.port = cls.server.start_background()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        cls.tmp.cleanup()

    def test_stock_is_default(self):
        status, body = get(self.port, "/")
        self.assertEqual(status, 200)
        self.assertIn("Ringside", body)

    def test_den_face_served_on_explicit_selection(self):
        status, body = get(self.port, "/?face=den")
        self.assertEqual(status, 200)
        self.assertIn("TIAMAT", body)
        self.assertNotIn("Ringside</title>", body)

    def test_unknown_face_is_a_loud_404(self):
        status, body = get(self.port, "/?face=nope")
        self.assertEqual(status, 404)
        self.assertIn("unknown face", body)

    def test_traversal_and_junk_names_rejected(self):
        for name in ("..%2F..%2Fetc", "a.b", "A", "x" * 40, "-lead"):
            status, _ = get(self.port, f"/?face={name}")
            self.assertEqual(status, 404, name)

    def test_face_name_regex_is_strict(self):
        ok = ringer.RINGSIDE_FACE_NAME_RE.fullmatch
        self.assertTrue(ok("den"))
        self.assertTrue(ok("den-2"))
        for bad in ("", ".", "..", "a/b", "a\\b", "A", "a" * 33, "-x", "a.html"):
            self.assertIsNone(ok(bad), bad)


class DenContractTest(unittest.TestCase):
    """The Den renders only fields the real API responses carry (honest data)."""

    @classmethod
    def setUpClass(cls):
        cls.den = (REPO / "dashboard" / "faces" / "den.html").read_text(encoding="utf-8")

    def test_self_contained(self):
        for marker in ('src="http', "src='http", 'href="http', "href='http",
                       "@import", "fonts.googleapis", "cdn."):
            self.assertNotIn(marker, self.den, marker)

    def test_run_fields_exist_in_fixture_and_face(self):
        payload = json.loads((FIXTURES / "api_runs.json").read_text())
        run = payload["runs"][0]
        task = run["tasks"][0]
        for field in ("run_name", "run_id", "state", "pass", "fail", "tokens",
                      "elapsed_s", "identity", "report_path", "live_path"):
            self.assertIn(field, run, field)
            self.assertIn(field, self.den, field)
        for field in ("key", "engine", "model", "status", "attempts",
                      "tokens", "elapsed_s", "verified"):
            self.assertIn(field, task, field)
            self.assertIn(field, self.den, field)

    def test_model_fields_exist_in_fixture_and_face(self):
        payload = json.loads((FIXTURES / "api_models.json").read_text())
        group = payload["groups"][0]
        for field in ("harness", "identity_key", "lab", "attempts",
                      "first_try_pass_rate", "median_tokens", "median_duration_ms"):
            self.assertIn(field, group, field)
            self.assertIn(field, self.den, field)


if __name__ == "__main__":
    unittest.main()
