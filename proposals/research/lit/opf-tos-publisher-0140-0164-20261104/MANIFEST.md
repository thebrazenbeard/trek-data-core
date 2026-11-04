# LIT held publisher media ingestion: 23 TOS / film-novelization OPF-local editions

**2026-11-04 · Source-relative research proposal, not accepted literary coverage.** Started from accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91`. Source packet is the accepted, digest-pinned owner-private-derived **347 OPF metadata observations** (`5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`), not the owner's private ebook or converted OPF XML bodies.

## Actual ingestion checkpoint

| Required batch step | Actual result | Evidence class |
|---|---:|---|
| Candidate scope chosen | 23 OPF-local records: `0140`–`0164`, excluding already-studied `0150` and `0155` | Accepted source-ID inspection and live open-PR overlap check |
| **SOURCE_RETRIEVED** | **23/23** official Simon & Schuster book-product pages opened | Live web full-page retrieval; exact per-row URLs in `records.json` |
| **CONTENT_READ** | **23/23** visible headings/bylines/formats, `About the Book`, and `Product Details` sections actually read | Publisher webpage rendered text, not ebook narrative |
| **RECORDS_GENERATED** | **23/23** original short publisher-description paraphrases plus source-local edition metadata, ISBN, locator and uncertainty | `records.json` SHA-256 `5e20783761b1651713d69e08eaa8395115bc0ec4561f44b3203ce1654a622410` |
| **VALIDATION_PASSED** | **23/23** rows plus fifteen local tests (including mutations) and ISBN/lineage/privacy gates | `validate.py`, `test_validate.py` |
| **BATCH_MANIFEST_GENERATED** | This complete bounded manifest | No open/private copyrighted source content |

`SOURCE_RETRIEVED` and `CONTENT_READ` mean **publisher product page metadata and promotional book descriptions**, not full novel text or film scripts. The web tool returned renderer-accessible pages that sometimes had older crawl-cache labels (ranging from recent to several months old); raw publisher HTML response bytes were **not** captured or hashed. Each product URL and its visible `Product Details` are therefore a reproducible **locator and attributed observation**, not an immutable publisher snapshot or an authenticated private edition. The full retrieved page was examined around product heading, publisher description and details; no snippets substituted for unvisited pages.

## Edition and lineage findings

All 23 direct official book pages list **eBook** products under **Pocket Books/Star Trek**. They belong to **one Simon & Schuster corporate source lineage**, not 23 independent publishers. All 23 recorded ISBN13 values satisfy check digits and correspond to exact ISBN-ending publisher product URLs. Five accepted OPF source-local ISBN10 values, `0140`–`0144`, mathematically convert to the corresponding publisher ISBN13, but this is **bibliographic agreement only**, not the claim that the owner-private file contains identical text or even that the local source correctly describes its contents. The other 18 OPF rows lack a checksum-valid source ISBN; a matching title is not enough to bind a manifestation.

| OPF ID | First-party product ISBN13 | Original short paraphrase and explicit disposition |
|---|---|---|
| `0140` | `9780743412087` | *Star Trek: The Motion Picture* publisher product has title **Star Trek** with subtitle **The Motion Picture**; source displays **THE MOTION PICTURE™**. Keep display difference, do not flatten or bind private edition. |
| `0141`–`0144` | `9780743412094`, `9780743412100`, `9780743412117`, `9780743412124` | Four additional checksum-aligned OPF/publisher ISBN candidates; *Prometheus Design* has reversed source-OPF versus publisher two-author order. Preserve both source claims. |
| `0145`–`0149` | Exact ISBNs in `records.json` | Product titles include *The Abode of Life*, *The Wrath of Khan* film novelization, *Black Fire*, *Triangle*, and *Web of the Romulans*. OPF `0145` lacks creator; `0148` combines authors in reverse order. No owner-private text read. |
| `0151`–`0154` | Exact ISBNs in `records.json` | *Mutiny*, *Wounded Sky*, *Trellisane*, *Corona*. Source `0152` lacks creator; source `0153` uses uppercase creator typography. Publisher bylines stay independently attributed. |
| `0156`–`0162` | Exact ISBNs in `records.json` | Official *Search for Spock* product is labeled a film novelization; series and adaptation do not prove script equivalence. Source `0159` and `0160` lack creator. The official *My Enemy, My Ally* eBook page simultaneously presents **Rihannsu #1** and **Book #18 of The Original Series**; they are compatible subseries/parent-series labels, **not a conflict**. Private edition equivalence remains unverified. |
| `0163` | `9780743419789` | **CRITICAL creator conflict:** owner OPF metadata says **Kevin Underwood**, while the actual publisher *Mindshadow* ebook credits **J.M. Dillard**. Do not repair either source by assumption or silently map the private item to this publisher edition. |
| `0164` | `9780743419802` | *Dreadnought!* publisher ebook attributed to Diane Carey; owner-private edition equality unverified. |

The original per-row author/title labels remain in the accepted 347-row source metadata. This proposal records publisher bylines and packaging without changing those literals. The `publisher_blurb_paraphrase` fields are original short summaries of **what the publisher claims on its product page**, not source-grounded novel events, independently verified canon, episode contents or film-script text.

> **Hostile challenge — provenance contamination:** If a projection treats an OPF filename/title hint plus a publisher's marketing synopsis as two independent confirmations of the same novel's plot, it has fabricated independent evidence. The OPF is owner-private conversion metadata with unresolved edition identity; the synopsis is a corporate publisher claim about a specific ISBN manifestation. Neither is a full-source close read.

> **Hostile challenge — identity:** OPF `0163` creator **Kevin Underwood** directly conflicts with the publisher's **J.M. Dillard** credit for *Mindshadow*. Matching title/sequence/series would mask a source-versus-publisher discordance. Record `CREATOR_CONFLICT` and preserve both. At `0157`, **Rihannsu #1** and **TOS #18** are compatible series labels simultaneously shown on the official product page, **not an identity dispute**; private edition equality is still unverified.

## Non-overlap and remaining gates

- Open literary proposal chain reviewed: [#512](https://github.com/thebrazenbeard/trek-data-core/pull/512) `0055`–`0079`, [#524](https://github.com/thebrazenbeard/trek-data-core/pull/524) `0080`–`0086`, [#526](https://github.com/thebrazenbeard/trek-data-core/pull/526) `0087`–`0093`, [#533](https://github.com/thebrazenbeard/trek-data-core/pull/533) `0094`–`0100`, [#542](https://github.com/thebrazenbeard/trek-data-core/pull/542) `0101`–`0107`, and [#549](https://github.com/thebrazenbeard/trek-data-core/pull/549) `0108`–`0114`. These remain proposals. Existing accepted seven/five OPF publisher crosschecks include `0150` and `0155` respectively; both excluded.
- The owner-private LIT/OPF source receipts remain a shared possible conversion lineage. No extra distinct Work denominator can be inferred from `23` pages, `347` OPFs, `347` originals, or any combination.
- This batch does **not** read `.lit`, `.txt`, converted `.opf` XML/HTML spine, book chapters, screenplay, audiobook, artwork or cover bytes. Rights stay `UNKNOWN`; exact source-text/edition equivalence `NOT_VERIFIED`; global identity `NOT_RECONCILED`.
- No accepted Source→Work bindings, book coverage, close reads, canonical events, cross-work hypotheses, public Explorer release, Supabase mutation, merge, deployment or license assertion. Issue [#23](https://github.com/thebrazenbeard/trek-data-core/issues/23) remains the literary admission gate.

## Validation

```sh
python3 proposals/research/lit/opf-tos-publisher-0140-0164-20261104/validate.py
python3 -m unittest discover -s proposals/research/lit/opf-tos-publisher-0140-0164-20261104 -p 'test_validate.py' -v
python3 -O -m unittest discover -s proposals/research/lit/opf-tos-publisher-0140-0164-20261104 -p 'test_validate.py' -v
python3 tools/build_private_opf_metadata_index.py --check
```

Validator pins accepted-source and packet hashes, exactly 23 non-overlapping source-local IDs and OPF entry digests, official URL/ISBN/format/imprint checks, five exact ISBN10-to-13 alignments, source-absent creators, reversed-author flags, *Mindshadow* creator contradiction, compatible Rihannsu #1 / TOS #18 multiseries presentation and all protected admission/release counters. Independent hostile review identified Python's `bool` subclassing `int` loophole; the **15 tests** now reject boolean masquerading as publisher page extent, require exact JSON type for every protected envelope field, and prevent stale wording from reclassifying compatible series labels as a conflict. It never fetches a new publisher page; its PASS confirms the held **report's deterministic integrity**, not mutable publisher text or owner-source authenticity.

**Next frontier:** independent, blinded adversarial review of the 23 web product receipts—especially *Mindshadow*—and source/rights/edition governance under #23. Only afterward should a Librarian propose edition custody records and a Consolidator consider public projections.
