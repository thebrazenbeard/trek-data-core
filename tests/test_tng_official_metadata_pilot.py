"""Proposal-only guardrails for five official TNG metadata references."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "proposals/librarian/tng-official-metadata-20261102/bundle.json"
EXPECTED = {
    "Q1058477": (
        "The Neutral Zone",
        "https://www.startrek.com/videos/star-trek-the-next-generation-the-neutral-zone",
        "OFFICIAL_VIDEO_PAGE_METADATA",
    ),
    "Q16744120": (
        "New Ground",
        "https://www.startrek.com/videos/watch-star-trek-the-next-generation-new-ground",
        "OFFICIAL_VIDEO_PAGE_METADATA",
    ),
    "Q1102231": (
        "Hide and Q",
        "https://www.startrek.com/videos/episode-preview-hide-and-q",
        "OFFICIAL_PREVIEW_PAGE_METADATA",
    ),
    "Q1392472": (
        "Skin of Evil",
        "https://www.startrek.com/news/a-look-back-at-skin-of-evil",
        "OFFICIAL_EDITORIAL_RETROSPECTIVE_METADATA",
    ),
    "Q14045941": (
        "Brothers",
        "https://www.startrek.com/news/your-ultimate-star-trek-picard-watch-guide",
        "OFFICIAL_WATCH_GUIDE_REFERENCE_METADATA",
    ),
}

ALLOWED_PAGE_METADATA = {
    "page_kind", "observed_title", "observed_series", "observed_season",
    "observed_episode", "observed_on",
}


def pilot_boundary_errors(bundle):
    """A separate, fail-closed pilot gate; the general registry accepts later promotions."""
    errors = []
    if set(bundle) != {"batch_id", "proposal_status", "sources", "works",
                       "bindings", "crosswalks", "analysis_passes"}:
        errors.append("unexpected proposal envelope, including possible evidence/coverage")
    if bundle.get("proposal_status") != "PROPOSAL_ONLY_NOT_ADMITTED":
        errors.append("proposal status promoted")
    if bundle.get("analysis_passes") != []:
        errors.append("analysis passes are not within this pilot")
    for kind, key, state_key, state in (
        ("sources", "source_id", "status", "PROPOSED"),
        ("works", "work_id", "status", "PROPOSED"),
        ("bindings", "binding_id", "lifecycle", "PROPOSED"),
        ("crosswalks", "crosswalk_id", "mapping_status", "CANDIDATE"),
    ):
        for row in bundle.get(kind, []):
            if row.get(state_key) != state:
                errors.append(f"{row.get(key)}: forbidden promotion")
            if row.get("fixture_only") is not False:
                errors.append(f"{row.get(key)}: fixture boundary changed")
    for source in bundle.get("sources", []):
        sid = source.get("source_id")
        if source.get("content_hash") is not None or source.get("content_fingerprint") is not None:
            errors.append(f"{sid}: unsourced content digest")
        if source.get("source_version") is not None or source.get("retrieved_at") is not None:
            errors.append(f"{sid}: invented version or retrieval timestamp")
        if source.get("source_variant") != "WEB_METADATA_ONLY":
            errors.append(f"{sid}: source variant promoted")
        if source.get("independence_group") != "publisher:startrek.com":
            errors.append(f"{sid}: publisher pseudo-independence")
        if source.get("derived_from") != []:
            errors.append(f"{sid}: unexpected derivative")
        if set(source.get("provider_metadata", {})) - ALLOWED_PAGE_METADATA:
            errors.append(f"{sid}: unexpected source content in metadata")
        position = {
            "https://www.startrek.com/videos/star-trek-the-next-generation-the-neutral-zone": (1, 26),
            "https://www.startrek.com/videos/watch-star-trek-the-next-generation-new-ground": (5, 10),
        }.get(source.get("locator"))
        metadata = source.get("provider_metadata", {})
        observed = (metadata.get("observed_season"), metadata.get("observed_episode"))
        if position is None and any(x is not None for x in observed):
            errors.append(f"{sid}: unsupported publisher ordinal")
        elif position is not None and observed != position:
            errors.append(f"{sid}: changed publisher ordinal")
    for binding in bundle.get("bindings", []):
        if binding.get("mapping_role") != "METADATA_ONLY":
            errors.append(f"{binding.get('binding_id')}: binding role promoted")
    return errors


def load_bundle():
    def reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(BUNDLE.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)


class OfficialMetadataPilotTests(unittest.TestCase):
    def test_valid_librarian_contract_and_no_admitted_pairs(self):
        spec = importlib.util.spec_from_file_location(
            "librarian_validator", ROOT / "tools/validate_librarian_registry.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        bundle = load_bundle()
        paths = [
            (BUNDLE, row)
            for k in ("sources", "works", "bindings", "crosswalks")
            for row in bundle[k]
        ]
        self.assertEqual(
            mod.validate_registry(
                bundle["sources"], bundle["works"],
                bundle["bindings"], bundle["crosswalks"], paths
            ), [],
        )
        self.assertEqual(mod.source_bound_pairs(bundle["bindings"]), [])
        self.assertEqual(pilot_boundary_errors(bundle), [])

    def test_five_unadmitted_identity_proposals(self):
        bundle = load_bundle()
        self.assertEqual(bundle["proposal_status"], "PROPOSAL_ONLY_NOT_ADMITTED")
        for key in ("sources", "works", "bindings", "crosswalks"):
            self.assertEqual(len(bundle[key]), 5)
        works = {w["work_id"]: w for w in bundle["works"]}
        sources = {s["source_id"]: s for s in bundle["sources"]}
        bindings = {b["work_id"]: b for b in bundle["bindings"]}
        xwalk = {c["target_id"]: c for c in bundle["crosswalks"]}
        self.assertEqual(len(works), 5)
        self.assertEqual(len(sources), 5)
        self.assertEqual(set(works), set(bindings) & set(xwalk))
        self.assertEqual({c["external_id"] for c in xwalk.values()}, set(EXPECTED))

        for work_id, work in works.items():
            with self.subTest(work_id=work_id):
                self.assertEqual(work["record_type"], "work")
                self.assertEqual(work["status"], "PROPOSED")
                self.assertEqual(work["work_type"], "EPISODE")
                self.assertIsNone(work["parent_work_id"])
                self.assertIsNone(work["component_label"])
                self.assertFalse(work["fixture_only"])
                self.assertTrue(work_id.startswith("proposal:tng:work:"))

                binding = bindings[work_id]
                self.assertEqual(binding["lifecycle"], "PROPOSED")
                self.assertEqual(binding["mapping_role"], "METADATA_ONLY")
                self.assertIsNone(binding["exclusive_scope_key"])
                self.assertIsNone(binding["supersedes_binding_id"])
                self.assertFalse(binding["fixture_only"])
                self.assertTrue(binding["basis"])
                self.assertEqual(binding["source_scope"], {"scope_type": "WHOLE", "locator": None})
                self.assertEqual(binding["work_scope"], {"scope_type": "WHOLE", "component_label": None})
                source = sources[binding["source_id"]]
                self.assertEqual(source["record_type"], "source")
                self.assertEqual(source["status"], "PROPOSED")
                self.assertIsNone(source["content_hash"])
                self.assertIsNone(source["content_fingerprint"])
                self.assertEqual(source["derived_from"], [])
                self.assertFalse(source["fixture_only"])
                self.assertEqual(source["independence_group"], "publisher:startrek.com")
                self.assertEqual(source["provider"], "StarTrek.com")
                self.assertEqual(source["provider_metadata"]["observed_on"], "2026-11-02")
                self.assertNotIn("page_body", source["provider_metadata"])

                crosswalk = xwalk[work_id]
                self.assertEqual(crosswalk["mapping_status"], "CANDIDATE")
                self.assertEqual(crosswalk["target_kind"], "WORK")
                self.assertEqual(crosswalk["external_system"], "WIKIDATA")
                self.assertEqual(crosswalk["retrieved_at"], "2026-11-02T11:46:04Z")
                self.assertEqual(crosswalk["snapshot"], "WDQS-TNG-Q16290-20261102-10ROW-001")
                self.assertFalse(crosswalk["fixture_only"])
                title, url, kind = EXPECTED[crosswalk["external_id"]]
                self.assertEqual(work["title"], title)
                self.assertEqual(source["locator"], url)
                self.assertEqual(source["source_kind"], kind)

    def test_ordinal_claims_limited_to_two_official_video_pages(self):
        bundle = load_bundle()
        source_by_id = {s["source_id"]: s for s in bundle["sources"]}
        crosswalk_by_id = {c["target_id"]: c for c in bundle["crosswalks"]}
        by_qid = {
            crosswalk_by_id[b["work_id"]]["external_id"]: source_by_id[b["source_id"]]
            for b in bundle["bindings"]
        }
        self.assertEqual(
            (by_qid["Q1058477"]["provider_metadata"]["observed_season"],
             by_qid["Q1058477"]["provider_metadata"]["observed_episode"]),
            (1, 26),
        )
        self.assertEqual(
            (by_qid["Q16744120"]["provider_metadata"]["observed_season"],
             by_qid["Q16744120"]["provider_metadata"]["observed_episode"]),
            (5, 10),
        )
        for qid in ("Q1102231", "Q1392472", "Q14045941"):
            self.assertNotIn("observed_season", by_qid[qid]["provider_metadata"])
            self.assertNotIn("observed_episode", by_qid[qid]["provider_metadata"])
        self.assertEqual(
            by_qid["Q1392472"]["provider_metadata"]["observed_title"],
            "A Look Back at 'Skin of Evil'",
        )

    def test_each_metadata_only_binding_rejects_accepted_promotion(self):
        spec = importlib.util.spec_from_file_location(
            "librarian_validator", ROOT / "tools/validate_librarian_registry.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        original = load_bundle()
        for i, binding in enumerate(original["bindings"]):
            with self.subTest(binding=binding["binding_id"]):
                mutated = copy.deepcopy(original)
                mutated["bindings"][i]["lifecycle"] = "ACCEPTED"
                self.assertTrue(pilot_boundary_errors(mutated))
                errors = mod.validate_registry(
                    mutated["sources"], mutated["works"],
                    mutated["bindings"], mutated["crosswalks"]
                )
                self.assertTrue(
                    any("ACCEPTED binding must be EVIDENCE_BEARING" in e for e in errors),
                    errors,
                )
                self.assertEqual(mod.source_bound_pairs(mutated["bindings"]), [])

    def test_pilot_guard_rejects_content_pseudo_independence_and_coverage(self):
        original = load_bundle()
        mutations = (
            ("accepted_work", lambda b: b["works"][0].update(status="ACCEPTED")),
            ("accepted_source", lambda b: b["sources"][0].update(status="ACCEPTED")),
            ("accepted_crosswalk", lambda b: b["crosswalks"][0].update(mapping_status="ACCEPTED")),
            ("evidence_role", lambda b: b["bindings"][0].update(mapping_role="EVIDENCE_BEARING")),
            ("invented_digest", lambda b: b["sources"][0].update(content_hash="sha256:not-a-capture")),
            ("invented_retrieval", lambda b: b["sources"][0].update(retrieved_at="2026-11-02T00:00:00Z")),
            ("publisher_split", lambda b: b["sources"][0].update(independence_group="independent:page")),
            ("page_body", lambda b: b["sources"][0]["provider_metadata"].update(page_body="unlicensed")),
            ("preview_ordinal", lambda b: b["sources"][2]["provider_metadata"].update(observed_episode=10)),
            ("narrative_evidence", lambda b: b.update(evidence=[{"claim": "invented"}])),
            ("coverage", lambda b: b.update(coverage_events=[{"count": 5}])),
        )
        for name, mutate in mutations:
            with self.subTest(mutation=name):
                bundle = copy.deepcopy(original)
                mutate(bundle)
                self.assertTrue(pilot_boundary_errors(bundle))


if __name__ == "__main__":
    unittest.main()
