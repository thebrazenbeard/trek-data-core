# LIT held official publisher edition checkpoint: OPF-local 0165–0189

**Status:** HELD REVIEW PROPOSAL ONLY. Parent: accepted `main` `3028765359001b90bc3e6b5c1835ee283b326e91` (2026-11-04). This is a source-local **edition metadata and publisher promotional-paraphrase** tranche, not a novel reading or Work-level analysis. Issue #23's protected literary close-read/source-admission hold remains controlling. No new public Explorer content, canon evidence, episode relationships, coverage, artwork release, or identity decisions result from this packet.

## Actual bounded work

| Stage | Count | Evidence class / limitations |
| --- | ---: | --- |
| Source retrieval | 24/24 | Distinct full official Simon & Schuster eBook product pages successfully opened by URL. |
| Content actually read | 24/24 | Rendered product title and byline, *About the Book* marketing paragraph, eBook format and *Product Details* imprint/date/extent/ISBN13. **Not** the copyrighted eBooks. |
| Records produced | 24/24 | `records.json`: OPF-local ID and pinned digest; first-party product URL; exact displayed product metadata; short original paraphrase; uncertainty/contradiction hold. |
| Deterministically validated | 24/24 | `validate.py` and adversarial `test_validate.py`; packet is byte pinned to SHA-256 `3bb921242e992f45d9f16e8814e36c3c0db24aa3c06711e1f650659eafce1ed2`. |
| Manifest generated | 1 | This file. |
| Source-to-Work admission | **0** | Private OPF edition equivalence not authenticated. Source rights UNKNOWN. |
| Literary close reads | **0** | No private ebook prose was accessed in this batch. |

**Scope:** `opf-local:0165`–`0177` and `0179`–`0189` = 24 owner-derived source-local observations. `opf-local:0178` (*The Kobayashi Maru*) is omitted because an accepted publisher edition lead for the product ISBN `9780743419987` already exists under `lit-three-archive-discovered-publisher-editions-20261103`; this is **not** a claim that the private edition matches it. All 24 original OPF source ISBN lists are empty, so **zero** edition-level ISBN10/ISBN13 alignments are claimed. The accepted owner-source observation packet remains `proposals/librarian/private-opf-metadata-20261103/observations.json`, SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`; its 347 OPF observations derive from private owner metadata, not public copyrighted book text.

## Source-relative exceptions retained

| Source ID | Page or owner-derived discrepancy | Status |
| --- | --- | --- |
| `0169` | OPF creator **Carmen Carter**. Publisher *Dreams of the Raven* product heading says **Carter Carmen** while its author bio says **Carmen Carter**. The first-party page is internally inconsistent. | **HELD**, no normalized author identity. [Official edition page](https://www.simonandschuster.com/books/Dreams-of-the-Raven/Carter-Carmen/Star-Trek-The-Original-Series/9780743419857) |
| `0170` | *The Romulan Way* publisher presents **Rihannsu #2** and **TOS #35** simultaneously. These are **compatible nested series labels**, not contradictory catalog facts; OPF lacks creator. | **HELD** for owner private-edition authenticity only. [Official edition page](https://www.simonandschuster.com/books/The-Romulan-Way/Diane-Duane/Star-Trek-The-Original-Series/9780743419864) |
| `0173` | Owner metadata calls item `Idic Plan`; first-party title is **The IDIC Epidemic**, eBook ISBN `9780743419895`. | **HELD**, not silently equated. [Official edition page](https://www.simonandschuster.com/books/The-IDIC-Epidemic/Jean-Lorrah/Star-Trek-The-Original-Series/9780743419895) |
| `0177` | The observed first-party *Vulcan's Glory* is **2006 eBook** ISBN `9780743419956`. A **2010 Gallery Books trade paperback** uses ISBN `9781451623345`. | Separate edition candidates; no cross-edition substitution. [2006 eBook](https://www.simonandschuster.com/books/Vulcans-Glory/D-C-Fontana/Star-Trek-The-Original-Series/9780743419956) |
| `0183`–`0184` | Owner titles both embed number **53**; official *Home Is the Hunter* is TOS **#52** and *Ghost-Walker* TOS **#53**. | **HELD** ordering/label issue, no automatic correction of owner text. [Home Is the Hunter](https://www.simonandschuster.com/books/Home-Is-the-Hunter/Dana-Kramer-Rolls/Star-Trek-The-Original-Series/9780743420037) |
| `0185` | Official *A Flag Full of Stars* publisher product heading is itself visibly truncated as **“A Star Trek: The Original Series: A Flag Full of Sta”** while OPF supplies a full title. | **HELD**; retain exact observed heading with warning. [Official edition page](https://www.simonandschuster.com/books/A-Star-Trek-The-Original-Series-A-Flag-Full-of-Sta/Brad-Ferguson/Star-Trek-The-Original-Series/9780743420051) |
| `0188` | Publisher's *The Rift* promotional text says a gateway opens every **33** years, but later says it will close for another **50** years. | **Publisher-copy internal inconsistency**; do not infer fictional timeline. [Official edition page](https://www.simonandschuster.com/books/The-Rift/Peter-David/Star-Trek-The-Original-Series/9780743420082) |
| `0189` | OPF creator string lists **Peter David, Michael Jan Friedman, Robert Greenberger**. The observed publisher product byline lists **Peter David** only. | **HELD** attribution discrepancy, no contributor erasure. [Official edition page](https://www.simonandschuster.com/books/The-Disinherited/Peter-David/Star-Trek-The-Original-Series/9780743420105) |

Publisher URLs for **every** row, including `0165`–`0168`, `0171`–`0172`, `0174`–`0176`, `0179`–`0182`, `0186`–`0187`, reside directly in `records.json`. Each recorded description is a fresh one-sentence paraphrase of **publisher marketing**, not an assertion of what the novel text objectively contains or what belongs to franchise canon. A single publisher corporate evidence lineage covers these 24 pages; it is not 24 independent confirmations. Web crawled pages can change; we did not capture publisher HTML byte hashes, so this validator protects the written observation packet rather than proving a future live page has not changed.

## Validation and protected limits

```bash
python3 -m unittest discover -s proposals/research/lit/opf-tos-publisher-0165-0189-20261104 -p 'test_validate.py' -v
python3 proposals/research/lit/opf-tos-publisher-0165-0189-20261104/validate.py
python3 tools/build_private_opf_metadata_index.py --check
```

The tests mutate publisher ISBN/URL/checksum, source ID/fingerprint, incompatible 2006/2010 edition substitutions, multi-series labels, author order, title conflict, source numbering, short promotional paraphrase size, corporate source-independence, and attempted Work/coverage/release upgrades. Validation never fetches ebook prose, performs source admission, or infers global Work equivalence.

**Next frontier (no further broad metadata waves):** Resolve #23 privately replayable rights/edition custody and exact source-to-Work admission criteria. Any publisher metadata/crosswalk correction must proceed as a separately reviewable proposed decision; leave incompatible or unverified identity `UNKNOWN`.
