# Artwork candidate intake, ten source-backed metadata records — **all held**

Local proposal only, against authoritative GitHub `main@3028765359001b90bc3e6b5c1835ee283b326e91` (confirmed separately by literal GitHub remote lookup). Previous source-rights audit: local `d8fcd7b`. The checkout's `origin` is another **local** worktree and must never be mistaken for live GitHub `main`.

## Actual bounded result

`records.json` deterministically projects **ten already observed first-party publisher image-URL leads** from the accepted Librarian source packet `artwork-primary-asset-locators-20261103`:

| Lane | Exact source-local observations | Kind | Rights/eligibility |
| --- | ---: | --- | --- |
| Episodes | 4 SNW S3 episode-card thumbnails on Paramount+ | Publisher page cards | Permission **not** established; held |
| Films | 3 StarTrek.com `og:image` headers | Generic film site headers, **not** verified theatrical posters | Permission **not** established; held |
| Literature/editions | 1 S&S eBook jacket, 2 distinct *audio-edition* cover links | Edition-specific publisher cover links | Permission **not** established; held |
| **Total** | **10** | **Metadata references only** | **0 public/rehost eligible** |

The exact publisher page URL, image locator URL, source-local ID, image type, source-packet digest, accepted source-input file and digest, source-worker locator observation digest, and current review/rights state are recorded per candidate. `source_receipt` is a **reported source/HTML observation and deterministic file lineage**, not a copyright clearance document or independent re-fetch of the original HTML today. No image data, local image path, Base64, binary digest masquerading as permission, or transcript/book contents are included.

Source packet digest: `9ffde76a5cd14d915dd17e672c8a5e3dc87d9f7fbc1d085e2638ab732f40f972`. The accepted source packet's own validator pins each of the ten exact publisher-page → image URL → source-local ID relations and the four underlying source input digests. The builder refuses a modified packet before producing the queue.

## Publication and authorization

> **Hostile review:** A publisher's `og:image`, episode-card CDN link, or downloadable book jacket shows where its page refers to an image. It does not grant an independent third party permission to mirror, transform, or publicly display copyrighted artwork.

> **Hostile review:** A source-local ID is not a globally reconciled Work ID. Rebranding two audio-edition covers as print books or generic film headers as theatrical posters would manufacture image-work coverage.

> **Hostile review:** A rights label, arbitrary uploaded permission string, hash, attribution, or one reviewer name in a proposed JSON document cannot self-authorize a Pages release. An independent rights review and the existing separate code-owned `tools/validate_artwork_release.py` pin gate remain mandatory.

`tools/build_artwork_candidate_intake.py` has only two modes:

- `--build` creates **only** the fixed proposed metadata packet (refuses overwrite).
- `--check` validates it byte-lineage-equivalent against the accepted source receipt; no remote requests or artwork copy.

The builder has **no API** to promote, license, copy, rehost, or render images. Every candidate is `HELD_SOURCE_URL_ONLY`, with `UNDERLYING_IMAGE_COPYRIGHT_UNRESOLVED`, null license/rights/visual reviewers, empty allowed operations, and false display/rehost eligibility. A future rights-cleared image needs **independently recorded** image identity, rights holder and scope (display versus download/rehost, derivatives, attribution, term), source URL, specific image bytes hash, legal permission/license receipt, separate reviewer, exact image-work binding, versioned acceptance and release gate tests. Any new rights conclusion should be a separately reviewed record, not an in-place overwrite of this held source packet.

The six existing **opt-in Open Library API jacket previews** remain a separate existing path with documented provider API embedding but unresolved underlying copyright; they are not among these ten rights-unverified first-party publisher asset leads. None of the ten are automatically rendered by Explorer. LCARS abstract placeholders do not count as real episode/film thumbnail coverage.

## Checks

```bash
python3 tools/build_artwork_candidate_intake.py --check
python3 -m unittest tests.test_artwork_candidate_ingestion -v
python3 proposals/librarian/artwork-primary-asset-locators-20261103/test_validate.py
python3 tools/validate_artwork_release.py --check --verify-git
```

The 20 new negative/contract tests challenge fabricated license/reviewer/permission receipts, false coverage, film-header versus poster and audio-versus-book type changes, source-row or URL swaps, duplicate keys, source path injection and source hash drift. **Coverage, accepted Source/Work, UI, public release, remote write effects: NONE.**
