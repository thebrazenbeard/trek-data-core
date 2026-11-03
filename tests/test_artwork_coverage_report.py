"""Adversarial synthetic tests for source-local visual mapping, not canon coverage."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import report_artwork_coverage as visual


class SourceLocalVisualCoverageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.sources = [
            {"row_id": "episode:example", "medium": "EPISODE",
             "source_locator": "https://example.org/episode"},
            {"row_id": "film:film-a", "medium": "FILM",
             "source_locator": "https://example.org/film"},
            {"row_id": "literature:book-a", "medium": "LITERATURE",
             "source_locator": "https://example.org/book-a"},
            {"row_id": "literature:book-b", "medium": "LITERATURE",
             "source_locator": "https://example.org/book-b"},
            {"row_id": "short:example", "medium": "SHORT_FORM",
             "source_locator": "https://example.org/short"},
            {"row_id": "audio:example", "medium": "AUDIO",
             "source_locator": "https://example.org/audio"},
        ]
        self.films = [{"id": "film-a", "source_locator": "https://example.org/film"}]
        self.artwork = [
            {"row_id": "film:film-a", "source_locator": "https://example.org/film",
             "rights_status": "PUBLIC_DISPLAY_PERMISSION_VERIFIED"},
            {"row_id": "directory:literature:book-a", "source_locator": "https://example.org/book-a",
             "rights_status": "API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED"},
        ]
        self.held = [{"row_id": "literature:book-b", "reason": "IMAGE_VISUALLY_REJECTED_TITLE_PAGE"}]
        self._write()
        self.original_held_packet_sha = hashlib.sha256(
            (self.root / visual.artwork.OL_SOURCE_PACKET).read_bytes()).hexdigest()

    def _json(self, path: str, obj):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")), encoding="utf-8")

    def _write(self):
        self._json("explorer/discovery-catalog.json", {
            "data_status": "DISCOVERY_ONLY", "coverage_effect": "NONE",
            "admission_effect": "NONE", "row_count": len(self.sources), "rows": self.sources})
        self._json("explorer/film-catalog.json", {
            "data_status": "DISCOVERY_ONLY", "coverage_effect": "NONE",
            "film_count": len(self.films), "films": self.films})
        self._json(visual.artwork.MANIFEST, {
            "schema_version": "1.3.0", "data_status": "PROVENANCE_REVIEWED_ARTWORK",
            "coverage_effect": "NONE", "rights_policy": "PER_ENTRY_DISPLAY_GATE",
            "artwork_count": len(self.artwork), "artwork": self.artwork})
        self._json(visual.artwork.OL_SOURCE_PACKET, {
            "data_status": "PROPOSAL_ONLY_INDEPENDENT_ARTWORK_REVIEW_REQUIRED",
            "coverage_effect": "NONE", "public_artwork_release_effect": "NONE",
            "held_count": len(self.held), "held": self.held})

    def _report(self, *, allow_synthetic_held_mutation=False):
        # The separate release-validator suite owns image/rights pin tests.
        # Inject only that validator's synthetic success; these tests exercise
        # source-local mapping and the report's additional invariants.
        response = {"status": "REVIEWED_ARTWORK_READY_FOR_SEPARATE_UI_RELEASE",
                    "artwork_count": len(self.artwork), "coverage_effect": "NONE"}
        historical_sha = (hashlib.sha256((self.root / visual.artwork.OL_SOURCE_PACKET).read_bytes()).hexdigest()
                          if allow_synthetic_held_mutation else self.original_held_packet_sha)
        with patch.object(visual.artwork, "validate_manifest", return_value=response), patch.object(
                visual, "HISTORIC_PACKET_SHA256", historical_sha):
            return visual.report(self.root)

    def test_mixed_media_report_separates_parallel_films_and_unreviewed_rows(self):
        report = self._report()
        self.assertEqual(report["canonical_works_coverage"], "NOT_MEASURED")
        self.assertEqual(report["research_coverage_effect"], "NONE")
        self.assertEqual(report["source_local_metadata_row_total"], 6)
        self.assertEqual(report["parallel_film_projection_rows_not_additive"], 1)
        self.assertEqual(report["reviewed_artwork_mapping_total"], 2)
        categories = {row["medium"]: row for row in report["per_medium"]}
        self.assertEqual(categories["FILM"]["reviewed_artwork_mappings"], 1)
        self.assertEqual(categories["LITERATURE"]["source_local_metadata_rows"], 2)
        self.assertEqual(categories["LITERATURE"]["historical_held_artwork_proposals"], 1)
        self.assertEqual(categories["EPISODE"]["unmapped_source_local_rows"], 1)
        self.assertEqual(sum(row["source_local_metadata_rows"] for row in report["per_medium"]), 6)

    def test_append_unrelated_source_row_changes_only_its_metadata_denominator(self):
        # This isolates the report from the separately owned artwork release
        # validator. It is NOT evidence that the current historical whole-file
        # source hash gate accepts an append; that needs its own custody patch.
        baseline = self._report()
        self.sources.append({"row_id": "literature:book-c", "medium": "LITERATURE",
                             "source_locator": "https://example.org/book-c"})
        self._write()
        changed = self._report()
        literary = next(row for row in changed["per_medium"] if row["medium"] == "LITERATURE")
        self.assertEqual(changed["source_local_metadata_row_total"],
                         baseline["source_local_metadata_row_total"] + 1)
        self.assertEqual(literary["source_local_metadata_rows"], 3)
        self.assertEqual(literary["reviewed_artwork_mappings"], 1)
        self.assertEqual(literary["historical_held_artwork_proposals"], 1)
        self.assertEqual(changed["reviewed_artwork_mapping_total"],
                         baseline["reviewed_artwork_mapping_total"])

    def test_directory_and_film_aliases_cannot_double_count_one_film_row(self):
        self.artwork[1] = {**self.artwork[0], "row_id": "directory:film:film-a"}
        self._write()
        with self.assertRaisesRegex(visual.CoverageRejected, "duplicate"):
            self._report()

    def test_unmatched_artwork_source_and_rights_spoofs_fail(self):
        edits = (
            {"row_id": "directory:missing"},
            {"source_locator": "https://attacker.invalid/film"},
            {"rights_status": "PUBLIC_DOMAIN"},
            {"row_id": "film:not-in-projection"},
        )
        original = dict(self.artwork[0])
        for changed in edits:
            with self.subTest(changed=changed):
                self.artwork[0] = {**original, **changed}
                self._write()
                with self.assertRaises(visual.CoverageRejected):
                    self._report()

    def test_unreviewed_changes_to_directory_and_parallel_film_projection_fail(self):
        self.sources.append(dict(self.sources[0]))
        self._write()
        with self.assertRaisesRegex(visual.CoverageRejected, "duplicate"):
            self._report()
        self.sources.pop()
        self.films[0]["source_locator"] = "https://example.org/wrong"
        self._write()
        with self.assertRaisesRegex(visual.CoverageRejected, "film projection"):
            self._report()

    def test_historical_held_is_not_generic_rights_denial_and_must_bind_to_source(self):
        self.held[0]["row_id"] = "episode:example"
        self._write()
        with self.assertRaisesRegex(visual.CoverageRejected, "literary"):
            self._report(allow_synthetic_held_mutation=True)
        self.held[0]["row_id"] = "literature:book-b"
        self.held.append(dict(self.held[0]))
        self._write()
        with self.assertRaisesRegex(visual.CoverageRejected, "duplicate"):
            self._report(allow_synthetic_held_mutation=True)

    def test_historical_held_reason_cannot_be_rewritten_as_new_rights_claim(self):
        self.held[0]["reason"] = "PUBLIC_DISPLAY_PERMISSION_VERIFIED"
        self._write()
        with self.assertRaisesRegex(visual.CoverageRejected, "immutable reviewed observation"):
            self._report()

    def test_false_research_admission_and_release_coverage_fail_closed(self):
        directory = json.loads((self.root / "explorer/discovery-catalog.json").read_text())
        directory["admission_effect"] = "ACCEPTED_WORKS"
        self._json("explorer/discovery-catalog.json", directory)
        with self.assertRaisesRegex(visual.CoverageRejected, "discovery"):
            self._report()
        self._write()
        with patch.object(visual.artwork, "validate_manifest", return_value={
                "coverage_effect": "ACCEPTED", "artwork_count": 2}), patch.object(
                visual, "HISTORIC_PACKET_SHA256", self.original_held_packet_sha):
            with self.assertRaisesRegex(visual.CoverageRejected, "claimed coverage"):
                visual.report(self.root)

    def test_non_object_source_or_historical_packet_fail_without_attribute_error(self):
        self._json("explorer/discovery-catalog.json", [])
        with self.assertRaisesRegex(visual.CoverageRejected, "JSON objects"):
            self._report()
        self._write()
        self._json(visual.artwork.OL_SOURCE_PACKET, [])
        with self.assertRaisesRegex(visual.CoverageRejected, "JSON object"):
            self._report(allow_synthetic_held_mutation=True)

    def test_cli_rejects_deep_json_recursion_without_traceback(self):
        stderr = io.StringIO()
        with patch.object(visual, "report", side_effect=RecursionError("nested input")), redirect_stderr(stderr):
            self.assertEqual(visual.main(["--check"]), 1)
        self.assertIn("ARTWORK_COVERAGE_REJECTED: nested input", stderr.getvalue())

    def test_accepted_repository_report_is_deterministic_and_has_no_write_effect(self):
        directory = ROOT / "explorer/discovery-catalog.json"
        before = hashlib.sha256(directory.read_bytes()).hexdigest()
        first = visual.report(ROOT)
        self.assertEqual(first, visual.report(ROOT))
        self.assertEqual(hashlib.sha256(directory.read_bytes()).hexdigest(), before)
        self.assertEqual(first["reviewed_artwork_mapping_total"], 4)
        self.assertEqual(first["historical_held_artwork_proposal_total_not_rights_denials"], 5)


if __name__ == "__main__":
    unittest.main()
