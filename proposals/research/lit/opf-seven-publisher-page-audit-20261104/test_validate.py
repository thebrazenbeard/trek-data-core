"""Hold-state regressions, not live web or private-source verification."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import validate as subject


class PublisherPageAuditTests(unittest.TestCase):
    def test_accepted_publisher_packet_matches_visible_product_fields(self):
        self.assertEqual(subject.validate(), (7, 8))

    def test_isbn13_format_checksum(self):
        self.assertTrue(all(subject.isbn13_valid(row[1]) for row in subject.EXPECTED))
        self.assertTrue(subject.isbn13_valid(subject.EBOOK_0110[0]))
        self.assertFalse(subject.isbn13_valid("9780743499973"))
        self.assertFalse(subject.isbn13_valid("97807434X9972"))

    def test_source_receipt_tampering_fails_closed(self):
        with tempfile.TemporaryDirectory() as place:
            root = Path(place)
            target = root / subject.SOURCE.relative_to(subject.ROOT)
            target.parent.mkdir(parents=True)
            shutil.copyfile(subject.SOURCE, target)
            doc = json.loads(target.read_text())
            doc["rows"][-1]["publisher_series_ordinal"] = 7
            target.write_text(json.dumps(doc))
            with self.assertRaisesRegex(ValueError, "pinned accepted held publisher proposal changed"):
                subject.validate(root)


if __name__ == "__main__":
    unittest.main()
