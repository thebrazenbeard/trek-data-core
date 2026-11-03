# PIC: Paramount+ Season 1 episode-guide cards 6–10 (source-local proposal)

**Batch:** `PIC.PPLUS.S1.LAST5.CARDS.20261103`  
**Role:** `PIC`, original source-local research; separate from accepted PR #358 (S1 episodes 1–5)  
**Accepted baseline inspected:** `b731dc6c08725b0fee52ce589b5ec159db1a0f9b`  
**Live `main` rechecked at branch creation:** `7e0c56e5bbef70296de034e5283ed6217e6e7f91`; PR #358's S1 E1–5 source-local batch was then accepted; this proposal's E6–10 IDs and paths remain distinct.  
**Records SHA-256:** `fe962cc235ffc84f5cff7a970a940419cf9a21dce72cd5844cae76ce89f9a9cc`

## Primary source actually read

- Official first-party season guide: https://www.paramountplus.com/shows/star-trek-picard/episodes/1/ (Paramount+, United States page). The rendered page was read on **2026-11-03**, including all five description-card windows in the table below. It showed ten Season 1 cards; this batch addresses only the *last five*.
- On Lappy/WSL, two direct HTTP GET responses were independently retrieved as source access checks: both HTTP **200**, each **273,178 bytes**, with SHA-256 digests `201bdde6ffbe0dcceaf3a65d6f677d9e5f6d657bfd676bcadb8a046a029ea664` and `20a548779772d17dd70723d8f61c3f3d3b2a8c199b9f2b7f8af686bc1992462d`. **Different digests** mean the complete HTML is not a stable byte-identical immutable source. Raw source bytes are not republished or archived in this public proposal.
- The HTML was inspected around the corresponding `div.episode` card blocks to recover five distinct Paramount+ `/shows/video/{id}/` link targets, each paired with its `thumbnails.cbsig.net` card image URL. These are **publisher-displayed URL locators**, not a guarantee that video streams or images are freely playable/reusable.
- Existing accepted discovery inventory crosscheck: `proposals/discovery/modern-paramount-season1-20261102/pic-observed-slots.csv`, exact SHA-256 `a3c798fce4ab4121f8487319d921a56f42a3793b4668273474e69a74842f383c`. That inventory derives from the same publisher guide/source family, **not** independent corroboration.

| Paramount+ guide slot | Source-local card title | Rendered guide lines | Extracted fields |
| --- | --- | --- | --- |
| S1 E6 | The Impossible Box | 128–132 | Video link; image URL; literal name/phrase mentions; held original synopsis |
| S1 E7 | Nepenthe | 133–137 | Same fields |
| S1 E8 | Broken Pieces | 138–142 | Same fields |
| S1 E9 | Et in Arcadia Ego, Part 1 | 143–147 | Same fields |
| S1 E10 | Et in Arcadia Ego, Part 2 | 148–152 | Same fields |

Every name or phrase recorded in `literal_name_mentions` is a term in the *publisher's guide-description text*, not proof that a character appears on screen, a claim is objectively true in that fictional world, or a global entity resolution. Original concise `synopsis_paraphrase_candidate` fields restate *promotional card descriptions*, **held** with state `HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE`. The worker did **not** view complete copyrighted episodes, scripts, or transcripts and must not claim close-read or full audiovisual indexing.

## Artwork provenance and display boundary

Five exact `thumbnails.cbsig.net` URL locators were recovered from first-party HTML adjacent to the five corresponding video IDs. **No image binary was downloaded, mirrored, committed, hotlinked for Explorer, or granted public-display rights.** Every image field stays `HELD_NO_PUBLIC_DISPLAY_LICENSE`. The mere existence of a publisher CDN URL is **not** a license. Any later display decision needs a separate documented authorization/assessment; this proposal is an inventory of candidates.

## Integration and coverage boundary

- This is `SOURCE → source-local guide card → publisher text/video/image locators → source-relative evidence`, **not** a global Work admission or canonical entity projection.
- All `accepted_source_binding_effect`, `accepted_work_effect`, `coverage_effect`, and `denominator_effect` are explicitly `NONE`. There is no accepted `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, or `AUDITED` promotion.
- `pic-s1-e06-pplus-guide` through `pic-s1-e10-pplus-guide` are disjoint from now-accepted PR #358's `pic-s1-e01-pplus-guide` through `pic-s1-e05-pplus-guide`.
- No copyrighted transcripts, complete publisher promotional blurbs, ebook content, video, or image bytes are published; no paid endpoints, account credentials, or hosted costs used.

## Reproducibility and falsification

```bash
python proposals/research/pic/picard-s1-last5-guide-cards-20261103/validate.py
python -O proposals/research/pic/picard-s1-last5-guide-cards-20261103/validate.py
python -m unittest discover -s proposals/research/pic/picard-s1-last5-guide-cards-20261103 -p 'test_*.py' -v
python -O -m unittest discover -s proposals/research/pic/picard-s1-last5-guide-cards-20261103 -p 'test_*.py' -q
python tools/validate.py
python -m unittest discover -s tests -p 'test_*.py' -q
```

`validate.py` pins exact video/CDN pairs, episode title/position, metadata line windows, literal terms, held original synopsis candidates, upstream digest and retrieved HTML receipts. Adversarial probes exercise source-spoofing, copyright/publication and coverage promotion, source-family laundering, first-five collisions, image/episode link swaps, invalid episode types, new plot assertions, and duplicate JSON fields. These are deterministic structural tests and model-written source analysis, **not human or independent real-world audiovisual verification**.

**Next frontier:** Independent reviewer to corroborate the first-party guide, source-local semantics and current-head CI before any protected integration. Then obtain appropriate image display rights, or select original licensed alternatives, before Explorer publication.
