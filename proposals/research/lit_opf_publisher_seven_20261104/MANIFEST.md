# HELD: seven TNG publisher eBook edition metadata leads

**Status:** local proposal only. Based on accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91`; this packet is **not** an accepted Source, Work, Evidence, canonical assertion, cross-reference, coverage event, Pages asset, or public Explorer update.

## Bounded read and lineage

The [accepted-public owner OPF inventory](../../librarian/private-opf-metadata-20261103/observations.json) was read as **source-local XML metadata only**; it reports 347 OPF packages, no book-text read, and no verified private edition identity. Its exact bytes are pinned to SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. Owner-private member paths, OPF XML bodies, ebook prose, covers, and other media were not copied, quoted, or retrieved for this tranche.

Seven *different* official [Simon & Schuster](https://www.simonandschuster.com/) eBook product pages were read on 2026-11-04 for bibliographic display fields (title, listed author/creators, format, US edition date, page count, ISBN13) and their publisher descriptions. Each `held_synopsis` in `records.json` is an original one-sentence paraphrase of that publisher description; it is **not** claimed as a close-read or independently validated story summary. There are seven page locators, but just **one publisher upstream family**; they are not seven independent source families.

| OPF local ID | Publisher title | OPF-claimed ISBN10 | Publisher ISBN13 | Publisher ebook pages | Official publisher source |
| --- | --- | --- | --- | ---: | --- |
| `0055` | *Power Hungry* | `0743420861` | `9780743420860` | 272 | [Page](https://www.simonandschuster.com/books/Power-Hungry/Howard-Weinstein/Star-Trek-The-Next-Generation/9780743420860) |
| `0056` | *Masks* | `074342087X` | `9780743420877` | 288 | [Page](https://www.simonandschuster.com/books/Masks/John-Vornholt/Star-Trek-The-Next-Generation/9780743420877) |
| `0057` | *A Call to Darkness* | `0743420896` | `9780743420891` | 272 | [Page](https://www.simonandschuster.com/books/A-Call-to-Darkness/Michael-Jan-Friedman/Star-Trek-The-Next-Generation/9780743420891) |
| `0058` | *A Rock and a Hard Place* | `074342090X` | `9780743420907` | 288 | [Page](https://www.simonandschuster.com/books/A-Rock-and-a-Hard-Place/Peter-David/Star-Trek-The-Next-Generation/9780743420907) |
| `0059` | *Gulliver's Fugitives* | `0743420918` | `9780743420914` | 256 | [Page](https://www.simonandschuster.com/books/Gullivers-Fugitives/Keith-Sharee/Star-Trek-The-Next-Generation/9780743420914) |
| `0060` | *Doomsday World* | `0743420926` | `9780743420921` | 276 | [Page](https://www.simonandschuster.com/books/Doomsday-World/Peter-David/Star-Trek-The-Next-Generation/9780743420921) |
| `0061` | *The Eyes of the Beholders* | `0743420934` | `9780743420938` | 256 | [Page](https://www.simonandschuster.com/books/The-Eyes-of-the-Beholders/A-C-Crispin/Star-Trek-The-Next-Generation/9780743420938) |

All seven OPF-declared ISBN10 strings pass check-digit validation, convert to the exact publisher ISBN13 using the `978` prefix and ISBN13 checksum, and agree with the respective source-local OPF title/creator claims. This is an **edition metadata crosswalk lead**, not proof that a privately converted ebook has the publisher's exact bytes, a licensed edition, or complete text. The OPF `date` fields for some converted packages differ from the official publisher US eBook product date; those dates are deliberately **not rewritten** or presumed to designate the same event.

The official publisher's *Doomsday World* author header lists **`Carter Carmen`**, whereas the same page's author biography says **`Carmen Carter`**, aligning with the owner OPF creator field. The row preserves the exact header spelling and `CARTER_CARMEN_HEADER_VS_BIO_OPF_UNRESOLVED`. No silent identity normalization occurs.

The packet adds **7 HELD edition metadata rows** alongside an existing *separate* 10-row HELD publisher draft preview; it does **not** convert 10+7 into accepted Work, close-read, corpus, or coverage counts. None of these seven ISBN13s appears among those ten prior HELD ISBNs. No global identity or schema registry was modified.

## Validation and falsifiers

Run:

```bash
python3 proposals/research/lit_opf_publisher_seven_20261104/validate.py
python3 -m unittest tests.test_lit_opf_publisher_seven_held -v
```

The validator pins the source-public OPF JSON SHA, its exact seven local-row IDs/entry fingerprints, ISBN10→ISBN13 checksums, the first-party publisher URL/edition/title/creator/date/extent fields, anomaly attribution and zero-effect flags. It rejects row swaps, bad checksums, private-content injection, source promotion, and host/query spoofing. It does **not** retrieve official pages during CI; the publisher URLs are human review locators and would need a retrieval snapshot/check before admission.

> **Hostile challenge:** One publisher family can replicate its own catalog errors across pages. Seven matching ISBNs are not seven independent confirmations, and publisher sales copy is not a read of seven books.

> **Hostile challenge:** A converted OPF's title, creator and ISBN may be edited, stale or wrong. Alignment with a catalog identifies a bibliographic candidate, not a cryptographic relationship between the owner's OPF bytes and the publisher's described edition, nor between OPF and original LIT bytes.

> **Hostile challenge:** The publisher calls `Carter Carmen` an author in its display header while its biography and local metadata use `Carmen Carter`. Without a separate reviewed decision, automatic normalization would erase a material attribution discrepancy.

> **Hostile challenge:** The one-sentence synopsis rows paraphrase **publisher descriptions**, not actual close-read narrative events; the pages might change or contain inaccuracies. They remain proposal-local and may not be pushed to a public Explorer shelf as verified summaries.

**Next gate:** independent primary publisher page recheck and metadata snapshot, verify/correct anomalies, source-to-edition custody for private OPF/LIT representations, rights/access decision for actual close reads, and Auditor/Consolidator admission review. No merges, remote writes, deployment, ebook prose or artwork distribution authorized or performed by this packet.
