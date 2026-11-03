# Three publisher-verified eBook editions in absent literary series

**LIBRARIAN proposal only** · accepted `main@5b0fb86b322811ccea58f88f20d69bd4e62e9b22` · observed 2026-11-03 UTC.

The accepted candidate Explorer directory at `explorer/discovery-catalog.json` has 1,214 source-local rows and **zero exact literary title rows** for the three independently reopened publisher pages below. This is a discovery-directory **gap**, not three unrecorded books in the entire repository: legacy unaccepted literary imports may discuss overlapping titles. Three newly source-local edition candidates extend the proposal frontier across series absent from the current nine-row literary display.

| Series | Publisher Work label / creator | Publisher-listed eBook edition | Date / page count |
| --- | --- | --- | --- |
| Deep Space Nine | [*A Stitch in Time*](https://www.simonandschuster.com/books/A-Stitch-in-Time/Andrew-J-Robinson/Star-Trek-Deep-Space-Nine/9780743420587) / Andrew J. Robinson | ISBN 9780743420587 | 2000-05-01 / 432 |
| The Next Generation | [*Q-in-Law*](https://www.simonandschuster.com/books/Q-in-Law/Peter-David/Star-Trek-The-Next-Generation/9780671040994) / Peter David | ISBN 9780671040994 | 1991-10-01 / 252 |
| Voyager | [*Homecoming*](https://www.simonandschuster.com/books/Homecoming/Christie-Golden/Star-Trek-Voyager/9780743475631) / Christie Golden | ISBN 9780743475631 | 2003-05-12 / 288 |

Each official Simon & Schuster product page was independently opened through the public web reader, and its publisher-imprint/date/pages/ISBN from the **Product Details** section was checked. These are rendered-page observations, *not* exact HTTP response bytes or immutable revision captures. The three books share **one publisher lineage**. The dates and lengths are **edition/product-page fields**, not proof of original first publication, chapter completeness or format equivalence. The publisher pages also expose book-cover download links, but **no cover-use rights were established**; no cover assets or narrative text were copied.

**Important title-collision rule:** The literary eBook *Homecoming* must not be reconciled from its title alone with the similarly titled DS9 episode *The Homecoming*. Publisher series, creator, ISBN, format and source locator distinguish this metadata proposal; they do not settle eventual global Work identity.

> **Hostile challenge:** A valid ISBN and official product page prove a source-local catalog observation; they do not prove private ownership of the exact edition bytes, the rights to train/reproduce content, a completed source read, in-universe canon, an accepted Source↔Work binding or a new covered Work. Multiple formats or mirrors copied from Simon & Schuster are not independent testimony.

`records.json` pins the accepted directory SHA-256 `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`, preserves all three ISBN/product identity pairs, and records zero accepted effects. `validate.py` rejects catalog drift, wrong host/title/author/ISBN combinations, unsupported record fields, duplicate editions, false receipts/rights and nonzero admission counts. This tranche does **not** change the generated Explorer directory, accepted Source/Work registry, coverage ledger or live Pages deployment.

Run `python3 proposals/librarian/ss-three-series-ebooks-20261103/validate.py` and `cd proposals/librarian/ss-three-series-ebooks-20261103 && python3 -m unittest -v test_validate`.
