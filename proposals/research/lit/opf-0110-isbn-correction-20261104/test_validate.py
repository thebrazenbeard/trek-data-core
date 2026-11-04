"""Synthetic-only, private-source-free regression for held OPF ISBN extraction."""

import unittest

from candidate_parser import extract_candidates, normalized_checksum_isbn
import validate as correction
from tools.inventory_opf_metadata import IntakeError


NS = "http://purl.org/metadata/dublin_core"


def fixture(*, identifier_tag="Identifier", literal="ISBN 0-7434-9997-2", others=""):
    return (f'<?xml version="1.0" encoding="utf-8"?>'
            f'<package xmlns:dc="{NS}"><metadata><dc-metadata>'
            f'<dc:Title>Sample Title</dc:Title>'
            f'<dc:{identifier_tag}>{literal}</dc:{identifier_tag}>{others}'
            f'</dc-metadata></metadata></package>').encode("utf-8")


class HeldIdentifierCorrectionTests(unittest.TestCase):
    def test_mixed_case_identifier_tag_is_not_lost(self):
        body = fixture(others=(
            '<dc:Identifier>urn:uuid:123e4567-e89b-12d3-a456-426614174000</dc:Identifier>'
            '<dc:identifier>isbn:0-7434-9997-2</dc:identifier>'))
        # A case-sensitive legacy-looking literal string filter *would* miss
        # the first tag. That is a synthetic mechanism, not proof of the
        # original owner-host extraction implementation.
        self.assertNotIn(b"<dc:identifier>ISBN 0-7434-9997-2", body)
        result = extract_candidates(body)
        self.assertEqual(result["isbn10_candidates"], ["0743499972"])
        self.assertEqual(result["isbn13_candidates"], [])
        self.assertEqual(result["source_xml_review_hold"], False)
        self.assertNotIn("uuid", str(result).lower())

    def test_lowercase_tag_and_checksum_failure(self):
        result = extract_candidates(fixture(identifier_tag="identifier", literal="isbn-10: 0 7434 9997 2"))
        self.assertEqual(result["isbn10_candidates"], ["0743499972"])
        self.assertEqual(extract_candidates(fixture(literal="ISBN 0-7434-9997-3"))["isbn10_candidates"], [])

    def test_no_scraping_book_prose_or_unsupported_freeform_identifiers(self):
        extra = ('<dc:Description>Story content should never be exported.</dc:Description>'
                 '<dc:Identifier>ebook-id:0743499972-not-an-isbn</dc:Identifier>')
        result = extract_candidates(fixture(literal="urn:uuid:123e4567-e89b-12d3-a456-426614174000", others=extra))
        self.assertEqual(result["isbn10_candidates"], [])
        self.assertEqual(result["isbn13_candidates"], [])
        self.assertEqual(result["source_xml_review_hold"], False)
        self.assertNotIn("Story content", str(result))

    def test_unbound_namespace_recovers_only_under_explicit_review_hold(self):
        no_namespace = fixture().replace(f' xmlns:dc="{NS}"'.encode(), b"")
        result = extract_candidates(no_namespace)
        self.assertEqual(result["isbn10_candidates"], ["0743499972"])
        self.assertTrue(result["source_xml_review_hold"])

    def test_known_official_ebook_vs_trade_product_remain_separate(self):
        self.assertEqual(extract_candidates(fixture())["isbn10_candidates"], ["0743499972"])
        self.assertNotEqual("9780743499972", "9781982134907")

    def test_same_token_in_isbn13_and_invalid_prefixed_free_text(self):
        self.assertEqual(normalized_checksum_isbn("ISBN-13: 978-0-7434-9997-2"), "9780743499972")
        self.assertIsNone(normalized_checksum_isbn("UUID ISBN 0-7434-9997-2"))
        self.assertIsNone(normalized_checksum_isbn("http://example.invalid/9780743499972"))

    def test_unsafe_external_entity_not_resolved(self):
        unsafe = (b'<!DOCTYPE package [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
                  b'<package xmlns:dc="http://purl.org/dc/elements/1.1/">'
                  b'<metadata><dc:Title>x</dc:Title><dc:Identifier>&xxe;</dc:Identifier>'
                  b'</metadata></package>')
        with self.assertRaises(IntakeError):
            extract_candidates(unsafe)

    def test_held_correction_matches_accepted_source_and_publisher(self):
        correction.validate()


if __name__ == "__main__":
    unittest.main()
