# The Q Continuum: three numbered works and one unresolved adjacent product

**Role:** LIT. **Date:** 2026-11-03 UTC. **State:** source-local publisher observations only, no admission or coverage. Accepted-base `main@f7c111f351ab2f0eb629883a045ffc697c3d3209`.

I read the official Simon & Schuster *About the Book* and product-detail sections for four ISBN-specific eBook listings. The publisher explicitly numbers **Book One**, **Book Two**, and **Book Three**. It also lists a later, unnumbered product titled *The Q Continuum*. All four share Greg Cox, Star Trek: The Next Generation and the Pocket Books/Star Trek imprint. They are still **four product listings from one publisher family**, not four independently corroborating narrative sources.

| Publisher title | Exact first-party edition | Product date, extent |
|---|---|---|
| *The Q Continuum: Book One: Q-Space* | [9780671041014](https://www.simonandschuster.com/books/The-Q-Continuum-Book-One-Q-Space/Greg-Cox/Star-Trek-The-Next-Generation/9780671041014) | 1999-07-14; eBook, 288 pages |
| *The Q Continuum: Book Two: Q-Zone* | [9780671041021](https://www.simonandschuster.com/books/The-Q-Continuum-Book-Two-Q-Zone/Greg-Cox/Star-Trek-The-Next-Generation/9780671041021) | 1999-07-14; eBook, 288 pages |
| *The Q Continuum: Book Three: Q-Strike* | [9780671041038](https://www.simonandschuster.com/books/The-Q-Continuum-Book-Three-Q-Strike/Greg-Cox/Star-Trek-The-Next-Generation/9780671041038) | 1999-07-14; eBook, 288 pages |
| *The Q Continuum* — **unnumbered, relationship held** | [9780743491822](https://www.simonandschuster.com/books/The-Q-Continuum/Greg-Cox/Star-Trek-The-Next-Generation/9780743491822) | 2003-10-07; eBook, 368 pages |

The publisher's unnumbered 368-page product does **not explicitly say** it contains the complete trilogy. Three separate 288-page products total 864 **listed pages**, but that arithmetic alone neither proves nor disproves abridgment, omnibusing, repackaging or alternate-text identity. The product descriptions overlap in Q/Picard/galactic-barrier premise; shared promotional content is not full-book equivalence. The unnumbered product therefore has `UNRESOLVED_NOT_A_VERIFIED_OMNIBUS_OR_SAME_TEXT_EDITION` and is not counted as a fourth **verified Work** or as a known three-Work container.

## Existing owner-private OPF discovery context — holds, not bindings

The accepted [Librarian sanitized OPF metadata](../../librarian/private-opf-metadata-20261103/observations.json) contains three probable *Q Continuum* title leads:

| OPF candidate | Sanitized metadata issue | Publisher comparison status |
|---|---|---|
| `opf-local:0094` | “TNG 047 - Q-Space”; no checksum-valid ISBN, no creator | Title similarity only; no edition binding |
| `opf-local:0095` | “TNG 046 - Q-Zone”; no checksum-valid ISBN, no creator | “046” conflicts with “047” ordering; unresolved |
| `opf-local:0096` | “The Q Continuum 3 - Q-Strike”; no checksum-valid ISBN; creator lists **William C. Deets & Dean Williams** | The publisher names **Greg Cox**; material creator conflict held |

The accepted OPF observation bytes are pinned SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`, and this proposal checks those three exact source-local IDs/fields. An OPF title resemblance, especially with absent ISBN and creator conflict, cannot establish a publisher-book edition identity or private file reading.

> **Hostile challenge:** The 2003 listing could be a repackaging or partial version of an earlier numbered book rather than a three-book omnibus. Only licensed source-specific content/edition custody or an explicit publisher contents claim could resolve that; neither is present.

## Evidence limits and repeatable gates

All four original 32–40-word paraphrases derive **only from the publisher's About the Book**. No ebook body, chapter, private archive member, artwork binary, or full publisher passage was copied. Raw HTML byte custody is absent. The publisher links to cover resources, but reuse/display rights are not verified and no image URL is emitted as an approved asset.

The official Director [issue #23](https://github.com/thebrazenbeard/trek-data-core/issues/23) remains open, and accepted private archive receipts are aggregate metadata, not per-book licensed Source→Work bindings. No new book close-read was started. This wave made no site/project coverage change.

`observations.json` SHA-256 `ccd22f2159985e37522471bb02bcef4d68f763e366f810be27ec30b018acc488` is pinned by `validate.py`. The validator closes all root/product/OPF fields, checks exact first-party URLs and ISBN-13 checksums, numbered sequence, page/date/format differences, unnumbered hold, original paraphrase length and anchors, and zero accepted or display effects. The 15 hostile tests include unknown private paths, book prose and artwork claims, false OPF ISBN or creator reconciliation, full-trilogy inference and `python3 -O` bypass. Current accepted proposals are scanned for exact duplicate edition ISBNs.

**Next frontier:** independent first-party review of these four publisher pages and publication-content relationship, then Librarian-owned source/edition reconciliation. No global Work conclusion or CLOSE_READ coverage is recommended from this packet.
