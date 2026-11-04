"""Offline, synthetic adversarial fixtures; no production refs are changed."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools import held_integration_preflight as preflight


class GitFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="trek-held-git-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Synthetic Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.write("README.md", "Accepted fixture baseline\n")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture base")
        self.base = self.sha()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True,
                              text=True, check=True).stdout.strip()

    def sha(self):
        return self.git("rev-parse", "HEAD")

    def write(self, filename, content):
        target = self.root / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def draft(self, name, filename, content):
        self.git("checkout", "-q", "-b", name, self.base)
        self.write(filename, content)
        self.git("add", ".")
        self.git("commit", "-qm", name)
        head = self.sha()
        self.git("checkout", "-q", "main")
        return head

    def plan(self, candidate, drafts, selected, mode="review"):
        return {"base_head": self.base, "candidate_head": candidate, "mode": mode,
                "selected": selected, "drafts": drafts}

    @staticmethod
    def codes(result):
        return {row["code"] for row in result["blockers"]}

    def test_doc_only_reference_is_not_implicit_integration(self):
        doc = self.draft("director", "proposals/director/HELD.md", "PR #11 and #12 are drafts\n")
        result = preflight.evaluate(self.root, self.plan(doc, [{"id": "director", "head": doc, "depends_on": []}], ["director"]))
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["selected"][0]["integration"], "ANCESTOR")

    def test_independent_draft_not_in_candidate_is_blocked(self):
        head = self.draft("source", "proposals/research/literature/s1.json", "{}\n")
        result = preflight.evaluate(self.root, self.plan(self.base, [{"id": "source", "head": head, "depends_on": []}], ["source"]))
        self.assertIn("DRAFT_NOT_IN_CANDIDATE", self.codes(result))

    def test_missing_declared_dependency_is_blocked(self):
        first = self.draft("first", "proposals/research/literature/a.json", "{}\n")
        second = self.draft("second", "proposals/research/literature/b.json", "{}\n")
        drafts = [{"id": "first", "head": first, "depends_on": []},
                  {"id": "second", "head": second, "depends_on": ["first"]}]
        result = preflight.evaluate(self.root, self.plan(second, drafts, ["second"]))
        self.assertIn("MISSING_DRAFT_DEPENDENCY", self.codes(result))

    def test_dependency_already_in_accepted_base_needs_no_reselection(self):
        first = self.draft("accepted", "proposals/a.json", "{}\n")
        self.git("merge", "-q", "--ff-only", "accepted")
        self.base = self.sha()
        second = self.draft("successor", "proposals/b.json", "{}\n")
        drafts = [{"id": "accepted", "head": first, "depends_on": []},
                  {"id": "successor", "head": second, "depends_on": ["accepted"]}]
        result = preflight.evaluate(self.root, self.plan(second, drafts, ["successor"]))
        self.assertNotIn("MISSING_DRAFT_DEPENDENCY", self.codes(result))

    def test_independent_conflicting_public_file_edits_are_blocked(self):
        one = self.draft("one", "explorer/app.js", "const one=true;\n")
        two = self.draft("two", "explorer/app.js", "const two=true;\n")
        drafts = [{"id": "one", "head": one, "depends_on": []},
                  {"id": "two", "head": two, "depends_on": []}]
        result = preflight.evaluate(self.root, self.plan(one, drafts, ["one", "two"]))
        self.assertIn("DRAFT_PATH_COLLISION", self.codes(result))

    def test_original_proposal_only_does_not_fake_public_release(self):
        head = self.draft("lit", "proposals/research/literature/batch.json", "{\"status\":\"HELD\"}\n")
        result = preflight.evaluate(self.root, self.plan(head, [{"id": "lit", "head": head, "depends_on": []}], ["lit"], "production"))
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["public_changed_paths"], [])

    def test_artwork_raster_release_requires_rights_review(self):
        head = self.draft("art", "explorer/licensed-artwork/cover.png", "synthetic not actually image\n")
        result = preflight.evaluate(self.root, self.plan(head, [{"id": "art", "head": head, "depends_on": []}], ["art"], "production"))
        self.assertIn("ARTWORK_RIGHTS_GATE", self.codes(result))

    def test_held_episode_or_literature_public_semantic_projection_blocked(self):
        for lane,filename in (("episode", "explorer/episode-synopses.json"),
                              ("literature", "explorer/lit-publisher-leads.json")):
            with self.subTest(lane=lane):
                head = self.draft(lane, filename, "{\"claimed\":\"accepted\"}\n")
                result = preflight.evaluate(self.root, self.plan(head, [{"id": lane, "head": head, "depends_on": []}], [lane], "production"))
                self.assertIn("SEMANTIC_PROJECTION_REVIEW_REQUIRED", self.codes(result))

    def test_unnamed_public_json_cannot_evade_semantic_gate(self):
        head = self.draft("unknown", "explorer/random.json", "{\"work_count\":999}\n")
        result = preflight.evaluate(self.root, self.plan(head, [{"id": "unknown", "head": head, "depends_on": []}], ["unknown"], "production"))
        self.assertIn("SEMANTIC_PROJECTION_REVIEW_REQUIRED", self.codes(result))

    def test_cyclic_draft_dependencies_do_not_qualify(self):
        first = self.draft("cycleA", "proposals/a.json", "{}\n")
        second = self.draft("cycleB", "proposals/b.json", "{}\n")
        plan = self.plan(first, [{"id": "a", "head": first, "depends_on": ["b"]},
                                 {"id": "b", "head": second, "depends_on": ["a"]}], ["a", "b"])
        result = preflight.evaluate(self.root, plan)
        self.assertIn("DRAFT_DEPENDENCY_CYCLE", self.codes(result))

    def test_identical_changes_from_independent_drafts_do_not_conflict(self):
        first = self.draft("sameA", "proposals/a.txt", "exact content\n")
        second = self.draft("sameB", "proposals/a.txt", "exact content\n")
        result = preflight.evaluate(self.root, self.plan(first,
            [{"id": "a", "head": first, "depends_on": []},
             {"id": "b", "head": second, "depends_on": []}], ["a", "b"]))
        self.assertNotIn("DRAFT_PATH_COLLISION", self.codes(result))
        self.assertNotIn("DRAFT_NOT_IN_CANDIDATE", self.codes(result))

    def test_missing_or_unpinned_commit_fails_closed(self):
        result = preflight.evaluate(self.root, self.plan("0" * 40, [], []))
        self.assertIn("UNKNOWN_CANDIDATE_HEAD", self.codes(result))
        with self.assertRaises(ValueError):
            preflight.evaluate(self.root, {**self.plan(self.base, [], []), "base_head": "main"})

    def test_untrusted_unhashable_dependency_is_validation_error(self):
        with self.assertRaisesRegex(ValueError, "depends_on"):
            preflight.evaluate(self.root, self.plan(self.base,
                [{"id": "draft", "head": self.base, "depends_on": [{"untrusted": "object"}]}], ["draft"]))


if __name__ == "__main__":
    unittest.main()
