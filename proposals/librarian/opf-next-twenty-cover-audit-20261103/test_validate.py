"""Deterministic falsifiers for the twenty OPF ISBN / seven held jacket tranche."""
import copy
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("opf_next_twenty", HERE / "validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class OPFNextTwentySourceTests(unittest.TestCase):
    def setUp(self):
        self.data = validator.load(HERE / "records.json")

    def test_exact_baseline_denominators_are_not_works_or_release(self):
        self.assertEqual(validator.validate(self.data), {
            "opf_metadata_rows": 20, "distinct_opf_entry_digests": 20,
            "open_library_responses_200": 18, "open_library_responses_404": 2,
            "medium_title_jackets_held": 7, "exact_publisher_isbn_matches": 4,
            "different_publisher_isbn_holds": 3, "no_cover_field_holds": 11,
            "existing_public_edition_duplicate": 1,
            "source_or_work_admissions": 0, "images_released": 0,
        })

    def test_record_and_rights_mutations_fail_closed(self):
        mutators = (
            lambda x: x["rows"][0].update(opf_id="opf-local:9999"),
            lambda x: x["rows"][0].update(opf_sha256="f" * 64),
            lambda x: x["rows"][0].update(isbn10="0743475926"),
            lambda x: x["rows"][0].update(isbn13="9780743475938"),
            lambda x: x["rows"][0].update(ol_status=404),
            lambda x: x["rows"][0].update(ol_edition="OL1M"),
            lambda x: x["rows"][0].update(ol_response_sha256="f" * 64),
            lambda x: x["rows"][0].update(cover_id=9999999),
            lambda x: x["rows"][0].update(medium_sha256="f" * 64),
            lambda x: x["rows"][0].update(medium_bytes=1),
            lambda x: x["rows"][0].update(visual="OFFICIAL_JACKET_LICENSED"),
            lambda x: x["rows"][0].update(publisher_page_isbn13="9780743475922"),
            lambda x: x["rows"][0].update(publisher_url="https://fake.example/edition"),
            lambda x: x["rows"][7].update(publisher_page_isbn13="9780743419260"),
            lambda x: x["rows"][7].update(publisher_relation="EXACT_ISBN_OFFICIAL_PUBLISHER"),
            lambda x: x["rows"][5].update(ol_status=200),
            lambda x: x["rows"][5].update(ol_edition="OL99999M"),
            lambda x: x["rows"][11].update(publisher_relation="NOT_EVALUATED_NO_IMAGE"),
            lambda x: x["rows"][2].update(cover_id=12345),
            lambda x: x["rows"].append(copy.deepcopy(x["rows"][0])),
            lambda x: x["rows"].pop(),
            lambda x: x["rows"][0].update(private_archive_filename="owner.txt"),
            lambda x: x.update(image_bytes_committed=True),
            lambda x: x.update(source_or_work_admission="CLOSE_READ"),
            lambda x: x.update(explorer_display_effect="PUBLISHED"),
            lambda x: x.update(copyright_status="PUBLIC_DOMAIN"),
            lambda x: x.update(private_narrative_read=True),
            lambda x: x.update(source_metadata_sha256="0" * 64),
        )
        for mutation in mutators:
            candidate = copy.deepcopy(self.data)
            mutation(candidate)
            with self.subTest(line=mutation.__code__.co_firstlineno):
                with self.assertRaises((ValueError, KeyError, TypeError)):
                    validator.validate(candidate)

    def test_checksum_and_prior_public_edition_receipt(self):
        self.assertEqual(validator.isbn10_to13("0743412095"), "9780743412094")
        self.assertEqual(validator.isbn10_to13("074341926X"), "9780743419260")
        self.assertEqual(validator.sha(validator.ROOT / validator.METADATA_PATH),
                         validator.METADATA_SHA256)
        self.assertEqual(validator.sha(validator.ROOT / validator.ENTROPY_PATH),
                         validator.ENTROPY_SHA256)
        with self.assertRaises(ValueError):
            validator.isbn10_to13("0743419260")

    def test_all_held_packet_members_are_pinned_in_clean_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            related = [validator.METADATA_PATH, validator.ENTROPY_PATH]
            packet_files = [validator.PART / name for name in validator.ALLOWED_PACKET]
            for relative in [*related, *packet_files]:
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(validator.ROOT / relative, destination)
            self.assertEqual(validator.validate(self.data, root=root)["images_released"], 0)
            folder = root / validator.PART
            manifest = folder / "MANIFEST.md"
            original = manifest.read_text("utf-8")
            for snippet in (
                "\n## Official license granted for every cover\n",
                "\n![Cover released](https://covers.openlibrary.org/b/id/12055672-M.jpg)\n",
                "\n<img src=\"https://covers.openlibrary.org/b/id/12055672-M.jpg\">\n",
                "\n<svg><image href=\"data:image/png;base64,AAAA\"/></svg>\n",
            ):
                with self.subTest(manifest_injection=snippet[:25]):
                    manifest.write_text(original + snippet, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        validator.validate(self.data, root=root)
            manifest.write_text(original, encoding="utf-8")
            for name in ("extra.jpg", "extra.html", "extra.json"):
                with self.subTest(extra_file=name):
                    extra = folder / name
                    extra.write_bytes(b"not reviewed")
                    with self.assertRaises(ValueError):
                        validator.validate(self.data, root=root)
                    extra.unlink()
            with self.subTest(nested_files=True):
                folder.joinpath("unreviewed").mkdir()
                with self.assertRaises(ValueError):
                    validator.validate(self.data, root=root)
                folder.joinpath("unreviewed").rmdir()
            with self.subTest(nested_cache_media=True):
                cache = folder / "__pycache__"
                cache.mkdir()
                cache.joinpath("unreviewed.png").write_bytes(b"PNG")
                with self.assertRaises(ValueError):
                    validator.validate(self.data, root=root)
                shutil.rmtree(cache)
            with self.subTest(symlinked_packet_member=True):
                backup = root / "manifest-backup.md"
                shutil.copyfile(manifest, backup)
                manifest.unlink()
                manifest.symlink_to(backup)
                with self.assertRaises(ValueError):
                    validator.validate(self.data, root=root)


if __name__ == "__main__":
    unittest.main()
