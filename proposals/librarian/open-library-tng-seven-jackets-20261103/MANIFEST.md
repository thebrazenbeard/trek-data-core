# Seven new TNG cover-image source candidates — held Librarian tranche

**Source snapshot:** accepted `main@4b047d014c57b7fd4a56628acb6c9a631cc21c74` · **observed:** 2026-11-03 UTC · **role:** LIBRARIAN · **status:** SOURCE-ONLY / independent image and release review required.

This packet expands the *source-local visual candidate queue*, **not** the public Explorer, governed Work inventory, private-book identity ledger, or semantic coverage. No image, ebook, private archive member name/path, or copyrighted prose is committed. Seven third-party Open Library cover previews were visibly inspected by the Librarian; an independent reviewer still must examine the specific source↔image association and display gate.

## Why the apparent 600-book discrepancy exists

Accepted aggregate private-custody receipts record **347 OPF metadata entries** (75 carrying checksum-valid ISBN candidates) and a separate container with **347 LIT plus 220 TXT** entries. These are overlapping file/metadata denominators, **not 914 distinct novels or 567 established Works**. The 347 OPFs were metadata parsed, but the original LIT/TXT narrative bodies were not read or admitted in that batch. The private count cannot honestly become a public literary *Work* or close-read count by adding filenames.

Accepted Explorer source-local discovery has **1,214 metadata rows of which nine are literary**. The accepted v1.3 artwork sidecar presents only **four** ISBN-bound Open Library autobiography jackets among those nine. Thus the visible literary jacket gap is **five of nine** current displayed literature leads, while the owner-private archive and publisher edition proposal queues are much larger and not yet projected into that directory. Existing held candidates include an *Enterprise War* Open Library image independently rejected as an interior title page. All numbers are distinct evidence scopes.

## Newly observed API source tranche

To find next cover leads without relabeling private ebooks as display-ready Works, I checked **23** separately ISBN-specific public Open Library edition JSON responses. **Only the seven cover-candidate rows are source-bound here**: their publisher ISBN, title and URL are replayed against two accepted, byte-pinned Simon & Schuster metadata proposals. The **16 no-cover hold rows are Open Library observation receipts only** and lack publisher-locator fields in this packet; they are explicitly publisher-**UNBOUND**, not 16 additional proven manifestations.

- Twenty ISBN lookup inputs came from earlier TNG source-local public listings across `opf-publisher-crosscheck-next-ten` and `opf-publisher-crosscheck-third-ten`. **Seven** candidate rows, not all twenty, replay exact first-party publisher title/ISBN/URL against both accepted source files. Their references to owner-private OPFs still do not establish private edition-byte equivalence. The other **thirteen** are held Open Library ISBN/edition/hash observations without a publisher source locator or replay check in this packet.
- Three additional cross-series lookup inputs (*A Stitch in Time*, *Q-in-Law*, and *Homecoming*) were exploratory controls sourced outside those two pinned TNG input packets. Their exact Open Library ISBN editions returned metadata but **no `covers` field**. They, too, remain **publisher-UNBOUND within this packet**; their publisher source lineage must be independently supplied before promotion.

All 23 ISBN JSON lookups returned HTTP 200 for an edition JSON response on this observation. A field absent in an observed response is **not** a permanent claim that no image exists elsewhere. Raw response SHA-256 observations and edition IDs are in `records.json`. The 20 TNG observations yielded **seven nonempty `covers` associations** and **13 holds**; the three cross-series observations add three holds: **7 source-bound visual candidates + 16 source-unbound no-cover holds = 23 public ISBN API responses checked**. This is neither 23 verified publisher-to-Open-Library crosswalks nor 23 accepted literary Works.

### Seven medium JPEG candidates (all held)

| Publisher-title observation | ISBN-13 | Open Library edition | Cover ID | Result |
| --- | --- | --- | ---: | --- |
| *The Children of Hamlin* | `9780743412155` | `OL34434131M` | `13778645` | TNG jacket visually read; OL title drops “The”; publisher byline `Carter Carmen` versus OPF `Carmen Carter` remains unresolved |
| *Masks* | `9780743420877` | `OL27033844M` | `8641748` | TNG jacket visually read |
| *Fortune's Light* | `9780743420952` | `OL33980014M` | `13902771` | TNG jacket visually read |
| *Contamination* | `9780743420969` | `OL33984080M` | `13787094` | TNG jacket visually read |
| *Boogeymen* | `9780743420976` | `OL33973436M` | `13778643` | TNG jacket visually read |
| *Imbalance* | `9780743421027` | `OL7949640M` | `476408` | TNG jacket visually read; actual eBook-format artwork equivalence unproven |
| *Guises of the Mind* | `9780743421102` | `OL33985771M` | `13783845` | TNG jacket visually read |

The Open Library Covers API medium endpoint was fetched for each exact cover ID and returned HTTP 200 `image/jpeg`. Each returned JPEG's **byte length and raw SHA-256** are recorded. The visual reading checks jacket versus title page and the on-image work label; it **does not prove** the publisher used that same image for the particular eBook ISBN edition, nor does it transfer copyright. Some Open Library edition images can originate from earlier print jackets and be attached to later digital-edition records. In particular, do not silently convert an Open Library cover-field association into independently verified *edition-specific publisher artwork*.

## Rights and controlled next integration gate

[Open Library Covers API](https://openlibrary.org/dev/docs/api/covers) documents use of its cover API on public web pages with attribution guidance and size variants. [Open Library licensing](https://openlibrary.org/developers/licensing) does **not** grant a blanket right over publisher artwork; third-party rights may persist. Each image remains `API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED`. Remote preview availability, API-use documentation, publisher permission, and copyright ownership are separate claims.

> **Hostile challenge:** A cover image visibly titled *Masks* proves what that image depicts, and an ISBN edition JSON `covers` field proves its present Open Library association. Neither, by itself, proves that the pictured artwork is the official jacket for that specific eBook manifestation. Publisher re-use of older print covers and mutable crowdsourced edition metadata remain competing explanations.

> **Hostile challenge:** Reusing 347 OPF records and 567 LIT/TXT files as independent evidence would double-count source families and leak owner-private custody information. All visual proposals must be matched to accepted public source-local rows and independently reviewed before a page can display them.

Next: independent reviewer re-opens the seven exact `-M` images, compares title/visuals to public publisher product descriptions and, where possible, official cover previews; evaluates rights/attribution; then the Consolidator can propose public source-local **directory** expansion and a separate opt-in artwork release. The current nine-row directory has **no matching TNG row IDs** for these seven, so no automatic art sidecar admission can be made. The Director must reconcile Work/Source roles separately.

## Reproducibility and limits

```sh
python3 proposals/librarian/open-library-tng-seven-jackets-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/open-library-tng-seven-jackets-20261103 -p test_validate.py -v
python3 -O -m unittest discover -s proposals/librarian/open-library-tng-seven-jackets-20261103 -p test_validate.py -v
```

`validate.py` verifies immutable record-packet set SHA, code-owned seven ISBN/cover pins, upstream accepted publisher-record file hashes, **seven** first-party product title/ISBN/URL associations, and all held/release flags. It **does not verify publisher origin for the sixteen no-cover holds**; those records have no publisher locator and must remain publisher-UNBOUND. It does **not** re-fetch remote mutable Open Library JSON/JPEGs, reverify private ZIP bytes, prove licensed image rights, or read any book narrative. Direct API and visual observations are explicitly operator observations, awaiting a separate reviewer. **Source/Work admissions: 0; close reads: 0; Explorer images released: 0.**
