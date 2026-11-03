"""Hostile source/rights/identity regressions for Lower Decks S4 L004."""

import copy
import tempfile
import unittest
from pathlib import Path

from validate import HERE, load, validate


class LowerDecksS4GuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load(HERE / "observations.json")

    def rejected(self, mutate):
        forged = copy.deepcopy(self.baseline)
        mutate(forged)
        with self.assertRaises(ValueError):
            validate(forged)

    def test_exact_ten_and_held_scope(self):
        self.assertEqual(validate(self.baseline), 10)
        self.assertEqual([r["episode"] for r in self.baseline["records"]], list(range(1, 11)))
        self.assertEqual(len({r["publisher_thumbnail_url_held"] for r in self.baseline["records"]}), 10)
        self.assertEqual(self.baseline["source"]["full_episode_or_script_read"], False)
        for field in ("accepted_source_work_effect", "accepted_work_effect", "coverage_effect",
                      "denominator_effect", "public_synopsis_effect", "public_artwork_effect"):
            self.assertEqual(self.baseline[field], "NONE")
        raw = (HERE / "observations.json").read_text(encoding="utf-8")
        for prohibited in ("synopsis_paraphrase", "licensed_asset", "full_episode_text",
                           "C:\\Users", "/mnt/d/", "OneDrive/"):
            self.assertNotIn(prohibited, raw)

    def test_source_identity_rights_and_per_card_hostile_mutations(self):
        probes = [
            ("schema", lambda d: d.update(schema_version="2.0.0")),
            ("batch", lambda d: d.update(batch_id="ld-s5-guide")),
            ("role", lambda d: d.update(role="DIRECTOR")),
            ("proposal", lambda d: d.update(proposal_only=False)),
            ("baseline", lambda d: d.update(baseline_accepted_main="0" * 40)),
            ("publisher independence", lambda d: d["source"].update(publisher_family="independent")),
            ("guide cross-host", lambda d: d["source"].update(guide_url="https://example.org/episodes/4/")),
            ("source method", lambda d: d["source"].update(method="FULL_EPISODE_WATCH")),
            ("HTTP bool", lambda d: d["source"].update(http_status_observed=True)),
            ("HTTP response", lambda d: d["source"].update(http_status_observed=404)),
            ("HTML byte count", lambda d: d["source"].update(html_bytes_observed=271582)),
            ("HTML raw fingerprint", lambda d: d["source"].update(html_sha256_observed="a" * 64)),
            ("fake raw capture", lambda d: d["source"].update(raw_html_retained=True)),
            ("fake immutable edition", lambda d: d["source"].update(source_edition_stability="IMMUTABLE")),
            ("claimed viewing", lambda d: d["source"].update(full_episode_or_script_read=True)),
            ("source scope", lambda d: d["source"].update(scope="TRANSCRIPT_CLOSE_READ")),
            ("predecessor source", lambda d: d["accepted_predecessor"].update(path="../secret")),
            ("predecessor hash", lambda d: d["accepted_predecessor"].update(sha256="0" * 64)),
            ("predecessor independence", lambda d: d["accepted_predecessor"].update(relation="INDEPENDENT")),
            ("binding", lambda d: d.update(accepted_source_work_effect="SOURCE_BOUND")),
            ("Work", lambda d: d.update(accepted_work_effect="ADMITTED")),
            ("coverage", lambda d: d.update(coverage_effect="CLOSE_READ")),
            ("denominator", lambda d: d.update(denominator_effect="10")),
            ("public synopsis", lambda d: d.update(public_synopsis_effect="PUBLISHED")),
            ("public artwork", lambda d: d.update(public_artwork_effect="PUBLISHED")),
            ("extra identity", lambda d: d.update(verified_global_works=10)),
            ("missing row", lambda d: d["records"].pop()),
            ("duplicate row", lambda d: d["records"].append(copy.deepcopy(d["records"][0]))),
            ("reordered rows", lambda d: d["records"].reverse()),
            ("card ID", lambda d: d["records"][0].update(local_card_entity_id="ld-l003-card-01")),
            ("duplicate ID", lambda d: d["records"][1].update(observation_id="ld-l004-o01")),
            ("boolean season", lambda d: d["records"][0].update(season=True)),
            ("episode slot", lambda d: d["records"][0].update(episode=2)),
            ("fake title", lambda d: d["records"][5].update(publisher_card_title="Parth Ferengi Heart Place")),
            ("other season description", lambda d: d["records"][0].update(publisher_description_sha256="a" * 64)),
            ("locator mismatch", lambda d: d["records"][0].update(card_locator="S4E2")),
            ("false mention", lambda d: d["records"][1]["literal_mentions"].append("Kirk")),
            ("same host art swap", lambda d: d["records"][0].update(
                publisher_thumbnail_url_held=d["records"][1]["publisher_thumbnail_url_held"])),
            ("foreign artwork host", lambda d: d["records"][2].update(
                publisher_thumbnail_url_held="https://example.com/thumbnail.jpg")),
            ("same host new artwork", lambda d: d["records"][3].update(
                publisher_thumbnail_url_held="https://thumbnails.cbsig.net/_x/w400/fake.jpg")),
            ("artwork credentials", lambda d: d["records"][4].update(
                publisher_thumbnail_url_held="https://user:pass@thumbnails.cbsig.net/_x/w400/fake.jpg")),
            ("rights claim", lambda d: d["records"][5].update(image_license="VERIFIED")),
            ("synopsis prose", lambda d: d["records"][6].update(synopsis="An unsourced plot claim")),
            ("global identity", lambda d: d["records"][7].update(accepted_work_id="global:ld:s4e8")),
            ("episode media", lambda d: d["records"][8].update(video_stream_sha256="a" * 64)),
        ]
        self.assertGreaterEqual(len(probes), 40)
        for label, mutate in probes:
            with self.subTest(probe=label):
                self.rejected(mutate)

    def test_duplicate_raw_json_keys_fail_closed(self):
        for raw in (
            '{"coverage_effect":"CLOSE_READ","coverage_effect":"NONE"}',
            '{"source":{"full_episode_or_script_read":true,"full_episode_or_script_read":false}}',
            '{"records":[{"episode":2,"episode":1}]}',
        ):
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "duplicate.json"
                path.write_text(raw, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                    load(path)

    def test_previous_accepted_source_must_remain_byte_identical(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            target = base / self.baseline["accepted_predecessor"]["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "previous accepted source bytes drifted"):
                validate(self.baseline, root=base)


if __name__ == "__main__":
    unittest.main()
