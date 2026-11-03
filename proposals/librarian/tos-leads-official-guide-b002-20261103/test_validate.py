"""Hostile source-local invariants for TOS archived-lead/Paramount guides."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("validate.py")
SPEC = importlib.util.spec_from_file_location("tos_lead_b002_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class TosLeadSourceB002Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = validator.load_strict(MODULE_PATH.with_name("observations.json"))

    def reject(self, mutation) -> None:
        changed = copy.deepcopy(self.payload)
        mutation(changed)
        with self.assertRaises(validator.SourceCrosswalkError):
            validator.validate_payload(changed)

    def test_exact_valid_batch_does_not_admit_works_or_publish(self) -> None:
        self.assertEqual(validator.validate_payload(self.payload), 13)
        self.assertEqual(len({r["qid"] for r in self.payload["rows"]}), 13)
        self.assertEqual(len({(r["season"], r["episode"]) for r in self.payload["rows"]}), 13)
        self.assertEqual(sum(r["title_match"] == "EXACT" for r in self.payload["rows"]), 12)
        self.assertEqual(sum(r["title_match"] == "PUNCTUATION_VARIANT_HELD" for r in self.payload["rows"]), 1)
        self.assertEqual(self.payload["accepted_work_effect"], "NONE")

    def test_accepted_row_duplicate_fails_closed(self) -> None:
        self.reject(lambda p: p["rows"].append(copy.deepcopy(p["rows"][0])))
        self.reject(lambda p: p["rows"][1].update(lead_id=p["rows"][0]["lead_id"]))
        self.reject(lambda p: p["rows"].reverse())

    def test_title_qid_slot_and_same_source_page_rebindings_fail(self) -> None:
        for mutation in (
            lambda p: p["rows"][0].update(qid="Q999999999"),
            lambda p: p["rows"][0].update(archived_title="Charlie Z"),
            lambda p: p["rows"][1].update(publisher_title="Charlie X"),
            lambda p: p["rows"][1].update(season=2, episode=7),
            lambda p: p["rows"][1].update(episode=6),
            lambda p: p["rows"][1].update(publisher_guide_url=p["rows"][5]["publisher_guide_url"]),
            lambda p: p["rows"][5].update(publisher_guide_url="https://www.paramountplus.com/shows/star_trek/episodes/1/"),
            lambda p: p["rows"][1].update(publisher_description_sha256=p["rows"][0]["publisher_description_sha256"]),
        ):
            with self.subTest(mutation=mutation):
                self.reject(mutation)

    def test_held_punctuation_case_cannot_be_silently_resolved(self) -> None:
        self.reject(lambda p: p["rows"][0].update(title_match="EXACT", mismatch=None))
        self.reject(lambda p: p["rows"][0].update(publisher_title="Charlie X"))
        self.reject(lambda p: p["rows"][2].update(title_match="PUNCTUATION_VARIANT_HELD"))

    def test_source_origin_and_temporal_custody_rebindings_fail(self) -> None:
        for mutation in (
            lambda p: p.update(publisher_independence_family="memory_alpha"),
            lambda p: p.update(wikidata_source_independence="INDEPENDENT_CORROBORATION"),
            lambda p: p.update(archived_leads_sha256="0" * 64),
            lambda p: p["published_page_reads"][1].update(official_url="https://evil.invalid/shows/star_trek/episodes/2/"),
            lambda p: p["published_page_reads"][1].update(lappy_direct_http_status=404),
            lambda p: p["published_page_reads"][1].update(lappy_transient_html_sha256="a" * 64),
            lambda p: p["published_page_reads"][1].update(raw_body_archived=True),
            lambda p: p["published_page_reads"][1].update(raw_body_digest_replayable=True),
            lambda p: p.update(observed_utc_date="2026-11-04"),
        ):
            with self.subTest(mutation=mutation):
                self.reject(mutation)

    def test_rights_work_coverage_synopsis_and_explorer_promotions_fail(self) -> None:
        for effect in (
            "accepted_work_effect", "accepted_source_work_binding_effect", "governed_coverage_effect",
            "explorer_publication_effect", "artwork_release_effect", "original_synopsis_release_effect",
        ):
            with self.subTest(effect=effect):
                self.reject(lambda p, effect=effect: p.update({effect: "ACCEPTED"}))
        self.reject(lambda p: p["rows"][0].update(canonical_work_id="tos-charlie-x"))

    def test_strict_duplicate_json_keys_fail(self) -> None:
        with self.assertRaisesRegex(validator.SourceCrosswalkError, "duplicate JSON key"):
            json.loads('{"qid":"Q1","qid":"Q2"}', object_pairs_hook=validator.reject_duplicate_keys)
        self.reject(lambda p: p.update(unknown_extra="injected"))

    def test_untrusted_bool_ordinal_does_not_pass_as_integer(self) -> None:
        self.reject(lambda p: p["rows"][0].update(season=True))
        self.reject(lambda p: p["published_page_reads"][0].update(lappy_direct_http_status=True))

    def test_python_optimized_mode_validates_and_rejects_mutation(self) -> None:
        okay = subprocess.run([sys.executable, "-O", "-B", str(MODULE_PATH)], capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(okay.returncode, 0, okay.stderr)
        with tempfile.TemporaryDirectory(prefix="trek-tos-b002-opt-") as folder:
            poisoned_path = Path(folder) / "poisoned.json"
            changed = copy.deepcopy(self.payload)
            changed["rows"][3]["publisher_description_sha256"] = "f" * 64
            poisoned_path.write_text(json.dumps(changed), encoding="utf-8")
            probe = (
                "import importlib.util;from pathlib import Path;"
                f"s=importlib.util.spec_from_file_location('v',{str(MODULE_PATH)!r});"
                "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
                f"m.validate_payload(m.load_strict(Path({str(poisoned_path)!r})))"
            )
            failed = subprocess.run([sys.executable, "-O", "-B", "-c", probe], cwd=validator.ROOT, capture_output=True, text=True, timeout=30, check=False)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("SourceCrosswalkError", failed.stderr)


if __name__ == "__main__":
    unittest.main()
