"""Adversarial static gate regression for first opt-in event photo pilot."""
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.validate_beyond_documentary_photo import ROOT, ReleaseRejected, validate


class PremiereReleaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = validate(ROOT)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for filename in ("beyond-premiere-photo.json", "beyond-premiere-release-decision.json",
                         "index.html", "app.css", "app.js"):
            source = ROOT / "explorer" / filename
            dest = self.root / "explorer" / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)

    def test_exact_candidate_passes_without_claiming_film_admission(self):
        self.assertEqual(self.expected["status"], "HELD_SOURCE_BOUND_DOCUMENTARY_PHOTO_CANDIDATE")
        self.assertEqual(self.expected["coverage_effect"], "NONE")
        self.assertEqual(self.expected["work_admission_effect"], "NONE")
        self.assertEqual(self.expected["image_observed_bytes"], 116536)
        self.assertEqual(validate(self.root), self.expected)

    def test_missing_tampered_and_symlinked_source_receipts_rejected(self):
        path = self.root / "explorer" / "beyond-premiere-photo.json"
        path.unlink()
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        shutil.copyfile(ROOT / "explorer" / "beyond-premiere-photo.json", path)
        path.write_text(path.read_text().replace("CC BY 2.0", "CC0 1.0"))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        path.unlink()
        path.symlink_to(ROOT / "explorer" / "beyond-premiere-photo.json")
        with self.assertRaises(ReleaseRejected):
            validate(self.root)

    def test_false_held_release_decision_never_admits_public_pixels(self):
        decision = self.root / "explorer" / "beyond-premiere-release-decision.json"
        decision.write_text(decision.read_text().replace('"public_image_display_authorized": false',
                                                         '"public_image_display_authorized": true'))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        shutil.copyfile(ROOT / "explorer" / "beyond-premiere-release-decision.json", decision)
        target = self.root / "explorer" / "licensed-artwork" / "beyond-premiere-japan-2016-960.jpg"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"not allowed prior to the separate rights release")
        with self.assertRaises(ReleaseRejected):
            validate(self.root)

    def test_provenance_gated_image_never_preloads_from_markup_or_css(self):
        html = self.root / "explorer" / "index.html"
        html.write_text(html.read_text().replace(
            '<div id="beyond-premiere-image" class="beyond-premiere-image"',
            '<img src="https://thumb.wikimedia.org/forged.jpg"><div id="beyond-premiere-image" class="beyond-premiere-image"'))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        shutil.copyfile(ROOT / "explorer" / "index.html", html)
        html.write_text(html.read_text().replace(
            "</head>", '<link rel="preload" as="image" href="https://thumb.wikimedia.org/fake.jpg"></head>'))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        shutil.copyfile(ROOT / "explorer" / "index.html", html)
        html.write_text(html.read_text().replace(
            "</head>", '<img src="https://thumb.wikimedia.org/fake.jpg"></head>'))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        shutil.copyfile(ROOT / "explorer" / "index.html", html)
        html.write_text(html.read_text().replace(
            "</head>", '<input type="image" src="https://thumb.wikimedia.org/fake.jpg"></head>'))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        shutil.copyfile(ROOT / "explorer" / "index.html", html)
        html.write_text(html.read_text().replace(
            "</head>", '<span style="background-image:url(https://thumb.wikimedia.org/fake.jpg)"></span></head>'))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        shutil.copyfile(ROOT / "explorer" / "index.html", html)
        css = self.root / "explorer" / "app.css"
        css.write_text(css.read_text().replace(
            ".beyond-premiere-panel[hidden] { display: none; }",
            ".beyond-premiere-panel[hidden] { display: block; }"))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        shutil.copyfile(ROOT / "explorer" / "app.css", css)
        css.write_text(css.read_text() + "\nbody { background-image: url(https://thumb.wikimedia.org/fake.jpg); }\n")
        # Even with a correctly refreshed cache key (avoiding an accidental
        # pass from the generic cache-key check), external CSS fetch is held.
        import hashlib
        fresh = hashlib.sha256(css.read_bytes()).hexdigest()
        before = hashlib.sha256((ROOT / "explorer" / "app.css").read_bytes()).hexdigest()
        html.write_text(html.read_text().replace(f"./app.css?v={before}", f"./app.css?v={fresh}"))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)

    def test_csp_broadening_and_consent_guard_removal_rejected(self):
        html = self.root / "explorer" / "index.html"
        html.write_text(html.read_text().replace(
            "https://*.us.archive.org;", "https://*.us.archive.org https://thumb.wikimedia.org;"))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)
        shutil.copyfile(ROOT / "explorer" / "index.html", html)
        js = self.root / "explorer" / "app.js"
        js.write_text(js.read_text().replace("premierePhotoState.epoch !== epoch", "false"))
        with self.assertRaises(ReleaseRejected):
            validate(self.root)


if __name__ == "__main__":
    unittest.main()
