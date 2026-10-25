import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "opencode_usage.py"
SPEC = importlib.util.spec_from_file_location("opencode_usage", SCRIPT)
opencode_usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(opencode_usage)


class OpenCodeUsageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.state = self.root / "state.json"
        self.catalog = self.root / "models.json"
        self.database = self.root / "opencode.db"
        opencode_usage.STATE_FILE = self.state
        opencode_usage.MODEL_CACHE = self.catalog
        opencode_usage.DATABASE = self.database

    def tearDown(self):
        self.temp.cleanup()

    def write_fixture(self, favorites):
        self.state.write_text(json.dumps({"favorite": favorites}), encoding="utf-8")
        self.catalog.write_text(json.dumps({
            "openai": {"models": {"gpt-test": {"name": "GPT Test", "limit": {"context": 1000}}}},
        }), encoding="utf-8")
        with sqlite3.connect(self.database) as db:
            db.execute("CREATE TABLE message (data TEXT, time_created INTEGER)")
            db.execute("INSERT INTO message VALUES (?, ?)", (json.dumps({
                "role": "assistant",
                "providerID": "openai",
                "modelID": "gpt-test",
                "tokens": {"total": 420},
            }), 1))

    def test_returns_favorite_context_usage(self):
        self.write_fixture([{"providerID": "openai", "modelID": "gpt-test"}])

        result = opencode_usage.read_favorites()

        self.assertTrue(result["ok"])
        self.assertEqual(result["favorites"][0]["percent"], 42)
        self.assertEqual(result["favorites"][0]["bar"], "████░░░░░░")

    def test_empty_favorites_returns_empty_list(self):
        self.write_fixture([])

        self.assertEqual(opencode_usage.read_favorites(), {"ok": True, "favorites": []})


if __name__ == "__main__":
    unittest.main()
