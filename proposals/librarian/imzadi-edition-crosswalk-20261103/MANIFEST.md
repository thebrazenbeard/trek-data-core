# Imzadi publisher product-edition crosswalk — Librarian proposal

**Batch:** `LIBRARIAN.IMZADI.EDITION.CROSSWALK.20261103`
**Authoritative accepted-main baseline:** `51b7c99a15d8295ba9d87f2088d36866140c1a79`
**Observation date:** 2026-11-03 (UTC)
**State:** four **first-party rendered publisher product-detail page reads**, candidate **edition metadata only**. No Source admission, Work reconciliation, full-source ingestion, image retrieval/display, literary coverage increment, or deployment.

## Original page observations

These metadata values were actually read from Simon & Schuster's current public *Product Details* sections. Source pages are one publisher lineage, **not four independent corroborating publishers**. Page line references are rendered-read locators, not cryptographic copies of the live HTML.

| Publisher product / family | Product format, ISBN-13 | Product date and extent | Exact first-party evidence |
|---|---|---|---|
| *Imzadi Forever* | Trade Paperback · `9780743485104` | Pocket Books/Star Trek · 2003-12-02 · 432 pages | [S&S paperback product](https://www.simonandschuster.com/books/Imzadi-Forever/Peter-David/Star-Trek-The-Next-Generation/9780743485104), *Product Details* around line 381 |
| *Star Trek: Signature Edition: Imzadi Forever* | eBook · `9780743492645` | Pocket Books/Star Trek · 2003-12-02 · 432 pages | [S&S Signature eBook product](https://www.simonandschuster.com/books/Star-Trek-Signature-Edition-Imzadi-Forever/Peter-David/Star-Trek-The-Next-Generation/9780743492645), *Product Details* around line 264 |
| *Star Trek: The Next Generation: Triangle: Imzadi II* | eBook · `9780743420716` | Pocket Books/Star Trek · 2000-09-22 · 384 pages | [S&S Triangle eBook product](https://www.simonandschuster.com/books/Star-Trek-The-Next-Generation-Triangle-Imzadi-II/Peter-David/Star-Trek-The-Next-Generation/9780743420716), *Product Details* around line 384 |
| *Star Trek: The Next Generation: Triangle: Imzadi II* | Abridged Audio Download · `9780743566827` | Simon & Schuster Audio · 1998-10-01 · 3 hours · reader Robert O'Reilly | [S&S Triangle audio product](https://www.simonandschuster.com/books/Star-Trek-The-Next-Generation-Triangle-Imzadi-II/Peter-David/Star-Trek-The-Next-Generation/9780743566827), *Product Details* around line 292 |

All four list author Peter David. Product format and ISBN distinguish publisher *edition products*. The publisher page for one format offers the other as a format choice. The **2003 Signature Edition eBook has a different displayed product title from its paperback counterpart**. The 1998 audio is explicitly **abridged** and must never be silently treated as the 2000 eBook's complete text or the same edition. The product names suggest related `Imzadi` titles, but the evidence here is insufficient to certify the contents of *Imzadi Forever* as an omnibus or establish canonical component Work IDs. Those relations deliberately remain `CONTAINMENT_UNVERIFIED`/`NOT_ASSERTED`.

## Existing repo crosswalk and denominator

- Accepted Explorer discovery-catalog SHA-256 `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`: **1,214** source-local discovery rows, **nine** `LITERATURE` rows; **zero** exact displayed-product-title matches to the four rows above. This is **a directory title gap**, not four missing admitted literary Works.
- Existing accepted **private** OPF metadata source `proposals/librarian/private-opf-metadata-20261103/observations.json` includes `opf-local:0128` title *Imzadi Forever*, creator Peter David, publisher Pocket Books, year 2003, entry fingerprint `f36bfb5d8c37a5045d24298385c629d08cb064d8e6228acd7bd96dc6eb074232`. That OPF observation has **no ISBN-13**, so it supplies a **title/creator/publisher/year discovery lead only**. It cannot bind the private member to paperback `9780743485104` or eBook `9780743492645`, establish legal source custody, or assert text coverage. No private member path, private bibliographic identifier, or private bytes are published by this packet.
- All metadata here is from the same Simon & Schuster catalog lineage; any inherited intermediary product list repeating ISBNs is not an independent witness. Date/extent are **publisher product metadata**, not proven characteristics of the private OPF member.

## Reproducible checks and falsifiers

From repository root:

```bash
python3 proposals/librarian/imzadi-edition-crosswalk-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/imzadi-edition-crosswalk-20261103 -p 'test_validate.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

The deterministic validator pins the reviewed accepted-main SHA, four exact publisher URLs, product titles, ISBN13 checksums, formats, publisher imprints/dates/extents/readers, title-family labels, no-rights/no-custody status, original source line anchors, a fixed catalog denominator SHA, and existing OPF source digest + *title-only* entry fingerprint. It uses a closed schema and confirms the baseline `LITERATURE` medium, not a guessed category. Adversarial tests cover ISBN swaps, eBook↔abridged-audio format substitution, same-publisher URL crossover, false private OPF ISBN binding, fabricated containment, rights/source/coverage escalation, forged catalog digest, private OPF bytes modified to invent an ISBN, and disabled Python assertions (`-O`).

The independent hostile review found that permissive JSON parsing could silently discard a duplicate `rights_status` value containing an unauthorized release assertion while the later field retained the original rights hold. The corrective parser rejects repeated keys at **all object depths**, for the packet and both baseline source JSON files, before applying semantic validation. The exact smuggling mutation is now a normal and optimized-Python regression. This does not increase copyright or image permissions.

> **Hostile limitation:** a page read provides first-party publisher metadata, not access to the complete original book, a rights grant to republish books or covers, proof that two products are textually identical, or independently verifiable preservation of live publisher HTML. The discrepancy between Signature/regular titles and differing audio/eBook release years warrants source-relative edition separation until full source custody and neutral close-read are lawfully established.

**Next frontier:** independently confirm exact physical/eBook/abridged contents and the private OPF member's own edition identity, *without* inferring an ISBN from its title. Any future publisher product rows should be accepted as source-local metadata only after separate review and integration by the Consolidator.
