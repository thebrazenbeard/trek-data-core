# PIC: Paramount+ Season 2 episode-guide cards 6–10 (source-local)

**Batch:** `PIC.PPLUS.S2.LAST5.CARDS.20261103`  
**Worker role:** PIC source-relative researcher  
**State:** proposal only; no accepted Work, coverage, publication, or rights effects  
**Accepted main at selection:** `1ef3e4ef9cefa0e3ccd90caa4530a84c167a8ca6`  
**Related accepted batch:** PR #366 (S2 episodes 1–5), merged before this proposal was pushed  
**Live main rechecked at branch preparation:** `e5bfab953a9da961fd9d7ebc5d94b432ebca8fbc` (S2 E1–5 accepted; no E6–10 batch present).  
**Records SHA-256:** `5e98f1e15c9be958512e64d719ded6549f70069b0b252f42f253785351f6c8ef`

## First-party source actually read

- Paramount+ U.S. *Star Trek: Picard* Season 2 guide: https://www.paramountplus.com/shows/star-trek-picard/episodes/2/. The visible guide card descriptions, in episode order, were read at the source on **2026-11-03**. The guide presents ten slots; this proposal covers **exactly episodes 6–10**.
- Direct HTML retrieved twice on Lappy/WSL via HTTP GET, both HTTP 200 and 271,518 bytes, but **different** SHA-256 values: `b609f7a17bb94e2a502cb875d7f90b25aea0978961070103751aa58fc84bae5e` and `741f6748b12dfd6d521783c1915704373a0874897b58936cae7084d66fdf2669`. The source is mutable, and the raw HTML is **not** archived or republished; these receipts document access, not a replayable immutable snapshot.
- **Independent digest-rebind repair:** another two HTTP 200 samples produced differing whole-page SHA-256 receipts `04b808109afc6b2e18e8ce8881c7a0747949f9b36d09b48a2fd9c567314590cf` and `d086694d2bc089996e3058470d0070e50053dd337a561bf8d14385804a143b3b`; the five *per-card decoded description* fingerprints below were identical across both samples. Each fingerprint is computed on that same card's `js-episode-copy` HTML after stripping tags, HTML entity decoding, collapsing whitespace, and SHA-256 encoding UTF-8 (`HTML_CARD_COPY_TEXT_ENTITY_DECODE_TAG_STRIP_COLLAPSE_WHITESPACE_SHA256_UTF8_V1`). The full publisher descriptions are **not** published.
- Actually inspected each HTML episode card's `aa-link` identifier and adjacent `href="/shows/video/.../"` / `<img src="https://thumbnails.cbsig.net/...jpg">` URL pair. No episode video, script, transcript, image binary, or image license was obtained by this retrieval.

| Publisher slot | Card title | Rendered lines | Publisher description SHA-256 / normalized length |
| --- | --- | --- | --- |
| S2E6 | Two of One | 129–133 | `388ed86b460ad19399bbf920eed661573c0f805e4e56f8384614644e61632ab1` / 270 |
| S2E7 | Monsters | 134–138 | `c8be163ef81d669f6fcb416264e18f2c0f554f37399a0a0a153baa59528e3c26` / 289 |
| S2E8 | Mercy | 139–143 | `42fe8ed9fafa491224d4f3e92d923ad3b23347e0998c31894ecdea172fe1abf5` / 202 |
| S2E9 | Hide and Seek | 144–148 | `763e650173da661155c882183e9f59c46aa72d912a155035c15cf87c49d36a3e` / 221 |
| S2E10 | Farewell | 149–153 | `72e6692eb404ac5b778dc5b6b4818323d7dc29ee350f9f0898fd104d8fa3e892` / 145 |

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

The closed-schema validator pins five title/slot/line windows, exact publisher video–image URL pairs, **same-card normalized publisher description SHA/length**, retrieved HTML receipts, held original summaries and literal mentions, plus accepted discovery bytes and non-admitted leads. The optional `source_html` validator mode extracts all 10 live-guide cards and rechecks episode position, heading, anchor, video, thumbnail, and description digest as one atomic group. More than 35 hostile field/value mutations and duplicate-key examples include same-source cross-row digest/length swaps, fake digest, malformed digest algorithm, forged media rights/coverage/identity, and title/media/synopsis swaps. A synthetic card-page fixture tests same-card parser behavior without storing publisher prose. Dynamic HTML receipts remain observational rather than immutable replay; only a fresh first-party source fetch can independently corroborate source assertions. Structural tests do not substitute for independent source review.

**Next frontier:** independent hostile reviewer verify first-party direct page and this exact proposed head; if qualified, protected integration. A separate approved artwork publication pathway remains necessary for Explorer thumbnails.
