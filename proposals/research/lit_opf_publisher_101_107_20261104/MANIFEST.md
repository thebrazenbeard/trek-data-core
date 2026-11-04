# HELD owner OPF / publisher edition leads 0101–0107 — 2026-11-04

**Scope:** source-local metadata only, **not** accepted research, edition authentication, copyrighted ebook close-read, Explorer display, cover release, or Work/Source admission.

## Custody and method

- Accepted `main` baseline: `3028765359001b90bc3e6b5c1835ee283b326e91`, distinguished from locally stacked HELD commits (`4cde2f6` and predecessors) and GitHub draft PR chain #512 → #524 → #526 → #533.
- Owner OPF metadata source: `proposals/librarian/private-opf-metadata-20261103/observations.json`, SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`; this local receipt contains 347 source-local metadata entries, not 347 admitted Works. Exact per-entry hashes and literal title/creator/ISBN claims preserved in `records.json`.
- Opened **seven** official Simon & Schuster publisher ebook pages on 2026-11-04. One upstream publisher family; these pages are not independent corroborating sources and no page HTML snapshot or immutable remote-content digest is claimed.
- `held_synopsis` values are original one-sentence paraphrases of publisher descriptions. They are not extracted from an ebook or based on a full-text reading. No copyrighted book prose, private ebook path, publisher cover, or other media bytes included.
- ISBN-10 checksum validity is **not** verification that the owner-controlled file is the referenced edition. Two Gemworld ISBNs are valid but **do not match the currently presented publisher ebook ISBN13**. Their edition identity remains unresolved, without inferring publisher error or private edition binding.

## Publisher receipts and falsifiable local comparisons

| Owner OPF | Official publisher ebook page | OPF-to-edition observation |
| --- | --- | --- |
| `0101` | [The First Virtue](https://www.simonandschuster.com/books/The-First-Virtue/Michael-Jan-Friedman/Star-Trek-The-Next-Generation/9780743421362), Michael Jan Friedman and Christie Golden; ISBN13 `9780743421362`, September 22, 2000, 304 pp. | OPF title suggests Double Helix #6 but contains neither author nor ISBN; **title-only hold**. |
| `0102` | [The Forgotten War](https://www.simonandschuster.com/books/The-Forgotten-War/William-R-Forstchen/Star-Trek-The-Next-Generation/9780743421386), William R. Forstchen; ISBN13 `9780743421386`, September 1, 1999, 304 pp. | OPF ISBN10 `0743421388` converts to matching ISBN13. **Checksum alignment only**, owner edition unverified. |
| `0103` | [Gemworld — Book One Of Two](https://www.simonandschuster.com/books/Gemworld/John-Vornholt/Star-Trek-The-Next-Generation/9780743406772), John Vornholt; ISBN13 `9780743406772`, February 5, 2000, 272 pp. | Owner OPF valid ISBN10 `074342140X` → `9780743421409` **differs** from this publisher page. Direct official URL lookup of converted ISBN was not accessible. Exact manifestation identity **unresolved**. |
| `0104` | [Gemworld — Book Two Of Two](https://www.simonandschuster.com/books/Gemworld/John-Vornholt/Star-Trek-The-Next-Generation/9780743406789), John Vornholt; ISBN13 `9780743406789`, February 1, 2000, 272 pp. | Owner OPF valid ISBN10 `0743421426` → `9780743421423` **differs** from this publisher page. Direct official URL lookup of converted ISBN was not accessible. Exact manifestation identity **unresolved**. |
| `0105` | [Tooth and Claw](https://www.simonandschuster.com/books/Tooth-and-Claw/Doranna-Durgin/Star-Trek-The-Next-Generation/9780743419499), Doranna Durgin; ISBN13 `9780743419499`, July 11, 2001, 272 pp. | Owner title has extra trailing punctuation, creator agrees, no ISBN. **Title/creator hold**. |
| `0106` | [Diplomatic Implausibility](https://www.simonandschuster.com/books/Diplomatic-Implausibility/Keith-R-A-DeCandido/Star-Trek-The-Next-Generation/9780743419505), Keith R. A. DeCandido; ISBN13 `9780743419505`, July 7, 2001, 272 pp. | Owner title says `Next Generations`, creator spelling lacks spaces between initials, and no ISBN. **Title/creator hold**, variant unresolved. |
| `0107` | [Maximum Warp: Book One](https://www.simonandschuster.com/books/Maximum-Warp-Book-One/Greg-Brodeur/Star-Trek-The-Next-Generation/9780743419529), Greg Brodeur / Dave Galanter; ISBN13 `9780743419529`, April 11, 2001, 256 pp. | Owner creator order Dave Galanter then Greg Brodeur is reversed from publisher credits, and no ISBN. **Title/creator hold**; no claim that order implies a different Work. |

## Honest totals, tests and next frontier

- New source-local OPF leads: **7**; checksum-aligned only **1**; owner ISBN10 valid but edition divergence **2**; owner ISBN absent **4**. All seven keep `private_source_edition_verified=false` and no accepted effects.
- Cumulative local HELD source-local OPF leads (`0055–0107` contiguous): **53**. These are NOT 53 newly admitted works, 53 independently read books, 53 source-bound editions, or 53 new public literary cards. Other separately HELD Consolidator publisher-draft cards are not added to this count.
- `validate.py` pins owner inventory and per-entry SHA, official first-party URL, ISBN, exact publisher title including Gemworld part, page extent, date and creators, typed contradiction states and synopsis hashes. Hostile tests reject unauthorized admission/coverage, nonexistent OPF ISBN filling, rehashed false edition match, URL spoofing, metadata mutation, and private content smuggling. Earlier HELD packets are explicitly nonoverlapping by owner-local IDs and displayed publisher ISBNs.
- **Next frontier:** `opf-local:0108` onward for bounded metadata; independent owner-authorized investigation needed to determine why Gemworld owner ISBN10 claims differ from current official publisher ebook manifestations. Do not reconcile from title alone or release copyrighted text.
