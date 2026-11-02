"""Synthetic fail-closed checks; does not attest publisher or source authority."""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_local_custody as custody  # noqa: E402
from check_local_custody import (  # noqa: E402
    CustodyError, MAX_CANDIDATE_BYTES, MAX_SNAPSHOT_BYTES, bounded_bytes,
    bounded_candidate_bytes, check_capture, publisher_slots, sha256,
)


def fake_publisher_html(**season_fields):
    season = {"@type": "TVSeason", "name": "Season 1", "episode": [
        {"@type": "TVEpisode", "episodeNumber": "1", "name": "The Cage"},
    ]}
    season.update(season_fields)
    payload = {"@type": "TVSeries", "containsSeason": season}
    return ('<script type="application/ld+json">'
            + json.dumps(payload) + '</script>').encode("utf-8")


def fake_candidate():
    return {
        "mission_id": "tos",
        "observation": {"primary_locator": "https://example.invalid/official-season-1",
                        "independence_group": "publisher:paramount"},
        "accepted_work_effect": "NONE",
        "accepted_source_binding_effect": "NONE",
        "coverage_effect": "NONE",
        "denominator_effect": "NONE",
        "episode_slots": [{"season": 1, "episode_number": 1, "title": "The Cage"}],
    }


def fake_capture_fixture(private: str):
    root = Path(private) / "repo"
    root.mkdir()
    snapshot_dir = Path(private) / "snapshots"
    snapshot_dir.mkdir()
    body = fake_publisher_html()
    (snapshot_dir / "snapshot.html").write_bytes(body)
    candidate_bytes = json.dumps(fake_candidate()).encode("utf-8")
    (root / "candidate.json").write_bytes(candidate_bytes)
    capture = {
        "snapshot_filename": "snapshot.html",
        "body_sha256": sha256(body),
        "body_octets": len(body),
        "candidate_path": "candidate.json",
        "candidate_sha256": sha256(candidate_bytes),
        "mission_id": "tos",
        "url": "https://example.invalid/official-season-1",
        "http_status": 200,
        "candidate_slots": 1,
    }
    return root, snapshot_dir, capture


class LocalCustodyBoundaryTests(unittest.TestCase):
    def test_matching_declared_season_and_episode(self):
        self.assertEqual(publisher_slots(fake_publisher_html(seasonNumber="1"), 1),
                         {1: "The Cage"})

    def test_conflicting_explicit_season_number_rejected(self):
        with self.assertRaisesRegex(CustodyError, "publisher seasonNumber 99"):
            publisher_slots(fake_publisher_html(seasonNumber="99"), 1)

    def test_conflicting_season_name_rejected(self):
        with self.assertRaisesRegex(CustodyError, "TVSeason name"):
            publisher_slots(fake_publisher_html(name="Season 99"), 1)

    def test_season_identity_absent_rejected(self):
        html = fake_publisher_html().replace(b'"name": "Season 1", ', b'')
        with self.assertRaisesRegex(CustodyError, "omits an inspectable season"):
            publisher_slots(html, 1)

    def test_symlink_snapshot_rejected(self):
        with tempfile.TemporaryDirectory() as private:
            body = Path(private) / "body.html"
            link = Path(private) / "link.html"
            body.write_bytes(fake_publisher_html())
            os.symlink(body, link)
            with self.assertRaises(CustodyError):
                bounded_bytes(link)

    def test_oversized_snapshot_rejected(self):
        with tempfile.TemporaryDirectory() as private:
            body = Path(private) / "oversized.html"
            with body.open("wb") as stream:
                stream.truncate(MAX_SNAPSHOT_BYTES + 1)
            with self.assertRaises(CustodyError):
                bounded_bytes(body)

    def test_matching_bounded_candidate_passes_synthetic_comparison(self):
        with tempfile.TemporaryDirectory() as private:
            root, snapshots, capture = fake_capture_fixture(private)
            with patch.object(custody, "REPO", root):
                result = check_capture(capture, snapshots)
            self.assertEqual(result["checked_candidate_slots"], 1)
            self.assertEqual(result["status"], "LOCAL_BYTE_AND_JSONLD_SLOT_MATCH_NOT_ADMITTED")

    def test_candidate_symlink_rejected_before_digest(self):
        with tempfile.TemporaryDirectory() as private:
            root, snapshots, capture = fake_capture_fixture(private)
            candidate = root / "candidate.json"
            real = root / "real.json"
            candidate.rename(real)
            candidate.symlink_to(real)
            with patch.object(custody, "REPO", root):
                with self.assertRaisesRegex(CustodyError, "candidate cannot be read safely"):
                    check_capture(capture, snapshots)

    def test_candidate_symlinked_parent_directory_rejected(self):
        with tempfile.TemporaryDirectory() as private:
            root, snapshots, capture = fake_capture_fixture(private)
            real_dir = root / "real"
            real_dir.mkdir()
            (root / "candidate.json").rename(real_dir / "candidate.json")
            (root / "linked").symlink_to(real_dir, target_is_directory=True)
            capture["candidate_path"] = "linked/candidate.json"
            with patch.object(custody, "REPO", root):
                with self.assertRaisesRegex(CustodyError, "candidate cannot be read safely"):
                    check_capture(capture, snapshots)

    def test_candidate_oversized_regular_file_rejected_before_digest(self):
        with tempfile.TemporaryDirectory() as private:
            root, snapshots, capture = fake_capture_fixture(private)
            with (root / "candidate.json").open("wb") as stream:
                stream.truncate(MAX_CANDIDATE_BYTES + 1)
            with patch.object(custody, "REPO", root):
                with self.assertRaisesRegex(CustodyError, "not a bounded regular file"):
                    check_capture(capture, snapshots)

    def test_candidate_relative_escape_rejected(self):
        with self.assertRaisesRegex(CustodyError, "candidate path escapes"):
            bounded_candidate_bytes(Path("../elsewhere.json"))


if __name__ == "__main__":
    unittest.main()
