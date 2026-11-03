# Three additional literary publisher-description candidates

**Role:** LIT · **2026-11-03 UTC** · **proposal only** · starting accepted main `5ea4a8d562e76931218329b8386e363e3c40845f`.

I opened and inspected the ISBN-specific **publisher product-description and bibliographic portions** of four Simon & Schuster pages. Three pages support one original short marketing-description paraphrase per candidate title. A fourth page distinguishes a second edition of *The Eternal Tide*. No complete book, chapter sequence, authenticated publisher HTML byte snapshot, private OPF/ZIP member, ebook bytes, audio or image was read or copied into Git. The publisher page's optional excerpt was not coded as full-book evidence.

| Publisher title and first-party product page | Exactly observed manifestation | Date and imprint | Overview scope |
| --- | --- | --- | --- |
| [*A Stitch in Time*](https://www.simonandschuster.com/books/A-Stitch-in-Time/Andrew-J-Robinson/Star-Trek-Deep-Space-Nine/9780743420587), Andrew J. Robinson | eBook ISBN `9780743420587`, 432 pages | 2000-05-01, Pocket Books/Star Trek | Publisher's reconstruction-and-Garak-life-framing, not a read of the memoir-like narrative |
| [*Star Trek: The Next Generation: Q&A*](https://www.simonandschuster.com/books/Star-Trek-The-Next-Generation-Q-A/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9781982160357), Keith R. A. DeCandido | Trade paperback ISBN `9781982160357`, 320 pages | 2020-05-02, Gallery Books | Publisher's Q/Picard crisis premise, not independently established story events |
| [*The Eternal Tide*](https://www.simonandschuster.com/books/The-Eternal-Tide/Kirsten-Beyer/Star-Trek-Voyager/9781668288559), Kirsten Beyer | Trade paperback ISBN `9781668288559`, 400 pages | 2026-10-17, Gallery Books | Publisher's Voyager fleet and Afsarah Eden premise; returning leader remains unnamed |

The separate [2012 mass-market edition page for *The Eternal Tide*](https://www.simonandschuster.com/books/The-Eternal-Tide/Kirsten-Beyer/Star-Trek-Voyager/9781451668186) lists ISBN `9781451668186`, Pocket Books/Star Trek, August 28, 2012, 400 pages. Its same title and creator are **source-local bibliographic evidence of a related manifestation**, not evidence of text equivalence or two independent narrative Works. In particular, a 2026 trade paperback listing does not make the underlying plot newly written in 2026; the separate earlier edition must remain visible during reconciliation.

## Deliberate nonduplication and source lineage

The accepted `explorer/synopsis-catalog.json` had 23 entries: **nine literary directory rows and fourteen film rows**. The independently accepted `proposals/publication/lit-overview-expansion-20261103/editorial-request.json` had **18 further literary candidates**, already staged for separate semantic editorial review. These three title/ISBN pairs occur in neither accepted candidate set. The validator pins exact snapshots of both, refusing silent duplicate reuse or source drift. This is a **three-source-local-candidate proposal**, not a declaration that all remaining Star Trek literature has been counted.

All four page readings share the **one Simon & Schuster publisher lineage**. Multiple formats or pages are not independent plot corroboration. The paraphrases capture what the publisher **describes**; they do not establish fictional-world facts, source-authenticated textual identity, full-text availability or the validity of the promotional claims. No numeric evidence confidence is invented. Exact raw HTML hashes are null because those bytes were not archived. The direct book text and rights/custody gap remains unresolved.

## Publication and rights hold

- Every original synopsis is marked `PUBLISHER_DESCRIPTION_PARAPHRASE` and `PROMOTIONAL_PAGE_CLAIMS_NOT_VERIFIED_BOOK_EVENTS`.
- Accepted Source↔Work bindings, accepted Works, evidence assertions, global identity, governed coverage and Explorer synopsis publication remain `NONE`. All book-reading and content tiers remain false.
- No book-cover URL, cover image, book excerpt or other publisher binary was republished; display rights are `NOT_ESTABLISHED_NO_PUBLIC_DISPLAY`.
- Director issue [#23](https://github.com/thebrazenbeard/trek-data-core/issues/23) still holds new novel close reads. Private holdings cannot be matched to these ISBN editions from title alone; no attempt to open the owner's private Books ZIPs was made.

## Validation and next gate

```bash
python3 proposals/research/lit-three-publisher-overviews-20261103/validate.py
python3 -O proposals/research/lit-three-publisher-overviews-20261103/validate.py
python3 -m unittest tests.test_lit_three_publisher_overviews -v
```

The validator pins exact observation bytes, author/title/ISBN-page metadata, the source publication status, the unresolved 2012-versus-2026 edition distinction, and the accepted preexisting literary sets. It rejects unauthorized fields and image/source/coverage promotion under optimized Python. Human independent source-review and Librarian edition family reconciliation are required before any directory or website publication, followed by the Director's separate protected-effect gate. No new close reading until #23 is released by accepted governance and authenticated source bindings.
