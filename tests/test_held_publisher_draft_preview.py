"""Adversarial tests for a NON-PUBLIC, draft-dependent literary metadata preview.

The preview is not accepted main, not an Explorer index and not Work admission.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "build_held_publisher_draft_preview.py"
spec = importlib.util.spec_from_file_location("held_publisher_preview", TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def encoded(value):
    return (json.dumps(value, sort_keys=True) + "\n").encode()


def payloads():
    ss = {
        "schema_version": "trek-lit-five-first-party-edition-leads-v1",
        "proposal_only": True,
        "first_party_upstream_family": "publisher:simonandschuster.com",
        "first_party_upstream_family_count": 1,
        "candidate_work_count": 5,
        "publisher_edition_count": 5,
        "full_text_or_audio_read": False,
        "edition_completeness_verified": False,
        "private_source_edition_matches_verified": False,
        "copyrighted_story_text_or_art_reproduced": False,
        **{k: "NONE" for k in mod.EFFECT_FIELDS},
        "candidates": [],
    }
    titan = {
        "schema_version": "trek-lit-titan-five-nonfiction-artbook-editions-v1",
        "proposal_only": True,
        "first_party_publisher_lineage": "publisher:titanbooks.com",
        "first_party_publisher_family_count": 1,
        "local_work_candidate_count": 5,
        "publisher_edition_count": 5,
        "full_book_text_read": False,
        "full_artwork_read_or_stored": False,
        "edition_completeness_verified": False,
        "private_source_matches_verified": False,
        **{k: "NONE" for k in mod.EFFECT_FIELDS},
        "works": [],
    }
    simon_isbns = ["9780743453868", "9780743453851", "9780743420730", "9780743400817", "9780743419864"]
    titan_isbns = ["9781785659119", "9781785659348", "9781781166703", "9781785653872", "9781789095159"]
    for i, isbn in enumerate(simon_isbns):
        ss["candidates"].append({
            "local_work_candidate_id": f"lit-sim-{i}", "publisher_work_title": f"Title {i}",
            "publisher_creator_credits": [{"name": "Research Author", "role": "AUTHOR"}],
            "publisher_series": "Star Trek: Voyager",
            "source_url": f"https://www.simonandschuster.com/books/Title-{i}/Research-Author/Star-Trek-Voyager/{isbn}",
            "source_kind": "FIRST_PARTY_PUBLISHER_PRODUCT_METADATA", "edition_format": "EBOOK",
            "edition_isbn13": isbn, "edition_imprint": "Pocket Books/Star Trek",
            "edition_publication_date": "2002-10-04", "edition_extent_pages": 320,
            "source_discovery_state": "PUBLISHER_PAGE_READ_METADATA_ONLY",
            "local_edition_identity_status": "PUBLISHER_PRODUCT_ONLY_NO_PRIVATE_MATCH",
            "publisher_copy_anomaly": "AUTHOR_HEADER_JERI_VS_DESCRIPTION_TERI_UNRESOLVED" if i == 2 else None,
        })
    for i, isbn in enumerate(titan_isbns):
        titan["works"].append({
            "local_work_candidate_id": f"lit-titan-{i}", "publisher_display_title": f"Artbook {i}",
            "publisher_creator_credits": [{"name": "Research Artist", "role": "AUTHOR_ARTIST"}],
            "work_form": "NONFICTION_ILLUSTRATED_PRODUCTION_ART_BOOK",
            "publisher_source_url": f"https://titanbooks.com/{1000 + i}-star-trek-artbook/",
            "source_kind": "FIRST_PARTY_TITAN_PUBLISHER_PRODUCT_METADATA",
            "edition_isbn13": isbn, "edition_format": "HARDBACK",
            "edition_page_count_display": 208, "edition_published_us": "2018-11-27",
            "edition_published_uk": "2018-11-20",
            "source_discovery_state": "PUBLISHER_CATALOG_METADATA_ONLY",
            "private_manifestation_binding": "NOT_EVALUATED",
        })
    return ss, titan


class HeldPreviewTests(unittest.TestCase):
    def build(self, ss=None, titan=None):
        a, b = payloads()
        a = a if ss is None else ss
        b = b if titan is None else titan
        raw = (encoded(a), encoded(b))
        return mod.build(raw, tuple(hashlib.sha256(r).hexdigest() for r in raw),
                         require_pinned=False)

    def rejects(self, change, family=0):
        docs = list(payloads())
        change(docs[family])
        with self.assertRaises(ValueError):
            self.build(*docs)

    def test_ten_metadata_only_rows_with_source_lineage_and_no_admission(self):
        out = self.build()
        self.assertEqual(out["row_count"], 10)
        self.assertEqual(out["source_family_count"], 2)
        self.assertEqual(out["status"], "HELD_DRAFT_METADATA_PREVIEW_NOT_ACCEPTED")
        self.assertEqual(out["public_explorer_effect"], "NONE")
        self.assertEqual(out["coverage_effect"], "NONE")
        self.assertEqual(out["accepted_work_effect"], "NONE")
        self.assertEqual({r["source_pr"] for r in out["rows"]}, {494, 497})
        self.assertEqual(len({r["isbn13"] for r in out["rows"]}), 10)
        self.assertTrue(all(r["admission_effect"] == "NONE" and
                            r["full_text_status"] == "NOT_READ" for r in out["rows"]))
        self.assertEqual(len([r for r in out["rows"] if r["source_anomaly"]]), 1)

    def test_exact_source_digest_required_for_real_draft_projection(self):
        raws = tuple(encoded(d) for d in payloads())
        with self.assertRaisesRegex(ValueError, "digest"):
            mod.build(raws, ("0" * 64, "1" * 64), require_pinned=True)

    def test_standalone_preview_bytes_are_deterministic_valid_utf8_and_newline_terminated(self):
        preview = self.build()
        first = mod.encode_preview(preview)
        second = mod.encode_preview(preview)
        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertEqual(json.loads(first), preview)

    def test_semantic_promotions_are_fail_closed(self):
        self.rejects(lambda x: x.update(accepted_work_effect="ONE"))
        self.rejects(lambda x: x.update(full_text_or_audio_read=True))
        self.rejects(lambda x: x.update(proposal_only=False), 1)
        self.rejects(lambda x: x.update(private_source_matches_verified=True), 1)
        self.rejects(lambda x: x["candidates"][0].update(local_edition_identity_status="MATCHED"))
        self.rejects(lambda x: x["works"][0].update(private_manifestation_binding="MATCHED"), 1)

    def test_path_hosts_identity_and_duplicate_inputs_are_fail_closed(self):
        self.rejects(lambda x: x["candidates"][0].update(source_url="http://evil.test/"))
        self.rejects(lambda x: x["works"][0].update(publisher_source_url="https://titanbooks.com.evil.test/"), 1)
        self.rejects(lambda x: x["candidates"][0].update(edition_isbn13="9780000000000"))
        self.rejects(lambda x: x["works"][0].update(edition_isbn13="9781785659348"), 1)
        self.rejects(lambda x: x.update(first_party_upstream_family_count=2))
        self.rejects(lambda x: x["works"][0].update(work_form="NOVEL"), 1)
        self.rejects(lambda x: x["candidates"][0].update(publisher_copy_anomaly="CLEAR"))


if __name__ == "__main__":
    unittest.main()
