# LD L003 — Paramount+ Lower Decks Season 3 guide-card observations

**Batch:** `ld-s3-guide-l003-20261103`
**Role:** Lower Decks series researcher (source-relative only)
**Accepted selection base:** `main` `1ef3e4ef9cefa0e3ccd90caa4530a84c167a8ca6`
**Observations SHA-256:** `e8153b87644354a60ff900f0cc612b4efe37aae9dccbd13fc95960879f575e65`
**State:** draft proposal, not admitted Work/episode semantic coverage.

## Actual primary source and scope

- Official Paramount+ U.S. [Lower Decks Season 3 episode guide](https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/3/), all ten displayed cards **actually read** on 2026-11-03 UTC, rendered view lines 108–162.
- The separately retrieved direct HTTP response was **200**, 272,206 bytes, SHA-256 `6047c304d8af99e889c8bfb489a5c09584aa8b2e9847fb9eba1ebe655b1726e8`. The changing source HTML is **not archived** in the public repository. This receipt is an observed hash of one transient retrieval, not an independently replayable or authenticated immutable edition.
- For **each individual publisher card** the current response was checked for exact title, S3 E1–E10 slot, SHA-256 of its decoded/trimmed publisher description, and every literal name/term listed. The description bytes themselves are omitted; no copyrighted description paragraph is reproduced.
- A prior accepted source-local Season 3 discovery CSV and bundle recorded the ten title/slot candidates: `proposals/discovery/modern-paramount-season3-20261102/ld-observed-slots.csv` SHA-256 `51687fbbeec8ef721c053f5f96d65724ccb23262f5464229757616870bc1690e`, `ld/bundle.json` SHA-256 `1c23cb2c7ca77089deeb2191447bc9ab5241d1103750105c1ef6e23032e41dbd`. That prior extraction is from the **same publisher lineage** and not independent episode corroboration; the strict validator rehashes these accepted files.

## Ten publisher cards inspected

| Publisher card | Source-local title | Rendered web-reader locator |
| --- | --- | --- |
| S3 E1 | Grounded | guide lines 108–112 |
| S3 E2 | The Least Dangerous Game | 113–117 |
| S3 E3 | Mining the Mind's Mines | 119–123 |
| S3 E4 | Room for Growth | 124–128 |
| S3 E5 | Reflections | 130–134 |
| S3 E6 | Hear All, Trust Nothing | 136–140 |
| S3 E7 | A Mathematically Perfect Redemption | 142–145 |
| S3 E8 | Crisis Point 2: Paradoxus | 147–151 |
| S3 E9 | Trusted Sources | 153–157 |
| S3 E10 | The Stars at Night | 158–162 |

Line windows are current rendered web-reader positions, not persistent transcript offsets. Each card's canonical locator in the records is its **guide title/slot/description grouping**, not the line number alone.

## Explicit holds

- **Source → local card entity → publisher description term observation**. A string in promotional copy proves that Paramount published that phrase on the current page; it does **not** prove that the character appeared, said the phrase, or performed the depicted action in the episode. No global identity reconciliation.
- **No scripts, episodes, video or audiovisual close-reads** were accessed; a full page guide read is not a full episode read.
- `synopsis_status = HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE`: no description copy or paraphrase is committed for publication.
- `artwork_candidate_page_url` points to the publisher guide only. `artwork_asset_url = null` and `artwork_rights_status = UNKNOWN_HELD`: no image bytes, CDN image links, implied hotlink rights or public display.
- Accepted Source–Work, Work, coverage, public synopsis and public artwork effects are **all NONE**. No SOURCE_BOUND/SEMANTICALLY_ANALYZED/CLOSE_READ/ENTITY_LINKED/AUDITED denominator promotion.

## Deterministic checks

```bash
python3 proposals/research/ld-s3-guide-l003-20261103/validate.py
python3 -m unittest discover -s proposals/research/ld-s3-guide-l003-20261103 -p 'test_*.py' -q
python3 -O -m unittest discover -s proposals/research/ld-s3-guide-l003-20261103 -p 'test_*.py' -q
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

The fail-closed schema/pins reject changed source ancestry, unknown authenticity fields, duplicate raw JSON keys, title/slot/description-fingerprint edits, reorderings, false name observations, identity promotion, forged artwork licenses, image asset injection, and false coverage or episode-read status. The pins protect **this reviewed proposal's contents**; they are not a substitute for independent current publisher rereading.

**Next nonduplicate frontier:** Lower Decks Season 4 guide source-relative cards, after fresh accepted `main` and open-draft checks. No merge authority inferred.
