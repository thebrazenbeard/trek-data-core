# Voyager V003 — Season 2 publisher-guide tail, ten source-local cards

**Role/scope:** Voyager source extraction, publisher guide metadata only. **Selection main:** `aebf9e8a69ab44919f2d89ab60dd1e824e05a807` (2026-11-03 UTC). **Result:** proposal only; no global Work IDs, no audiovisual close-read, no accepted coverage or admitted Source–Work identity.

## Direct primary publisher source

I retrieved and actually parsed Paramount+'s [Star Trek: Voyager Season 2 guide](https://www.paramountplus.com/shows/star_trek_voyager/episodes/2/) as HTTP 200, 317568 raw HTML bytes, SHA-256 `f85cbd5121dabf75f60508a84feb9019ba3a6c04fda0cb7dd366a7dc71c49f26`. The raw page bytes are **not** committed; the checksum is a retrieval receipt, not independent proof of a permanent page or authenticated playback. Each target own-card section was read and its displayed title, S2 E# slot, video locator, adjacent thumbnail candidate and description text were inspected. The description is not reproduced in this repository: a deterministic SHA-256 of each decoded/tag-stripped/trimmed own-card description plus selected **literal publisher wording tokens** are retained.

| Source-local guide slot | Exact publisher title | Local observation |
| --- | --- | --- |
| S2E16 | *Meld* | `voy-v003-o01` |
| S2E17 | *Dreadnought* | `voy-v003-o02` |
| S2E18 | *Death Wish* | `voy-v003-o03` |
| S2E19 | *Lifesigns* | `voy-v003-o04` |
| S2E21 | *Deadlock* | `voy-v003-o05` |
| S2E22 | *Innocence* | `voy-v003-o06` |
| S2E23 | *The Thaw* | `voy-v003-o07` |
| S2E24 | *Tuvix* | `voy-v003-o08` |
| S2E25 | *Resolutions* | `voy-v003-o09` |
| S2E26 | *Basics, Part 1* | `voy-v003-o10` |

The accepted 26-row historical publisher directory `proposals/discovery/legacy-paramount-season2-20261102/voy.csv` and bundle are source-lineage seeds in **the same Paramount publisher family**, not independent corroboration. The accepted B006 Voyager card recheck already includes S2E20 *Investigations* (`lead:0077`); this batch **explicitly skips E20** and does not recount it. The earlier accepted V001 S2E6–15 remains separate. All ten records pin exact publisher-own-card URLs, source-relative position, description fingerprint and selected literal publisher mention terms; those terms show what the *card says*, not what a video episode independently depicts.

## Held rights and identity

- Each CDN thumbnail is a **held lead** for eventual rights/attribution adjudication, not a permission grant, approved display asset, or obtained image binary. No image is downloaded, committed, embedded, or hotlinked into a public view.
- Video URLs are first-party card locators; neither video content nor scripts were obtained or viewed. No `CLOSE_READ`, source-body custody or edition/work identity is claimed.
- All synopses held. No copyrighted source description or public paraphrase is stored.
- Admission effects: `accepted_source_work_effect=NONE`, `accepted_work_effect=NONE`, `coverage_effect=NONE`, `public_synopsis_effect=NONE`, `public_artwork_effect=NONE`.

> **Hostile falsifier:** Different edition/region cuts, cards rearranged by the publisher, reworded descriptions or reused thumbnail filenames could defeat naive slot joins. These are only date-scoped publisher metadata observations; a paired title, slot, SHA and media URL still cannot prove playback source identity or a license. The validator pins this reviewed proposal, not the live external website.

## Validation and next frontier

`validate.py` rejects duplicate raw JSON keys, fabricated rights/admission/status keys, row swaps, forged source URLs, title/slot changes, description hash changes, literal mention changes and historical family drift. `test_validate.py` exercises normal and optimized-Python falsifiers. Run:

```bash
python3 proposals/research/voy-s2-tail-v003-20261103/validate.py
python3 -m unittest discover -s proposals/research/voy-s2-tail-v003-20261103 -p 'test_validate.py'
python3 tools/validate.py
```

**Next Voyager guide frontier:** Unclaimed source-first cards in another Voyager season (with accepted overlap exclusion) or true source custody for any held episode; source metadata alone cannot advance audiovisual/literary semantic coverage.
