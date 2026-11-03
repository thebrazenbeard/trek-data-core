"""Adversarial fail-closed tests for exact S&S edition candidates."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("sns_seven_validate", HERE / "validate.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class SnsSevenEditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = MOD.load(HERE / "records.json")

    def rejects(self, alter, *, scan_accepted=False):
        changed = copy.deepcopy(self.packet)
        alter(changed)
        with self.assertRaises(ValueError):
            MOD.validate(changed, scan_accepted=scan_accepted)

    def test_actual_accepted_baseline_and_seven_distinct_isbns(self):
        self.assertEqual(MOD.validate(), 7)
        self.assertEqual(len({r["isbn13"] for r in self.packet["rows"]}), 7)

    def test_all_envelope_rights_and_admission_attacks_fail(self):
        variants = [
            ("source_body_archived", True), ("full_books_or_audio_consumed", True),
            ("copyright_full_text_published", True), ("public_cover_display_authorized", True),
            ("accepted_work_effect", "ADMITTED"), ("coverage_effect", "CLOSE_READ"),
            ("global_edition_equivalence_effect", "SAME_WORK"),
            ("role", "CONSOLIDATOR"), ("publisher", "unattributed"),
            ("source_family", "wikipedia"), ("retrieval_surface", "FULL_BOOK_READ"),
            ("description_digest_method", "SHA1"),
            ("observed_utc", "2026-11-02"), ("accepted_main_at_selection", "0" * 40),
            ("schema_version", "2.0"), ("proposal_only", False),
        ]
        for field, value in variants:
            with self.subTest(field=field):
                self.rejects(lambda p, f=field, v=value: p.update({f: v}))
        self.rejects(lambda p: p.update({"published_image_url": "https://example.invalid/cover.jpg"}))
        self.rejects(lambda p: p.pop("global_edition_equivalence_effect"))

    def test_exact_row_publisher_binding_and_cross_editions(self):
        for i in range(7):
            fields = {
                "isbn13": "9780000000000", "publisher_title": "Changed", "contributors": ["Fake"],
                "series": "Other", "format": "EBOOK", "imprint": "Other",
                "publication_date": "2020-01-01", "pages": 123,
                "runtime_minutes": 123, "narrator_credit": "Not on page",
                "source_url": "https://www.simonandschuster.com/other",
                "publisher_about_sha256": "f" * 64,
                "publisher_about_codepoints": 999,
                "cover_url_held": "https://d28hgpri8am2if.cloudfront.net/other.jpg",
                "cover_rights_state": "PUBLIC_USE_LICENSE_GRANTED",
                "text_rights_state": "FULL_TEXT_ALLOWED",
                "identity_state": "SAME_GLOBAL_WORK",
            }
            for field, value in fields.items():
                if self.packet["rows"][i][field] == value:
                    value = False
                with self.subTest(row=i, field=field):
                    self.rejects(lambda p, index=i, f=field, v=value:
                                 p["rows"][index].update({f: v}))

    def test_crossrow_reassignments_same_title_and_source_family(self):
        for i, j in ((2, 3), (3, 4), (5, 6), (0, 1)):
            for field in ("publisher_about_sha256", "cover_url_held", "source_url", "isbn13",
                          "format", "imprint", "publication_date", "runtime_minutes",
                          "identity_state"):
                if self.packet["rows"][i][field] == self.packet["rows"][j][field]:
                    continue
                with self.subTest(i=i, j=j, field=field):
                    self.rejects(lambda p, a=i, b=j, f=field:
                                 p["rows"][a].update({f: p["rows"][b][f]}))
        self.rejects(lambda p: p["rows"].reverse())
        self.rejects(lambda p: p["rows"].append(copy.deepcopy(p["rows"][0])))
        self.rejects(lambda p: p["rows"].pop())

    def test_url_credential_and_shape_forgery(self):
        for payload in (
            "https://d28hgpri8am2if.cloudfront.net/book_images/a.jpg?token=123",
            "http://d28hgpri8am2if.cloudfront.net/book_images/a.jpg",
            "https://evil.example/book_images/onix/cvr9781668066133/a.jpg",
            "https://d28hgpri8am2if.cloudfront.net@evil.example/book.jpg",
            "https://d28hgpri8am2if.cloudfront.net/book_images/a.jpg#tracking",
        ):
            self.rejects(lambda p, url=payload: p["rows"][2].update({"cover_url_held": url}))
        self.rejects(lambda p: p["rows"][0].update({"pages": True}))
        self.rejects(lambda p: p["rows"][1].update({"publisher_about_codepoints": True}))
        self.rejects(lambda p: p["rows"][4].update({"runtime_minutes": 99.0}))

    def test_accepted_collision_and_snapshot_drift_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path in MOD.SNAPSHOTS:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((MOD.REPO / path).read_bytes())
            for base in ("proposals/librarian", "proposals/research/lit", "explorer"):
                (root / base).mkdir(parents=True, exist_ok=True)
            self.assertEqual(MOD.validate(self.packet, root), 7)
            newfile = root / "proposals/librarian/another-batch.json"
            newfile.write_text(json.dumps({"isbn13": "9781797168432"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "accepted ISBN collision"):
                MOD.validate(self.packet, root)
            newfile.unlink()
            one = root / next(iter(MOD.SNAPSHOTS))
            one.write_bytes(one.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "accepted catalogue bytes drift"):
                MOD.validate(self.packet, root)

    def test_duplicate_raw_json_keys_rejected_in_normal_and_optimized_modes(self):
        raw = (HERE / "records.json").read_text(encoding="utf-8")
        for needle, injected in (
            ('"coverage_effect": "NONE"', '"coverage_effect": "AUDITED", "coverage_effect": "NONE"'),
            ('"public_cover_display_authorized": false',
             '"public_cover_display_authorized": true, "public_cover_display_authorized": false'),
            ('"identity_state": "ISBN_SPECIFIC_EDITION_NO_ACCEPTED_GLOBAL_WORK_LINK"',
             '"identity_state": "GLOBAL_WORK", "identity_state": "ISBN_SPECIFIC_EDITION_NO_ACCEPTED_GLOBAL_WORK_LINK"'),
        ):
            self.assertIn(needle, raw)
            with tempfile.TemporaryDirectory() as temp:
                malicious = Path(temp) / "malicious.json"
                malicious.write_text(raw.replace(needle, injected, 1), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                    MOD.load(malicious)
                for flag in ([], ["-O"]):
                    run = subprocess.run(
                        [sys.executable, *flag, str(HERE / "validate.py")],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                    cmd = [sys.executable, *flag, "-c",
                           "import sys,importlib.util;sp=importlib.util.spec_from_file_location('mod',sys.argv[1]);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.load(__import__('pathlib').Path(sys.argv[2]))",
                           str(HERE / "validate.py"), str(malicious)]
                    reject = subprocess.run(cmd, capture_output=True, text=True, check=False)
                    self.assertNotEqual(reject.returncode, 0)
                    self.assertIn("duplicate JSON key", reject.stderr)


if __name__ == "__main__":
    unittest.main()
