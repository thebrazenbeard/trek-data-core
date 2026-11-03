"""Adversarial source and rights isolation tests for the seven TNG jackets."""

import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("tng_cover_validator", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class HeldJacketSourceTests(unittest.TestCase):
    def setUp(self):
        self.payload = validator._load(HERE / "records.json")

    def test_baseline_no_admission_or_display(self):
        self.assertEqual(validator.validate(self.payload), {
            "isbn_checked": 23, "visually_reviewed_held_jackets": 7,
            "no_cover_field_holds": 16, "work_admissions": 0,
            "images_released": 0,
        })

    def test_visual_and_source_mutations_fail_closed(self):
        cases = [
            lambda d: d["candidates"][0].update(cover_id=12857937),
            lambda d: d["candidates"][0].update(isbn13="9780743412162"),
            lambda d: d["candidates"][0].update(publisher_title="Masks"),
            lambda d: d["candidates"][0].update(publisher_locator="https://fake.example/book"),
            lambda d: d["candidates"][0].update(medium_url="https://fake.example/image.jpg"),
            lambda d: d["candidates"][0].update(medium_sha256="f" * 64),
            lambda d: d["candidates"][0].update(medium_bytes=1),
            lambda d: d["candidates"][0].update(open_library_edition="OL99999M"),
            lambda d: d["candidates"][0].update(open_library_response_sha256="f" * 64),
            lambda d: d["candidates"][0].update(visual_result="COVER_LICENSED_BY_PARAMOUNT"),
            lambda d: d["candidates"][0].update(specific_hold="NONE"),
            lambda d: d["candidates"].pop(),
            lambda d: d["candidates"].append(copy.deepcopy(d["candidates"][0])),
            lambda d: d["holds"].pop(),
            lambda d: d["holds"][0].update(reason="NOT_A_BOOK"),
            lambda d: d["holds"][0].update(open_library_response_sha256="f" * 64),
            lambda d: d["holds"].append(copy.deepcopy(d["holds"][0])),
            lambda d: d["candidates"][0].update(private_archive_member="leak.txt"),
            lambda d: d.update(source_or_work_admission_effect="ADMITTED"),
            lambda d: d.update(literary_coverage_effect="CLOSE_READ"),
            lambda d: d.update(explorer_artwork_release_effect="DISPLAY_APPROVED"),
            lambda d: d.update(image_bytes_committed=True),
            lambda d: d.update(private_archive_members_or_text_exported=True),
            lambda d: d.update(copyright_disposition="PUBLIC_DOMAIN"),
            lambda d: d.update(candidate_review_disposition="INDEPENDENTLY_LICENSED"),
            lambda d: d["publisher_packet_receipts"]["NEXT_TEN"].update(sha256="f" * 64),
        ]
        for mutation in cases:
            data = copy.deepcopy(self.payload)
            mutation(data)
            with self.subTest(mutation=mutation.__code__.co_firstlineno):
                with self.assertRaises((ValueError, KeyError, TypeError)):
                    validator.validate(data)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError):
            validator.json.loads('{"cover_id":123,"cover_id":456}',
                                      object_pairs_hook=validator._pairs_unique)

    def test_source_packets_are_byte_pinned(self):
        for label, receipt in self.payload["publisher_packet_receipts"].items():
            self.assertEqual(validator._sha(validator.ROOT / receipt["path"]),
                             receipt["sha256"], label)

    def test_manifest_and_whole_packet_fail_closed(self):
        packet_part = HERE.relative_to(validator.ROOT)
        members = validator.EXPECTED_PACKET_FILES
        upstream = [Path(r["path"]) for r in self.payload["publisher_packet_receipts"].values()]
        with tempfile.TemporaryDirectory() as temporary:
            staged = Path(temporary)
            for relative in [*upstream, *(packet_part / n for n in members)]:
                destination = staged / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(validator.ROOT / relative, destination)
            self.assertEqual(validator.validate(self.payload, root=staged)["images_released"], 0)
            manifest = staged / packet_part / "MANIFEST.md"
            original = manifest.read_text("utf-8")
            attacks = (
                "\n## Official unrestricted reproduction\n![TNG cover released for display](https://covers.openlibrary.org/b/id/13778645-M.jpg)\n",
                "\n<img src=https://covers.openlibrary.org/b/id/13778645-M.jpg>\n",
                "\n<svg><image href=\"data:image/png;base64,abcd\"/></svg>\n",
                "\nLicensing now PUBLIC DOMAIN; authorized for display.\n",
            )
            for attack in attacks:
                with self.subTest(manifest_attack=attack[:25]):
                    manifest.write_text(original + attack, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        validator.validate(self.payload, root=staged)
            manifest.write_text(original, encoding="utf-8")
            folder = staged / packet_part
            for name, media in (("unreviewed-held-cover.jpg", b"\xff\xd8\xff\xe0"),
                                ("unreviewed.html", b"<img src=x>"),
                                ("unreviewed.svg", b"<svg></svg>")):
                with self.subTest(extra_member=name):
                    extra = folder / name
                    extra.write_bytes(media)
                    with self.assertRaises(ValueError):
                        validator.validate(self.payload, root=staged)
                    extra.unlink()
            with self.subTest(nested_directory=True):
                nested = folder / "hidden"
                nested.mkdir()
                with self.assertRaises(ValueError):
                    validator.validate(self.payload, root=staged)
                nested.rmdir()
            with self.subTest(symlink=True):
                source = folder / "MANIFEST.md"
                original_copy = staged / "manifest-backup.md"
                shutil.copyfile(source, original_copy)
                source.unlink()
                source.symlink_to(original_copy)
                with self.assertRaises(ValueError):
                    validator.validate(self.payload, root=staged)


if __name__ == "__main__":
    unittest.main()
