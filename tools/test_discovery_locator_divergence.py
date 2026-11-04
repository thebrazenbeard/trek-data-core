"""Regression tests for source-local locator divergence triage."""

import unittest

from tools.audit_discovery_lineage import audit_rows


URL = "https://www.startrek.com/shows/star-trek-the-original-series"


def row(row_id, title, *, context="Season 1", medium="television", url=URL):
    return {
        "row_id": row_id,
        "source_group": "publisher:startrek.com",
        "medium": medium,
        "context": context,
        "title": title,
        "source_input": "Publisher catalog",
        "source_locator": url,
        "identity_scope": "SOURCE_LOCAL",
        "verification_status": "UNVERIFIED_METADATA",
        "admission_effect": "NONE",
        "coverage_effect": "NONE",
    }


class DivergentLocatorTest(unittest.TestCase):
    def test_same_url_distinct_title_triage_only(self):
        result = audit_rows([row("a", "Pilot"), row("b", "Second Pilot")])
        self.assertEqual(result["same_url_divergent_observation_count"], 1)
        self.assertEqual(
            result["same_url_divergent_observations"][0]["interpretation"],
            "TRIAGE_ONLY_NOT_A_WORK_IDENTITY_DECISION",
        )
        self.assertEqual(result["audit_status"], "SOURCE_LOCAL_ONLY_NO_ADMISSION")

    def test_normalized_duplicate_not_divergent(self):
        result = audit_rows([row("a", "STAR TREK"), row("b", "  star   trek  ")])
        self.assertEqual(result["same_url_divergent_observation_count"], 0)

    def test_medium_case_variant_is_one_normalized_duplicate(self):
        result = audit_rows([
            row("a", "Pilot", medium="episode"),
            row("b", "Pilot", medium="Episode"),
        ])
        self.assertEqual(result["duplicate_signature_count"], 1)
        self.assertEqual(result["duplicate_extra_row_count"], 1)
        self.assertEqual(result["same_url_divergent_observation_count"], 0)
        self.assertEqual(result["duplicate_signatures"][0]["medium"], "episode")
        self.assertEqual(result["duplicate_signatures"][0]["row_ids"], ["a", "b"])

    def test_unicode_nfkc_medium_title_context_variants_are_duplicates(self):
        result = audit_rows([
            row("a", "Café", context="Season 1", medium="episode"),
            row("b", "Cafe\u0301", context="Ｓｅａｓｏｎ １", medium="ＥＰＩＳＯＤＥ"),
        ])
        self.assertEqual(result["duplicate_signature_count"], 1)
        self.assertEqual(result["same_url_divergent_observation_count"], 0)
        self.assertEqual(result["duplicate_signatures"][0]["title_normalized"], "café")
        self.assertEqual(result["duplicate_signatures"][0]["context_normalized"], "season 1")

    def test_distinct_normalized_medium_remains_divergent(self):
        result = audit_rows([
            row("a", "Pilot", medium="episode"),
            row("b", "Pilot", medium="film"),
        ])
        self.assertEqual(result["duplicate_signature_count"], 0)
        self.assertEqual(result["same_url_divergent_observation_count"], 1)

    def test_context_matters(self):
        result = audit_rows([
            row("a", "Pilot", context="Season 1"),
            row("b", "Pilot", context="Season 2"),
        ])
        self.assertEqual(result["same_url_divergent_observation_count"], 1)

    def test_order_independent(self):
        rows = [row("b", "Second Pilot"), row("a", "Pilot")]
        self.assertEqual(audit_rows(rows), audit_rows(list(reversed(rows))))

    def test_separate_urls_not_divergent(self):
        rows = [
            row("a", "Pilot"),
            row(
                "b", "Second Pilot",
                url="https://www.startrek.com/shows/star-trek-the-next-generation",
            ),
        ]
        self.assertEqual(audit_rows(rows)["same_url_divergent_observation_count"], 0)


if __name__ == "__main__":
    unittest.main()
