"""Source-only safety checks for the public Pages artifact boundary."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "static.yml"


class PagesArtifactScopeTests(unittest.TestCase):
    def test_artifact_is_only_the_explorer_directory(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("path: explorer", text)
        self.assertNotIn("path: '.'", text)
        self.assertNotIn('path: "."', text)

    def test_requires_index_and_entrypoint(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("test -f explorer/index.html", text)
        self.assertIn("test -f explorer/index.json", text)

    def test_drops_unfinished_template_steps(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertNotIn("actions/cache@", text)
        self.assertNotIn("actions/setup-dotnet@", text)
        self.assertIn("actions/upload-pages-artifact@v4", text)


if __name__ == "__main__":
    unittest.main()
