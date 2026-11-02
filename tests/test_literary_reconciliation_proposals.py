"""Synthetic tests for a private, proposal-only literary reconciliation lane."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "literary_proposals", ROOT / "tools" / "reconcile_literary_metadata.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

SHA = "a" * 64
OTHER_SHA = "b" * 64


def record(path="private/Story One.opf", title="Story One", creator="A. Writer",
           *, metadata_status="PARSED_UNVERIFIED", hold=False, opf_hash=SHA):
    item = {
        "record_type": "literary_work_metadata_candidate",
        "status": "CANDIDATE",
        "canonical_work_id": None,
        "accepted_corpus_effect": "NONE",
        "archive_member": path,
        "opf_sha256": opf_hash,
        "metadata_status": metadata_status,
        "metadata": {
            "title": title,
            "creators": [creator],
            "identifiers": ["synthetic-id"],
            "publishers": ["Fictional Publisher"],
            "dates": ["2001"],
            "languages": ["en"],
        },
        "original_lit_match": "MATCHED_STEM",
    }
    if hold:
        item["review_hold"] = "synthetic legacy correction"
        item["metadata_status"] = "PARSED_LEGACY_REVIEW_REQUIRED"
    return item


def inventory(*rows):
    return {
        "schema_version": "0.1.0",
        "proposal_only": True,
        "rights_status": "USER_SUPPLIED_FILES_RIGHTS_NOT_VERIFIED",
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "input_receipts": {"opf_archive_sha256": SHA, "original_archive_sha256": OTHER_SHA},
        "summary": {
            "opf_packages": len(rows),
            "parsed_metadata": sum(x["metadata"] is not None for x in rows),
            "review_holds": sum("review_hold" in x for x in rows),
            "matched_lit_stems": sum(x["original_lit_match"] == "MATCHED_STEM" for x in rows),
            "source_asset_extensions": {".lit": 1},
        },
        "candidates": list(rows),
    }


def citation(*supports):
    return {
        "provider": "Fictional Library Catalog",
        "url": "https://catalog.example.test/record/42",
        "retrieved_on": "2026-11-02",
        "supports": list(supports),
    }


def work(title="Story One"):
    return {"title": title, "creators": ["A. Writer"], "work_type": "NOVEL"}


def decision(candidate_id, form="SINGLE_WORK", works=None, parts=None, refs=None):
    return {
        "candidate_id": candidate_id,
        "publication_form": form,
        "works": [work()] if works is None else works,
        "parts": [] if parts is None else parts,
        "bibliographic_references": [citation("PUBLICATION_FORM", "WORK_STRUCTURE")]
        if refs is None else refs,
    }


def reviews(*items):
    return {"schema_version": "0.1.0", "reviews": list(items)}


class LiteraryProposalTests(unittest.TestCase):
    def test_unreviewed_candidate_separates_manifestation_edition_and_unknown_work(self):
        result = mod.build_proposals(inventory(record()))
        self.assertTrue(result["proposal_only"])
        self.assertEqual(result["summary"]["unresolved_structure"], 1)
        item = result["items"][0]
        self.assertEqual(item["publication_form"], "UNRESOLVED")
        self.assertEqual(item["work_candidates"], [])
        self.assertEqual(item["part_candidates"], [])
        self.assertEqual(item["edition_candidate"]["metadata"]["title"], "Story One")
        self.assertEqual(item["source_manifestation"]["kind"], "CONVERTED_OPF_DESCRIPTION")
        self.assertEqual(item["source_manifestation"]["independent_witness_count"], 0)
        self.assertEqual(item["source_manifestation"]["lineage"], "DERIVED_FROM_USER_SOURCE")
        for key in ("canonical_work_id", "canonical_edition_id", "canonical_source_id"):
            self.assertIsNone(item[key])
        for effect in ("accepted_work_effect", "accepted_source_binding_effect", "coverage_effect"):
            self.assertEqual(result[effect], "NONE")

    def test_exact_title_creator_cluster_is_review_hint_not_merge(self):
        result = mod.build_proposals(inventory(
            record("a/Story One.opf", opf_hash=SHA),
            record("b/Story One.opf", opf_hash=OTHER_SHA),
        ))
        a, b = result["items"]
        self.assertNotEqual(a["candidate_id"], b["candidate_id"])
        self.assertIsNotNone(a["possible_related_group"])
        self.assertEqual(a["possible_related_group"], b["possible_related_group"])
        self.assertEqual(a["work_candidates"], b["work_candidates"])
        self.assertEqual(a["work_candidates"], [])
        self.assertEqual(result["summary"]["related_review_groups"], 1)

    def test_single_work_review_is_only_a_candidate_even_with_citation(self):
        initial = mod.build_proposals(inventory(record()))["items"][0]
        result = mod.build_proposals(inventory(record()), reviews(decision(initial["candidate_id"])))
        item = result["items"][0]
        self.assertEqual(item["publication_form"], "SINGLE_WORK")
        self.assertEqual(item["structure_review"], "REVIEWER_PROPOSED_UNVERIFIED")
        self.assertEqual(len(item["work_candidates"]), 1)
        self.assertIsNone(item["work_candidates"][0]["canonical_work_id"])
        self.assertEqual(item["work_candidates"][0]["status"], "CANDIDATE")
        self.assertEqual(item["source_manifestation"]["independent_witness_count"], 0)
        self.assertEqual(result["accepted_source_binding_effect"], "NONE")

    def test_omnibus_anthology_and_multipart_have_distinct_work_shapes(self):
        item = mod.build_proposals(inventory(record()))["items"][0]
        cid = item["candidate_id"]
        for form in ("OMNIBUS_EDITION", "ANTHOLOGY_EDITION"):
            with self.subTest(form=form):
                review = decision(cid, form, works=[work("First Work"), work("Second Work")])
                result = mod.build_proposals(inventory(record()), reviews(review))["items"][0]
                self.assertEqual(len(result["work_candidates"]), 2)
                self.assertEqual(result["part_candidates"], [])
                self.assertTrue(all(w["canonical_work_id"] is None for w in result["work_candidates"]))
        multipart = decision(
            cid, "MULTIPART_SINGLE_WORK", works=[work("One Work")],
            parts=["Volume I", "Volume II"],
            refs=[citation("PUBLICATION_FORM", "WORK_STRUCTURE", "PART_STRUCTURE")],
        )
        item = mod.build_proposals(inventory(record()), reviews(multipart))["items"][0]
        self.assertEqual(len(item["work_candidates"]), 1)
        self.assertEqual(len(item["part_candidates"]), 2)
        self.assertEqual(item["part_candidates"][0]["work_candidate_id"],
                         item["work_candidates"][0]["candidate_id"])

    def test_bad_structure_and_uncited_claims_fail_closed(self):
        cid = mod.build_proposals(inventory(record()))["items"][0]["candidate_id"]
        bad = [
            decision(cid, "OMNIBUS_EDITION", works=[work()]),
            decision(cid, "ANTHOLOGY_EDITION", works=[work("Same"), work("Same")]),
            decision(cid, "SINGLE_WORK", works=[work(), work("Other")]),
            decision(cid, "SINGLE_WORK", parts=["Chapter 1"]),
            decision(cid, "MULTIPART_SINGLE_WORK", parts=["Volume I"]),
            decision(cid, "MULTIPART_SINGLE_WORK", parts=["Volume I", "Volume II"]),
            decision(cid, refs=[]),
            decision(cid, refs=[citation("EDITION_METADATA")]),
            decision(cid, refs=[{**citation("PUBLICATION_FORM", "WORK_STRUCTURE"),
                                 "url": "file:///private/ebooks.lit"}]),
        ]
        for index, item in enumerate(bad):
            with self.subTest(index=index), self.assertRaises(mod.ReconciliationError):
                mod.build_proposals(inventory(record()), reviews(item))

    def test_unknown_or_duplicate_review_target_rejected(self):
        cid = mod.build_proposals(inventory(record()))["items"][0]["candidate_id"]
        with self.assertRaises(mod.ReconciliationError):
            mod.build_proposals(inventory(record()), reviews(decision("PRIVATE-LIT-nonexistent")))
        with self.assertRaises(mod.ReconciliationError):
            mod.build_proposals(inventory(record()), reviews(decision(cid), decision(cid)))

    def test_unparsed_metadata_cannot_be_supplied_work_identity(self):
        row = record()
        row["metadata"] = None
        row["metadata_status"] = "REVIEW_REQUIRED"
        row["opf_sha256"] = None
        inp = inventory(row)
        cid = mod.build_proposals(inp)["items"][0]["candidate_id"]
        self.assertIn("OPF_METADATA_UNPARSED", mod.build_proposals(inp)["items"][0]["review_flags"])
        with self.assertRaises(mod.ReconciliationError):
            mod.build_proposals(inp, reviews(decision(cid)))

    def test_input_contract_rejects_acceptance_tampering_and_unsafe_metadata(self):
        for mutate in (
            lambda x: x.update(accepted_work_effect="ACCEPTED"),
            lambda x: x["candidates"][0].update(canonical_work_id="WORK-123"),
            lambda x: x["candidates"][0].update(status="ACCEPTED"),
            lambda x: x["candidates"][0].update(archive_member="../escape.opf"),
            lambda x: x["candidates"][0]["metadata"].update(description="Copyrighted prose"),
            lambda x: x["candidates"][0]["metadata"].update(title="X" * 501),
            lambda x: x["candidates"][0].update(metadata_status=[]),
        ):
            inp = inventory(record())
            mutate(inp)
            with self.assertRaises(mod.ReconciliationError):
                mod.build_proposals(inp)

    def test_input_review_hold_cannot_be_cleared_by_review_decision(self):
        inp = inventory(record(hold=True))
        cid = mod.build_proposals(inp)["items"][0]["candidate_id"]
        item = mod.build_proposals(inp, reviews(decision(cid)))["items"][0]
        self.assertIn("INPUT_REVIEW_HOLD", item["review_flags"])
        self.assertIn("LEGACY_XML_REPAIR_UNVERIFIED", item["review_flags"])

    def test_reject_duplicate_input_path_and_inconsistent_summary(self):
        with self.assertRaises(mod.ReconciliationError):
            mod.build_proposals(inventory(record(), record()))
        inp = inventory(record())
        inp["summary"]["opf_packages"] = 0
        with self.assertRaises(mod.ReconciliationError):
            mod.build_proposals(inp)

    def test_private_output_cli_nonoverwrite_mode_and_no_private_description(self):
        with tempfile.TemporaryDirectory() as temp:
            outer = Path(temp)
            inp, out = outer / "inventory.json", outer / "proposals.json"
            data = inventory(record())
            data["candidates"][0]["unexpected_private_description"] = "PRIVATE BODY SHOULD NOT EXPORT"
            inp.write_text(json.dumps(data), encoding="utf-8")
            cmd = [sys.executable, str(ROOT / "tools" / "reconcile_literary_metadata.py"),
                   "--inventory", str(inp), "--out", str(out)]
            previous = os.umask(0o022)
            try:
                first = subprocess.run(cmd, capture_output=True, text=True)
            finally:
                os.umask(previous)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)
            payload = out.read_text(encoding="utf-8")
            self.assertNotIn("PRIVATE BODY SHOULD NOT EXPORT", payload)
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("overwrite", second.stderr)
            self.assertEqual(json.loads(payload)["summary"]["items"], 1)

    def test_public_checkout_output_is_refused(self):
        with self.assertRaises(mod.ReconciliationError):
            mod.private_destination(ROOT / "proposals.json")
        with tempfile.TemporaryDirectory() as temp:
            nested_checkout = Path(temp) / "another-public-checkout"
            nested_checkout.mkdir()
            (nested_checkout / ".git").mkdir()
            (nested_checkout / ".git" / "HEAD").write_text("ref: refs/heads/main\n")
            with self.assertRaises(mod.ReconciliationError):
                mod.private_destination(nested_checkout / "proposals.json")

    def test_duplicate_json_keys_and_nonfinite_values_are_not_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "inventory.json"
            for data in ('{"schema_version":"0.1.0","schema_version":"0.2.0"}',
                         '{"value":NaN}'):
                with self.subTest(data=data):
                    path.write_text(data, encoding="utf-8")
                    with self.assertRaises(mod.ReconciliationError):
                        mod.read_private_json(path)

    def test_private_input_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "real.json"
            source.write_text(json.dumps(inventory(record())), encoding="utf-8")
            link = root / "linked.json"
            link.symlink_to(source)
            with self.assertRaises(mod.ReconciliationError):
                mod.read_private_json(link)

    def test_private_input_fifo_swap_is_nonblocking_and_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "inventory.json"
            source.write_text(json.dumps(inventory(record())), encoding="utf-8")
            genuine_open = os.open

            def swap_after_lstat(path, flags, *args, **kwargs):
                if Path(path) == source:
                    source.unlink()
                    os.mkfifo(source)
                return genuine_open(path, flags, *args, **kwargs)

            # With the historical blocking Path.open(), this swap could hang
            # indefinitely. The hardened code requires O_NONBLOCK and tests
            # the pinned descriptor's file kind before reading any bytes.
            with mock.patch.object(mod.os, "open", side_effect=swap_after_lstat):
                with self.assertRaises(mod.ReconciliationError):
                    mod.read_private_json(source)
            self.assertTrue(stat.S_ISFIFO(source.lstat().st_mode))

    def test_private_input_different_regular_inode_swap_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "inventory.json"
            source.write_text(json.dumps(inventory(record())), encoding="utf-8")
            prior = root / "original.json"
            genuine_open = os.open

            def swap_after_lstat(path, flags, *args, **kwargs):
                if Path(path) == source:
                    source.rename(prior)
                    source.write_text(json.dumps(inventory(record(title="Substituted"))),
                                      encoding="utf-8")
                return genuine_open(path, flags, *args, **kwargs)

            with mock.patch.object(mod.os, "open", side_effect=swap_after_lstat):
                with self.assertRaises(mod.ReconciliationError):
                    mod.read_private_json(source)
            self.assertTrue(prior.is_file())

    def test_parent_symlink_swap_cannot_redirect_private_proposal_into_public_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            outer = Path(temp)
            private_dir = outer / "private"
            private_dir.mkdir()
            moved = outer / "moved"
            inp = outer / "inventory.json"
            inp.write_text(json.dumps(inventory(record())), encoding="utf-8")
            leaf = f"synthetic-race-{outer.name}.json"
            target = private_dir / leaf
            escaped = ROOT / leaf

            def race(*args):
                private_dir.rename(moved)
                private_dir.symlink_to(ROOT, target_is_directory=True)
                return original_build(*args)

            original_build = mod.build_proposals
            try:
                with mock.patch.object(mod, "build_proposals", side_effect=race):
                    exit_code = mod.main(["--inventory", str(inp), "--out", str(target)])
                self.assertNotEqual(exit_code, 0)
                self.assertFalse(escaped.exists())
            finally:
                escaped.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
