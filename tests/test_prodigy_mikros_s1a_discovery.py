"""Fail-closed checks for an inferred, never-admitted studio title sequence."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_prodigy_mikros_s1a_discovery as discovery


INTRO = '<p>The first ten episodes of Star Trek: Prodigy Season 1 Volume 1 are available.</p>'
LIST = ('<p>The set includes&nbsp;<strong>“Lost and Found, Part I” and “Part II,” '
        '“Starstruck,” “Dreamcatcher,” “Terror Firma,” “Kobayashi,” '
        '“First Con-tact,” “Time Amok,”&nbsp;</strong>and&nbsp;'
        '<strong>“A Moral Star, Part 1” and “Part 2.”</strong></p>')
CAPTION = '<figure><figcaption>“Starstruck” Ep#103 — production still</figcaption></figure>'


def raw_page(body: str = INTRO + LIST, canonical: str = discovery.URL) -> bytes:
    return ('<html><head><link rel="canonical" href="' + canonical + '" /></head><body>' +
            body + '</body></html>' + ' ' * 10_000).encode("utf-8")


class MikrosVolumeOneTests(unittest.TestCase):
    def test_private_source_read_rejects_symlink_and_oversized_html_before_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            actual = directory / "actual.html"
            actual.write_bytes(raw_page(body=INTRO + LIST + CAPTION))
            shortcut = directory / "shortcut.html"
            shortcut.symlink_to(actual)
            with self.assertRaisesRegex(ValueError, "symlink forbidden"):
                discovery.ingest(shortcut)

            actual.write_bytes(b" " * 3_000_001)
            with self.assertRaisesRegex(ValueError, "bounded regular HTML"):
                discovery.ingest(actual)
            actual.write_bytes(raw_page(body=INTRO + LIST + CAPTION) + b" " * 500_000)
            with self.assertRaisesRegex(ValueError, "Mikros article outside bounded byte size"):
                discovery.ingest(actual)

    def test_private_source_read_rejects_inode_replacement_between_lstat_and_open(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            original = directory / "source.html"
            replacement = directory / "replacement.html"
            retired = directory / "original.html"
            valid = raw_page(body=INTRO + LIST + CAPTION)
            original.write_bytes(valid)
            replacement.write_bytes(valid)
            original_open = discovery.source_reader.os.open
            swapped = False

            def swap_before_open(path, flags, *args, **kwargs):
                nonlocal swapped
                if Path(path) == original and not swapped:
                    swapped = True
                    original.rename(retired)
                    replacement.rename(original)
                return original_open(path, flags, *args, **kwargs)

            with patch.object(discovery.source_reader.os, "open", side_effect=swap_before_open):
                with self.assertRaisesRegex(ValueError, "changed during open"):
                    discovery.ingest(original)
            self.assertTrue(swapped)
            self.assertEqual(retired.read_bytes(), valid)
            self.assertEqual(original.read_bytes(), valid)

    def test_exactly_ten_source_relative_title_candidates(self):
        rows = discovery.extract(raw_page())
        self.assertEqual([n for _, n, _ in rows], list(range(1, 11)))
        self.assertEqual(rows[1], (1, 2, "Lost and Found, Part II"))
        self.assertEqual(rows[9], (1, 10, "A Moral Star, Part 2"))
        data = discovery.bundle(rows)
        self.assertEqual(data["proposal_status"], "CANDIDATE_METADATA_ONLY")
        self.assertEqual(data["accepted_work_effect"], "NONE")
        self.assertEqual(data["roster_completeness"], "UNRESOLVED")
        self.assertFalse(data["observation"]["audiovisual_content_inspected"])

    def test_forged_missing_and_duplicate_canonicals_rejected(self):
        with self.assertRaisesRegex(ValueError, "canonical"):
            discovery.extract(raw_page(canonical="https://forged.invalid/story"))
        with self.assertRaisesRegex(ValueError, "canonical"):
            discovery.extract(raw_page().replace(b'rel="canonical"', b'rel="alternate"'))
        with self.assertRaisesRegex(ValueError, "canonical"):
            discovery.extract(raw_page().replace(b'</head>',
                b'<link rel="canonical" href="' + discovery.URL.encode() + b'" /></head>'))
        with self.assertRaisesRegex(ValueError, "duplicate HTML"):
            discovery.extract(raw_page().replace(b'rel="canonical"',
                b'rel="canonical" rel="canonical"'))

    def test_missing_or_ambiguous_source_scope_rejected(self):
        with self.assertRaisesRegex(ValueError, "scope"):
            discovery.extract(raw_page(body=LIST))
        with self.assertRaisesRegex(ValueError, "scope"):
            discovery.extract(raw_page(body=INTRO + LIST + LIST))
        with self.assertRaisesRegex(ValueError, "ten studio-listed"):
            discovery.extract(raw_page(body=INTRO + LIST.replace('“Time Amok,”', '')))
        with self.assertRaisesRegex(ValueError, "multipart"):
            discovery.extract(raw_page(body=INTRO + LIST.replace('“Part II,”', '“Other Part II,”')))

    def test_candidate_csv_and_receipt_consistency(self):
        self.assertIsNone(discovery.check())
        source = json.loads((discovery.ROOT / discovery.BASE / "index.json").read_text())
        self.assertEqual(source["listed_title_count"], 10)
        self.assertIn("INFERRED", source["ordinal_basis"])
        self.assertEqual(source["caption_exception"]["literal_label"], "Ep#103")
        self.assertEqual(source["caption_exception"]["origin"], "SAME_MIKROS_ARTICLE_FIGCAPTION")
        self.assertEqual(source["caption_exception"]["season_ordinal_or_independence_effect"], "NONE")
        self.assertEqual(source["admission_effect"], "NONE")
        csv_data = (discovery.ROOT / discovery.BASE / "mikros-s1a.csv").read_bytes()
        self.assertEqual(discovery.read_csv(csv_data)[0][2], "Lost and Found, Part I")
        with self.assertRaisesRegex(ValueError, "unexpected inferred local"):
            discovery.read_csv(csv_data.replace(b"1,1,", b"1,11,"))

    def test_caption_is_same_source_exception_not_general_ordinal_confirmation(self):
        raw = raw_page(body=INTRO + LIST + CAPTION)
        observed = discovery.caption_exception(raw)
        self.assertEqual(observed["literal_label"], "Ep#103")
        self.assertEqual(observed["season_ordinal_or_independence_effect"], "NONE")
        self.assertIn("INFERRED", discovery.index(raw, discovery.csv_bytes(discovery.extract(raw)))["ordinal_basis"])
        with self.assertRaisesRegex(ValueError, "caption label absent"):
            discovery.caption_exception(raw_page(body=INTRO + LIST))


if __name__ == "__main__":
    unittest.main()
