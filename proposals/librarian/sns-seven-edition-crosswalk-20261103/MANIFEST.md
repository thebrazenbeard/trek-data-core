# S&S seven distinct official ISBN-format locators — held source-first librarian tranche

**Batch:** `SNS.PUBLIC.SEVEN.EDITION.LOCATORS.20261103`  
**Role:** Librarian source/edition inventory; proposal-only, no published source/Work, no rights or coverage effect.  
**Accepted main at final branch preparation:** `6271a861f6dbf5337a6a6792bb4b5ee355311157` (2026-11-03 UTC; refreshed from earlier selection `f2a98d5a958ce6263ca37ac0bf44e3d074751211`).  
**Records SHA-256:** `87b2567138265ff76a709233c47f5d0490d5f6cb52f74fc4866342ffa1cd881e`

## First-party pages actually read

The publisher's own HTML was not available through the Lappy direct HTTP route, so I used the *rendered* Simon & Schuster first-party edition pages, including each page's title/byline, selected format, ISBN13, imprint and publisher date, length/runtime, **About the Book** paragraphs, and linked **High Resolution Images** resource. This is an honestly bounded *publisher listing* read, not a book/script/audio read or raw HTML custody claim. Page contents are mutable; no raw source was archived. The links below are direct publisher **edition-specific** sources.

