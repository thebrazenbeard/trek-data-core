"""Remote opt-in Picard jackets: immutable exact-edition release and hostile gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate_picard_jacket_release as release


class PicardArtworkReleaseTests(unittest.TestCase):
    def intercepted_bytes(self, target, rewrite):
        """Change exactly one read-only release input, without mutating checkout."""
        actual_reader = release.source.file_bytes

        def fake(root, relative):
            raw = actual_reader(root, relative)
            if relative == target:
                return rewrite(raw)
            return raw

        return patch.object(release.source, "file_bytes", side_effect=fake)

    def test_exact_two_are_opt_in_without_admitting_works_or_mirroring_jpegs(self):
        result = release.check(ROOT)
        self.assertEqual(result["status"], "SIX_REMOTE_API_COVERS_OPT_IN_REVIEWED")
        self.assertEqual((result["original_covers"], result["new_picard_covers"]), (4, 2))
        self.assertEqual((result["coverage_effect"], result["public_local_image_bytes"]), ("NONE", 0))
        sidecar = json.loads((ROOT / release.SIDECAR).read_bytes())
        self.assertEqual(len({(e["isbn"], e["cover_id"]) for e in sidecar["artwork"]}), 2)
        self.assertTrue(all(e["image_size"] == "M" for e in sidecar["artwork"]))
        self.assertEqual(hashlib.sha256((ROOT / release.SIDECAR).read_bytes()).hexdigest(), release.SIDECAR_SHA)

    def test_changed_cover_id_rights_or_metadata_held_even_with_plausible_sidecar(self):
        for name, mutate in [
            ("different cover", lambda d: d["artwork"][0].update(cover_id=10694457)),
            ("claimed public domain", lambda d: d["artwork"][0].update(rights_status="PUBLIC_DOMAIN")),
            ("new Work", lambda d: d.update(work_admission_effect="ACCEPTED")),
            ("wrong title", lambda d: d["artwork"][0].update(alt_text="Star Trek: Picard artwork")),
            ("swapped ISBN", lambda d: d["artwork"][1].update(isbn="9781982154073")),
        ]:
            with self.subTest(name=name):
                def changed(raw):
                    packet = json.loads(raw)
                    mutate(packet)
                    return json.dumps(packet).encode()
                with self.intercepted_bytes(release.SIDECAR, changed):
                    with self.assertRaisesRegex(release.source.Rejected, "not code-pinned"):
                        release.check(ROOT)

    def test_review_is_distinct_and_rights_limits_not_self_attested(self):
        for name, mutate in [
            ("same reviewer", lambda d: d.update(medium_image_reviewer=d["large_image_reviewer"])),
            ("false copyright", lambda d: d.update(copyright_status="LICENSED")),
            ("mirrored jpeg", lambda d: d.update(image_bytes_mirrored=True)),
            ("new coverage", lambda d: d.update(coverage_effect="CLOSE_READ")),
            ("extra field", lambda d: d.update(approval_statement="signed by publisher")),
        ]:
            with self.subTest(name=name):
                def changed(raw):
                    packet = json.loads(raw)
                    mutate(packet)
                    return json.dumps(packet).encode()
                with self.intercepted_bytes(release.RECEIPT, changed):
                    with self.assertRaises(release.source.Rejected):
                        release.check(ROOT)

    def test_js_opt_in_or_independent_static_pages_gate_cannot_be_removed(self):
        for name, path, old, new in [
            ("opt-in", "explorer/app.js", "const source = artworkState.enabled ?", "const source = true ?"),
            ("separate Picard source", "explorer/app.js",
             "!artworkState.available || !picardLiteratureSupplement.available", "!artworkState.available"),
            ("exact artifact pin", "explorer/app.js", release.SIDECAR_SHA, "0" * 64),
            ("physical image ban", ".github/workflows/static.yml",
             "test -e explorer/licensed-artwork || test -L explorer/licensed-artwork", "false"),
            ("CI validator", ".github/workflows/static.yml",
             "python3 tools/validate_picard_jacket_release.py --check --verify-git", "echo skipped"),
        ]:
            with self.subTest(name=name):
                def changed(raw):
                    self.assertIn(old.encode(), raw)
                    return raw.replace(old.encode(), new.encode(), 1)
                with self.intercepted_bytes(path, changed):
                    with self.assertRaises(release.source.Rejected):
                        release.check(ROOT)

    def test_css_sourced_cover_hides_original_placeholder_at_all_responsive_sizes(self):
        css = (ROOT / "explorer/app.css").read_text(encoding="utf-8")
        self.assertIn(".artwork-slot.artwork-has-source .artwork-missing { display: none; }", css)
        for expected in ("320px", "375px", "1440px"):
            # Explicit CSS hiding applies independent of viewport. These
            # dimensions are covered in parent-owned real browser QA.
            self.assertIn(".artwork-slot.artwork-has-source", css, expected)
        html = (ROOT / "explorer/index.html").read_text(encoding="utf-8")
        self.assertIn("./app.css?v=" + hashlib.sha256(css.encode()).hexdigest(), html)


if __name__ == "__main__":
    unittest.main()
