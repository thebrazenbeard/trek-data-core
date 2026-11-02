"""Prevent release workflows from skipping Explorer keyboard navigation checks."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ExplorerCiCoverageTests(unittest.TestCase):
    def test_both_ci_and_pages_gate_explorer_accessibility(self):
        for workflow in ("ci.yml", "static.yml"):
            with self.subTest(workflow=workflow):
                text = (ROOT / ".github" / "workflows" / workflow).read_text(encoding="utf-8")
                self.assertIn("node tests/test_explorer.mjs", text)
                self.assertIn("node tests/test_explorer_accessibility.mjs", text)


if __name__ == "__main__":
    unittest.main()
