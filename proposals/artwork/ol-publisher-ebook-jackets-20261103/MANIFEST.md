# Two additional genuine book jackets — HELD edition-specific source observations

Research date: 2026-11-03. Accepted source snapshot: `main`
`885df8dc60122e55d9f37195eabd0b1a7c67b3c6`; its **existing six**
Explorer covers are untouched. This packet is neither a release nor a Work
reconciliation. [Source rows](../../../explorer/discovery-catalog.json) SHA-256:
`2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`.

## Exact candidates

| Public source-local literary row | Publisher eBook edition identity | Open Library exact edition / cover | Actual M front jacket verified | Actual L file verified |
| --- | --- | --- | --- | --- |
| `literature:proposed-lit-picard-second-self` | *Star Trek: Picard: Second Self* — Una McCormack — `9781982194840` | `OL34985674M`, cover `14663887` | 180×280 JPEG, 21,305 B, SHA `c37b62e49e1c14f5b925ad295a20230341ce7dc9e8dbeefcb8893aa173860a11` | 257×400, 34,166 B, SHA `c876b5f87b1525d3fdc43e0d4b2efe3ba6e10068d8389dd7582d2138159ae0a1` |
| `literature:proposed-lit-snw-high-country` | *Star Trek: Strange New Worlds: The High Country* — John Jackson Miller — `9781668002407` | `OL38063809M`, cover `12773868` | 180×271 JPEG, 23,434 B, SHA `11fdfa946b3834be1a0bce29925bd10ed78f101e791949fc42758edcb0321566` | 315×475, 47,677 B, SHA `743d327a97a0820268a00328b76fdb4436b408d31051833254e8c63fcad428dd` |

First-party edition pages (the existing public rows currently point to
**trade-paperback** product URLs; these exact, separately selected variants
are **eBooks**, both listed in each public row's `details`):

- [*Second Self* eBook ISBN `9781982194840`](https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781982194840)
- [*The High Country* eBook ISBN `9781668002407`](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-The-High-Country/John-Jackson-Miller/Star-Trek-Strange-New-Worlds/9781668002407)

Open Library **edition JSON** raw-byte SHA values and source URLs are in
`records.json`. Each exact edition response advertises that ISBN in
`isbn_13` and the displayed cover ID in `covers`. Actual M and L JPEG bytes
were fetched and decoded with Pillow on Lappy; SHA/bytes/dimensions above
come from the responses. Both exact **M JPEG pixels were directly inspected**
and are front jackets displaying the corresponding titles and authors, not
interior pages or audiobook narration artwork. No image bytes were committed.

Open Library [Covers API](https://openlibrary.org/dev/docs/api/covers)
documents consumer display endpoints and attribution, **not** copyright
ownership or redistribution clearance. Underlying copyright remains
`UNRESOLVED`. Four distinct independent roles and browser opt-in tests would
still be required before *any* separately proposed 6→8 UI release.

## Explicitly excluded findings, not invented cover counts

- *The Enterprise War*: trade-paperback ISBN `9781982113315` Open Library
  cover `12857937` was previously actually inspected as an **interior title
  page**, not a jacket. Its eBook ISBN `9781982113322` has a genuine
  front jacket (`11752674`) but Open Library `/books/OL33050254M.json`
  asserts `physical_format: paperback` while first-party Simon & Schuster
  identifies that same ISBN as **eBook**. Preserve this format disagreement;
  do not silently release it as an edition-verified eBook jacket.
- *Second Self* Open Library *work-level* cover `13195854` is square and
  visibly prints an audiobook reader credit, so it is **not** the paperback
  or eBook front-jacket candidate used here.
- *Ring of Fire* public hardcover ISBN `9781668095898` and eBook ISBN
  `9781668095911` have Open Library edition JSON but no `covers` field;
  `9781668095904` trade paperback and *The Autobiography of Benjamin Sisko*
  paperback `9781803366258` return 404 from Open Library ISBN JSON at this
  checkpoint. A Sisko hardcover variant `9781803366234` has a cover but is
  **not the paperback ISBN listed in the accepted public row**. No guessed
  cross-edition image was assigned.
- The owner's ten private OPF crosswalk candidates were **not** source-bound
  to these accepted public rows and are not cover release authority.

Validation: `python3 tools/validate_two_ebook_cover_candidates.py --check`
and `python3 -m unittest tests.test_two_ebook_cover_candidates -q`.

Next frontier: independent publisher/edition verification and separately
fetched M/L JPEG **visual** inspection by different reviewers. Only then
consider a narrow opt-in public release, with the six existing covers as
immutable fallback, no physical image binaries in GitHub Pages, and no
changes to literary/semantic coverage.
