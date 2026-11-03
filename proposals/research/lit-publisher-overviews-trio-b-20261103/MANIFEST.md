# Three additional literary publisher-overview candidates — wave B

**Role:** LIT. **Observation date:** 2026-11-03 UTC. **State:** `PROPOSAL_ONLY`, not an accepted Source, Work, Evidence, overview release, or coverage advancement. Based on accepted `main` `8a89b16e96220188d200b6ff9300fb90fa137627`. Research governance issue #23 still holds new literary close-reading; this packet used only public official publisher metadata and description sections.

I read the publisher's *About the Book* and edition product information for **three distinct book titles/four edition pages** and wrote original short, explicitly source-labeled paraphrases. The site exposes images as resources, but **no cover binary, image URL, ebook bytes, or raw copied marketing text** is in this packet. Book text was not read, possessed, or checked. The raw HTML/page bytes are not in custody and cannot be hashed or treated as an immutable source here. All pages belong to **one upstream publisher**; four URLs are not four independent corroborators.

| Source-local title candidate | Publisher edition page | Metadata observed |
|---|---|---|
| *The Captain's Oath* — Christopher L. Bennett | [9781982113292](https://www.simonandschuster.com/books/The-Captains-Oath/Christopher-L-Bennett/Star-Trek-The-Original-Series/9781982113292) | Pocket Books/Star Trek; trade paperback; May 28, 2019; 400 pages |
| *Star Trek: Deep Space Nine: The Never Ending Sacrifice* — Una McCormack | [9781439109618](https://www.simonandschuster.com/books/Star-Trek-Deep-Space-Nine-The-Never-Ending-Sacrifice/Una-McCormack/Star-Trek-Deep-Space-Nine/9781439109618) | Pocket Books/Star Trek; mass-market paperback; August 25, 2009; 384 pages |
| *Architects of Infinity* — Kirsten Beyer | [9781668282182](https://www.simonandschuster.com/books/Architects-of-Infinity/Kirsten-Beyer/Star-Trek-Voyager/9781668282182) | Gallery Books; trade paperback; September 12, 2026; 400 pages |
| **Separate edition of the same publisher-displayed title** | [9781501138768](https://www.simonandschuster.com/books/Architects-of-Infinity/Kirsten-Beyer/Star-Trek-Voyager/9781501138768) | Pocket Books/Star Trek; mass-market paperback; March 27, 2018; 400 pages |

The publisher displays “The Never Ending Sacrifice” **without a hyphen** in the book title, while its author biography uses “The Never-Ending Sacrifice.” This packet records the edition-page title verbatim as a title value; the discrepancy needs source-aware reconciliation. It does not silently normalize the two strings.

*Architects of Infinity* has two distinct publisher-listed ISBN formats with identical listed extent. **That is not proof their full text is byte- or content-equivalent.** The alternate edition is retained as `text_equivalence=UNVERIFIED` rather than collapsed into one edition. Cover resource links on these publisher pages do **not** provide a verified redistribution/display license, so all artwork remains on hold.

## Deterministic checks

`observations.json` SHA-256 is `042591beed80964fe6e050f38f8947a6f0a55d7fec0e4b66cf13c32edfd55e15`; `validate.py` pins its exact byte hash, checks all nested field shapes, ISBN-13 checksums, verified edition/URL combinations, content anchors, source lineage and hold flags. It also inspects current accepted proposal JSON for exact title/ISBN overlaps. The 16 hostile unit tests reject injected private paths, copyrighted prose, image links or claimed rights, provenance/identity promotions, swapped edition metadata, checksum invalidity, unanchored overviews and `python3 -O` bypass.

Distinct proposals already on `main` or pending in separate local branches were checked during selection; candidates are not a claim of exhaustive franchise novelty or a globally reconciled Work identity. No `explorer/` asset, release, site, global identity mapping, or coverage ledger is edited. Independent publisher re-read and separate editorial admission would be required before use in public projections.
