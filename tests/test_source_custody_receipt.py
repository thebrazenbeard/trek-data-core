"""Adversarial tests for local byte custody without corpus admission."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest


MODULE = Path(__file__).resolve().parents[1] / "tools" / "source_custody_receipt.py"
spec = importlib.util.spec_from_file_location("source_custody_receipt", MODULE)
custody = importlib.util.module_from_spec(spec)
spec.loader.exec_module(custody)


def request() -> dict:
    return {
        "record_type": "source_custody_request", "schema_version": "1.0.0",
        "receipt_id": "source-receipt-synthetic-001",
        "source_candidate_id": "source-synthetic-001",
        "source_kind": "AUDIOVISUAL_EPISODE",
        "locator_kind": "PRIVATE_OPAQUE",
        "source_locator": "private:source-synthetic-001",
        "source_version": "synthetic-master-v1",
        "edition_identity": "synthetic fixture edition, not Star Trek",
        "provenance_family": "SYNTHETIC_TEST_FIXTURE",
        "independence_group": "SYNTHETIC_TEST_FIXTURE",
        "rights_basis_reported": "OWNED_COPY",
        "observed_on": "2026-11-03",
        "declared_sha256": None,
    }


class SourceCustodyReceiptTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.root = Path(self.td.name)
        self.source = self.root / "synthetic-source.bin"
        self.raw = b"SYNTHETIC TEST FIXTURE: not Star Trek source media.\x00\xff"
        self.source.write_bytes(self.raw)
        self.request_path = self.root / "request.json"
        self.request_path.write_text(json.dumps(request()), encoding="utf-8")
        self.receipt_path = self.root / "receipt.json"

    def capture(self, *, request_path=None, source=None):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = custody.main(["capture", "--request", str(request_path or self.request_path),
                               "--source-file", str(source or self.source)])
        return rc, out.getvalue()

    def verify(self, *, receipt_path=None, request_path=None, source=None):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = custody.main(["verify", "--request", str(request_path or self.request_path),
                               "--source-file", str(source or self.source),
                               "--receipt", str(receipt_path or self.receipt_path)])
        return rc, out.getvalue()

    def make_receipt(self):
        code, output = self.capture()
        self.assertEqual(code, 0)
        receipt = json.loads(output)
        self.receipt_path.write_text(output, encoding="utf-8")
        return receipt

    def test_real_local_hash_and_replay_are_deterministic(self):
        receipt = self.make_receipt()
        self.assertEqual(receipt["content_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(receipt["size_bytes"], len(self.raw))
        self.assertEqual(receipt["acceptance_effect"], "NONE")
        self.assertEqual(receipt["coverage_effect"], "NONE")
        self.assertEqual(receipt["rights_verification"], "NOT_PERFORMED")
        self.assertEqual(receipt["hash_scope"], "EXACT_LOCAL_FILE_BYTES")
        self.assertEqual(receipt["source_metadata_verification"], "DECLARED_NOT_INDEPENDENTLY_VERIFIED")
        self.assertEqual(self.verify()[0], 0)
        self.assertEqual(self.capture()[1], self.capture()[1])
        self.assertNotIn(str(self.root), json.dumps(receipt))
        self.assertNotIn("SYNTHETIC TEST FIXTURE:", json.dumps(receipt))
        self.assertNotIn("work_id", receipt)

    def test_changed_bytes_and_false_declared_hash_fail_closed(self):
        receipt = self.make_receipt()
        self.source.write_bytes(self.raw + b"altered")
        self.assertEqual(self.verify()[0], 1)
        self.source.write_bytes(self.raw)
        bad = request()
        bad["declared_sha256"] = "0" * 64
        self.request_path.write_text(json.dumps(bad), encoding="utf-8")
        self.assertEqual(self.capture()[0], 1)
        self.assertNotEqual(receipt["content_sha256"], "0" * 64)

    def test_tampered_receipt_or_metadata_fails_replay(self):
        receipt = self.make_receipt()
        tampered = copy.deepcopy(receipt)
        tampered["source_version"] = "different-edition"
        self.receipt_path.write_text(json.dumps(tampered), encoding="utf-8")
        self.assertEqual(self.verify()[0], 1)
        self.receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        altered = request()
        altered["edition_identity"] = "different edition"
        self.request_path.write_text(json.dumps(altered), encoding="utf-8")
        self.assertEqual(self.verify()[0], 1)

    def test_symlink_fifo_and_directory_are_rejected(self):
        link = self.root / "linked.bin"
        link.symlink_to(self.source)
        self.assertEqual(self.capture(source=link)[0], 1)
        self.assertEqual(self.capture(source=self.root)[0], 1)
        if hasattr(os, "mkfifo"):
            fifo = self.root / "pipe"
            os.mkfifo(fifo)
            self.assertEqual(self.capture(source=fifo)[0], 1)

    def test_empty_source_is_not_a_custody_witness(self):
        self.source.write_bytes(b"")
        self.assertEqual(self.capture()[0], 1)

    def test_invalid_public_url_and_missing_lineage_are_rejected(self):
        bad = request()
        bad.update(locator_kind="PUBLIC_HTTPS", source_locator="https://user:secret@localhost/private?token=123")
        self.request_path.write_text(json.dumps(bad), encoding="utf-8")
        self.assertEqual(self.capture()[0], 1)

    def test_malformed_field_types_fail_without_uncaught_exceptions(self):
        for field in ("source_kind", "rights_basis_reported", "locator_kind"):
            bad = request()
            bad[field] = []
            self.request_path.write_text(json.dumps(bad), encoding="utf-8")
            self.assertEqual(self.capture()[0], 1, field)
        bad = request()
        bad["independence_group"] = ""
        self.request_path.write_text(json.dumps(bad), encoding="utf-8")
        self.assertEqual(self.capture()[0], 1)

    def test_duplicate_json_keys_are_rejected(self):
        self.request_path.write_text('{"record_type":"source_custody_request", "record_type":"fake"}',
                                     encoding="utf-8")
        self.assertEqual(self.capture()[0], 1)

    def test_oversized_integer_json_rejects_without_traceback(self):
        # CPython raises ValueError for an integer longer than its digit limit.
        self.request_path.write_text('{"number":' + '9' * 5000 + '}', encoding="utf-8")
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            status, _ = self.capture()
        self.assertEqual(status, 1)
        self.assertIn("SOURCE_CUSTODY_REJECTED:", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())

    def test_hardlink_alias_is_same_bytes_not_independent_corroboration(self):
        alias = self.root / "same-inode.bin"
        os.link(self.source, alias)
        self.assertEqual(self.capture()[1], self.capture(source=alias)[1])
        self.assertEqual(self.source.stat().st_ino, alias.stat().st_ino)

    def test_json_through_symlinked_parent_is_rejected(self):
        real_dir = self.root / "private-input"
        real_dir.mkdir()
        original = real_dir / "request.json"
        original.write_text(json.dumps(request()), encoding="utf-8")
        alias = self.root / "linked-input-dir"
        alias.symlink_to(real_dir, target_is_directory=True)
        self.assertEqual(self.capture(request_path=alias / "request.json")[0], 1)

    def test_private_paths_cannot_be_copied_into_receipt_metadata(self):
        for field in ("source_version", "edition_identity", "provenance_family", "independence_group"):
            for leaked in (r"C:\Users\Example\Private\book.lit", "/home/example/private/book.epub"):
                bad = request()
                bad[field] = leaked
                self.request_path.write_text(json.dumps(bad), encoding="utf-8")
                self.assertEqual(self.capture()[0], 1, (field, leaked))


if __name__ == "__main__":
    unittest.main()
