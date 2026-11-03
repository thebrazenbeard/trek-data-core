# LD L005 — Paramount+ Season 5 source-local guide cards, held art and summaries

**Batch:** `ld-s5-guide-l005-20261103`
**Research role:** Lower Decks series worker
**Accepted selection base:** `7cf99513f36396cf54512f78faf9d59ceddf68f9`
**Observations SHA-256:** `33316497bf655f0497accccdeb061ce7f631c2fc1da808a5b4f2fca957a3b4bc`
**Status:** unaccepted draft research proposal; no Work/coverage/rights effects.

## Primary source actually read

- [Official Paramount+ Lower Decks Season 5 episode guide](https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/5/), ten complete **publisher episode cards** read on 2026-11-03, with current web-reader title/slot/description positions at lines 108–163. This is **not** the episode audiovisual material or its script.
- A separate direct HTTP GET returned **200**, 271,253 bytes, SHA-256 `03f94a288dd368474b5ecc0f4a7048ee641122531a7f08327de0a557350a1ad5`. This is a transient raw HTML response **not archived**, not an independently reproducible immutable edition or verified episode file.
- For each of ten individual `<div class="episode">` cards, I extracted and paired the exact title, S5 E1–E10 number, SHA-256 of the **decoded/HTML-tag-stripped/trimmed** description, linked relative video href expanded under Paramount+, adjacent `thumbnails.cbsig.net` `<img src>`, and selected literal promotional-description terms. Per-card source URL/description/image pairings were inspected together; they are not independent streams or image-rights receipts.
- Already accepted source-local Season 5 title/slot discovery: `proposals/discovery/publisher-season5-20261102/ld.csv` SHA-256 `500b9c1498c2fb493918d356f4c47ae31eba3c3554ac80ea48db356cb0be1d93`, and `ld/bundle.json` SHA-256 `49c52ca05f91373cd146039df14cefb9bfba0ee839a68034ec77297df0e2fc28`. These are one **shared Paramount publisher family**, not independent corroboration. The validator rehashes both accepted source-directory inputs.

## Exact ten publisher card titles and slots

| Official guide slot | Current card title | Rendered web-reader title/description window |
| --- | --- | --- |
| S5 E1 | Dos Cerritos | 108–112 |
| S5 E2 | Shades of Green | 114–118 |
| S5 E3 | The Best Exotic Nanite Hotel | 119–123 |
| S5 E4 | A Farewell to Farms | 125–129 |
| S5 E5 | Starbase 80?! | 131–135 |
| S5 E6 | Of Gods and Angles | 136–140 |
| S5 E7 | Fully Dilated | 142–146 |
| S5 E8 | Upper Decks | 148–152 |
| S5 E9 | Fissure Quest | 154–158 |
| S5 E10 | The New Next Generation | 159–163 |

These line windows refer only to the current rendered guide, not stable audiovisual or literary text offsets. The publisher's descriptions are exceptionally brief in Season 5; original one-sentence candidates in `synopsis_paraphrase_candidate` are **HELD**, not episodes fully read, objective depicted action assertions or public copy.

## Hard provenance and release limits

- Evidence means **what Paramount's article says**, not independent evidence that fictional events occurred. Literal mention tokens may be character labels, terms or genre phrases in the publisher's copy; they are **not global entity IDs or verified onscreen utterances**.
- Ten video-card hrefs identify page links only. **No video played, downloaded, authenticated or close-read**, no script or transcript processed.
- Ten exact CDN image URLs are **unfetched discovery leads only**. `HELD_NO_PUBLIC_DISPLAY_LICENSE`, `image_bytes_retrieved=false`. Neither page markup nor a filename grants copying, public display, hotlinking or embedding in Explorer/LCARS.
- All original concise paraphrases remain `HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_EPISODE_READ`. No copied long publisher descriptions or public synopsis publication.
- `accepted_source_work_effect`, `accepted_work_effect`, `coverage_effect`, `public_synopsis_effect`, `public_artwork_effect`: all exactly `NONE`. No global Source–Work binding, local-entity identity reconciliation, semantic episode coverage, denominator change, public artwork, Explorer change or deployment.
- Concurrent open LD S4 #373 is a **separate season/source partition**, and the S5 10-card accepted discovery is not counted again as ten new Works.

## Reproduction and attack probes

```bash
python3 proposals/research/ld-s5-guide-l005-20261103/validate.py
python3 -m unittest discover -s proposals/research/ld-s5-guide-l005-20261103 -p 'test_*.py' -q
python3 -O -m unittest discover -s proposals/research/ld-s5-guide-l005-20261103 -p 'test_*.py' -q
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

Static code-owned pins guard every per-card **title/slot/description digest/video URL/thumbnail URL/literal mentions/held synopsis** and all source/rights envelope fields, with a closed schema and duplicate raw JSON-key rejection. Adversarial tests include same-host video and thumbnail substitutions, combined same-card swaps, description digest swaps, reordered/duplicated episodes, forged image rights, Work/coverage promotions, false raw-source custody, and optimized-Python mutation paths. Exact code pins safeguard this reviewed proposal; future live publisher updates must be independently checked, **not silently accepted as a frozen source edition**.

**Next frontier:** independent exact-head audit of this held S5 source batch. Only after separate authority can any accepted research proposal be merged, and artwork rights must be separately proven for public display.
