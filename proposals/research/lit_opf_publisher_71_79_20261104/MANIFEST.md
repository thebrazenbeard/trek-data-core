# HELD: nine further TNG publisher edition leads (OPF 0071–0079)

**Status:** local source-relative bibliographic metadata proposal only, from accepted GitHub `main@3028765359001b90bc3e6b5c1835ee283b326e91`. This wave extends prior **local HELD** packets `3265e4a` (OPF 0055–0061) and `90392f0` (OPF 0062–0070), without changing accepted evidence, Source↔Work binding, governed Works, close-read coverage, synopsis publication, or live Explorer assets.

## Actual source reads and fingerprints

The accepted-public Librarian [OPF metadata inventory](../../librarian/private-opf-metadata-20261103/observations.json) was read as source-local *metadata* only and pinned at exact source-file SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`. Each edition metadata row additionally carries the **source-local OPF entry's actual SHA-256 fingerprint**, not a fabricated publisher-webpage digest. No owner-private member names or original OPF/LIT/ebook prose were copied or made public.

Nine official Simon & Schuster product pages were opened and read on 2026-11-04 for displayed title, listed creator, ebook manifestation, U.S. publisher date, length, ISBN13, and publisher description. The publisher's `.net` *Debtor's Planet* page is still **one Simon & Schuster upstream family**, not a second independent publisher. Publisher HTML bytes were not downloaded or hashed locally; product URLs are stable review locators but should not be misrepresented as immutable source snapshots.

Original one-sentence `held_synopsis` values are **paraphrases of publisher sales descriptions only**, not novel close-reads or independently verified canonical events.

| OPF local ID | Publisher title | OPF ISBN10 | Publisher ISBN13 | Evidence state | First-party source |
| --- | --- | --- | --- | --- | --- |
| `0071` | *War Drums* | **Missing** | `9780743421034` | Unverified title/creator only | [S&S](https://www.simonandschuster.com/books/War-Drums/John-Vornholt/Star-Trek-The-Next-Generation/9780743421034) |
| `0072` | *Nightshade* | **Missing** | `9780743421072` | Unverified title/creator only | [S&S](https://www.simonandschuster.com/books/Nightshade/Laurell-K-Hamilton/Star-Trek-The-Next-Generation/9780743421072) |
| `0073` | *Grounded* | `0743421086` | `9780743421089` | ISBN checksum alignment only | [S&S](https://www.simonandschuster.com/books/Grounded/David-Bischoff/Star-Trek-The-Next-Generation/9780743421089) |
| `0074` | *The Romulan Prize* | `0743421094` | `9780743421096` | ISBN checksum alignment only | [S&S](https://www.simonandschuster.com/books/The-Romulan-Prize/Simon-Hawke/Star-Trek-The-Next-Generation/9780743421096) |
| `0075` | *Guises of the Mind* | `0743421108` | `9780743421102` | ISBN checksum alignment only | [S&S](https://www.simonandschuster.com/books/Guises-of-the-Mind/Rebecca-Neason/Star-Trek-The-Next-Generation/9780743421102) |
| `0076` | *Here There Be Dragons* | `0743421116` | `9780743421119` | ISBN checksum alignment only | [S&S](https://www.simonandschuster.com/books/Here-There-Be-Dragons/John-Peel/Star-Trek-The-Next-Generation/9780743421119) |
| `0077` | *Star Trek: The Next Generation: Sins of Commission* | `0743421124` | `9780743421126` | ISBN checksum alignment only | [S&S](https://www.simonandschuster.com/books/Star-Trek-The-Next-Generation-Sins-of-Commission/Susan-Wright/Star-Trek-The-Next-Generation/9780743421126) |
| `0078` | *Star Trek: The Next Generation: Debtor's Planet* | `0743421132` | `9780743421133` | ISBN checksum alignment only | [S&S .net](https://www.simonandschuster.net/books/Star-Trek-The-Next-Generation-Debtors-Planet/W-R-Thompson/Star-Trek-The-Next-Generation/9780743421133) |
| `0079` | *Foreign Foes* | `0743421140` | `9780743421140` | ISBN checksum alignment only | [S&S](https://www.simonandschuster.com/books/Foreign-Foes/Dave-Galanter/Star-Trek-The-Next-Generation/9780743421140) |

Both title/creator-only rows retain the original owner OPF's empty `isbn_checksum_valid` list and a publisher-sourced ISBN13 as *separate claims*. Their ISBNs were **not inferred from the private files**. For seven other rows, checksum-valid OPF ISBN10 metadata mathematically converts to the listed first-party publisher ISBN13; that is not source-byte authentication.

The OPF source-local uppercase/abbreviated titles are preserved literally, including `SINS OF COMMISSION` and `DEBTOR'S PLANET`; the publisher expands those to full *Star Trek: The Next Generation* titles. Each row carries the exact publisher display string, not a fabricated canonical normalization. As with previous OPF intakes, any OPF metadata dates and publisher publication dates reflect potentially different events; no automatic equivalence is inferred.

## Falsifiers and effect boundary

```bash
python3 proposals/research/lit_opf_publisher_71_79_20261104/validate.py
python3 -m unittest tests.test_lit_opf_publisher_71_79_held -v
```

The validator checks exact OPF public inventory SHA-256 plus per-item entry hashes, contiguous source-local row identities, typed missing-ISBN states, valid ISBN10 and ISBN13 checksums, exact publisher ISBN URLs/hosts/titles/creators, dates/page extents, source variant flags, and zero accepted effects. Adversarial tests mutate the evidence state, private paths, source records, ISBNs, publisher hosts, anomalies, and data-rights claims to falsify unsafe promotion. Tests do **not** themselves retrieve official publisher content; independent source snapshots remain a separate admission requirement.

> **Hostile challenge:** An OPF-local title plus creator may point to a legitimate publisher product yet still be the wrong manifestation or private file. Missing ISBNs in `0071` and `0072` must remain unresolved, even though publisher pages supply valid ISBN13 numbers.

> **Hostile challenge:** Seven aligned ISBN check digits verify string compatibility, not completeness, licensed access, original LIT↔converted OPF equivalence or a close read. None of the nine metadata rows can inflate literary coverage.

> **Hostile challenge:** A first-party publisher's `.com` and `.net` pages share an upstream editorial/catalog system. Treating them as independent witnesses would launder publisher errors into false corroboration.

> **Hostile challenge:** Fictional events described in publisher marketing remain publisher *claims about* a story. Their paraphrases do not become objective fictional evidence until the actual book is read and source-relative citations are recorded.

**Effect:** exactly **9 new HELD edition metadata rows** (7 ISBN metadata alignments; 2 title/creator holds); **0 accepted Works/Sources/bindings/coverage**, no ebook prose, no cover/image, no remote push or Pages publication. Next decision gate is source/edition custody and rights, independent publisher metadata receipt, and Auditor/Consolidator review before any governed admission.
