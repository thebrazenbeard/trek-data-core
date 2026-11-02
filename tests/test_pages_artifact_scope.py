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

    def test_catalog_changes_redeploy_only_after_exact_regeneration(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('"registry/mission_catalog.json"', text)
        self.assertIn('"tools/build_explorer_index.py"', text)
        self.assertIn('"registry/approved_projection_hashes.json"', text)
        self.assertIn("python3 tools/build_explorer_index.py", text)
        self.assertIn('cmp "${RUNNER_TEMP}/trek-index-expected.json" explorer/index.json', text)

    def test_deployment_gates_on_behavior_and_exact_allowlist(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("persist-credentials: false", text)
        self.assertIn("node tests/test_explorer.mjs", text)
        self.assertIn("python3 -m unittest discover", text)
        self.assertIn("! -path explorer/app.js", text)
        self.assertIn("! -path explorer/app.css", text)
        self.assertIn("Refusing to publish an unexpected Explorer file", text)

    def test_manual_dispatch_cannot_deploy_a_review_branch(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("if: github.ref == 'refs/heads/main'", text)

    def test_pages_can_land_first_without_publishing_missing_explorer(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("id: readiness", text)
        self.assertIn("ready=false", text)
        self.assertIn("skipping Pages publication", text)
        self.assertEqual(text.count("if: steps.readiness.outputs.ready == 'true'"), 6)


if __name__ == "__main__":
    unittest.main()
