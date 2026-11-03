"""A proposal is discoverable without becoming a published synopsis or Work."""

import copy
import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "pending_synopsis_frontier", ROOT / "tools" / "audit_pending_synopsis_release.py"
)
frontier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(frontier)


def valid_literary_receipt_fixture():
    packet = frontier.lit_request.build()
    expected = frontier._expected_review_rows(
        "literature", packet, frontier.scouts_first.read_pinned(), frontier.scouts_second.read_pinned()
    )
    request_digest = hashlib.sha256(frontier.lit_request._read(frontier.lit_request.OUTPUT)).hexdigest()
    good = {
        "schema_version": "1.0.0", "review_kind": "SEPARATE_MODEL_EDITORIAL_REVIEW",
        "review_result": "PASS_SOURCE_LABELED_PARAPHRASES_DISPLAY_ONLY",
        "reviewed_on_utc": "2026-11-03", "reviewer_agent": "independent-auditor",
        "provider": "OpenAI", "runtime": "native model review (self-reported)",
        "separate_author_review": True, "review_request_sha256": request_digest,
        "reviewed_entry_count": 18, "reviewed_entries": expected,
        "source_review_method": "RENDERED_FIRST_PARTY_DESCRIPTION_CHECK_NOT_FULL_WORK_READ",
        "material_qualifications": ["Internal model review only", "No complete book was read"],
        "source_work_effect": "NONE", "coverage_effect": "NONE",
        "artwork_effect": "NONE", "site_effect": "NONE",
    }
    return expected, request_digest, good


class PendingSynopsisFrontierTests(unittest.TestCase):
    def test_current_frontier_is_source_local_but_not_publicly_approved(self):
        result = frontier.report()
        self.assertEqual(result["data_status"], "PROPOSAL_RELEASE_HELD")
        self.assertEqual(result["accepted_display_overviews"], 37)
        self.assertEqual(result["accepted_display_overviews_by_medium"],
                         {"FILM": 14, "LITERATURE": 9, "SHORT_FORM": 14})
        self.assertEqual(result["accepted_directory_rows"], 1214)
        self.assertEqual(result["literature"]["source_local_candidates"], 18)
        self.assertEqual(result["literature"]["accepted_directory_matches"], 0)
        self.assertEqual(result["literature"]["source_upstream_families"], 1)
        self.assertIn("DIRECTORY_ROW_ACCEPTANCE_REQUIRED", result["literature"]["blockers"])
        self.assertIn("INDEPENDENT_EDITORIAL_RECEIPT_REQUIRED", result["literature"]["blockers"])
        self.assertEqual(result["scouts"]["source_description_observations"], 10)
        self.assertEqual(result["scouts"]["accepted_directory_matches"], 10)
        self.assertEqual(result["scouts"]["opened_source_pages"], 0)
        self.assertIn("FULL_SOURCE_PAGE_OBSERVATION_REQUIRED", result["scouts"]["blockers"])
        self.assertIn("INDEPENDENT_EDITORIAL_RECEIPT_REQUIRED", result["scouts"]["blockers"])
        for name in ("coverage_effect", "admission_effect", "public_release_effect", "artwork_effect"):
            self.assertEqual(result[name], "NONE")
        serialized = json.dumps(result)
        self.assertNotIn("original_paraphrase", serialized)
        self.assertNotIn("cover_candidate_locator", serialized)

    def test_stale_literary_editorial_request_refused(self):
        original = frontier.lit_request.build
        with mock.patch.object(frontier.lit_request, "build", side_effect=lambda: {
            **original(), "public_site_effect": "PUBLISHED"
        }):
            with self.assertRaises(frontier.FrontierError):
                frontier.report()

    def test_forged_editorial_receipt_never_self_approves(self):
        with mock.patch.object(frontier, "receipt_state", return_value="UNPINNED_REVIEW_CLAIM"):
            result = frontier.report()
        self.assertEqual(result["literature"]["editorial_receipt_state"], "UNPINNED_REVIEW_CLAIM")
        self.assertIn("INDEPENDENT_EDITORIAL_RECEIPT_REQUIRED", result["literature"]["blockers"])

    def test_future_review_receipt_must_bind_all_exact_source_and_text_hashes(self):
        expected, request_digest, good = valid_literary_receipt_fixture()
        frontier.validate_review_receipt("literature", good, expected, request_digest)
        changes = [
            lambda x: x.update(review_request_sha256="a" * 64),
            lambda x: x.update(reviewed_entry_count=17),
            lambda x: x["reviewed_entries"][0].update(paraphrase_sha256="f" * 64),
            lambda x: x["reviewed_entries"][0].update(source_locator="https://unrelated.invalid"),
            lambda x: x.update(source_work_effect="ACCEPTED"),
            lambda x: x.update(site_effect="PUBLISHED"),
            lambda x: x.update(reviewer_agent=""),
            lambda x: x.update(separate_author_review=False),
            lambda x: x.update(extra_approval=True),
        ]
        for mutate in changes:
            forged = copy.deepcopy(good)
            mutate(forged)
            with self.subTest(mutate=mutate), self.assertRaises(frontier.FrontierError):
                frontier.validate_review_receipt("literature", forged, expected, request_digest)

    def test_future_exact_pinned_receipt_passes_full_receipt_state_path(self):
        expected_rows, request_digest, good = valid_literary_receipt_fixture()
        raw = json.dumps(good, sort_keys=True).encode("utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / frontier.REVIEW_RECEIPTS["literature"]
            target.parent.mkdir(parents=True)
            target.write_bytes(raw)
            with mock.patch.object(frontier, "ROOT", root):
                self.assertEqual(frontier.receipt_state("literature", expected_rows, request_digest),
                                 "UNPINNED_REVIEW_CLAIM")
                with mock.patch.dict(frontier.ACCEPTED_REVIEW_DIGESTS,
                                     {"literature": hashlib.sha256(raw).hexdigest()}):
                    self.assertEqual(frontier.receipt_state("literature", expected_rows, request_digest),
                                     "CODE_PINNED_REVIEW_RECEIPT_NOT_RELEASE_AUTHORIZATION")
                    with self.assertRaises(frontier.FrontierError):
                        frontier.receipt_state("literature", expected_rows, "f" * 64)

    def test_duplicate_json_keys_cannot_smuggle_second_review_state(self):
        with self.assertRaises(frontier.FrontierError):
            json.loads('{"site_effect":"NONE","site_effect":"PUBLISHED"}',
                       object_pairs_hook=frontier._unique_object_pairs)

    def test_promoted_scouts_description_is_rejected_before_status_report(self):
        original = frontier.scouts_first.read_pinned
        forged = copy.deepcopy(original())
        forged["video_pages_opened"] = True
        with mock.patch.object(frontier.scouts_first, "read_pinned", return_value=forged):
            with self.assertRaises(frontier.FrontierError):
                frontier.report()

    def test_missing_or_rewritten_accepted_23_overviews_refused(self):
        original = frontier.publisher._raw

        def altered(path):
            if path == frontier.publisher.PUBLIC_PATH:
                return b'{}\n'
            return original(path)

        with mock.patch.object(frontier.publisher, "_raw", side_effect=altered):
            with self.assertRaises(frontier.FrontierError):
                frontier.report()

    def test_rewritten_short_treks_reviewed_output_refused(self):
        valid = frontier.short_publisher.build()
        with mock.patch.object(frontier.short_publisher, "build", return_value={**valid, "synopsis_count": 15}):
            with self.assertRaises(frontier.FrontierError):
                frontier.report()


if __name__ == "__main__":
    unittest.main()
