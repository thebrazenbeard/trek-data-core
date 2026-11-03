"""Adversarial checks of held OPF source and image edition identity."""
import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("opf_final13", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class HeldLastThirteenTests(unittest.TestCase):
    def setUp(self):
        self.data = validator.load(HERE / "records.json")

    def test_exact_denom_and_no_release(self):
        self.assertEqual(validator.validate(self.data), {
            "exact_publisher_isbn_matches": 3,
            "publisher_different_isbn_holds": 1,
            "publisher_unbound_cover_holds": 1,
            "medium_jackets_held": 5,
            "api_no_cover_holds": 6,
            "api_404_holds": 2,
            "namespace_recovered_opf": 5,
            "opf_metadata_rows": 13,
            "distinct_opf_member_sha256": 13,
            "accepted_works": 0,
            "explorer_images_released": 0,
        })

    def test_adversarial_source_and_rights_mutations(self):
        changes = (
            lambda d: d["rows"][1].update(cover_id=999999),
            lambda d: d["rows"][1].update(medium_sha256="f" * 64),
            lambda d: d["rows"][1].update(medium_bytes=1),
            lambda d: d["rows"][1].update(visual="IMAGE_RIGHTS_APPROVED"),
            lambda d: d["rows"][1].update(publisher_isbn13="9780743464544"),
            lambda d: d["rows"][1].update(publisher_url="https://fake.example/image"),
            lambda d: d["rows"][9].update(publisher_relation="OFFICIAL_EXACT_ISBN_EBOOK"),
            lambda d: d["rows"][9].update(publisher_isbn13="9780671501068"),
            lambda d: d["rows"][11].update(publisher_isbn13="9780743427920"),
            lambda d: d["rows"][11].update(publisher_relation="OFFICIAL_EXACT_ISBN_EBOOK"),
            lambda d: d["rows"][10].update(isbn10="0743448724"),
            lambda d: d["rows"][10].update(isbn13="9780743448728"),
            lambda d: d["rows"][0].update(status=404),
            lambda d: d["rows"][6].update(status=200),
            lambda d: d["rows"][6].update(ol_edition="OL1234M"),
            lambda d: d["rows"][0].update(cover_id=12345),
            lambda d: d["rows"][1].update(opf_id="opf-local:9999"),
            lambda d: d["rows"][1].update(opf_sha256="0" * 64),
            lambda d: d["rows"].append(copy.deepcopy(d["rows"][1])),
            lambda d: d["rows"].pop(),
            lambda d: d.update(artwork_release="PUBLISHED"),
            lambda d: d.update(source_or_work_admission="WORKS_CREATED"),
            lambda d: d.update(image_bytes_committed=True),
            lambda d: d.update(private_narrative_read=True),
            lambda d: d.update(rights_status="PUBLIC_DOMAIN"),
            lambda d: d["rows"][1].update(private_member_filename="user.txt"),
        )
        for edit in changes:
            candidate = copy.deepcopy(self.data)
            edit(candidate)
            with self.subTest(edit=edit.__code__.co_firstlineno):
                with self.assertRaises((ValueError, TypeError, KeyError)):
                    validator.validate(candidate)

    def test_source_hashes_and_checksum_conversion(self):
        self.assertEqual(validator.isbn10_to13("0671501062"), "9780671501068")
        self.assertEqual(validator.isbn10_to13("0743427920"), "9780743427920")
        self.assertEqual(validator.sha(validator.ROOT / validator.OPF_PATH),
                         validator.OPF_SHA)
        with self.assertRaises(ValueError):
            validator.isbn10_to13("0743427921")

    def test_whole_packet_hotlink_and_binary_smuggling(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            for rel in [validator.OPF_PATH,
                        *(str(validator.PART / f) for f in validator.ALLOWED_FILES)]:
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(validator.ROOT / rel, dest)
            self.assertEqual(validator.validate(self.data, root=root)["explorer_images_released"], 0)
            packet = root / validator.PART
            manifest = packet / "MANIFEST.md"
            original = manifest.read_text("utf-8")
            for snippet in ("\nPublic domain. License granted by Paramount.\n",
                            "\n![Now live](https://covers.openlibrary.org/b/id/405687-M.jpg)\n",
                            "\n<img src=\"https://covers.openlibrary.org/\">\n"):
                with self.subTest(manifest=snippet[:20]):
                    manifest.write_text(original + snippet, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        validator.validate(self.data, root=root)
            manifest.write_text(original, encoding="utf-8")
            for sibling in ("unreviewed.jpg", "nested"):
                with self.subTest(sibling=sibling):
                    if sibling.endswith(".jpg"):
                        extra = packet / sibling
                        extra.write_bytes(b"JPEG")
                    else:
                        extra = packet / sibling
                        extra.mkdir()
                    with self.assertRaises(ValueError):
                        validator.validate(self.data, root=root)
                    extra.unlink() if extra.is_file() else extra.rmdir()
            with self.subTest(cache_media=True):
                cache = packet / "__pycache__"
                cache.mkdir()
                cache.joinpath("cover.jpg").write_bytes(b"JPG")
                with self.assertRaises(ValueError):
                    validator.validate(self.data, root=root)
                shutil.rmtree(cache)
            with self.subTest(symlink=True):
                backup = root / "manifest.md"
                shutil.copyfile(manifest, backup)
                manifest.unlink()
                manifest.symlink_to(backup)
                with self.assertRaises(ValueError):
                    validator.validate(self.data, root=root)


if __name__ == "__main__":
    unittest.main()
