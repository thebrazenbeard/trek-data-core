# Sisko paperback cover — publisher-bound artwork candidate (HELD)

**Role:** LIBRARIAN · **Batch:** `ARTWORK.PRH.SISKO.PAPERBACK.20261103`
**Accepted starting point:** `main@adf2ac38a4b3be24821663a2ae88601be17c3684`
**Accepted directory SHA-256:** `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`
**Observed:** 2026-11-03. **Effects:** no Work admission, research coverage, identity reconciliation, Explorer release, or image publication.

## Narrow gap

The accepted 1,214-row discovery directory has nine source-local literary leads. Four fictional autobiographies have reviewed *Open Library* cover API previews. Its fifth, [`literature:prh-autobiography-sisko`](../../../explorer/discovery-catalog.json), identifies **the paperback ISBN 9781803366258** but has no reviewed edition-bound cover. This packet researches **that edition only**. It does not promote the nine leads into nine reconciled Works or claim to have read the book.

## Primary observations, not reused images

1. The [Penguin Random House/Titan distributor product page](https://www.penguinrandomhouse.com/books/737400/the-autobiography-of-benjamin-sisko-by-derek-tyler-attico/) identifies *The Autobiography of Benjamin Sisko*, author Derek Tyler Attico, paperback ISBN **9781803366258**. Direct HTTP returned **200**; sampled UTF-8 HTML **258,297 bytes**, SHA-256 `f294a5c715e457b5125b5f0b411b83926c3990f450340e0b463ebb54990a95ef`. This is a time-bound snapshot hash, not a guarantee the dynamic page's bytes are stable.
2. Its actual product jacket `<img id="coverFormat">` points to **`https://images3.penguinrandomhouse.com/cover/9781803366258`**. I retrieved and visually inspected the **298×450 JPEG**, **29,616 bytes**, SHA-256 `2785f8b2bc671483813d69a56325585dbd8751c81490e44dbc0e118f3e132f0e`. The image is a front jacket featuring a gold/silver insignia motif on red, a Benjamin Sisko title and Derek Tyler Attico byline—not an interior book page or episode still. The product page also specifies a distinct social-card image at `https://images4.penguinrandomhouse.com/smedia/9781803366258`; the inspected jacket hash is for the **images3/cover** path only.
3. Direct *Open Library* JSON for the **same paperback ISBN** at `https://openlibrary.org/isbn/9781803366258.json` returned **HTTP 404** on 2026-11-03. This is only an endpoint observation, **not** proof that Open Library has no Sisko Work, the book is unpublished, or the publisher has no jacket.
4. A **different hardcover ISBN, 9781803366234**, has an [Open Library edition record](https://openlibrary.org/isbn/9781803366234.json), `OL48836302M`, cover ID **14433753**. That returned HTTP 200 and 790 bytes, SHA-256 `eac553f24cc2a33e706f0e58450df5ad77e4364128bff8072f08fffc23d2f307`. It is **not** the paperback row. The hardcover cover ID is explicitly prohibited as the paperback row's Open Library API crosswalk.

The publisher product page and publisher-hosted image belong to **one distribution source family**, not two independent witnesses. The different-edition Open Library record is a *counterexample to cross-edition image assignment*, not a corroboration of paperback cover rights. Source HTML, original JPEG and Open Library response bytes were retained only in a temporary Lappy evidence directory outside GitHub; no external pixels are copied by this packet.

## Four-factor thumbnail analysis: proposal, not permission

- **Purpose:** A future tiny, attributed image in an index would identify the exact ISBN and link to the publisher; this differs from selling/promoting a jacket, but publication purpose must be assessed on actual UI/context.
- **Nature:** The creative jacket is copyright-protected expression; a nonprofit site does not negate that factor.
- **Amount:** Even a reduced image uses the complete composition; no percentage threshold guarantees fair use.
- **Market:** A miniature catalog identification may be less substitutive than a high-quality reproduction, but no rights-holder market assessment or image-reuse license was obtained.

The relevant authorities are [17 U.S.C. §107](https://copyright.gov/title17/92chap1.html), the [Copyright Office's fact-specific explanation](https://copyright.gov/fair-use/), and [*Kelly v. Arriba Soft*'s thumbnail-search context](https://www.copyright.gov/fair-use/summaries/kelly-arriba-9thcir2003.pdf). *Kelly* is an analogy, **not** blanket authority for this jacket or public redistribution. The official product page supplies an image **locator**, not a public-use license.

> **Lou-Pole / model-audit counterexample:** A naive cover importer could see Open Library ID 14433753 under the correct *title* and set it on the current `literature:prh-autobiography-sisko` row. That obeys title matching while violating the promised **edition-specific** ISBN binding. The allowed state remains `HELD` until a genuinely matched paperback rendition, a justified legal basis and independent visual review exist.

> **Another counterexample:** Treating “product page displays the cover” or “small thumbnails often qualify as fair use” as equivalent to permission bypasses this repository's `PUBLIC_DISPLAY_PERMISSION_VERIFIED` release gate. This packet does **not** make that leap.

## Validator and handoff

Run `python -m unittest discover -s proposals/librarian/prh-sisko-paperback-cover-20261103 -p test_validate.py` and `python proposals/librarian/prh-sisko-paperback-cover-20261103/validate.py`. The validator checks the exact accepted source-local paperback row, the candidate record, held flags, fixed provider/ISBN/image receipts and the disallowed hardcover crosswalk.

**Next frontier:** an independent librarian/rights reviewer can decide whether a genuinely reduced, edition-bound paperback jacket for bibliographic identification has a defensible public display basis. If authorized, the **Consolidator** (not this source worker) must implement a separate code-owned release contract and browser/rights tests. **No visual becomes live from this candidate.**
