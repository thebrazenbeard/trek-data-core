# PIC: Paramount+ Season 2 episode-guide cards 1–5 (source-local)

**Batch:** `PIC.PPLUS.S2.FIRST5.CARDS.20261103`  
**Role:** PIC source-relative researcher  
**State:** proposal only, no accepted Work/coverage/publication effects  
**Accepted main at selection:** `d9294e19f812970fa70b45882c2d9813952e116a`  
**Live main rechecked before branch creation:** `90aee8750c87afb8f64fa5d687e76db6e3f1c7aa`; no Picard S2 source-local batch collision in its recursive tree.  
**Records SHA-256:** `832db61b789b9014e5e51dd43e2006751832dd01a8b37dd6db821de6c9854d80`

## Source actually read

- Paramount+ Season 2 episode guide, publisher edition: https://www.paramountplus.com/shows/star-trek-picard/episodes/2/. Its rendered card descriptions for S2E1–5 were actually read on 2026-11-03. The five episode numbers, titles, and literal mention tokens are grounded in those visible descriptions; they are publisher statements, not independent proof of depicted events.
- Direct HTTP GET of that page from Lappy/WSL returned **HTTP 200** twice with **271,518 bytes** in each response. SHA-256 receipts differed: `889000c328534710a7dd3b4f670cff0ea0a2bbb49b88ff41d6c1eebcd125a5e7` and `d0c28ad7afbd6b58d4e5ad12d9ac733243dc4d23c4be1d068da272a71eaddae3`. The complete HTML is **not stable across those retrievals**, and raw bytes are not archived in the public repo.
- Actual publisher card HTML was examined for the exact adjacent `/shows/video/{id}/` and `thumbnails.cbsig.net/_x/w400/...jpg` URL pair per episode. These are **source locators**, not observations that the full video was accessed or rights to reuse images.
- Prior source-local discovery file `proposals/discovery/modern-paramount-season2-first5-20261102/pic-observed-slots.csv`, pinned at SHA-256 `1ebab18e8e0ca4dc6a4204ddd6e68e338d8d346df5569a867f797b1dcbbeb78a`, independently rehashed. The historical CSV and fresh guide both derive from the same Paramount publisher family and are **not two independent witnesses**.

| Official publisher slot | Title | Rendered guide lines | Recorded work |
| --- | --- | --- | --- |
| S2E1 | The Star Gazer | 104–108 | Publisher card title, exact video/image URL locators, literal mentions, original HELD synopsis |
| S2E2 | Penance | 109–113 | Same fields |
| S2E3 | Assimilation | 114–118 | Same fields |
| S2E4 | Watcher | 119–123 | Same fields |
| S2E5 | Fly Me to the Moon | 124–128 | Same fields |

The `literal_name_mentions` array stores **publisher description terms only**, not asserted on-screen appearances or reconciled character identities. The short original `synopsis_paraphrase_candidate` strings are paraphrases of the publisher's brief descriptions, not verified complete-episode synopses. All five remain `HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE`.

## Release and acceptance gates

- Every discovered publisher CDN link is `HELD_NO_PUBLIC_DISPLAY_LICENSE`. **No image bytes** were downloaded, added to GitHub, published, or authorized for LCARS Explorer display.
- This batch does **not** include copyrighted full guide blurbs, transcripts, episode audio/video, scripts, or book text.
- The only asserted relation is **Source → source-local episode card → publisher-held locators/terms**. Work mapping, global identity, factual plot assertions, semantic analysis, and authoritative coverage projections remain outside the role.
- `accepted_source_binding_effect`, `accepted_work_effect`, `coverage_effect`, `denominator_effect` are all `NONE`. No move to `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, `ENTITY_LINKED`, or `AUDITED` is claimed.
- The IDs `pic-s2-e01-pplus-guide` through `pic-s2-e05-pplus-guide` are disjoint from Season 1 source-local IDs and from other Season 2 accepted/draft batches identified at selection. No paid services or access credentials used.

## Validation/falsification

```bash
python proposals/research/pic/picard-s2-first5-guide-cards-20261103/validate.py
python -O proposals/research/pic/picard-s2-first5-guide-cards-20261103/validate.py
python -m unittest discover -s proposals/research/pic/picard-s2-first5-guide-cards-20261103 -p 'test_*.py' -q
python -O -m unittest discover -s proposals/research/pic/picard-s2-first5-guide-cards-20261103 -p 'test_*.py' -q
python tools/validate.py
python -m unittest discover -s tests -p 'test_*.py' -q
```

`validate.py` pins five exact titles, positions, source HTML URL pairs, snippet references, original synopsis candidates, raw sample retrieval observations, and historical source input bytes. The independent hostile test suite (30 mutation cases and two duplicate-key probes) rejects title/ID/media swaps, false audiovisual read or rights, fake static HTML provenance, arbitrary source lineage, altered synopsis, fictional-truth promotion, and Work/coverage effects. Passing these model-written tests is **not** a substitute for independently comparing the actual first-party page.

**Next frontier:** Independent hostile review against live Paramount+ page and exact proposed commit, then review-qualified integration. Any public cover/episode still/thumbnail display requires separately established rights or an alternative licensed image.
