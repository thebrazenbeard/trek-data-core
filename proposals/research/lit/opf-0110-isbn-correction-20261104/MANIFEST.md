# OPF `0110`: held ISBN10 extraction correction candidate

**LIT proposal only** · Reviewed **2026-11-04** against accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91`. Issue #23 remains the controlling hold for literary source/edition admission and close reads. This is **not** an update to accepted Librarian observations, a private ebook edition authentication, or a production parser migration.

## Actual discrepancy, distinct from its unknown cause

The accepted metadata observation for `opf-local:0110` (`proposals/librarian/private-opf-metadata-20261103/observations.json`, source bytes SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`) reports the source-local title *A Time for War, A Time for Peace*, creator `Keith R.A. DeCandido`, publisher `Pocket Books`, year `2004`, and **empty** `isbn_checksum_valid` list. Its original OPF XML member fingerprint is `4c35fb7b4991d34add2e92c450475edda12e77b773d99de2e14bcab33d16b0aa`.

The already accepted held publisher proposal (`proposals/research/opf-seven-official-editions-20261103/observations.json`, SHA-256 `3d3aa4703bb2ab47291aa7fadb487320ed4cbef68c7456fabe09c52a1e848d42`) records a **prior independent owner-host XML byte audit**, observing `<dc:Identifier>ISBN 0-7434-9997-2</dc:Identifier>` (literal and casing), plus unrelated UUID identifiers. ISBN10 normalization and check-digit verification yield `0743499972`, which mathematically maps to ISBN13 `9780743499972`. The current source-local derivative's omission is therefore a **documented mismatch between two receipts**, not license to overwrite its original evidence. I did **not** personally reopen or rehash that owner-private XML this wave.

The currently checked-in `tools/inventory_opf_metadata.py::opf_metadata` already lowercases *namespaced XML local element names* before assigning whitelisted fields, so it should preserve `<dc:Identifier>` as a private `identifiers` entry. However, the separate owner-host routine that created the *accepted* `isbn_checksum_valid` projection is not available for code inspection here. **Its precise bug, including whether the cause was tag casing, identifier-string matching, data normalization, or a different stage, is UNKNOWN.** Do not report this synthetic reproduction as proof of an upstream bug in that routine.

## Red-before → green-after, strictly synthetic

`test_validate.py` contains miniature generated OPF packages with mixed-case `dc:Identifier`/`dc:identifier`, the exact syntactic ISBN10 **pattern** from the held receipt, checksum failures, a GUID, description text, and intentionally missing namespace. With a deliberately empty ISBN candidate extractor, tests were **RED: 4 assertion failures of 5 tests** (after a first missing-module import failure). The source-local proposal `candidate_parser.py` then implemented a narrow correction candidate, using the existing secure OPF metadata parser, strict whole-string ISBN token rules, checksum verification, duplicate suppression, and an explicit review hold when a missing namespace is repaired **in memory only**. The synthetic checks turned GREEN, with further negative cases for non-ISBN strings and external-entity declarations.

This parser exports only checksum-valid ISBN10/13 candidates plus a review flag. It does not export raw UUIDs, private paths, prose, covers, or direct files. It neither changes the global Librarian parser nor reprojects the accepted 347 OPFs. Its only production path is an explicit future governed review, not an automatic source mutation.

## Two real publisher product pages, still separate

I re-opened and read the product heading, format and `Product Details` on these two direct first-party Simon & Schuster pages (full rendered text, no raw HTML body snapshots):

| Publisher page | Observed bibliographic product | Relation to the owner-private source |
|---|---|---|
| [2004 eBook](https://www.simonandschuster.com/books/A-Star-Trek-The-Next-Generation-Time-9-A-Time-for-War-A-Time-for-Peace/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9780743499972) | Keith R. A. DeCandido; Pocket Books/Star Trek, October 1, 2004; **ebook**; 384 pages; ISBN13 **9780743499972** | Mathematically matches prior owner-XML ISBN10 and bibliographic publisher/year hints; **private source edition and text equivalence unverified**. |
| [2019 Trade Paperback](https://www.simonandschuster.com/books/A-Star-Trek-The-Next-Generation-Time-9-A-Time-for-War-A-Time-for-Peace/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9781982134907) | Same author and title; **Gallery Books**, May 18, 2019; **trade paperback**; 384 pages; ISBN13 **9781982134907** | Distinct publisher manifestation; **do not** substitute the trade ISBN, merge formats or infer text identity from equal page counts. |

Publisher promotional synopsis content is *publisher testimony*, not book close-read evidence or objective in-universe canon. Both pages come from **one corporate publisher family**, not two independent witness institutions. I neither read ebook prose nor collected image bytes.

> **Hostile challenge:** Correct checksum mathematics and a live publisher page can corroborate bibliographic identifiers, but they do not establish the content of the owner-private conversion, completeness, rights, original edition authenticity, Work equality or continuity class. Accepted source evidence should be corrected only by a versioned, separately reviewed Librarian/Consolidator decision that preserves the superseded observation and independent source byte receipts.

## Reproduce locally

```sh
python3 -m unittest discover -s proposals/research/lit/opf-0110-isbn-correction-20261104 -p 'test_validate.py' -v
python3 proposals/research/lit/opf-0110-isbn-correction-20261104/validate.py
python3 -m unittest tests.test_opf_metadata_intake tests.test_opf_seven_publisher_crosschecks -v
python3 tools/build_private_opf_metadata_index.py --check
python3 tools/build_opf_seven_publisher_crosschecks.py --check
```

The proposal validator pins accepted OPF and publisher receipt bytes, source-local row, original XML fingerprint and reported identifier, both distinct official product fields, and negative admission flags. It does **not** refetch publisher pages or private XML. New/accepted literary research counts and Explorer outputs remain unchanged: **0 additional Works, 0 accepted source/edition bindings, 0 close reads, 0 coverage change, 0 artwork release.**

**Next frontier:** Librarian/Consolidator independent review of the exact owner-host extraction path, original XML member and versioned correction record under #23, then requalify any source-binding proposals. Do not silently rewrite the 347-row derivative or its downstream search index.
