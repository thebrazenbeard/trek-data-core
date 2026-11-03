# PIC: Paramount+ Season 1 episode-guide cards 1–5 (source-local)

**Batch:** `PIC.PPLUS.S1.FIRST5.CARDS.20261103`  
**Worker role:** `PIC`  
**State:** bounded research proposal only  
**Records SHA-256:** `070dccdbda3b7a777e6f12201d725bd906610f4e1c5ee26e8c37c3a218c6829f`

## Primary source actual read

- Publisher: Paramount+ U.S. edition, one lineage `publisher:paramountplus.com`.
- Full publisher *season episode guide metadata*, **not** the five audiovisual episodes themselves: https://www.paramountplus.com/shows/star-trek-picard/episodes/1/
- On 2026-11-03 the rendered/text-extracted official guide was actually read (all ten Season 1 cards present), and the raw guide HTML was independently retrieved from Lappy through HTTP 200 to extract the exact first five card video and thumbnail URLs.
- Two 273,178-byte HTTP 200 source responses returned **different** SHA-256 values: `4c83db68d022e895fd5c1e7581e09aca04984828b6bc23ba4c7d0817f5e1356e` and `c0828d5836c211eebcc88bda32a21832d9ed8ac5b0bb08554f5d1ef984c0c250`. The raw changing HTML is **not** archived here. These are retrieval observations, not a replayable immutable source snapshot.
- Existing source-local inventory crosschecked: `proposals/discovery/modern-paramount-season1-20261102/pic-observed-slots.csv` at SHA-256 `a3c798fce4ab4121f8487319d921a56f42a3793b4668273474e69a74842f383c`. This corroborates display positions within the **same publisher family**, not independent story truth.

## Actually extracted work

| Official guide slot | Card title | Evidence locator | Other extracted structure |
| --- | --- | --- | --- |
| S1 E1 | Remembrance | Rendered guide lines 103–107 | Exact video-card URL, CDN thumbnail target, named mentions, held original synopsis paraphrase |
| S1 E2 | Maps and Legends | Rendered guide lines 108–112 | Same fields |
| S1 E3 | The End is the Beginning | Rendered guide lines 113–117 | Same fields |
| S1 E4 | Absolute Candor | Rendered guide lines 118–122 | Same fields |
| S1 E5 | Stardust City Rag | Rendered guide lines 123–127 | Same fields |

The five original synopsis candidates are concise restatements of the *publisher guide's description*, held as `HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE`, not verified full-episode plot summaries. Named mentions refer to words present on the publisher card; they do not attest to scene appearances or canonical identity reconciliation. Video-card URLs are *locators only*, not proof that a signed-in episode stream was played.

The five `thumbnails.cbsig.net` links were found directly in publisher page HTML, with each associated guide card's linked video ID. **No image bytes were downloaded or committed; none have a public-display license receipt.** Each remains `HELD_NO_PUBLIC_DISPLAY_LICENSE`. Do not show, mirror, or hotlink them in LCARS Explorer merely because these links were found.

## Hard acceptance boundary

- Source → potential Work index crosswalk only; no accepted global Source–Work binding, entities, reconciliation or formal semantic assertions.
- The guide's promotional descriptions are not complete episode texts, full audiovisual close-reads or independent corroboration.
- `coverage_effect`, `accepted_work_effect`, `accepted_source_binding_effect`, `denominator_effect`: all `NONE`.
- Five source-local records **do not advance** coverage to `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, or `AUDITED`.
- No copyrighted transcript text, video, audio or image binaries published. No monetary cost, source credentials, or private account session.

## Validation

```bash
python proposals/research/pic/picard-s1-first5-guide-cards-20261103/validate.py
python -m unittest discover -s proposals/research/pic/picard-s1-first5-guide-cards-20261103 -p 'test_*.py' -v
python tools/validate.py
python -m unittest discover -s tests -p 'test_*.py' -q
```

The validator pins all five episode positions, titles, original short paraphrases, named mentions, exact video/image URL pairs and observed source digests against an accepted discovery source hash. Its hostile tests reject same-host image substitution, video swaps, forged names, unreviewed synopsis edits, false rights, false close-read, identity promotion, fake raw source stability, duplicate JSON keys, and reordered/duplicate entries.

**Next PIC frontier:** S1 E6–10 of the same guide, using new source-relative structure and genuinely fresh accepted-main / open-draft deduplication. Independent review of this batch remains separate from the author.
