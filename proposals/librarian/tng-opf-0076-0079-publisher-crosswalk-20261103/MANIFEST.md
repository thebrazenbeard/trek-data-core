# TNG #28–31: publisher/OPF bibliographic-identifier crosswalk

**Batch:** `LIBRARIAN.TNG.OPF.0076-0079.PUBLISHER.20261103`
**Accepted-main snapshot:** `c7a201df1a50aadcd062063aa48476f8eb6f4222`
**Observed:** 2026-11-03 UTC
**State:** four **actually read first-party Simon & Schuster rendered eBook product-detail pages** and four existing accepted **sanitized private OPF metadata** observations. Metadata candidate only. Zero Source or Work admission, edition custody, literary coverage, text or cover publication, or deployment effects.

## Four publisher Product Details reads

All four displayed eBooks list the same corporate publisher family, Pocket Books/Star Trek, and the **publisher product date September 22, 2000**. This is a single upstream publishing lineage, not four independent content witnesses. Exact edition ISBN and format are product metadata, not a receipt for private ebook bytes.

| Publisher book and series number | Source Product Details | Publisher ISBN-13, pages | Existing OPF ID / checksum-valid ISBN-10 | OPF raw date |
|---|---|---|---|---|
| *Here There Be Dragons*, TNG #28 | [S&S first-party product](https://www.simonandschuster.com/books/Here-There-Be-Dragons/John-Peel/Star-Trek-The-Next-Generation/9780743421119), around line 254 | `9780743421119`, 288 | `opf-local:0076` / `0743421116` | `2000-08-05` |
| *Star Trek: The Next Generation: Sins of Commission*, #29 | [S&S first-party product](https://www.simonandschuster.com/books/Star-Trek-The-Next-Generation-Sins-of-Commission/Susan-Wright/Star-Trek-The-Next-Generation/9780743421126), around line 257 | `9780743421126`, 288 | `opf-local:0077` / `0743421124` | `2000-07-31` |
| *Star Trek: The Next Generation: Debtor's Planet*, #30 | [S&S first-party product](https://www.simonandschuster.com/books/Star-Trek-The-Next-Generation-Debtors-Planet/W-R-Thompson/Star-Trek-The-Next-Generation/9780743421133), around line 252 | `9780743421133`, 272 | `opf-local:0078` / `0743421132` | `2000-07-30` |
| *Foreign Foes*, TNG #31 | [S&S first-party product](https://www.simonandschuster.com/books/Foreign-Foes/Dave-Galanter/Star-Trek-The-Next-Generation/9780743421140), around line 262 | `9780743421140`, 320 | `opf-local:0079` / `0743421140` | `07/29/00` (raw syntax retained) |

The OPF observation baseline is `proposals/librarian/private-opf-metadata-20261103/observations.json`, SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. The four accepted OPF entry fingerprints are pinned in `records.json` and verified against the source baseline. Each ISBN-10 passes its checksum and converts mathematically to the exact first-party publisher ISBN-13, confirming **bibliographic identifier equivalence** without proving the privately held member has the corresponding complete text, ebook rendition, or license.

### Held discrepancies and non-equivalences

- All four OPF dates differ from the publisher product's September 22 date. We preserve the original OPF strings—including `07/29/00`—without inventing a date normalization or publication chronology. `date_relation=CONFLICT_UNRESOLVED` is intentionally not a Work/date reconciliation decision.
- The publisher expands *Sins of Commission* and *Debtor's Planet* with a franchise prefix absent from the capitalized OPF title fields. Their ISBN identifier matches are recorded independently of this display-title variation; no global Work identity resolution is performed.
- *Foreign Foes* displays two publisher authors, Dave Galanter and Greg Brodeur. Its OPF creator field is one literal combined string. This packet preserves both display forms and does not infer separate OPF contributor-role metadata.
- A first-party publisher page exposes promotional prose and links to marketing images, but **neither the text nor image bytes were imported**. The original book source remains unread for this batch; the page is not a standing license to redistribute its content.

### No overlap or denominator inflation

The current open [third OPF publisher draft #341](https://github.com/thebrazenbeard/trek-data-core/pull/341) covers `0062,0063,0064,0065,0067,0068,0069,0070,0074,0075`. This proposal covers **only `0076–0079`**, exactly four different private OPF source-local rows and four different first-party product URLs. Repeated use of Simon & Schuster is **one corporate source family** and not independent corroboration. The older local draft for `0062–0065` is redundant with #341 and should not be published separately absent deduplication.

The accepted `explorer/discovery-catalog.json` SHA-256 `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc` contains **1,214** discovery rows, **nine** with the actual `LITERATURE` medium, and zero exact publisher title hits for these four products. This is a bounded directory-index gap, not four admitted literary Works or four full-text reads.

## Validation and hostile test conditions

From repository root:

```bash
python3 proposals/librarian/tng-opf-0076-0079-publisher-crosswalk-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/tng-opf-0076-0079-publisher-crosswalk-20261103 -p 'test_validate.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -q
python3 tools/validate.py
```

The validator pins accepted main, source-path/hash snapshots, the exact four observed rows with **code-owned whole-record SHA-256 digests**, checks OPF source IDs/fingerprints/field values, ISBN-10 checksums and ISBN-13 conversions, publisher URL origin, product date/format/imprint and directory denominator. A closed schema and duplicate-key JSON parser reject smuggled rights or admission claims. Hostile regressions swap same-publisher pages, ISBNs and OPF bindings; forge rights/custody, series numbers and title/date metadata; alter the OPF source; and run under optimized Python `-O`.

> **Independent review target:** source-worker page observations lack committed remote HTML snapshots; pinning a source-reported tuple makes it tamper-evident within the repo but does not cryptographically prove what Simon & Schuster served. Reviewer should independently reopen the four product detail pages, verify edition and date values, and keep four date disagreements unresolved. ISBN identity is not private member content custody.

**Next frontier:** independent exact-page source audit, then candidate-only proposal integration. Do not promote public covers, book text, exact private edition identity, source admission or literary analysis coverage without separate evidence and authorization.
