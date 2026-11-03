"""Independent hostile checks on discovery overlap and publisher lineage."""

import copy
import json
import unittest
from pathlib import Path

from tools.audit_discovery_lineage import audit_rows, main


ROOT = Path(__file__).resolve().parents[1]


class DiscoveryLineageAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))["rows"]

    def test_independent_overlap_report_is_source_local_and_non_destructive(self):
        report = audit_rows(self.rows)
        self.assertEqual(report["audit_status"], "SOURCE_LOCAL_ONLY_NO_ADMISSION")
        self.assertEqual(report["row_count"], 1214)
        self.assertEqual(report["unique_source_locator_count"], 309)
        self.assertEqual(report["duplicate_signature_count"], 25)
        self.assertEqual(report["duplicate_extra_row_count"], 25)
        self.assertEqual(sum(len(c["row_ids"]) for c in report["duplicate_signatures"]), 50)
        self.assertTrue(all(len(c["independence_families"]) == 1
                            for c in report["duplicate_signatures"]))
        self.assertEqual(main(["--repo-root", str(ROOT)]), 0)

    def test_existing_paramount_alias_and_same_group_overlap_remain_observations(self):
        report = audit_rows(self.rows)
        clusters = [set(c["row_ids"]) for c in report["duplicate_signatures"]]
        for pair in (
            {"roster:tas:000", "publisher:tas:s1:000"},
            {"roster:ds9:000", "legacy:s1:ds9:000"},
            {"roster:voy:000", "legacy:s1:voy:000"},
            {"lead:0208", "publisher:0000"},
        ):
            self.assertIn(pair, clusters)
        alias = next(c for c in report["duplicate_signatures"]
                     if "roster:tas:000" in c["row_ids"])
        self.assertEqual(alias["source_groups"],
                         ["publisher:paramount", "publisher:paramountplus.com"])
        self.assertEqual(alias["independence_families"], ["paramount-publisher-family"])

    def test_colluding_aliases_never_become_independent_corroboration(self):
        one = copy.deepcopy(next(r for r in self.rows if r["row_id"] == "roster:tas:000"))
        other = copy.deepcopy(one)
        other["row_id"] = "adversarial:publisher-alias"
        other["source_group"] = "publisher:startrek.com"
        result = audit_rows([one, other])
        self.assertEqual(result["duplicate_signature_count"], 1)
        self.assertEqual(result["duplicate_signatures"][0]["independence_families"],
                         ["paramount-publisher-family"])
        self.assertEqual(len(result["same_url_multiple_source_groups"]), 1)
        self.assertEqual(result["row_count"], 2)  # neither raw observation lost

        other["source_group"] = "wikidata:wdqs"
        with self.assertRaisesRegex(ValueError, "incompatible independence families"):
            audit_rows([one, other])

    def test_unknown_independence_label_and_false_admission_fail_closed(self):
        source = copy.deepcopy(self.rows[0])
        for field, value in (
            ("source_group", "publisher:other-unreviewed-site"),
            ("identity_scope", "CANONICAL_WORK"),
            ("verification_status", "VERIFIED"),
            ("coverage_effect", "COUNTED"),
            ("admission_effect", "ACCEPTED"),
            ("source_locator", "http://www.wikidata.org/wiki/Q1136071"),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(source)
                changed[field] = value
                with self.assertRaises(ValueError):
                    audit_rows([changed])
        with self.assertRaisesRegex(ValueError, "duplicate source-local row_id"):
            audit_rows([source, copy.deepcopy(source)])


if __name__ == "__main__":
    unittest.main()
