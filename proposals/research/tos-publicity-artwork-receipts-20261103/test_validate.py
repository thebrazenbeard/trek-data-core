#!/usr/bin/env python3
"""Adversarial checks for the non-publishing TOS artwork packet."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from validate import DIRECTORY, PACKET, read_json, validate


class TestArtworkPacket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = read_json(PACKET)
        cls.directory = DIRECTORY.read_bytes()

    def modified(self):
        return copy.deepcopy(self.packet)

    def test_valid_packet(self):
        validate(self.modified(), self.directory)

    def test_mismatched_source_locator(self):
        row = self.modified()
        row["records"][0]["source_locator"] = "https://www.paramountplus.com/shows/star_trek/episodes/1/"
        with self.assertRaisesRegex(ValueError, "locator mismatch"):
            validate(row, self.directory)

    def test_mismatched_episode_identity(self):
        row = self.modified()
        row["records"][0]["directory_title"] = "Spock's Brain"
        with self.assertRaisesRegex(ValueError, "title/locator mismatch"):
            validate(row, self.directory)

    def test_rejected_unpinned_rights_page(self):
        row = self.modified()
        row["records"][0]["commons_pinned_revision"] = "https://commons.wikimedia.org/wiki/File:The_Paradise_Syndrome.jpg"
        with self.assertRaisesRegex(ValueError, "revision"):
            validate(row, self.directory)

    def test_forged_rights_tag(self):
        row = self.modified()
        row["records"][0]["commons_claimed_rights_tag"] = "CC0"
        with self.assertRaisesRegex(ValueError, "rights claim"):
            validate(row, self.directory)

    def test_cannot_promote_display(self):
        row = self.modified()
        row["records"][0]["public_display_eligible"] = True
        with self.assertRaisesRegex(ValueError, "public display"):
            validate(row, self.directory)

    def test_cannot_add_hotlink(self):
        row = self.modified()
        row["records"][0]["display_url"] = "https://example.org/image.jpg"
        with self.assertRaisesRegex(ValueError, "public display"):
            validate(row, self.directory)

    def test_cannot_promote_coverage(self):
        row = self.modified()
        row["coverage_effect"] = "CLOSE_READ"
        with self.assertRaisesRegex(ValueError, "unauthorized effect"):
            validate(row, self.directory)

    def test_cannot_add_unreviewed_field(self):
        row = self.modified()
        row["records"][0]["image_license_approved"] = True
        with self.assertRaisesRegex(ValueError, "schema changed"):
            validate(row, self.directory)

    def test_reject_tampered_directory(self):
        with self.assertRaisesRegex(ValueError, "directory bytes"):
            validate(self.modified(), self.directory + b" ")

    def test_reject_unverified_digest(self):
        row = self.modified()
        row["records"][1]["image_sha256"] = "f" * 64
        row["records"][1]["image_bytes"] = 13
        with self.assertRaisesRegex(ValueError, "extra image digests"):
            validate(row, self.directory)

    def test_reject_ambiguity_elision(self):
        row = self.modified()
        row["records"][5]["episode_link_basis"] = "EXPLICIT_COMMONS_DESCRIPTION"
        with self.assertRaisesRegex(ValueError, "inference distinction"):
            validate(row, self.directory)


if __name__ == "__main__":
    unittest.main()
