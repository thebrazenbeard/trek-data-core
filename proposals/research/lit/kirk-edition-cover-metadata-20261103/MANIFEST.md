# LIT format / jacket-link identity gap: *The Autobiography of James T. Kirk*

**2026-11-03 UTC · LIT · source-local metadata-only proposal**

Accepted starting head: `f387126c60942ff90952cd6e9251a67c8f5c26fa` (following merged #254). Live Director [#23](https://github.com/thebrazenbeard/trek-data-core/issues/23) still **holds new literary close reading**; this batch read no private ebook, prose, OPF content, sample or cover binary. Neither possession nor a publisher product listing establishes an authenticated source text or rights to reuse the book jacket. `records.json` is not a registry, accepted Work, or Explorer artwork sidecar.

## Specific gap resolved as a proposal

The accepted Explorer discovery row `literature:prh-autobiography-kirk` refers to the **2016 paperback** ISBN `9781783297481`. The distributor's public product page also displays **hardcover** and **ebook** variants. They cannot silently inherit the paperback's ISBN, citation or image identity.

| Format | ISBN-13 | US publication metadata | Exact public distributor jacket-image link (locator only) |
| --- | --- | --- | --- |
| Paperback | `9781783297481` | 2016-07-05 | `https://images1.penguinrandomhouse.com/cover/9781783297481` |
| Hardcover | `9781783297467` | 2015-09-08 | `https://images4.penguinrandomhouse.com/cover/9781783297467` |
| eBook | `9781783297474` | 2015-09-08 | `https://images1.penguinrandomhouse.com/cover/9781783297474` |

The three image addresses were followed from the three format images on [Penguin Random House's product page](https://www.penguinrandomhouse.com/books/250795/the-autobiography-of-james-t-kirk-by-david-a-goodman/) on this research pass. The **hardback's ISBN and date** are separately explicit on the [Titan Books publisher page](https://titanbooks.com/8302-the-autobiography-of-james-t-kirk/). The **eBook ISBN and release date** are explicit on [OverDrive's licensed-library listing](https://library2go.overdrive.com/library2go-111-134/content/media/2148177). These upstream records may propagate the same Titan metadata and are not three independent witnesses to narrative content. No source HTML bytes or jacket binaries were archived, so no such digest is asserted.

The [Open Library edition page OL28813033M](https://openlibrary.org/books/OL28813033M/Autobiography_of_James_T._Kirk) independently lists ISBN `9781783297481` (paperback identity crosscheck). Its direct `.json` edition endpoint was inaccessible in this pass; therefore **no Open Library cover ID or exact edition-JSON digest** is claimed. A generic cover image on a catalog page is not enough to produce the audited Open Library sidecar proof required by [the Explorer policy](../../../../docs/ARTWORK_THUMBNAIL_POLICY.md).

## Source-relative contradiction, not fictional history

The [Titan hardback product description](https://titanbooks.com/8302-the-autobiography-of-james-t-kirk/) gives a promotional life-date range of `2233–2293`, while the [Penguin Random House distributor description](https://www.penguinrandomhouse.com/books/250795/the-autobiography-of-james-t-kirk-by-david-a-goodman/) gives `2233–2371`. Both values remain distinct **marketing-source utterances**. They neither establish a storyline event nor prove that the two physical/digital editions contain different prose. The unreviewed edition and franchise-continuity interpretation is `UNRESOLVED`.

## Rights and effect boundary

- [Penguin Random House's terms](https://www.penguinrandomhouse.com/terms/) describe site images as copyrighted and restrict republication/reuse without permission. The product page's image-link availability is **not** public-display or hotlink authority. No binary, base64, image asset, Explorer sidecar or remote display toggle was added.
- No canonical Source/Work IDs, identity reconciliation, governed evidence, coverage, rights-admission, or content-read claims were created. All effect fields are `NONE`.
- No user private filename, local path, book source, purchase account, edition possession, OPF inventory member or ZIP data was read or disclosed. A separate accepted Librarian aggregate inventory identified 347 private OPF package observations and 15 metadata review holds, but those private records are not tied to this ISBN by this proposal.

## Deterministic replay

```bash
python3 proposals/research/lit/kirk-edition-cover-metadata-20261103/validate.py
python3 -O proposals/research/lit/kirk-edition-cover-metadata-20261103/validate.py
python3 -m unittest tests.test_lit_kirk_edition_cover_gap -v
```

The validator pins each format-to-ISBN-to-image locator, rejects attempts to promote image rights, content reads or coverage, checks the accepted discovery-row association, and preserves the unresolved marketing discrepancy. All public record levels have exact allowed-field sets; injected private paths, arbitrary publisher/provider labels, image fields, rights claims and substituted unresolved holds are rejected even under `python3 -O`. It validates **this public proposal**; it cannot prove publisher web-page permanence, image authorship, edition content equality, rights or physical custody.

**Exact next frontier:** a Librarian can independently fetch content-addressed edition JSON for this ISBN (if available), then perform format-specific rights review and distinguish the separate hardback/ebook record keys. A LIT worker must wait for accepted Source↔Work bindings and release of #23 before further close-reading.
