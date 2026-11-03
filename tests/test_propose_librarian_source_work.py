"""Proposal-only Librarian Source/Work bridge; fixtures are never admitted."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import source_custody_receipt as custody  # noqa: E402
import propose_librarian_source_work as librarian  # noqa: E402
from validate_librarian_registry import validate_registry  # noqa: E402


def declaration():
    return {
        "record_type": "work_identity_declaration", "schema_version": "1.0.0",
        "proposal_id": "proposal-synthetic-001", "work_candidate_id": "work-synthetic-001",
        "work_title": "Imaginary Synthetic Work", "work_type": "TEST_FIXTURE",
        "work_identity_note": "Test-only operator declaration without Trek content.",
        "work_identity_reference": None,
        "fixture_only": True,
    }


def request():
    return {
        "record_type": "source_custody_request", "schema_version": "1.0.0",
        "receipt_id": "receipt-synthetic-001", "source_candidate_id": "source-synthetic-001",
        "source_kind": "OTHER_SOURCE_BYTES", "locator_kind": "PRIVATE_OPAQUE",
        "source_locator": "private:fixture-opaque-001", "source_version": "fixture-v1",
        "edition_identity": "synthetic fixture, no Star Trek source",
        "provenance_family": "SYNTHETIC_ONLY", "independence_group": "SYNTHETIC_ONLY",
        "rights_basis_reported": "UNKNOWN", "observed_on": "2026-11-03",
        "declared_sha256": None,
    }


class ProposedLibrarianBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.content = b"Fixture-only arbitrary bytes. Not a Trek episode.\x00"
        self.source_file = self.root / "private-source.bin"
        self.source_file.write_bytes(self.content)
        self.req = request()
        self.receipt = custody.build_receipt(self.req, self.source_file)
        self.decl = declaration()

    def build(self):
        return librarian.build_proposal(self.req, self.receipt, self.decl, self.source_file)

    def test_replayed_bytes_generate_deterministic_valid_proposed_triad(self):
        proposal = self.build()
        self.assertEqual(proposal, self.build())
        s, w, b = proposal["source"], proposal["work"], proposal["source_work_binding"]
        self.assertEqual(s["content_hash"], "sha256:" + hashlib.sha256(self.content).hexdigest())
        self.assertEqual(s["status"], "PROPOSED")
        self.assertEqual(w["status"], "PROPOSED")
        self.assertEqual(b["lifecycle"], "PROPOSED")
        self.assertEqual(b["mapping_role"], "METADATA_ONLY")
        self.assertTrue(s["fixture_only"] and w["fixture_only"] and b["fixture_only"])
        self.assertEqual(b["basis"][0]["value"], s["content_hash"])
        self.assertEqual((b["source_id"], b["work_id"]), (s["source_id"], w["work_id"]))
        self.assertEqual(validate_registry([s], [w], [b], []), [])
        self.assertEqual(proposal["accepted_registry_effect"], "NONE")
        self.assertEqual(proposal["coverage_effect"], "NONE")
        self.assertEqual(proposal["rights_verification"], "NOT_PERFORMED")
        self.assertNotIn(str(self.root), json.dumps(proposal))
        self.assertNotIn(self.content.decode("latin1"), json.dumps(proposal))
        self.assertEqual(proposal["proposal_sha256"], hashlib.sha256(custody.canonical({k:v for k,v in proposal.items() if k != "proposal_sha256"})).hexdigest())

    def test_changed_bytes_rejected_before_proposal(self):
        self.source_file.write_bytes(self.content + b"tampered")
        with self.assertRaisesRegex(custody.Rejected, "receipt does not replay"):
            self.build()

    def test_declared_source_metadata_or_receipt_tampering_rejected(self):
        self.req["source_version"] = "different-version"
        with self.assertRaisesRegex(custody.Rejected, "receipt does not replay"):
            self.build()
        self.req = request()
        self.receipt["size_bytes"] += 1
        with self.assertRaisesRegex(custody.Rejected, "receipt does not replay"):
            self.build()

    def test_invalid_or_unbounded_work_identity_is_rejected(self):
        for key, value in (
            ("work_title", ""), ("work_type", []),
            ("work_identity_note", "unverified"),
            ("work_identity_reference", "https://user:secret@example.com/?token=123"),
            ("work_candidate_id", "../private"),
            ("proposal_id", "x" * 80),
            ("fixture_only", "false"),
            ("work_identity_note", r"C:\Users\Example\Private\source.mp4"),
            ("work_identity_note", "/home/example/private/episode.mkv"),
        ):
            self.decl = declaration()
            self.decl[key] = value
            with self.assertRaises(custody.Rejected, msg=key):
                self.build()

    def test_duplicate_ids_and_unexpected_fields_rejected(self):
        self.decl["work_candidate_id"] = "source-synthetic-001"
        with self.assertRaisesRegex(custody.Rejected, "unique"):
            self.build()
        self.decl = declaration()
        self.decl["acceptance_effect"] = "ACCEPTED"
        with self.assertRaisesRegex(custody.Rejected, "exact v1 fields"):
            self.build()

    def test_cli_produces_no_registry_files(self):
        request_file = self.root / "request.json"
        receipt_file = self.root / "receipt.json"
        declaration_file = self.root / "declaration.json"
        request_file.write_text(json.dumps(self.req), encoding="utf-8")
        receipt_file.write_text(json.dumps(self.receipt), encoding="utf-8")
        declaration_file.write_text(json.dumps(self.decl), encoding="utf-8")
        before = {p.name for p in self.root.iterdir()}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = librarian.main(["--request", str(request_file), "--receipt", str(receipt_file),
                                     "--source-file", str(self.source_file), "--work-declaration", str(declaration_file)])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.getvalue()), self.build())
        self.assertEqual({p.name for p in self.root.iterdir()}, before)

    def test_symlink_source_fails_closed(self):
        alias = self.root / "source-alias.bin"
        alias.symlink_to(self.source_file)
        with self.assertRaises(custody.Rejected):
            librarian.build_proposal(self.req, self.receipt, self.decl, alias)


if __name__ == "__main__":
    unittest.main()
