"""Guard immutable third-party Action revisions in validation workflows.

The allowlist is independently checked against the upstream GitHub tag refs.
Updating an Action deliberately requires reviewing and updating this list.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".github" / "workflows" / "workspace-startup-safety.yml",
)
REVIEWED_ACTIONS = {
    "actions/checkout": "11d5960a326750d5838078e36cf38b85af677262",
    "actions/setup-python": "a26af69be951a213d495a4c3e4e4022e16d87065",
}
USE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)


class CIActionPinTests(unittest.TestCase):
    def test_each_action_has_a_reviewed_immutable_revision(self):
        for path in WORKFLOWS:
            with self.subTest(workflow=path.name):
                text = path.read_text(encoding="utf-8")
                actions = USE.findall(text)
                self.assertTrue(actions, "workflow lost all external Action references")
                for use in actions:
                    with self.subTest(workflow=path.name, action=use):
                        self.assertIn("@", use)
                        name, revision = use.rsplit("@", 1)
                        self.assertIn(name, REVIEWED_ACTIONS, "unreviewed third-party Action")
                        self.assertEqual(revision, REVIEWED_ACTIONS[name])
                        self.assertRegex(revision, r"\A[0-9a-f]{40}\Z")

    def test_checkout_persists_no_repository_credentials(self):
        for path in WORKFLOWS:
            with self.subTest(workflow=path.name):
                text = path.read_text(encoding="utf-8")
                checkout = re.search(
                    r"(?m)^[ \t]*(?:-[ \t]+)?uses:[ \t]*actions/checkout@[^\n]*\n"
                    r"(?P<arguments>(?:[ \t]{8,}[^\n]*\n)*)",
                    text,
                )
                self.assertIsNotNone(checkout, "checkout step missing")
                self.assertRegex(checkout.group("arguments"), r"persist-credentials:\s*false")

    def test_workflows_have_read_only_token(self):
        for path in WORKFLOWS:
            with self.subTest(workflow=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertRegex(text, r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$")


if __name__ == "__main__":
    unittest.main()
