"""Synthetic-only, fail-closed bibliographic hypothesis tests."""

from __future__ import annotations

import hashlib
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
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
SPEC = importlib.util.spec_from_file_location(
    "private_txt_crosswalk", ROOT / "tools" / "reconcile_private_txt_opf_titles.py",
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def zip_fixture(path: Path, members):
    with ZipFile(path, "w") as archive:
        for name, data in members:
            archive.writestr(name, data)


def opf(title: str, creator: str = "Author"):
    return (f'<package xmlns:dc="http://purl.org/dc/elements/1.1/">'
            f'<metadata><dc:title>{title}</dc:title><dc:creator>{creator}</dc:creator>'
            f'</metadata></package>').encode("utf-8")


def ledger_fixture(path: Path, original_zip: Path) -> str:
    with ZipFile(original_zip) as archive:
        files = sorted((f for f in archive.infolist() if not f.is_dir()),
                       key=lambda f: mod._member_key(f.filename))
        rows = [{
            "member_id": f"member:{i:05d}",
            "media_hint": Path(f.filename).suffix.lstrip(".").upper(),
            "member_name_sha256": hashlib.sha256(f.filename.encode()).hexdigest(),
            "uncompressed_bytes": f.file_size,
            "compressed_bytes": f.compress_size,
            "crc32": f"{f.CRC:08x}",
            "byte_sha256": hashlib.sha256(archive.read(f)).hexdigest(),
            "canonical_source_id": None,
            "canonical_work_id": None,
        } for i, f in enumerate(files, 1)]
    ledger = {
        "record_type": "private_ebook_member_custody_inventory",
        "schema_version": "0.1.0",
        "proposal_only": True,
        "source_admission_effect": "NONE",
        "work_identity_effect": "NONE",
        "source_work_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "container_sha256": hashlib.sha256(original_zip.read_bytes()).hexdigest(),
        "member_receipts": rows,
    }
    path.write_text(json.dumps(ledger), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_case(temp: str, original_members, opf_members):
    folder = Path(temp)
    original, converted, ledger = (folder / "original.zip", folder / "converted.zip",
                                   folder / "private-ledger.json")
    zip_fixture(original, original_members)
    zip_fixture(converted, opf_members)
    ledger_sha = ledger_fixture(ledger, original)
    original_sha = hashlib.sha256(original.read_bytes()).hexdigest()
    converted_sha = hashlib.sha256(converted.read_bytes()).hexdigest()
    manifest = folder / "manifest.md"
    manifest.write_text(f"accepted-original {original_sha} accepted-opf {converted_sha}",
                        encoding="utf-8")
    return original, converted, ledger, original_sha, converted_sha, ledger_sha, manifest


def run_case(value):
    original, opfzip, ledger, sha_original, sha_opf, sha_ledger, manifest = value
    with mock.patch.object(mod, "MANIFEST", manifest):
        return mod.reconcile(original, opfzip, ledger,
                             expected_original=sha_original,
                             expected_opf=sha_opf,
                             expected_ledger=sha_ledger)


class PrivateTxtCrosswalkTests(unittest.TestCase):
    def test_exact_title_normalization_unique_and_no_source_leaks(self):
        with tempfile.TemporaryDirectory() as temp:
            case = build_case(temp, [
                ("source/Caf\u00e9 Trek.txt", b"copyrighted story remains opaque"),
                ("source/Other Thing.txt", b"private chapter text"),
                ("source/Unrelated.lit", b"opaque binary"),
            ], [
                ("opf/1/a.opf", opf("CAF\u00c9--TREK")),
                ("opf/2/b.opf", opf("Never Matching")),
            ])
            result = run_case(case)
            s = result["summary"]
            self.assertEqual(s["txt_file_observations"], 2)
            self.assertEqual(s["unique_exact_title_candidates_unverified"], 1)
            self.assertEqual(s["ambiguous_exact_title_txt_observations"], 0)
            self.assertEqual(s["no_exact_title_txt_observations"], 1)
            self.assertEqual(result["coverage_effect"], "NONE")
            self.assertEqual(result["accepted_work_effect"], "NONE")
            value = json.dumps(result)
            for private in ("Caf\u00e9 Trek", "CAF\u00c9", "source/", "copyrighted",
                            "private chapter", "Author", "Never Matching"):
                self.assertNotIn(private, value)

    def test_same_title_multiple_creators_and_txt_duplicates_are_ambiguous(self):
        with tempfile.TemporaryDirectory() as temp:
            case = build_case(temp, [
                ("part1/The Search.txt", b"unique text1"),
                ("part2/The Search.txt", b"unique text2"),
            ], [
                ("opf/1/a.opf", opf("The Search", creator="Creator A")),
                ("opf/2/b.opf", opf("The Search", creator="Creator B")),
            ])
            result = run_case(case)
            self.assertEqual(result["summary"]["ambiguous_exact_title_txt_observations"], 2)
            self.assertEqual(result["summary"]["unique_exact_title_candidates_unverified"], 0)
            self.assertTrue(all(len(row["opf_ordinals"]) == 2
                                for row in result["txt_candidate_rows"]))

    def test_one_to_many_does_not_claim_equivalent_editions(self):
        with tempfile.TemporaryDirectory() as temp:
            case = build_case(temp, [("source/Anthology.txt", b"stories")], [
                ("opf/a/a.opf", opf("Anthology")),
                ("opf/b/b.opf", opf("Anthology")),
            ])
            value = run_case(case)
            self.assertEqual(value["summary"]["ambiguous_exact_title_txt_observations"], 1)
            self.assertEqual(value["txt_candidate_rows"][0]["edition_equivalence_effect"], "NONE")

    def test_no_auto_prefix_stripping_articles_or_cross_script_confusables(self):
        with tempfile.TemporaryDirectory() as temp:
            case = build_case(temp, [
                ("source/Star Trek - Genesis.txt", b"sample"),
                ("source/A Return.txt", b"sample"),
                ("source/\u0391lpha.txt", b"sample"),  # Greek Alpha, not Latin A
            ], [
                ("opf/1/a.opf", opf("Genesis")),
                ("opf/2/b.opf", opf("Return")),
                ("opf/3/c.opf", opf("Alpha")),
            ])
            s = run_case(case)["summary"]
            self.assertEqual(s["no_exact_title_txt_observations"], 3)
            self.assertEqual(s["unique_exact_title_candidates_unverified"], 0)

    def test_opf_namespace_repair_hold_preserved_as_aggregate(self):
        with tempfile.TemporaryDirectory() as temp:
            old = (b"<package><metadata><dc-metadata>"
                   b"<dc:Title>Legacy Book</dc:Title></dc-metadata></metadata></package>")
            case = build_case(temp, [("source/Legacy Book.txt", b"story")],
                              [("opf/old/old.opf", old)])
            value = run_case(case)
            self.assertEqual(value["summary"]["opf_metadata_review_holds"], 1)
            self.assertEqual(value["summary"]["unique_exact_title_candidates_unverified"], 1)
            self.assertEqual(value["summary"]["txt_candidates_touching_opf_metadata_review_hold"], 1)
            self.assertTrue(value["txt_candidate_rows"][0]["opf_metadata_review_required"])

    def test_wrong_custody_digests_and_symlink_paths_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            case = build_case(temp, [("source/Book.txt", b"story")],
                              [("opf/book.opf", opf("Book"))])
            original, converted, ledger, so, sc, sl, manifest = case
            with mock.patch.object(mod, "MANIFEST", manifest):
                with self.assertRaises(mod.IntakeError):
                    mod.reconcile(original, converted, ledger,
                                  expected_original=so, expected_opf=sc,
                                  expected_ledger="0" * 64)
                alias = Path(temp) / "alias.zip"
                alias.symlink_to(original)
                with self.assertRaises(OSError):
                    mod.reconcile(alias, converted, ledger,
                                  expected_original=so, expected_opf=sc,
                                  expected_ledger=sl)

    def test_converted_opf_path_swap_cannot_change_parsed_source(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source = folder / "converted.zip"
            alternate = folder / "alternate.zip"
            moved = folder / "moved.zip"
            zip_fixture(source, [("opf/a/a.opf", opf("Original Title"))])
            zip_fixture(alternate, [("opf/b/b.opf", opf("Swapped Title"))])
            expected = hashlib.sha256(source.read_bytes()).hexdigest()
            original_parser = mod.build_opf_inventory

            def swap_before_helper_parses(pinned_path):
                source.rename(moved)
                alternate.rename(source)
                return original_parser(pinned_path)

            with mock.patch.object(mod, "build_opf_inventory",
                                   side_effect=swap_before_helper_parses):
                with self.assertRaisesRegex(mod.IntakeError, "changed during parsing"):
                    mod._pinned_opf_inventory(source, expected)
            self.assertNotEqual(hashlib.sha256(source.read_bytes()).hexdigest(), expected)

    def test_converted_opf_leaf_symlink_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            source, alias = folder / "converted.zip", folder / "alias.zip"
            zip_fixture(source, [("opf/a/a.opf", opf("Book Title"))])
            alias.symlink_to(source)
            expected = hashlib.sha256(source.read_bytes()).hexdigest()
            with self.assertRaises(OSError):
                mod._pinned_opf_inventory(alias, expected)

    def test_private_output_mode_and_public_checkout_denial(self):
        with tempfile.TemporaryDirectory() as temp:
            case = build_case(temp, [("source/Book.txt", b"copyrighted words")],
                              [("opf/book.opf", opf("Book"))])
            value = run_case(case)
            output = Path(temp) / "private-result.json"
            mod._write_private(output, value)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertNotIn("copyrighted words", output.read_text())
            with self.assertRaises(mod.IntakeError):
                mod._write_private(output, value)
            with self.assertRaises(mod.IntakeError):
                mod._write_private(ROOT / "oops.json", value)

    def test_tainted_prior_byte_receipt_is_not_accepted_even_if_rehashed(self):
        with tempfile.TemporaryDirectory() as temp:
            case = build_case(temp, [("source/Book.txt", b"test bytes")],
                              [("opf/book.opf", opf("Book"))])
            original, converted, ledger, so, sc, _sl, manifest = case
            baseline = ledger.read_text(encoding="utf-8")
            for mutation in (
                lambda d: d.update(work_identity_effect="ACCEPTED"),
                lambda d: d["member_receipts"][0].update(byte_sha256="not-a-hash"),
                lambda d: d["member_receipts"][0].update(canonical_work_id="fake"),
            ):
                with self.subTest(mutation=mutation):
                    value = json.loads(baseline)
                    mutation(value)
                    ledger.write_text(json.dumps(value), encoding="utf-8")
                    new_sha = hashlib.sha256(ledger.read_bytes()).hexdigest()
                    with self.assertRaises(mod.IntakeError):
                        run_case((original, converted, ledger, so, sc, new_sha, manifest))


if __name__ == "__main__":
    unittest.main()
