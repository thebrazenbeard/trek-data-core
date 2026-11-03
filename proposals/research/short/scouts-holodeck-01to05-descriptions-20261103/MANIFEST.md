# Scouts: Holodeck Rescues 1–5 — publisher-description research proposal

- Proposal version: `trek-scouts-holodeck-01to05-publisher-description-v1`
- Observed: 2026-11-03 UTC
- Candidate partition: `SHORT_FORM`; five `SOURCE_LOCAL` rows, `holodeck_rescues:01` through `:05`
- Raw source: official YouTube video search results from publisher channel `Blaze and the Monster Machines`; first episode-specific `Description` paragraph, not playback, subtitles or a successfully opened video-page body.
- Independent upstream families: **one** (`publisher:paramount-nickelodeon-youtube`). A cross-post copied by TV databases is not an independent validation.
- Local file: [`observations.json`](observations.json); SHA-256 `b2459678c03bd7b2cbadc297f662b178e81e4c266d451a8555bd1c3808b9cf9e`, sealed by [`validate.py`](validate.py).
- Proposed claim class: **original `PUBLISHER_DESCRIPTION_PARAPHRASE`**. These reflect a marketing synopsis, not proof that a fictional on-screen event actually happened.
- Protected effects: **NONE** on accepted source/work bindings, evidence, coverage, public Explorer synopsis release, or artwork.

| Source-local row | Official video locator | Publisher search-result display date | Original paraphrase constraint |
| --- | --- | --- | --- |
| `holodeck_rescues:01` | [69jkEMz87co](https://www.youtube.com/watch?v=69jkEMz87co) | 2026-01-23 | Volcano and separated cosmic animal, no invented species |
| `holodeck_rescues:02` | [6AAJlEn3DeY](https://www.youtube.com/watch?v=6AAJlEn3DeY) | 2026-01-24 | Shadowtrix and baby nobonimbus monkey, not actual playback |
| `holodeck_rescues:03` | [fybF9xOzXs4](https://www.youtube.com/watch?v=fybF9xOzXs4) | 2026-01-25 | Galactic pterodactyl nest threatened by mudslide |
| `holodeck_rescues:04` | [M02cKstXmjo](https://www.youtube.com/watch?v=M02cKstXmjo) | 2026-01-26 | Gormagander black hole; first-party search result observed, direct opening throttled |
| `holodeck_rescues:05` | [dZznmiZYV-A](https://www.youtube.com/watch?v=dZznmiZYV-A) | 2026-02-06 | Shadowtrix steals glowray's glow; avoid conflating glowrays and generic stingrays |

Four publisher video titles (#1, #2, #3, #5) differ in wording or suffix from the accepted discovery directory titles. The **current official YouTube title of #4**, independently observed for exact ID `M02cKstXmjo`, matches the discovery title (`Roo Helps a Space Whale Stuck in a Black Hole!`), whereas a downstream syndicated listing uses a distinct title (`Holodeck Rescues #4 | Star Trek Scouts Save a Space Whale From a Black Hole!`). That syndicated variant is **not** attributed here as the publisher's video title. The packet preserves the publisher title separately and does not silently supersede, normalize or merge aliases. The video ID is the narrow exact crosswalk; a title match alone cannot establish global work identity.

## Reproduction and limitations

Search first-party YouTube video IDs and copy only the `Description` *episode-specific paragraph* into an offline source comparison, recording date and corporate publisher; independently inspect each before accepting any paraphrase. Direct `open(https://www.youtube.com/watch?v=M02cKstXmjo)` returned a throttling error during this wave, so a searchable publisher Description is **not** a full video-page fetch. This packet does not store publisher text or video content.

Run:

```bash
python3 proposals/research/short/scouts-holodeck-01to05-descriptions-20261103/validate.py
python3 -O proposals/research/short/scouts-holodeck-01to05-descriptions-20261103/validate.py
python3 -m unittest discover -s tests -p test_scouts_holodeck_01to05_descriptions.py -v
python3 tools/validate.py
```

The generic `UNVERIFIED_METADATA` discovery tag remains intact. Human editorial source review, independent hostile verification, and a separate Consolidator projection decision are required for public display. No episode view, full-source close read, semantic research coverage, on-screen canonical assertion, or artwork right is claimed here.
