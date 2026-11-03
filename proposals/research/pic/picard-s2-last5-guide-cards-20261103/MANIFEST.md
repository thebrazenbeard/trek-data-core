# PIC: Paramount+ Season 2 episode-guide cards 6–10 (source-local)

**Batch:** `PIC.PPLUS.S2.LAST5.CARDS.20261103`  
**Worker role:** PIC source-relative researcher  
**State:** proposal only; no accepted Work, coverage, publication, or rights effects  
**Accepted main at selection:** `1ef3e4ef9cefa0e3ccd90caa4530a84c167a8ca6`  
**Related accepted batch:** PR #366 (S2 episodes 1–5), merged before this proposal was pushed  
**Live main rechecked at branch preparation:** `e5bfab953a9da961fd9d7ebc5d94b432ebca8fbc` (S2 E1–5 accepted; no E6–10 batch present).  
**Records SHA-256:** `830e1b95715058e43271e3eea8e2e4820b0a35bf83dd5ac6dbd4a1c7fa66c7d5`

## First-party source actually read

- Paramount+ U.S. *Star Trek: Picard* Season 2 guide: https://www.paramountplus.com/shows/star-trek-picard/episodes/2/. The visible guide card descriptions, in episode order, were read at the source on **2026-11-03**. The guide presents ten slots; this proposal covers **exactly episodes 6–10**.
- Direct HTML retrieved twice on Lappy/WSL via HTTP GET, both HTTP 200 and 271,518 bytes, but **different** SHA-256 values: `b609f7a17bb94e2a502cb875d7f90b25aea0978961070103751aa58fc84bae5e` and `741f6748b12dfd6d521783c1915704373a0874897b58936cae7084d66fdf2669`. The source is mutable, and the raw HTML is **not** archived or republished; these receipts document access, not a replayable immutable snapshot.
- Actually inspected each HTML episode card's `aa-link` identifier and adjacent `href="/shows/video/.../"` / `<img src="https://thumbnails.cbsig.net/...jpg">` URL pair. No episode video, script, transcript, image binary, or image license was obtained by this retrieval.

| Publisher slot | Card title | Rendered lines | Extracted source-relative fields |
| --- | --- | --- | --- |
| S2E6 | Two of One | 129–133 | Exact video-card and CDN thumbnail URL, literal publisher terms, original HELD synopsis |
| S2E7 | Monsters | 134–138 | Same fields |
| S2E8 | Mercy | 139–143 | Same fields |
| S2E9 | Hide and Seek | 144–148 | Same fields |
| S2E10 | Farewell | 149–153 | Same fields |

The terms in `literal_name_mentions` occur within the corresponding *publisher descriptions*. An utterance in a guide is evidence of publisher wording, **not** independent evidence that a character appears, that an alternate reality has a particular ontology, or that a promotional claim is objectively true within the fiction. Five original concise synopsis candidates paraphrase that same source and remain `HELD_SOURCE_RELATIVE_PARAPHRASE_NOT_FULL_EPISODE`, not fully read plot analyses.

## Discovery crosswalk without evidence laundering

The accepted `explorer/discovery-catalog.json` file (SHA-256 `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`) already contains five unverified Wikidata title-only leads `lead:0133` through `lead:0137`. They agree with the five Paramount card **titles**. That is a separate discovery lineage, but the leads do **not** establish publisher episode positions, actual audiovisual content, independent synopsis truth, or global identity. Their discovery-only, unverified, source-local, no-coverage status is deliberately preserved.

## Artwork, synopsis, and acceptance barriers

- Every recorded `thumbnail_url` is a directly observed source locator, with `thumbnail_status=HELD_NO_PUBLIC_DISPLAY_LICENSE`. **No image bytes were downloaded, mirrored, hotlinked for public Explorer display, or authorized for reuse**. Publisher CDN location alone is not a display grant.
- Five `synopsis_paraphrase_candidate` strings are original brief held research candidates, not public synopsis output; no full publisher description or transcript content was republished.
- `accepted_source_binding_effect`, `accepted_work_effect`, `coverage_effect`, and `denominator_effect` remain exactly `NONE`. No accepted Source–Work pair, global entity merge, semantic interpretation, or projection update.
- `pic-s2-e06-pplus-guide` through `pic-s2-e10-pplus-guide` are unique within Season 2 and disjoint from accepted PR #366's first-five IDs and already accepted Season 1 batches.
- This source-guided metadata research does **not** qualify as `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, or `AUDITED` audiovisual coverage.

## Reproducibility and adverse-case verification

```bash
python proposals/research/pic/picard-s2-last5-guide-cards-20261103/validate.py
python -O proposals/research/pic/picard-s2-last5-guide-cards-20261103/validate.py
python -m unittest discover -s proposals/research/pic/picard-s2-last5-guide-cards-20261103 -p 'test_*.py' -q
python -O -m unittest discover -s proposals/research/pic/picard-s2-last5-guide-cards-20261103 -p 'test_*.py' -q
python tools/validate.py
python -m unittest discover -s tests -p 'test_*.py' -q
```

The closed-schema validator pins five title/slot/line windows, exact publisher video–image URL pairs, retrieved HTML receipts, held original summaries and literal mentions, plus a current accepted discovery byte digest and non-admitted lead status. More than 30 hostile field/value mutations and three duplicate-key examples exercise forged media rights, coverage and identity promotion, title/video/thumbnail substitutions, evidence laundering, falsified raw HTML/source claims, and unreviewed synopsis changes. Structural tests and model reviewer agreement do not substitute for an independent source read.

**Next frontier:** independent hostile reviewer verify first-party direct page and this exact proposed head; if qualified, protected integration. A separate approved artwork publication pathway remains necessary for Explorer thumbnails.
