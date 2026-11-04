# HELD: seven additional TNG publisher edition metadata leads (OPF 0080–0086)

**State:** local, proposal-only, unadmitted. Accepted GitHub `main@3028765359001b90bc3e6b5c1835ee283b326e91` remains the authoritative project. GitHub PR #512 is open and **draft**, containing 25 earlier HELD edition proposals (OPF 0055–0079); it is **not** accepted main. This packet is the next nonoverlapping seven-row tranche, not a revision of those 25.

## Source provenance and rights boundary

The source-local owner OPF inventory `proposals/librarian/private-opf-metadata-20261103/observations.json` has public metadata-file SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. Every record contains the exact *OPF entry* SHA-256 from that accepted-public receipt, plus its original literal title and ISBN10 claim where available. This is metadata that was already extracted from private converted OPFs; the original ebooks/LIT bytes, private archive paths, prose, images, and full XML were not obtained or copied in this wave.

Seven corresponding **official Simon & Schuster** eBook product pages were opened and read on 2026-11-04, each for displayed title, creator credits, eBook format, publisher date, extent, ISBN13 and a brief product description. All belong to the *same upstream publisher family*. Their URLs are human-recheck locators, not proof of cryptographic HTTP snapshots: the page HTML itself was not locally captured or hashed, and publisher data can change. Original one-sentence `held_synopsis` entries paraphrase only publisher descriptions, **never a full-book close read**.

| OPF ID | Publisher title | OPF ISBN10 | Official ISBN13 | Local alignment / hold | Official page |
| --- | --- | --- | --- | --- | --- |
| `0080` | *Requiem* | `0743421159` | `9780743421157` | Checksum only; creator spelling anomaly | [S&S](https://www.simonandschuster.com/books/Requiem/Michael-Jan-Friedman/Star-Trek-The-Next-Generation/9780743421157) |
| `0081` | *Balance of Power* | **Missing** | `9780743421225` | **Title only; no local creator/ISBN** | [S&S](https://www.simonandschuster.com/books/Balance-of-Power/Dafydd-ab-Hugh/Star-Trek-The-Next-Generation/9780743421225) |
| `0082` | *Blaze of Glory* | `074342123X` | `9780743421232` | Checksum only | [S&S](https://www.simonandschuster.com/books/Blaze-of-Glory/Simon-Hawke/Star-Trek-The-Next-Generation/9780743421232) |
| `0083` | *The Romulan Stratagem* | **Missing** | `9780743421300` | **Title + creator only; no local ISBN** | [S&S](https://www.simonandschuster.com/books/The-Romulan-Stratagem/Robert-Greenberger/Star-Trek-The-Next-Generation/9780743421300) |
| `0084` | *Into the Nebula* | `074342137X` | `9780743421379` | Checksum only | [S&S](https://www.simonandschuster.com/books/Into-the-Nebula/Gene-DeWeese/Star-Trek-The-Next-Generation/9780743421379) |
| `0085` | *The Last Stand* | `0743421396` | `9780743421393` | Checksum only | [S&S](https://www.simonandschuster.com/books/The-Last-Stand/Brad-Ferguson/Star-Trek-The-Next-Generation/9780743421393) |
| `0086` | *Dragon's Honor* | `0743421418` | `9780743421416` | Checksum only; title spelling anomaly | [S&S](https://www.simonandschuster.com/books/Dragons-Honor/Kij-Johnson/Star-Trek-The-Next-Generation/9780743421416) |

This produces **7 HELD publisher edition metadata rows**, exactly **5 owner OPF ISBN10 to official publisher ISBN13 checksum-aligned leads**, and **2 title-only or title/creator-only unresolved local candidates**. No source text, exact private manifestation identity, edition equivalence, Work membership, or coverage was established. It does not change the count of admitted literary Works.

## Literal source disagreements

- `0080` OPF creator field says `MICHEAL JAN FRIEDMAN AND KEVIN RYAN`; publisher creator display is **Michael Jan Friedman and Kevin Ryan**. Typed anomaly `OPF_MICHEAL_VS_PUBLISHER_MICHAEL_CREATOR_UNRESOLVED`. There is one evident transcription issue, but no silent reconciliation is recorded.
- `0081` OPF title is `Star Trek - TNG 033 - Balance Of Power`, with no creator or ISBN. The publisher-page attribution to Dafydd ab Hugh and ISBN13 are independent publisher facts, **not validated fields of the private package**.
- `0083` OPF supplies a title and Robert Greenberger as creator, but no ISBN. Its official publisher ISBN is not an OPF conversion match.
- `0086` OPF writes `DRAGONS'S HONOR`; the publisher displays *Dragon's Honor*. Typed anomaly `OPF_DRAGONS_S_VS_PUBLISHER_DRAGONS_TITLE_UNRESOLVED`; both source strings remain preserved.

## Validation and hostile review

```bash
python3 proposals/research/lit_opf_publisher_80_86_20261104/validate.py
python3 -m unittest tests.test_lit_opf_publisher_80_86_held -v
```

The validator pins public OPF source SHA and per-entry hashes, exact row order/IDs, publisher edition ISBN/author/title/date/extent and URL, the two title-only holds, specific anomalies, checksum conversion, strict zero-effects, and no private text/image output. Adversarial tests reject dropped/swapped rows, forged source ISBNs, counterfeit publisher hosts, reattributed authors, anomaly erasure, source promotion, and copyright/rights overclaims. Tests do not independently fetch publisher pages or hash private ebook contents.

> **Hostile challenge:** Publisher catalogs can contain transcription errors and can update or withdraw pages. These seven source URLs are primary bibliographic observations but do not constitute immutable snapshots or independent corroboration from seven providers.

> **Hostile challenge:** A valid ISBN10→13 mathematical conversion does not prove that the owner's converted OPF came from that exact publisher edition, or that the original LIT contains the full book. The correct state remains **HELD source-local metadata**.

> **Hostile challenge:** *Balance of Power* and *The Romulan Stratagem* have no OPF ISBN. Their catalogue ISBNs may not be silently backfilled into private-source claims merely because the titles look right.

> **Hostile challenge:** Original publisher-description paraphrases are marketing-source summaries, not narrative evidence from a close read. They must not be presented as audited episode/book synopses or used to infer canon.

**Effect:** zero accepted Source/Work/Assertion/Evidence, zero literary coverage or public Explorer change, zero copyrighted prose/cover transfers, zero remote merge/deploy/push. **Next gate:** primary publisher metadata recheck with stable independent receipt, source/edition custody verification and rights/read authority, then Auditor and Consolidator review before any admission.
