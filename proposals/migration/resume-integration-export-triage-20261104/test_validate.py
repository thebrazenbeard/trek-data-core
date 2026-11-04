"""Hostile regression tests for historical-chat migration non-admission."""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate import DIRECTORY, LIT_MAIN, LIT_PICARD, ROOT, SHELF, verify

BATCH_REL = Path("proposals/migration/resume-integration-export-triage-20261104/MANIFEST.json")


class ResumeIntegrationMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for relative in (BATCH_REL, SHELF, DIRECTORY, LIT_MAIN, LIT_PICARD):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)

    def edit(self, relative: Path, change) -> None:
        path = self.root / relative
        value = json.loads(path.read_text(encoding="utf-8"))
        change(value)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def rejected(self, relative: Path, change, message: str) -> None:
        self.edit(relative, change)
        with self.assertRaisesRegex(ValueError, message):
            verify(self.root)

    def test_literary_effect_dimension_omission_is_rejected(self):
        self.rejected(LIT_MAIN, lambda d: d["accepted_effects"].pop("coverage"),
                      "literary metadata proposal promoted")

    def test_literary_effect_dimension_rename_is_rejected(self):
        def rename(d):
            d["accepted_effects"]["binding"] = d["accepted_effects"].pop("bindings")
        self.rejected(LIT_MAIN, rename, "literary metadata proposal promoted")

    def test_literary_extra_effect_dimension_is_rejected(self):
        self.rejected(LIT_MAIN,
                      lambda d: d["accepted_effects"].update({"invented": "NONE"}),
                      "literary metadata proposal promoted")

    def test_literary_effect_dimensions_wrong_type_are_rejected(self):
        self.rejected(LIT_MAIN, lambda d: d.update(accepted_effects=["NONE"]),
                      "literary metadata proposal promoted")

    def test_clean_accepted_snapshot_is_valid_proposal_only(self) -> None:
        verify(self.root)

    def test_historical_assistant_cannot_impersonate_primary_source_reader(self) -> None:
        self.rejected(BATCH_REL, lambda d: d["claims"][0].update(
            evidence_class="PRIMARY_LITERARY_SOURCE_REPLAY_VERIFIED"), "historical assertion")

    def test_historical_counts_cannot_promote_coverage(self) -> None:
        self.rejected(BATCH_REL, lambda d: d.update(coverage_effect="CLOSE_READ"),
                      "forbidden historical effect")

    def test_historical_chat_archive_hash_cannot_be_replaced(self) -> None:
        self.rejected(BATCH_REL, lambda d: d["source"].update(archive_sha256="0" * 64),
                      "source attribution")

    def test_historical_claim_cannot_be_silently_rewritten(self) -> None:
        self.rejected(BATCH_REL, lambda d: d["claims"][0].update(
            historical_claim="The chat confirmed 347 books were fully close-read."),
            "historical claim wording")

    def test_exact_isbn_membership_swap_fails_with_39_30_9_preserved(self) -> None:
        """Regress the historical #351 class of aggregate-preserving error."""
        def swap_status(d):
            first, second = d["rows"][:2]
            self.assertNotEqual(first["crosscheck_state"], second["crosscheck_state"])
            first["crosscheck_state"], second["crosscheck_state"] = (
                second["crosscheck_state"], first["crosscheck_state"])
            self.assertEqual(sum(r["crosscheck_state"] ==
                                 "ISBN_IDENTIFIER_AGREEMENT_SOURCE_LOCAL" for r in d["rows"]), 30)
        self.rejected(SHELF, swap_status, "ISBN membership drift")

    def test_isbn_rebinding_fails_even_if_aggregate_and_distinct_counts_hold(self) -> None:
        def swap_isbn(d):
            first, second = d["rows"][:2]
            first["publisher_isbn13"], second["publisher_isbn13"] = (
                second["publisher_isbn13"], first["publisher_isbn13"])
            self.assertEqual(len({r["publisher_isbn13"] for r in d["rows"]}), 39)
            self.assertEqual(d["publisher_isbn_identifier_agreements"], 30)
            self.assertEqual(d["held_discrepancy_count"], 9)
        self.rejected(SHELF, swap_isbn, "ISBN membership drift")

    def test_duplicate_second_self_row_fails_with_total_catalog_size_preserved(self) -> None:
        """Duplicating a literary ref while replacing a different row evades counts."""
        def duplicate(d):
            matches = [r for r in d["rows"] if r.get("row_id") ==
                       "literature:proposed-lit-picard-second-self"]
            self.assertEqual(len(matches), 1)
            victim = next(i for i, r in enumerate(d["rows"]) if
                          r.get("row_id") != matches[0]["row_id"])
            d["rows"][victim] = copy.deepcopy(matches[0])
            self.assertEqual(len(d["rows"]), d["row_count"])
        self.rejected(DIRECTORY, duplicate, "duplicated/inflated literary")

    def test_relabeling_duplicate_literary_ref_cannot_evade_overlap_gate(self) -> None:
        def clone_with_different_id(d):
            match = next(r for r in d["rows"] if r.get("row_id") ==
                         "literature:proposed-lit-picard-second-self")
            injected = copy.deepcopy(match)
            injected["row_id"] = "literature:second-self-accidental-clone"
            injected["source_locator"] = "https://example.invalid/edition-different-path"
            victim = next(i for i, r in enumerate(d["rows"]) if
                          r.get("row_id") != match["row_id"])
            d["rows"][victim] = injected
            self.assertEqual(len(d["rows"]), d["row_count"])
        self.rejected(DIRECTORY, clone_with_different_id, "duplicated/inflated literary")

    def test_second_self_proposal_work_id_conflict_requires_reconciliation(self) -> None:
        self.rejected(LIT_MAIN, lambda d: next(e for e in d["editions"] if
                      e["isbn13"] == "9781982194833").update(
                      candidate_work_id="invented-global-work"), "conflicting proposal")

    def test_second_self_same_isbn_wrong_publisher_url_fails(self) -> None:
        self.rejected(LIT_MAIN, lambda d: next(e for e in d["editions"] if
                      e["isbn13"] == "9781982194833").update(
                      publisher_product_url="https://example.invalid/book/9781982194833"),
                      "conflicting proposal")

    def test_same_publisher_proposals_cannot_claim_independent_witnesses(self) -> None:
        self.rejected(LIT_PICARD, lambda d: d.update(
            source_group="independent:publisher-mirror"), "falsely independent")

    def test_duplicate_edition_within_second_proposal_fails(self) -> None:
        def duplicate(d):
            second_self = next(e for e in d["editions"] if e["isbn13"] == "9781982194833")
            d["editions"].append(copy.deepcopy(second_self))
        self.rejected(LIT_MAIN, duplicate, "duplicated Second Self")

    def test_navigation_row_cannot_claim_global_work_reconciliation(self) -> None:
        self.rejected(DIRECTORY, lambda d: next(r for r in d["rows"] if
                      r.get("row_id") == "literature:proposed-lit-picard-second-self").update(
                      identity_scope="CANONICAL_WORK"), "duplicated/inflated literary")

    def test_duplicate_json_keys_are_rejected(self) -> None:
        path = self.root / BATCH_REL
        data = path.read_text(encoding="utf-8")
        path.write_text(data.replace('"role": "MIGRATION",',
                                     '"role": "MIGRATION", "role": "DIRECTOR",', 1),
                        encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main()
