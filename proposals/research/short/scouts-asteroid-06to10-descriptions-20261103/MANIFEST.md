# Scouts Asteroid Blasters #6–#10 — source-limited publisher paraphrases

**Status:** proposal-only local observations atop accepted
`main@0bcecb03fc4e494962c3c62619e4097bc40bd119`. Five new descriptions
refer only to existing `short:scouts:asteroid_blasters:06`–`10` SOURCE_LOCAL
candidate rows. No videos viewed, full scripts/transcripts read, Work admitted,
coverage promoted, fiction truth verified, artwork acquired, or Explorer page
changed. Do not silently equate *Scouts* mini-strand positions with canonical
television season order.

## Publisher Description fields actually encountered — 2026-11-03 UTC

The web-search tool returned official YouTube results attributed to the
Paramount/Nickelodeon *Blaze and the Monster Machines* publisher channel.
Each result exposed its **Description** heading and a complete-sounding
first episode-specific paragraph; I actually read those returned descriptions
and wrote five short paraphrases. I did not open the direct video landing-page
body: `youtu.be` opening was disabled and `youtube.com/watch` fetching was
throttled in this session. Thus `source_access` is explicitly a
**search-retrieved publisher video description**, not raw page custody or a
watched episode. The search index may truncate/rewrite/cross-cache descriptions.

| Existing source-local ID | Official video result / text locator | Publisher result date |
| --- | --- | --- |
| `short:scouts:asteroid_blasters:06` | [Corn-kernel/popcorn asteroid](https://www.youtube.com/watch?v=Ps3cQdL1By0), Description first paragraph | 2025-10-18 |
| `short:scouts:asteroid_blasters:07` | [Disco-ball asteroid](https://www.youtube.com/watch?v=GtJpqUH3gTA), Description first paragraph | 2025-11-01 |
| `short:scouts:asteroid_blasters:08` | [Bubble-gum asteroid](https://www.youtube.com/watch?v=6lnl4qzwHt8), Description first paragraph | 2025-11-08 |
| `short:scouts:asteroid_blasters:09` | [Chocolate-chip-cookie asteroid](https://www.youtube.com/watch?v=ODb0D3ZTgug), Description first paragraph | 2025-11-15 |
| `short:scouts:asteroid_blasters:10` | [Horta and Gorgonite asteroid](https://www.youtube.com/watch?v=fSRr1CGFYiY), Description first paragraph | 2025-12-06 |

The accepted discovery catalog retains the corresponding `youtu.be` short
URLs and previously verified publisher oEmbed titles; this proposal adds
only descriptions over those IDs. The YouTube result `Published` dates are
mutable metadata observations, **not independently audited first-release
facts**. All five share one Paramount corporate upstream family. External
episode listings that copy the publisher description do not supply another
independent witness.

## Interpretive boundaries and adversarial cautions

All five `synopsis` strings are original paraphrases of what the publisher
advertises; they are not actual outcomes, dialogue or scene depictions. The
fifth publisher blurb announces Shadowtrix seeking a Horta and a gorgonite
asteroid threat, **not** a completed rescue. This proposal deliberately
does not state that the Horta destroys the asteroid or that Shadowtrix is
defeated. Those claims require the primary audiovisual source itself.

> Publisher marketing blurbs cannot establish full-text coverage. Even
> faithful search-result paraphrases may omit important story context, since
> the search index is a mutable intermediary. A later attempt to use any
> public synopsis should bind directly reviewed publisher pages and preserve
> this retrieval limitation.

> The `VIDEO_ID` crosswalk identifies publisher-hosted candidate videos,
> not global Work identity, verified season order, or fictional canon.

The UTF-8 local observation-packet SHA-256 is
`a6d6aee00fb4e2735265960427f3e700e5d104a075c3a516879d5a810aa03092`.
No raw YouTube HTTP response digest is claimed.

## Deterministic checks

```bash
python3 proposals/research/short/scouts-asteroid-06to10-descriptions-20261103/validate.py
python3 -O proposals/research/short/scouts-asteroid-06to10-descriptions-20261103/validate.py
python3 -m unittest tests.test_scouts_asteroid_06to10_descriptions -v
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_explorer.mjs
```

The validator pins five local IDs, official video URLs/dates, one source
family, the exact proposal-byte digest, source access class and no-effect
fields; it does **not** independently authenticate search responses or assert
video viewing. Next after independent hostile source review: retain as a draft
proposal until direct publisher descriptions can be independently rechecked;
*Holodeck Rescues* #1–#10 remain a separate first-party metadata frontier.
