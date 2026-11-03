"""Reject drift in a derivative-source identity without claiming source authentication."""

import copy
import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "proposals/research/tos-charlie-x-derivative-close-read-20261103/validate.py"
namespace = runpy.run_path(str(VALIDATOR))
validate = namespace["validate"]
load = validate.__globals__["load"]


class CharlieXSourceIdentity(unittest.TestCase):
    def test_original_proposal(self):
        validate()

    def test_source_identity_and_scope_tampering_rejected(self):
        for path, replacement in (
            (("source", "source_kind"), "AUTHENTICATED_STUDIO_SCRIPT"),
            (("source", "authenticated_primary_video_verified"), True),
            (("work", "reconciled_global_work_id"), "tos-canonical-001"),
            (("accepted_coverage_events",), 100),
            (("source", "upstream_self_report", "attribution_is_independently_verified"), True),
            (("source", "upstream_self_report", "this_episode_upstream_match_verified"), True),
            (("source", "upstream_self_report", "attributed_upstream_url"),
             "https://malicious.example/"),
            (("source", "retrieval"), "AUTHENTICATED_PRIMARY_AV_WATCHED"),
            (("source", "private_source_custody"), "DURABLE_AUTHENTICATED_SOURCE"),
            (("source", "raw_html_sha256"), "0" * 64),
            (("source", "rendered_text_sha256"), "0" * 64),
            (("source", "url"), "https://example.org/unrelated"),
            (("source", "raw_html_candidate_dialogue_physical_lines_inclusive"), [1, 5]),
            (("work", "official_publisher_episode_page"), "https://example.org/other"),
            (("work", "official_publisher_title"), "Different Work"),
            (("work", "official_publisher_raw_html_hash_available"), True),
            (("base_accepted_main",), "0" * 40),
        ):
            manifest = copy.deepcopy(load("MANIFEST.json"))
            target = manifest
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = replacement

            def substituted(name):
                return manifest if name == "MANIFEST.json" else load(name)

            validate.__globals__["load"] = substituted
            try:
                with self.subTest(path=path):
                    with self.assertRaises(ValueError):
                        validate()
            finally:
                validate.__globals__["load"] = load


if __name__ == "__main__":
    unittest.main()