| Publisher title and ISBN | Format; imprint | Date; extent | Direct official page |
| --- | --- | --- | --- |
| *Star Trek: Picard: Firewall* `9781797168432` | Unabridged audio; Simon & Schuster Audio; January LaVoy | 2024-02-27; 12h 22m | [First-party edition](https://www.simonandschuster.com/books/Star-Trek-Picard-Firewall/David-Mack/Star-Trek-Picard/9781797168432) |
| *Pliable Truths* `9781668046425` | eBook; Pocket Books/Star Trek | 2024-05-21; 352 pp. | [First-party edition](https://www.simonandschuster.com/books/Pliable-Truths/Dayton-Ward/Star-Trek-The-Next-Generation/9781668046425) |
| *Star Trek: Picard: No Man's Land* `9781668066133` | Trade paperback **published script**; Pocket Books/Star Trek | 2024-09-24; 160 pp. | [First-party edition](https://www.simonandschuster.com/books/Star-Trek-Picard-No-Mans-Land/Kirsten-Beyer/9781668066133) |
| *Star Trek: Picard: No Man's Land* `9781668066140` | eBook **published script**; Pocket Books/Star Trek | 2024-09-24; 160 pp. | [First-party edition](https://www.simonandschuster.com/books/Star-Trek-Picard-No-Mans-Land/Kirsten-Beyer/9781668066140) |
| *Star Trek: Picard: No Man's Land* `9781797124537` | Unabridged audio download (**original audio drama**); Simon & Schuster Audio Originals, ensemble cast | 2022-02-22; 1h 39m | [First-party edition](https://www.simonandschuster.com/books/Star-Trek-Picard-No-Mans-Land/Kirsten-Beyer/Star-Trek-Picard/9781797124537) |
| *Star Trek: Strange New Worlds: Toward the Night* `9781668074565` | Hardcover; Pocket Books/Star Trek | 2025-04-29; 336 pp. | [First-party edition](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Toward-the-Night/James-Swallow/Star-Trek-Strange-New-Worlds/9781668074565) |
| *Star Trek: Strange New Worlds: Toward the Night* `9781668116968` | Unabridged audio; Simon & Schuster Audio; Robert Petkoff | 2025-04-29; 9h 56m | [First-party edition](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Toward-the-Night/James-Swallow/Star-Trek-Strange-New-Worlds/9781668116968) |

The same-title editions remain separate ISBN and SKU identities. Especially important, **No Man's Land's 2022 original audio drama is not silently identified as the same expression/Work as its 2024 printed or eBook script**, despite shared title and publisher overview. The audio page credits a large performer cast, and this batch retains only a provenance pointer instead of copying the entire credit list. Exact textual equivalence is *unresolved*; no reconciliation was attempted.

## Fingerprints and artwork (held)

Each `publisher_about_sha256` is a direct observation of the **rendered page's About the Book prose paragraphs**, trimming web navigation, disclaimers/trademark line, heading and author biography. I joined the paragraph lines with single spaces and collapsed repeated whitespace, then SHA-256 hashed the resulting UTF-8 text. The normalized text itself is deliberately absent from this public proposal. This is versioned as `WEB_RENDERED_ABOUT_BOOK_PARAGRAPHS_COLLAPSE_WHITESPACE_SHA256_UTF8_V1`. It is a *rendered-content* checksum, **not** a full immutable HTML fingerprint or full-text read.

| ISBN pages | SHA-256 About the Book | Codepoints |
| --- | --- | ---: |
| Firewall audio `9781797168432` | `d992282496fd0b99c87022f1a3a4be587ea64323960cd775a98ea17aaf117c3b` | 541 |
| Pliable Truths eBook `9781668046425` | `e1d4c074d1867edef1607901d886cddae4fd49f7bdfe9e01b3403ea2f6138ac3` | 1214 |
| No Man's Land script paperback/eBook/audio | `3480f4b02c12b7f301e78d1bdf19c6f70b86cc42c559cf1dbd34b0f1c83da011` | 807 |
| Toward the Night hardcover `9781668074565` | `58063e53ee9d81e5094f4ce8beec1d47f1e1650d9b5fd349583752656d731659` | 915 |
| Toward the Night audio `9781668116968` | `a22653d21319a11dd8e5ebc59b82df911e1e17a6f38531953da4ad4328f04217` | 1187 |

Seven **exact high-resolution JPEG URLs were discovered via the individual edition pages' publisher-linked cover resource** (`d28hgpri8am2if.cloudfront.net/book_images/onix/...`). These are locators only: attempts to follow the links through the search renderer returned binary/unsupported-content errors; the image bytes were **not acquired**, and no license to mirror, hotlink, or publish is established. All rows are explicitly `HELD_FIRST_PARTY_URL_ONLY_NO_PUBLIC_DISPLAY_LICENSE`. No book prose, audio, script text, complete publisher overview, or publisher image is republished here.

## Duplicate and non-admission checks

The accepted repository already contained **other formats of the same titles**: *Firewall* eBook `9781668046371`, *Pliable Truths* audiobook `9781797172699`, publisher research leads for *Firewall* paperback `9781668046364`, *Pliable Truths* paperback `9781668046418`, and *Toward the Night* paperback `9781668074572`. Those exact ISBNs were intentionally excluded. The current accepted `proposals/librarian`, `proposals/research/lit`, and `explorer` trees were searched for all seven chosen ISBN strings before authoring; none occurred. All 16 currently open PRs were checked for relevant ISBNs in PR summaries; there is no known direct overlap, though diff-level recheck at independent review remains appropriate. The validator rescans accepted source/Explorer JSON and fails if a duplicate appears.

Accepted provenance snapshots are byte pinned: `explorer/lit-publisher-edition-leads.json` at `0568db4c7313f3a3da4b3cd4a5d9e56430fe09e64ed0687d8d9690d782df67d5` and `explorer/publisher-isbn-crosschecks.json` at `1170e8cb56b4ff3c5beab8d412fa5613b6e3b9d0ab7b5a18f80fe403c5bde3e8`. They are inventory/reconciliation boundaries; their existence does **not** elevate title-level or private OPF leads to independent evidence. No private OneDrive file paths, title extraction data or private ebook body enters this proposal.

## Validation and hostile falsification

```bash
python3 proposals/librarian/sns-seven-edition-crosswalk-20261103/validate.py
python3 -O proposals/librarian/sns-seven-edition-crosswalk-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/sns-seven-edition-crosswalk-20261103 -p 'test_*.py' -v
python3 -O -m unittest discover -s proposals/librarian/sns-seven-edition-crosswalk-20261103 -p 'test_*.py' -q
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

Exact closed-schema URL/ISBN/creator/format/imprint/date/extent/digest/cover pins are checked, along with ISBN-13 checksums and duplicate accepted ISBN scan. Hostile tests include 16 envelope/promotion attacks; all 16 fields across seven rows; same-title ISBN/cover/source/description cross-row rebindings; change of audio to script or script to audio; exact title/edition collision; credential query/host spoofing; duplicate raw JSON keys in normal and optimized interpreters; accepted snapshot drift; and an accepted ISBN duplicate inserted under a separate librarian path. No test assertion depends on Python `assert` optimization behavior.

> **Hostile challenge:** The site serves mutable rendered pages; paragraph hashes are not immutable source custody and do not prove format text equivalence. Linking cover resources is not authorization to publish artwork. The audio drama and later printed script may share creative material but require separate Work/expression decisions grounded in full permitted sources. Keep all effects `NONE`.

**Next frontier:** independent source/edition audit of these seven exact publisher pages and source-level rebind tests, followed by protected acceptance only if qualified. More literary ISBN editions and full-text research remain separate work.
