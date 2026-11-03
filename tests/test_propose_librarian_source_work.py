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
            ("work_title", r"Work C:\Users\Example\Private\source.mp4"),
            ("work_title", "Memo /etc/passwd"),
            ("work_title", "Episode|/private/secret-path"),
            ("work_title", "Episode(/opt/source.mkv)"),
            ("work_title", "Episode(/home/user/private.mp4)"),
            ("work_title", "Episode,/tmp/story"),
            ("work_title", "/opt/secret"),
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

    def test_synthetic_markers_cannot_be_declared_nonfixture(self):
        # No amount of operator assertion can turn a named synthetic fixture
        # into nonfixture custody evidence by changing only this one flag.
        for marker in ("provenance_family", "independence_group", "work_type"):
            with self.subTest(marker=marker):
                self.req = request()
                self.decl = declaration()
                self.decl["fixture_only"] = False
                if marker != "work_type":
                    self.req["provenance_family"] = "DECLARED_PUBLISHER"
                    self.req["independence_group"] = "DECLARED_PUBLISHER"
                    self.req[marker] = "SYNTHETIC_ONLY"
                    self.decl["work_type"] = "EPISODE"
                else:
                    self.req["provenance_family"] = "DECLARED_PUBLISHER"
                    self.req["independence_group"] = "DECLARED_PUBLISHER"
                self.receipt = custody.build_receipt(self.req, self.source_file)
                with self.assertRaisesRegex(custody.Rejected, "synthetic fixture"):
                    self.build()

    def test_nonfixture_declaration_remains_proposal_only(self):
        self.req.update(
            receipt_id="receipt-publisher-001", source_candidate_id="source-publisher-001",
            source_locator="private:publisher-opaque-001", source_version="edition-v1",
            edition_identity="Publisher edition metadata not authenticated",
            provenance_family="PUBLISHER_DECLARED_ONLY",
            independence_group="PUBLISHER_DECLARED_ONLY",
        )
        self.decl.update(
            proposal_id="proposal-publisher-001", work_candidate_id="work-publisher-001",
            work_title="Publisher-declared candidate", work_type="EPISODE",
            work_identity_note="Operator-proposed linkage awaiting independent review.",
            fixture_only=False,
        )
        self.receipt = custody.build_receipt(self.req, self.source_file)
        proposal = self.build()
        self.assertFalse(proposal["fixture_only"])
        self.assertEqual(proposal["source_work_binding"]["mapping_role"], "METADATA_ONLY")
        self.assertEqual(proposal["source_work_identity_state"], "DECLARED_NOT_INDEPENDENTLY_VERIFIED")
        self.assertEqual(proposal["accepted_registry_effect"], "NONE")

    def test_other_explicit_fixture_markers_cannot_be_relabelled_nonfixture(self):
        # A receipt re-hashed after changing provenance still reflects the same
        # fixture bytes; its surviving edition/version labels must not be hidden.
        self.req["provenance_family"] = "DECLARED_PUBLISHER"
        self.req["independence_group"] = "DECLARED_PUBLISHER"
        self.decl["work_type"] = "EPISODE"
        self.decl["fixture_only"] = False
        self.receipt = custody.build_receipt(self.req, self.source_file)
        with self.assertRaisesRegex(custody.Rejected, "synthetic fixture"):
            self.build()

        for owner, key, value in (
            ("request", "source_version", "fixture-v1"),
            ("request", "edition_identity", "synthetic fixture, no Star Trek source"),
            ("request", "source_locator", "private:fixture-opaque-001"),
            ("request", "receipt_id", "receipt-synthetic-001"),
            ("request", "source_candidate_id", "source-fixture-001"),
            ("work", "proposal_id", "proposal-synthetic-001"),
            ("work", "work_candidate_id", "work-fixture-001"),
            ("work", "work_title", "Imaginary Synthetic Work"),
            ("work", "work_identity_note", "Test-only operator declaration without Trek content."),
        ):
            with self.subTest(owner=owner, key=key):
                self.req = request()
                self.req.update(
                    receipt_id="receipt-publisher-001", source_candidate_id="source-publisher-001",
                    source_locator="private:publisher-opaque-001", source_version="edition-v1",
                    edition_identity="Publisher edition metadata not authenticated",
                    provenance_family="PUBLISHER_DECLARED_ONLY",
                    independence_group="PUBLISHER_DECLARED_ONLY",
                )
                self.decl = declaration()
                self.decl.update(
                    proposal_id="proposal-publisher-001", work_candidate_id="work-publisher-001",
                    work_title="Publisher-declared candidate", work_type="EPISODE",
                    work_identity_note="Operator-proposed linkage awaiting independent review.",
                    fixture_only=False,
                )
                (self.req if owner == "request" else self.decl)[key] = value
                self.receipt = custody.build_receipt(self.req, self.source_file)
                with self.assertRaisesRegex(custody.Rejected, "synthetic fixture"):
                    self.build()

    def test_legitimate_slash_in_title_is_preserved_without_private_path(self):
        self.decl["work_title"] = "Synthetic episode A/B"
        self.assertEqual(self.build()["work"]["title"], "Synthetic episode A/B")

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
