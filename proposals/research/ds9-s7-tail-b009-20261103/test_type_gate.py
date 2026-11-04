"""DS9 B009 source-local type integrity; no admission effects."""

import unittest

from validate import HERE, read_json, validate


class DS9B009TypeGateTests(unittest.TestCase):
    def fresh(self):
        return read_json(HERE / "observations.json")

    def test_accepted_proposal_snapshot(self):
        self.assertEqual(validate(self.fresh()), 9)

    def test_integer_cannot_impersonate_proposal_boolean(self):
        data = self.fresh()
        data["proposal_only"] = 1
        with self.assertRaisesRegex(ValueError, "source/admission scope: proposal_only"):
            validate(data)

    def test_integer_cannot_impersonate_unread_flags(self):
        for field in ("current_raw_html_captured", "actual_episode_or_script_read"):
            with self.subTest(field=field):
                data = self.fresh()
                data[field] = 0
                with self.assertRaisesRegex(ValueError, "source/admission scope: " + field):
                    validate(data)

    def test_float_cannot_impersonate_integer_episode_slot(self):
        for field, value in (("season", 7.0), ("episode", 17.0)):
            with self.subTest(field=field):
                data = self.fresh()
                data["records"][0][field] = value
                with self.assertRaisesRegex(ValueError, "literal guide card title/slot"):
                    validate(data)

    def test_numeric_false_cannot_impersonate_finale_hold(self):
        data = self.fresh()
        data["finale_presentation_hold"]["additional_s7e26_inferred"] = 0
        with self.assertRaisesRegex(ValueError, "do not infer another finale"):
            validate(data)


if __name__ == "__main__":
    unittest.main()
