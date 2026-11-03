# Librarian next twenty OPF-to-ISBN lookups: seven held jacket observations

**SOURCE-ONLY PROPOSAL / NO IMAGE RELEASE / NO WORK ADMISSION.** Based on accepted `main@7b8ec8eb8e320002ee88280f11db2f108c38b85d`, observed 2026-11-03 UTC. No owner-private archive member path or narrative body is copied or read in this tranche. The accepted private OPF metadata observation is the only owner-derived source and is SHA-pinned in `records.json`.

## Denominator, boundaries, duplication

The twenty OPF local records are **twenty distinct OPF metadata-entry SHA-256 values**, and contain **twenty distinct checksum-valid ISBN-10 values** converting to twenty ISBN-13 lookup strings. Fifteen accepted OPF metadata entries have parse status `PARSED`, while five TOS classics (`opf-local:0140`–`0144`) have `OPF_XML_NAMESPACE_RECOVERED`; the latter are checksum-valid recovered XML metadata, not an independently verified original publication. This does **not** establish twenty original narrative texts, twenty edition-identical ebook binaries, or twenty accepted literary Works. Earlier 347 OPF entries, 347 LIT files, and 220 TXT files are different potentially overlapping file/metadata denominators, not additive book totals. This packet reads only already accepted sanitized OPF metadata and public web editions, never private story text or filename.

Open Library per-ISBN observation: **18 HTTP 200** edition JSON responses, **two HTTP 404** (both *Gemworld* parts). Among the eighteen returned edition records, **seven** contained a cover ID and **eleven** had no `covers` field. No-cover and 404 are point-in-time API states, not proof no artwork or book exists. The seven fetched public medium JPEGs all returned HTTP 200 `image/jpeg`, with distinct byte counts and SHA-256 pins in `records.json`. The Librarian visibly checked each as a **title-bearing book jacket**, not a text/interior page; another reviewer must independently verify both identity and usage rights.

| Public Open Library image candidate | OPF ID | ISBN-13 from OPF metadata | Open Library cover ID | Publisher relation | Release |
| --- | --- | --- | ---: | --- | --- |
| *Age of Unreason* | `opf-local:0037` | `9780743475921` | 12055672 | [Official Simon & Schuster eBook, exact ISBN](https://www.simonandschuster.net/books/Star-Trek-Age-of-Unreason/Scott-Ciencin/Star-Trek-Starfleet-Corps-of-Engineers/9780743475921) | HELD |
| *Balance of Nature* | `opf-local:0038` | `9780743475938` | 12055694 | [Official eBook, exact ISBN](https://www.simonandschuster.com/books/Star-Trek-Balance-of-Nature/Heather-Jarman/Star-Trek-Starfleet-Corps-of-Engineers/9780743475938) | HELD |
| *Dragon's Honor* | `opf-local:0086` | `9780743421416` | 14687625 | [Official eBook, exact ISBN](https://www.simonandschuster.biz/books/Dragons-Honor/Kij-Johnson/Star-Trek-The-Next-Generation/9780743421416) | HELD |
| *A Hard Rain* | `opf-local:0109` | `9780743419260` | 476375 | [Publisher eBook lists DIFFERENT ISBN 9780743419277](https://www.simonandschuster.com/books/A-Hard-Rain/Dean-Wesley-Smith/Star-Trek-The-Next-Generation/9780743419277): same-title lead, NOT exact edition | HELD |
| *The Battle of Betazed* | `opf-local:0119` | `9780743434348` | 476746 | [Publisher eBook lists DIFFERENT ISBN 9780743434355](https://www.simonandschuster.com/books/The-Battle-of-Betazed/Charlotte-Douglas/Star-Trek-The-Next-Generation/9780743434355): same-title lead, NOT exact edition | HELD |
| *Immortal Coil* | `opf-local:0123` | `9780743405928` | 475787 | [Publisher eBook lists DIFFERENT ISBN 9780743448468](https://www.simonandschuster.com/books/Immortal-Coil/Jeffrey-Lang/Star-Trek-The-Next-Generation/9780743448468): same-title lead, NOT exact edition | HELD |
| *Star Trek: The Motion Picture* | `opf-local:0140` | `9780743412087` | 10476824 | [Official eBook, exact ISBN](https://www.simonandschuster.com/books/Star-Trek/Gene-Roddenberry/Star-Trek/9780743412087) | HELD |

The **four exact-ISBN first-party publisher observations** are *public product-page evidence*, not verified physical identity of owner-private text or licensed image matching the eBook artwork. The **three different-ISBN official publisher matches** establish title/creator-family leads only; they explicitly **fail** the edition-exact gate. The eleven 200/no-cover rows have no proposed image. The two 404 rows remain unresolved. One no-cover row, `opf-local:0141` *The Entropy Effect*, refers to **an already catalogued official ISBN-13 eBook edition** in accepted `tos-classics-cover-editions-20261103`; it does not create a second new Work or a new publisher discovery. No automatic Work deduplication/reconciliation is performed.

Source-identity caveats kept visible: `opf-local:0086` privately parsed title reads `DRAGONS'S HONOR` (apostrophe error) while the publisher and image read *Dragon's Honor*; `opf-local:0140` contains `THE MOTION PICTURE™` while its official product title includes the *Star Trek* series prefix. Three returned Open Library edition JSON objects (Age of Unreason, A Hard Rain, The Battle of Betazed) carry the **ISBN-10 field but not an `isbn_13` field**: their 13-digit query URL redirects/locates an edition and the mathematically converted ISBN-10 matches, but the body does not independently assert the 13-digit representation. These are normalization observations, **not** permission for silent Work/edition identity collapse.

## Rights, invariants and next gate

[Open Library Covers API](https://openlibrary.org/dev/docs/api/covers) and [Open Library developer licensing](https://openlibrary.org/developers/licensing) are API-use context, not an unconditional grant over any publisher jacket. A fetched image is an observation, not copyright clearance; a public cover URL does not prove the image correctly belongs to the exact eBook manifestation. No artwork binaries, thumbnails, markdown-rendered images, or source texts are placed in the repo; all 7 images and 20 OPF records remain nonpublished metadata **proposals only**.

> Hostile challenge: The three similarly titled public publisher pages with different ISBNs could be wrong-edition visual associations even though Open Library maps the OPF lookup ISBN to a jacket. Recording the distinction is mandatory; do not quietly map publisher image rights across editions.

> Hostile challenge: Twenty independent-looking OPF metadata entries could be twenty exports or duplicate formats of fewer narrative Works. Unique OPF hashes and ISBNs prove neither Work uniqueness nor independently read source content. The Entropy Effect official eBook metadata already exists in a separate accepted public proposal, and must not be counted twice.

Before any Explorer expansion, an independent reviewer must reopen the **seven exact image URLs and hashes**, compare cover/ISBN/format to primary publisher source, challenge title/edition mismatches, and determine a separately authorized artwork display/attribution path. The Consolidator must generate public source-local associations and ask for exact permission to merge/release; neither this Librarian packet nor `validate.py` grants that authority.

## Validation

```sh
python3 proposals/librarian/opf-next-twenty-cover-audit-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/opf-next-twenty-cover-audit-20261103 -p test_validate.py -v
python3 -O -m unittest discover -s proposals/librarian/opf-next-twenty-cover-audit-20261103 -p test_validate.py -v
```

Validation source classes: accepted sanitized OPF metadata bytes+hash; public first-party publisher metadata links; Open Library observed JSON/cover IDs+byte/hash; operator visual check; deterministic local source-only tests. **No private book narrative reading, no source/Work admission, no images released, no merge/deploy.**
