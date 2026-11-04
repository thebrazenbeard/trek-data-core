"""Synthetic tests for source-local, private converter-manifest links."""

import contextlib
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

from tools.inventory_converted_derivative_members import canonical, inventory_zip


TOOL = Path(__file__).resolve().parents[1] / "tools" / "private_lit_opf_manifest_crosswalk.py"
spec = importlib.util.spec_from_file_location("private_lit_opf_manifest_crosswalk", TOOL)
crosswalk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(crosswalk)


class PrivateManifestCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.private = Path(self.temp.name)
        self.private.chmod(0o700)
        self.archive = self.private / "converted.zip"
        self.original = self.private / "original-receipt.json"
        self.converted = self.private / "converted-receipt.json"
        self.output = self.private / "crosswalk.json"
        self.names = ["Alpha", "Beta"]
        self.manifest = [
            ("Alpha.lit", "Alpha.opf", "success"),
            ("Beta.lit", "Beta.opf", "partial_with_opf"),
        ]

    def make_sources(self, *, opf_names=None, manifest=None, json_manifest=None):
        if opf_names is None:
            opf_names = ["Alpha.opf", "Beta.opf"]
        if manifest is None:
            manifest = self.manifest
        json_books = [{
            "source": src, "opf_files": opf if isinstance(opf, list) else [opf], "status": status,
        } for src, opf, status in (json_manifest if json_manifest is not None else manifest)]
        text = io.StringIO()
        writer = csv.DictWriter(text, fieldnames=["source_lit", "status", "drm", "exit_code",
                                                  "opf_files", "output_file_count", "reason"])
        writer.writeheader()
        for src, opf, status in manifest:
            writer.writerow({"source_lit": src, "status": status, "drm": "1",
                             "exit_code": "0", "opf_files": opf, "output_file_count": "1",
                             "reason": ""})
        with ZipFile(self.archive, "w", ZIP_DEFLATED) as z:
            for opf in opf_names:
                z.writestr("converted/" + opf, b"SYNTHETIC OPF METADATA")
            z.writestr("manifest/book-records.json", json.dumps({"books": json_books}))
            z.writestr("manifest/records.csv", text.getvalue())
        orig_members = [{
            "member_id": f"original-local:lit:{i:04d}",
            "member_name_private": "source/" + name + ".lit",
            "member_type": ".lit",
            "member_sha256": hashlib.sha256(name.encode()).hexdigest(),
        } for i, name in enumerate(self.names, 1)]
        original = {
            "record_type": "PRIVATE_ORIGINAL_EBOOK_MEMBER_CUSTODY",
            "archive_sha256": "a" * 64,
            "members": orig_members,
            "members_sha256": hashlib.sha256(canonical(orig_members)).hexdigest(),
            "counts_by_extension": {".lit": len(orig_members), ".txt": 0},
            "source_work_binding": "UNRESOLVED", "coverage_effect": "NONE",
            "work_admission_effect": "NONE",
        }
        converted = inventory_zip(self.archive)
        self.write_receipt(self.original, original)
        self.write_receipt(self.converted, converted)

    @staticmethod
    def write_receipt(path, payload):
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        path.chmod(0o600)

    def cli(self, mode, *, expect_lit=2, expect_opf=2, expect_records=2):
        original = json.loads(self.original.read_text(encoding="utf-8"))
        converted = json.loads(self.converted.read_text(encoding="utf-8"))
        args = [mode, "--original-receipt", str(self.original),
                "--converted-receipt", str(self.converted),
                "--converted-zip", str(self.archive),
                "--expect-original-sha256", original["archive_sha256"],
                "--expect-converted-sha256", converted["archive_sha256"],
                "--expect-lit", str(expect_lit), "--expect-opf", str(expect_opf),
                "--expect-manifest-rows", str(expect_records)]
        args.extend(["--out", str(self.output)] if mode == "capture"
                    else ["--receipt", str(self.output)])
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = crosswalk.main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_explicit_manifest_links_and_partial_status_stay_source_local(self):
        self.make_sources()
        self.assertEqual(self.cli("capture")[0], 0)
        receipt = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(receipt["candidate_link_count"], 2)
        self.assertEqual(receipt["ambiguous_original_count"], 0)
        self.assertEqual(receipt["unresolved_original_count"], 0)
        self.assertEqual(receipt["orphan_converted_opf_count"], 0)
        self.assertEqual(receipt["partial_candidate_count"], 1)
        self.assertEqual(receipt["manifest_json_csv_consistent_record_count"], 2)
        self.assertEqual(receipt["work_admission_effect"], "NONE")
        self.assertEqual(receipt["coverage_effect"], "NONE")
        self.assertEqual(receipt["content_completeness"], "NOT_ESTABLISHED")
        self.assertNotIn("Alpha.lit", self.output.read_text(encoding="utf-8"))
        self.assertNotIn("Beta.opf", self.output.read_text(encoding="utf-8"))
        status, stdout, _ = self.cli("verify")
        self.assertEqual(status, 0)
        self.assertIn("VERIFIED", stdout)

    def test_unreferenced_opf_never_rescued_by_equal_counts_or_order(self):
        self.make_sources(opf_names=["Alpha.opf", "Unlisted.opf"])
        self.assertEqual(self.cli("capture")[0], 0)
        d = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(d["candidate_link_count"], 1)
        self.assertEqual(d["unresolved_original_count"], 1)
        self.assertEqual(d["orphan_converted_opf_count"], 1)
        self.assertEqual(d["links"][1]["link_status"], "UNRESOLVED_DECLARED_OPF_ABSENT")

    def test_duplicate_converter_source_is_ambiguous_not_a_selected_candidate(self):
        manifest = self.manifest + [("Alpha.lit", "Beta.opf", "success")]
        self.make_sources(manifest=manifest)
        self.assertEqual(self.cli("capture", expect_records=3)[0], 0)
        d = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(d["candidate_link_count"], 1)
        self.assertEqual(d["ambiguous_original_count"], 1)
        self.assertEqual(d["unresolved_original_count"], 0)
        self.assertEqual(len(d["links"][0]["converted_opf_member_ids"]), 2)

    def test_multi_target_converter_row_preserves_both_alternatives(self):
        self.make_sources(json_manifest=[
            ("Alpha.lit", ["Alpha.opf", "Beta.opf"], "success"),
            ("Beta.lit", "Beta.opf", "partial_with_opf"),
        ])
        self.assertEqual(self.cli("capture")[0], 0)
        d = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(d["ambiguous_original_count"], 1)
        self.assertEqual(d["candidate_link_count"], 1)
        self.assertEqual(d["links"][0]["link_status"], "AMBIGUOUS_MULTIPLE_TARGET_CLAIMS")
        self.assertEqual(len(d["links"][0]["converted_opf_member_ids"]), 2)

    def test_json_csv_disagreement_is_contested(self):
        self.make_sources(json_manifest=[
            ("Alpha.lit", "Beta.opf", "success"),
            ("Beta.lit", "Beta.opf", "partial_with_opf"),
        ])
        self.assertEqual(self.cli("capture")[0], 0)
        d = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(d["contested_original_count"], 1)
        self.assertEqual(d["candidate_link_count"], 1)
        self.assertEqual(d["links"][0]["link_status"], "CONTESTED_MANIFEST_EXPORTS")
        self.assertEqual(len(d["links"][0]["converted_opf_member_ids"]), 2)

    def test_private_mode_and_receipt_integrity_fail_closed(self):
        self.make_sources()
        self.original.chmod(0o644)
        self.assertEqual(self.cli("capture")[0], 1)
        self.assertFalse(self.output.exists())
        self.original.chmod(0o600)
        source = json.loads(self.original.read_text(encoding="utf-8"))
        source["members_sha256"] = "0" * 64
        self.write_receipt(self.original, source)
        self.assertEqual(self.cli("capture")[0], 1)

    def test_output_no_overwrite_and_archive_mutation_replay_fails(self):
        self.make_sources()
        self.assertEqual(self.cli("capture")[0], 0)
        self.assertEqual(self.cli("capture")[0], 1)
        with self.archive.open("ab") as stream:
            stream.write(b"mutation")
        self.assertEqual(self.cli("verify")[0], 1)


if __name__ == "__main__":
    unittest.main()
