"""Fail-closed tests for publisher-only Star Trek: Prodigy metadata proposals."""

import unittest

from tools import build_prodigy_publisher_discovery as discovery


class ProdigyPublisherDiscoveryTests(unittest.TestCase):
    def fake(self, source_id, body):
        spec = discovery.source_for(source_id)
        return (
            '<link rel="canonical" href="' + spec[1] + '">' +
            body + ' ' * 100_000
        ).encode("utf-8")

    def test_s1b_first_list_only_and_heading_bound(self):
        titles = [f"Episode Number {n}" for n in range(11, 21)]
        listing = ('<h4><strong><em>Star Trek: Prodigy</em>: Season 1, Episodes 11-20</strong>:</h4>'
                   '<ul>' + ''.join('<li class="foo_listItem">' + t + '</li>' for t in titles) +
                   '</ul><ul><li class="foo_listItem">Bonus commentary</li></ul>')
        self.assertEqual(discovery.extract_source(self.fake("s1b", listing), "s1b"),
                         [(1, n, title) for n, title in zip(range(11, 21), titles)])
        with self.assertRaisesRegex(ValueError, "unsupported publisher title|expected season-local slots"):
            discovery.extract_source(self.fake("s1b", listing.replace(titles[4], "")), "s1b")

    def test_s2_201_to_220_italic_markup(self):
        listing = ''.join(
            '<strong>' + str(n) + ' – &quot;Episode ' +
            ('<em>Protostar</em>' if n == 211 else str(n)) + '&quot;</strong>'
            for n in range(201, 221)
        )
        rows = discovery.extract_source(self.fake("s2", listing), "s2")
        self.assertEqual(len(rows), 20)
        self.assertEqual(rows[10], (2, 11, "Episode Protostar"))
        with self.assertRaisesRegex(ValueError, "expected season-local slots"):
            discovery.extract_source(self.fake("s2", listing.replace("219 –", "2199 –")), "s2")

    def test_forged_canonical_or_unsupported_markup_rejected(self):
        listing = ''.join(f'<strong>{n} – &quot;Title {n}&quot;</strong>' for n in range(201, 221))
        with self.assertRaisesRegex(ValueError, "canonical locator"):
            discovery.extract_source(b'<link rel="canonical" href="https://example.org">' +
                                     listing.encode() + b' ' * 100_000, "s2")
        with self.assertRaisesRegex(ValueError, "unsupported publisher title"):
            discovery.extract_source(self.fake("s2", listing.replace("Title 204", "<script>bad</script>")), "s2")

    def test_committed_metadata_and_candidate_outputs_rebuild(self):
        self.assertEqual(discovery.check(), 0)

    def test_csv_source_local_ordinal_tamper_rejected(self):
        rows = [(1, n, f"Title {n}") for n in range(11, 21)]
        data = discovery.csv_bytes(rows)
        self.assertEqual(discovery.read_csv(data, "s1b"), rows)
        with self.assertRaisesRegex(ValueError, "unexpected Prodigy source-local slots"):
            discovery.read_csv(data.replace(b"1,11,", b"1,1,"), "s1b")


if __name__ == "__main__":
    unittest.main()
