# TNG B011 — ten new season-one official publisher cards (held research proposal)

**Distinct source-local frontier:** Accepted `main@a81d1829b394af66fb1a1d1a2c93a6b374fa81ef` contains the previous accepted B010 tranche of ten *other* first-party TNG S1 card observations (`legacy:s1:tng:000`–`007`, `009`–`010`). This B011 proposal covers the next **ten non-overlapping** accepted discovery rows, `legacy:s1:tng:011`–`020`. The broader B001 discovery inventory previously carried these rows as `UNVERIFIED_METADATA`; merely listing them was not an actual full card reread. No existing B010 rows are rewritten.

**Source read:** The complete rendered [Paramount+ *Star Trek: The Next Generation* Season 1 episode guide](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/) and its raw public HTML card blocks were actually read again on 2026-11-03. For each selected card, the current publisher heading, season/episode ordinal, short description, and source HTML `<img src>` thumbnail locator were individually examined. Raw HTML bytes were not archived, so `raw_webpage_sha256` is `null`. The short description is fingerprinted as SHA-256 of its HTML-unescaped, trimmed text; the copyrighted description itself is not reproduced in the public repo. This is a **same-family Paramount reread**, not second independent-source corroboration or audiovisual full-work access.

| Discovery row | Publisher title and card slot | Description and artwork |
| --- | --- | --- |
| `legacy:s1:tng:011` | Datalore — S1E13 | Hash, held blurb, held asset URL |
| `legacy:s1:tng:012` | Angel One — S1E14 | Hash, held blurb, held asset URL |
| `legacy:s1:tng:013` | 11001001 — S1E15 | Hash, held blurb, held asset URL |
| `legacy:s1:tng:014` | Too Short a Season — S1E16 | Hash, held blurb, held asset URL |
| `legacy:s1:tng:015` | When the Bough Breaks — S1E17 | Hash, held blurb, held asset URL |
| `legacy:s1:tng:016` | Home Soil — S1E18 | Hash, held blurb, held asset URL |
| `legacy:s1:tng:017` | Coming of Age — S1E19 | Hash, held blurb, held asset URL |
| `legacy:s1:tng:018` | Heart of Glory — S1E20 | Hash, held blurb, held asset URL |
| `legacy:s1:tng:019` | The Arsenal of Freedom — S1E21 | Hash, held blurb, held asset URL |
| `legacy:s1:tng:020` | Symbiosis — S1E22 | Hash, held blurb, held asset URL |

**Original publisher-description synopsis drafts:** Ten newly authored one-sentence paraphrases are held as **editorial proposals**, not public synopsis approval or source-truth of the episode's events. Character/organization mentions are pinned to **literal strings appearing in the corresponding publisher descriptions**—no shorthand lore reconciliation. For example, the *Coming of Age* card literally names `Captain Picard`, while *The Arsenal of Freedom* says only `Picard`, and that distinction is preserved. The compiler refuses adversarial, plausibly worded replacements to held synopsis text, not just `TODO` placeholders.

**Exact artwork mapping:** Each official thumbnail URL string found in the card HTML is pinned to the exact card's discovery row, title, episode ordinal and description fingerprint. A valid `thumbnails.cbsig.net` URL from a different episode fails validation. The URLs are **asset discovery leads only**: no image download into GitHub, no reuse license determination, no hotlink permission assertion, and no Explorer/public display.

**Identity and coverage:** No selected card is a visibly multipart/variant card; all ten still retain `NO_GLOBAL_WORK_IDENTITY_ASSERTED`. There is no new Source↔Work binding, global entity resolution, episode viewing, transcript extraction, close reading, semantic assertions, accepted governed coverage, published artwork, or Explorer population. The accepted discovery projection remains untouched. `SOURCE → WORK → LOCAL ENTITY → EVIDENCE → ASSERTION` remains an admission boundary rather than an inferred completion checklist.

Validation:

```bash
python3 tools/build_tng_publisher_cards_b011.py --check
python3 -m unittest tests.test_tng_publisher_cards_b011
python3 -m unittest discover -s tests -p 'test_*.py'
```

Deterministic code binds ten exact source-local IDs to the accepted 1,214-row discovery snapshot; pins publisher title, ordinal, description digest, exact per-row artwork URL, literal source-relative mentions and the held synopsis candidate; rejects false rights/media/coverage claims, changed Source identity, alias promotion, swapped image leads, and fabricated blurbs. It does **not** independently re-fetch at CI time or turn machine agreement into source authentication; a separate reviewer should check source fidelity and prose originality at the exact Git head.

**Next frontier after independently reviewed acceptance:** `legacy:s1:tng:021` onward (publisher S1 cards *Skin of Evil*, *We'll Always Have Paris*, *Conspiracy*, and *The Neutral Zone*) with overlap screening against accepted B004 first. Further breadth proceeds source-first; neither this batch nor a CI pass authorizes merging or public release.
