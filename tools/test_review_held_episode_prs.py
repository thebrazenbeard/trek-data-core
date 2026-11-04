"""Synthetic and optionally real-Git adversarial checks for offline PR reviews."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


FILE = Path(__file__).with_name("review_held_episode_prs.py")
SPEC = importlib.util.spec_from_file_location("held_pr_offline_review", FILE)
reviewer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = reviewer
SPEC.loader.exec_module(reviewer)


def descriptor(pr=538, profile="TNG", count=1):
    return {"pr": pr, "commit": "a" * 40, "path": "proposals/research/mock/records.json",
            "sha256": "b" * 64, "profile": profile, "expected_rows": count}


def tng():
    return {"coverage_effect": "NONE", "new_works": 0, "governed_research_admissions": 0,
            "publisher_family": "paramount_corporate_publisher_family",
            "data_status": "HELD_TNG_S2_FIRST_FIVE_PUBLISHER_DESCRIPTION_OBSERVATIONS",
            "records": [{"source_local_row_id": "legacy:s2:tng:000", "title": "The Child",
                         "admission_effect": "NONE", "coverage_effect": "NONE", "global_work_identity": "UNRESOLVED",
                         "synopsis_publication_status": "PENDING_EDITORIAL_AND_SOURCE_REVIEW",
                         "evidence_frame": "PUBLISHER_DESCRIPTION_NOT_EPISODE_DEPICTION",
                         "source_custody": "NO_RAW_HTML_BYTES",
                         "original_editorial_paraphrase_held": "A publisher description makes a claim about Counselor Troi.",
                         "publisher_card": {"season": 2, "episode": 1, "raw_webpage_sha256": None,
                                            "guide_url": "https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/2/",
                                            "rendered_description_sha256": "c" * 64}}]}


def ds9():
    title = "The Search, Part 1"
    return {"proposal_only": True, "accepted_work_effect": "NONE", "accepted_source_binding_effect": "NONE",
            "episode_research_coverage_effect": "NONE", "synopsis_publication_effect": "NONE", "admitted_briefings": 0,
            "episode_census_claim": "NONE", "observed_card_count": 1, "missing_publisher_ordinals_in_extraction": [4, 26],
            "source": {"url": "https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/3/",
                       "raw_source_body_sha256": None, "raw_html_bytes_pinned": False,
                       "full_episode_audiovisual_or_script_read": False},
            "source_local_episode_slots": [{"id": "slot1", "season": 3, "source_episode_ordinal": 1,
                                           "publisher_title": title, "source_card_locator": "Season 3 > S3 E1",
                                           "source_description_sha256": "d" * 64, "work_ref": None,
                                           "work_binding_status": "UNRESOLVED"}],
            "local_entities": [{"id": "entity1", "slot_id": "slot1"}],
            "evidence": [{"id": "ev1", "local_entity_id": "entity1", "locator": "Season 3 > S3 E1",
                          "description_sha256": "d" * 64}],
            "assertions": [{"id": "assert1", "subject_local_entity_id": "entity1", "supporting_evidence_id": "ev1",
                            "status": "PROPOSED_SOURCE_LOCAL", "predicate": "PUBLISHER_GUIDE_DESCRIBES",
                            "fictional_truth_scope": "NOT_OBJECTIVELY_ASSERTED",
                            "original_held_paraphrase": "The publisher describes a journey into disputed space."}]}


class DraftEpisodeReviewTests(unittest.TestCase):
    def test_manifest_pins_eight_distinct_draft_heads(self):
        manifest = reviewer.read_manifest()
        self.assertEqual(len(manifest["sources"]), 8)
        self.assertEqual(sum(x["expected_rows"] for x in manifest["sources"]), 184)
        self.assertEqual({x["pr"] for x in manifest["sources"]}, {538, 551, 559, 554, 557, 560, 544, 558})
        self.assertEqual(manifest["admission_status"], "UNMERGED_PR_PROPOSALS_NOT_ACCEPTED_RESEARCH")

    def test_rejects_unsafe_git_path_and_nonsha_ref(self):
        example = descriptor()
        example["path"] = "../registry/authoritative/works.json"
        with self.assertRaisesRegex(ValueError, "unsafe proposal"):
            reviewer.validate_descriptor(example)
        example = descriptor()
        example["commit"] = "refs/heads/main"
        with self.assertRaisesRegex(ValueError, "invalid pinned commit"):
            reviewer.validate_descriptor(example)

    def test_blob_bytes_must_match_exact_sha_and_duplicate_keys_rejected(self):
        source = descriptor()
        with mock.patch.object(reviewer, "run_git", return_value=b'{}'):
            with self.assertRaisesRegex(ValueError, "pinned draft blob bytes changed"):
                reviewer.load_candidate(source)
        payload = b'{"records":[],"records":[]}'
        source["sha256"] = hashlib.sha256(payload).hexdigest()
        with mock.patch.object(reviewer, "run_git", return_value=payload):
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                reviewer.load_candidate(source)

    def test_tng_requires_held_original_publisher_frame(self):
        row = tng()
        result, gaps, anomalies = reviewer.parse_candidate(descriptor(), row)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["canonical_work_id"], None)
        self.assertEqual((gaps, anomalies), ([], []))
        row["records"][0]["synopsis_publication_status"] = "APPROVED"
        with self.assertRaisesRegex(ValueError, "identity hold promoted"):
            reviewer.parse_candidate(descriptor(), row)

    def test_ds9_keeps_extraction_gaps_and_does_not_forge_missing_slots(self):
        source = descriptor(pr=557, profile="DS9_S3_S4")
        rows, gaps, anomalies = reviewer.parse_candidate(source, ds9())
        self.assertEqual(len(rows), 1)
        self.assertEqual(gaps, [4, 26])
        self.assertEqual(anomalies, [])
        self.assertEqual(rows[0]["source_episode_ordinal"], 1)
        changed = ds9()
        changed["assertions"][0]["status"] = "ACCEPTED"
        with self.assertRaisesRegex(ValueError, "assertion promoted"):
            reviewer.parse_candidate(source, changed)
        changed = ds9()
        changed["evidence"][0]["description_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fingerprint misaligned"):
            reviewer.parse_candidate(source, changed)

    def test_held_text_private_output_refuses_repo_and_creates_mode_600(self):
        source = descriptor()
        note = reviewer.note(source, row_id="slot-a", series="TNG", season=2, ordinal=1,
                             title="The Child", synopsis="A publisher description of the episode card.",
                             guide="https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/2/",
                             locator="publisher S2 E1")
        with self.assertRaisesRegex(ValueError, "outside|inside or above"):
            reviewer.private_output(reviewer.REPO / "private-notes.json", [note], {})
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "held-review.json"
            receipt = reviewer.private_output(out, [note], {"status": "DRAFT_ONLY"})
            self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(), receipt)
            self.assertEqual(os.stat(out).st_mode & 0o777, 0o600)
            with self.assertRaisesRegex(ValueError, "requires new file"):
                reviewer.private_output(out, [note], {})

    def test_real_eight_draft_git_objects_if_fetched_locally(self):
        manifest = reviewer.read_manifest()
        available = all(subprocess.run(["git", "cat-file", "-e", f"{item['commit']}^{{commit}}"],
                                       cwd=reviewer.REPO, stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL).returncode == 0 for item in manifest["sources"])
        if not available:
            self.skipTest("exact unmerged draft commits not fetched locally; synthetic validation still runs")
        summary, cards = reviewer.review()
        self.assertEqual((len(cards), summary["held_paraphrase_count"], summary["withheld_identity_count"]),
                         (184, 183, 1))
        self.assertEqual(summary["by_series_observations"], {"DIS": 5, "DS9": 73, "ENT": 25,
                                                              "PIC": 10, "TNG": 48, "VOY": 23})
        self.assertEqual([x["missing_publisher_ordinals_in_extraction"] for x in summary["missing_extraction_ordinals"]],
                         [[4, 26], [2, 26]])
        self.assertEqual(len(summary["unresolved_description_alignment_hypotheses"]), 1)


if __name__ == "__main__":
    unittest.main()
