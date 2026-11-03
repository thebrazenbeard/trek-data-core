"""The historical Open Library source receipt must survive additive Picard rows.

These tests never reauthorize artwork or rewrite the source proposal's original
1,214-row directory snapshot. Any drift outside the exactly two new source-
local publisher ISBN observations must invalidate the release compatibility.
"""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools import build_unified_discovery as discovery
from tools import validate_artwork_release as artwork


ROOT = Path(__file__).resolve().parents[1]


class HistoricalOpenLibraryDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.packets = (artwork.OL_SOURCE_PACKET,
                        "explorer/discovery-catalog.json",
                        str(discovery.PICARD_COMPANIONS))
        for relative in self.packets:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        self.packet = json.loads((self.root / artwork.OL_SOURCE_PACKET).read_text(encoding="utf-8"))

    def write_directory(self, change):
        path = self.root / "explorer/discovery-catalog.json"
        current = json.loads(path.read_text(encoding="utf-8"))
        change(current)
        path.write_text(json.dumps(current, sort_keys=True, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")

    def test_exact_additive_two_rows_preserve_original_custody_receipt(self):
        artwork._historical_directory_receipt_intact(self.root, self.packet)
        self.assertEqual(self.packet["source_catalog_sha256"], artwork.HISTORICAL_OL_DIRECTORY_SHA256)
        self.assertEqual(self.packet["source_catalog_commit"], artwork.HISTORICAL_OL_DIRECTORY_COMMIT)
        current = json.loads((self.root / "explorer/discovery-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(current["counts_by_medium"]["LITERATURE"], 11)
        self.assertEqual(current["row_count"], 1216)

    def test_invariant_breaking_directory_mutations_fail_closed(self):
        def picard_indices(d):
            return [i for i, row in enumerate(d["rows"])
                    if row["row_id"] in {
                        "literature:proposed-lit-picard-the-dark-veil",
                        "literature:proposed-lit-picard-rogue-elements"}]

        changes = (
            lambda d: d["rows"][0].__setitem__("title", "Injected into historical source"),
            lambda d: d["rows"].__setitem__(slice(0, 2), [d["rows"][1], d["rows"][0]]),
            lambda d: d["rows"][picard_indices(d)[0]].__setitem__("title", "False Picard edition"),
            lambda d: d["rows"][picard_indices(d)[1]]["details"].__setitem__(0, "Wrong ISBN"),
            lambda d: d["rows"].__setitem__(slice(*[picard_indices(d)[0], picard_indices(d)[1]+1]),
                                                    [d["rows"][picard_indices(d)[1]],
                                                     d["rows"][picard_indices(d)[0]]]),
            lambda d: d["rows"].pop(picard_indices(d)[0]),
            lambda d: d["rows"].append(copy.deepcopy(d["rows"][picard_indices(d)[0]])),
            lambda d: d.__setitem__("coverage_effect", "CLOSE_READ"),
            lambda d: d["counts_by_medium"].__setitem__("LITERATURE", 12),
            lambda d: d["source_digests"][0].__setitem__("sha256", "0" * 64),
        )
        for mutate in changes:
            with self.subTest(line=mutate.__code__.co_firstlineno):
                # Each test starts from the original approved 1,216-row build.
                shutil.copyfile(ROOT / "explorer/discovery-catalog.json",
                                self.root / "explorer/discovery-catalog.json")
                self.write_directory(mutate)
                with self.assertRaises(ValueError):
                    artwork._historical_directory_receipt_intact(self.root, self.packet)

    def test_source_packet_or_additional_publisher_source_cannot_self_approve(self):
        packet_path = self.root / artwork.OL_SOURCE_PACKET
        original = packet_path.read_bytes()
        tampered = json.loads(original)
        tampered["source_catalog_sha256"] = "0" * 64
        packet_path.write_text(json.dumps(tampered), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "immutable Open Library source packet changed"):
            artwork._historical_directory_receipt_intact(self.root, tampered)
        packet_path.write_bytes(original)

        picard_path = self.root / discovery.PICARD_COMPANIONS
        picard = json.loads(picard_path.read_text(encoding="utf-8"))
        picard["sources"][0]["provider_metadata"]["title"] = "Publisher source substituted"
        picard_path.write_text(json.dumps(picard), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unreviewed Picard directory addition"):
            artwork._historical_directory_receipt_intact(self.root, self.packet)


if __name__ == "__main__":
    unittest.main()
