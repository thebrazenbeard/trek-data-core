# Classic TOS: ISBN-specific edition and publisher cover-source observations

**LIBRARIAN candidate only** · baseline accepted `main@8a89b16e96220188d200b6ff9300fb90fa137627` · observed 2026-11-03 UTC.

Four rendered first-party Simon & Schuster product pages were actually read in their `Product Details` and `Resources and Downloads > High Resolution Images` sections. They represent **four ISBN-specific manifestations of three proposed Work labels**. All four names are absent as literary titles from the pinned 1,214-row Explorer candidate directory; this is *not* a claim they were absent from legacy literary imports or the franchise.

| Publisher Work label | Edition/ISBN | Imprint · publisher-listed date · length | Cover-source locator |
| --- | --- | --- | --- |
| *The Entropy Effect* (Vonda N. McIntyre) | [eBook · 9780743412094](https://www.simonandschuster.com/books/The-Entropy-Effect/Vonda-N-McIntyre/Star-Trek/9780743412094) | Pocket Books/Star Trek · 2002-10-08 · 224 pages | Official product page `Resources and Downloads > High Resolution Images > Book Cover Image (jpg)` |
| *The Entropy Effect* (Vonda N. McIntyre) | [Trade paperback · 9781451607536](https://www.simonandschuster.com/books/The-Entropy-Effect/Vonda-N-McIntyre/Star-Trek-The-Original-Series/9781451607536) | Gallery Books · 2010-06-01 · 224 pages | Same section on its **separate edition product page** |
| *The Wounded Sky* (Diane Duane) | [eBook · 9780743419642](https://www.simonandschuster.com/books/The-Wounded-Sky/Diane-Duane/Star-Trek-The-Original-Series/9780743419642) | Pocket Books/Star Trek · 2000-09-22 · 224 pages | Same section on its edition product page |
| *The Final Reflection* (John M. Ford) | [eBook · 9780743419673](https://www.simonandschuster.com/books/The-Final-Reflection/John-M-Ford/Star-Trek-The-Original-Series/9780743419673) | Pocket Books/Star Trek · 2000-09-22 · 256 pages | Same section on its edition product page |

The publisher exposes cover-image links on all four pages. **Only the presence and page-section location of those links were indexed**; their image URLs, bytes, licenses, uploader identities, dimensions and actual visual content were neither retrieved nor authenticated. An official marketing download link is not in itself permission to reproduce or hotlink art on a GitHub Pages site. No thumbnail/display, CDN allowlist, image transfer or rights promotion follows from this proposal.

## Edition and lineage holds

- The eBook and Gallery trade paperback of *The Entropy Effect* have different ISBNs, imprints and publisher dates; identical listed 224-page extents do **not** demonstrate identical text or the same source bytes.
- Earlier [legacy external crosswalk tranche 001](../legacy-intake/ST_LIBRARIAN_EXTERNAL_CROSSWALK_TRANCHE_001.json) includes *The Wounded Sky* with legacy Memory Alpha-derived print ISBN-10 `0671473891` and 255 pages. Its old print observation and this modern eBook `9780743419642` / 224 pages are **not the same edition** merely because title and author match; no accepted Source↔Work reconciliation is made.
- All four observations share the **one Simon & Schuster publisher family**, though two imprints appear. A retailer mirror, STAPI, Memory Alpha, or another descendant may repeat data and should not automatically count as independent corroboration.
- Publisher product dates are publisher-listed edition metadata, **not asserted original release dates**, complete book reads, legal clearance, canonical continuity, edition equivalence or source-body custody. Rendered page text was examined; raw HTTP response bytes and versions were unavailable. No book prose, summaries or photographs were imported.

> **Hostile challenge:** A `Book Cover Image` link can identify promotional media without demonstrating rights to display it. A valid ISBN and visually plausible cover could still refer to a different manifestation. Later edition data can disagree with historical print metadata without either field being automatically false; preserve the source and edition scopes before reconciliation.

Reproduce: `python3 proposals/librarian/tos-classics-cover-editions-20261103/validate.py` and `cd proposals/librarian/tos-classics-cover-editions-20261103 && python3 -O -m unittest -v test_validate`. The validator pins the accepted catalog SHA, exact publisher-title/author/format/imprint/date/pages/ISBN/URL mapping, four link-presence statuses and zero protected effects. **Coverage:** zero new accepted Sources, Works, editions, bindings, close reads, research events, thumbnails or deployed assets.
