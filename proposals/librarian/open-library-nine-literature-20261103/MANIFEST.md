# Librarian Open Library covers — nine accepted source-local literary rows

Status: **proposal-only / independent artwork review required**. Base: accepted
`main` `da44aecc4a44829c2cd8c969e80ade7d311c355d` (2026-11-03). This packet
records **four edition-specific jacket image candidates** and **five
explicit holds** for the nine literary rows of `explorer/discovery-catalog.json`.
It neither generates nor authorizes `explorer/artwork-catalog.json`.

## Source observations

- `explorer/discovery-catalog.json` was read byte-for-byte at the pinned main
  commit; raw SHA-256 `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`.
  All nine rows are `SOURCE_LOCAL`/`UNVERIFIED_METADATA` with zero admission and
  coverage effects, **not nine reconciled Works**.
- Simon & Schuster and Penguin Random House/Titan publisher source-input
  receipt digests are pinned per candidate in `records.json`. One
  publisher/distributor listing is not an independent second witness merely
  because Open Library may carry a matching ISBN.
- On 2026-11-03, Lappy's Windows Python HTTPS client fetched the exact
  `openlibrary.org/isbn/<isbn>.json` redirect targets with status 200. The
  SHA-256 receipts in `records.json` hash the **raw UTF-8 HTTP response body**,
  not a reconstructed or normalized subset. JSON `isbn_13`, `key`, `covers`,
  and displayed title were inspected. Open Library responses can be edited;
  hashes identify this observation, not a permanent server state.
- All five original `covers.openlibrary.org/b/id/<id>-S.jpg?default=false`
  endpoints returned HTTP HEAD 200, `image/jpeg` and an Internet Archive image
  redirect. **HEAD success is not proof of jacket artwork**: an independent
  browser visual audit later rejected the `The Enterprise War` image as an
  interior title page. **No cover image bytes were downloaded, mirrored or hashed
  by this Librarian.**
- The Open Library [Covers API](https://openlibrary.org/dev/docs/api/covers)
  documents public HTML display and attribution. Its separate
  [licensing explanation](https://openlibrary.org/developers/licensing)
  cautions that underlying material may retain copyright. These are
  **API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED**, not licensed files.

## Four visually reviewed jacket receipts

| Accepted source-local row | Publisher edition ISBN | Open Library edition | Cover ID |
| --- | --- | --- | --- |
| `literature:prh-autobiography-kirk` | `9781783297481` | `OL28813033M` | `13083310` |
| `literature:prh-autobiography-picard` | `9781785659409` | `OL32028282M` | `10694457` |
| `literature:prh-autobiography-janeway` | `9781789095333` | `OL30052366M` | `12097815` |
| `literature:prh-autobiography-spock` | `9781785659416` | `OL33271375M` | `11945787` |

For Kirk, Open Library
omits the initial article in its edition title; the ISBN and publisher row
still agree. These title renderings are preserved rather than silently
rewritten. The exact raw JSON digests, publisher source locators, collection
lineage, and opt-in cover URLs reside in `records.json`.

## Five holds

- *The Enterprise War* (`9781982113315`, `OL28720619M`): metadata/ISBN
  crosswalk verified (raw edition JSON SHA
  `ecaca36ebb2419de7d96214f8ed8145c13bf1d90a20d0e72ac62e71090425208`);
  **independent hostile browser visual inspection on 2026-11-03 found
  `cover_id=12857937` depicts an interior title page, not the jacket**.
  This image is explicitly `IMAGE_VISUALLY_REJECTED_TITLE_PAGE` and must not
  render as a book cover. The review came from the separately assigned
  independent Auditor; no durable image-byte or screenshot digest is asserted.
- *Ring of Fire* (`9781668095898`, `OL57519042M`), *Second Self*
  (`9781982194833`, `OL48686369M`) and *The High Country*
  (`9781668002391`, `OL51045316M`) each had a 200 edition response with **no
  `covers` field**, not a verified available cover.
- *The Autobiography of Benjamin Sisko* (`9781803366258`) returned HTTP 404
  at its exact ISBN JSON endpoint. That does not prove no matching edition or
  jacket exists elsewhere; this row stays held.

## Independent review and release boundary

The independent Auditor's visual assessment distinguishes the four actual
jacket images from the rejected title page, but **this proposal cannot
authorize itself**. A separate code-owned, publisher-ISBN-bound release
validator and Pages package must then
verify those reviewed tuples; this proposal cannot approve itself. The
browser's existing opt-in/attribution/no-referrer policy applies if any are
later accepted for public API preview. No publisher art or private ebook cover
is reproduced in this repository.

Run:

```sh
python3 proposals/librarian/open-library-nine-literature-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/open-library-nine-literature-20261103 -p 'test_validate.py' -v
python3 -O -m unittest discover -s proposals/librarian/open-library-nine-literature-20261103 -p 'test_validate.py' -v
```

Coverage: **0 accepted Sources, Works, bindings, content close reads or coverage
events**; **0 publicly released cover assets or artwork sidecar entries**.
