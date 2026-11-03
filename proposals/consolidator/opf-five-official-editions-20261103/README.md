# HELD — five owner-local OPF bibliographic crosswalk candidates

**Consolidator draft; no Work admission or public Explorer effect.** This bounded tranche compares five exact owner-private OPF XML source records with five directly read Simon & Schuster publisher eBook product pages. It records the publisher's **specific ebook ISBN, byline, imprint, date and page extent** as a separate, source-local *edition candidate*. All five OPF metadata observations have no recorded ISBN; title/creator overlap does **not** establish the private file's edition identity.

| OPF source-local ID | Original OPF title token | Independent publisher eBook product page | Publisher ISBN-13 / date / extent |
| --- | --- | --- | --- |
| `opf-local:0106` | *Diplomatic Implausibility* | [Simon & Schuster](https://www.simonandschuster.com/books/Diplomatic-Implausibility/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9780743419505) | `9780743419505` · 2001-07-07 · 272 pp. |
| `opf-local:0155` | *The Final Reflection* | [Simon & Schuster](https://www.simonandschuster.com/books/The-Final-Reflection/John-M-Ford/Star-Trek-The-Original-Series/9780743419673) | `9780743419673` · 2000-09-22 · 256 pp. |
| `opf-local:0231` | *Prime Directive* | [Simon & Schuster](https://www.simonandschuster.com/books/Prime-Directive/Judith-Reeves-Stevens/Star-Trek-The-Original-Series/9780743454186) | `9780743454186` · 2002-10-02 · 406 pp. |
| `opf-local:0236` | *Spock's World* | [Simon & Schuster](https://www.simonandschuster.com/books/Spocks-World/Diane-Duane/Star-Trek-The-Original-Series/9780671041137) | `9780671041137` · 2001-06-07 · 400 pp. |
| `opf-local:0301` | *The 34th Rule* | [Simon & Schuster](https://www.simonandschuster.com/books/The-34th-Rule/Armin-Shimerman/Star-Trek-Deep-Space-Nine/9780743420549) | `9780743420549` · 2000-09-22 · 448 pp. |

Dates in the table are **the publisher's product listing dates**, not proven original novel publication dates or owner-file edition dates. The source pages were read through their public rendered text on 2026-11-03; their raw HTML response bodies were not archived and have no claimed SHA-256 receipt.

## Independent original OPF source custody

The Librarian independently re-read the owner-held converted OPF ZIP **read-only** and rehashed the whole container (`0b2b27b3a8a37e8bae667ef2cdeaed31580c3782452aead1d561047e8b61975f`) and the five original uncompressed XML members against the accepted 347-row metadata packet. Each digest matched. Uncompressed OPF XML sizes were **1,096; 2,802; 3,178; 951; and 1,009 bytes**, respectively, in the table's order. Neither copyrighted ebook prose nor artwork was read or copied. The public crosswalk deliberately omits private paths.

The accepted 347-row observation packet has SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. The corresponding 39-row HELD review sample is already accepted on `main` and its source-local IDs are verified by the compiler. The historic 1,214-row discovery catalog SHA remains `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`.

## Unresolved identity and lineage differences

- `0106`: local OPF writes *Next Generations*, while official publisher title-series label is *The Next Generation*. This is a title-string discrepancy, not a corrected local source.
- `0155`: local OPF includes *World's Apart, Book One* while the publisher product page identifies *The Final Reflection* as TOS #16. Another **already accepted source-local Simon & Schuster edition candidate** is `TOS-FINAL-REFLECTION-EBOOK-9780743419673` in `proposals/librarian/tos-classics-cover-editions-20261103/records.json`; both observations depend on the same publisher lineage, **not two independent attestations**. Omnibus/containment scope is unresolved.
- `0231`: local OPF credits Judith **and Garfield** Reeves-Stevens; this particular official product-page byline displays Judith Reeves-Stevens alone, although its biographical description discusses both. Both strings remain preserved, no author identity edit.
- `0301`: OPF has a comma-separated combined creator string while publisher shows two bylines; the source-relative DS9 #23 matches the publisher's numbering but does not prove local edition authenticity.
- All five: the archive OPF lacks an ISBN, publication date and publisher field. Publisher ISBN-13s identify **external publisher eBook candidates**, not the owner's converted LIT/OPF manifestation. A valid source SHA does not prove identity with the publisher's listing.

> **Hostile falsifier:** If an owner-held OPF conversion originated from a different edition—or copied the correct title and creator from a different release—this exact source and publisher metadata agreement would still occur. Edition-equivalence and Source→Work relations therefore stay **NOT_VERIFIED** and **NOT_RECONCILED**.

Five public publisher pages are **one corporate source family**. The accepted earlier *Final Reflection* product record is part of the same lineage. The crosswalk adds no independent corroboration count, synopsis, artwork license, published Explorer entries, admitted Works, or book close-read coverage. The publisher hosts promotional cover-download links, but their presence is **not** image-display authorization.

## Reproduce

```bash
python3 tools/build_opf_five_publisher_crosschecks.py --check
python3 -m unittest tests.test_opf_five_publisher_crosschecks -v
```

The compiler reads the pinned owner-local OPF metadata derivative, the accepted 39-row review sample, the earlier same-publisher *Final Reflection* edition observation, and the unchanged historical directory. It deterministically emits `crosschecks.json`, validates each source-to-product locator and ISBN, and fails closed on protected-effect, publisher-metadata, source-ID, or lineage drift. A green test proves internal custody and shape, **not live independent publisher response immutability**.
