"""Keep reviewed candidate-only inventory gates connected to Core Validation.

These are explicit, reviewed paths. Do not discover and execute every
``proposals/**/validate.py``: proposals are untrusted until individually
reviewed, and a new file must not silently become executable CI code.
"""

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
REVIEWED_COMMANDS = (
    "python proposals/librarian/artwork-sourcing-wave2-20261103/validate.py",
    "python proposals/films/afi-theatrical-release-20261103/validate.py",
    "python proposals/librarian/picard-companion-editions-20261103/validate.py --check",
)


class ReviewedCandidateCITest(unittest.TestCase):
    def test_explicit_candidate_validator_gate(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("- name: Validate explicitly reviewed candidate proposals", workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_*.py' -v", workflow)
        for command in REVIEWED_COMMANDS:
            with self.subTest(command=command):
                self.assertEqual(workflow.count(command), 1, "missing or duplicated reviewed validator")
                script = command.split()[1]
                self.assertTrue((ROOT / script).is_file(), "reviewed validator missing from repository")
        self.assertNotIn("proposals/**/validate.py", workflow)

    def test_reviewed_validators_do_not_use_optimizable_assertions(self):
        # ``python -O`` removes assert statements. Rights and admission gates
        # must not depend on a check that can disappear at runtime.
        for command in REVIEWED_COMMANDS:
            with self.subTest(command=command):
                script = ROOT / command.split()[1]
                tree = ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
                self.assertFalse(
                    any(isinstance(node, ast.Assert) for node in ast.walk(tree)),
                    "reviewed validation gates must use explicit exceptions, not assert",
                )


if __name__ == "__main__":
    unittest.main()
