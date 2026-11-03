# Source-local discovery rechecks B001 — proposal, not research admission

Status: `PROPOSAL_ONLY_SOURCE_LOCAL_VERIFICATION_LEDGER`
Source: accepted `explorer/discovery-catalog.json` at `f387126c60942ff90952cd6e9251a67c8f5c26fa`
Source SHA-256: `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`
Observation date (UTC): `2026-11-03`
Admission effect: `NONE`; coverage effect: `NONE`.

## Actual bounded work

The generator maps **all 1,214 source-local discovery rows** to a deterministic triage ledger without deduplicating, assigning work identity, or changing their research coverage tier. Every row is explicitly `source_local_discovery_state: CATALOGUED_METADATA_ONLY`, `governed_research_coverage_state: NOT_ADMITTED` (not a governed `DISCOVERED` coverage promotion). On **eight** rows, an agent actually consulted rendered official product/episode pages and recorded exact matching metadata fields. Search/read tooling supplied rendered page text, **not a captured raw HTML body**. Therefore `raw_body_sha256` is null for every row; no raw page custody, complete copyrighted work, close reading, or cross-work evidence is asserted.

| Source-local row | Official page actually viewed | Matched against source row | Additional observed fields, not yet independently row-compared |
| --- | --- | --- | --- |
| `literature:prh-autobiography-kirk` | [PRH/Titan Kirk](https://www.penguinrandomhouse.com/books/250795/the-autobiography-of-james-t-kirk-by-david-a-goodman/) | title, author, ISBN, edition locator | Titan Books publisher |
| `literature:prh-autobiography-picard` | [PRH/Titan Picard](https://www.penguinrandomhouse.com/books/555327/the-autobiography-of-jean-luc-picard-by-david-a-goodman/) | title, author, ISBN, edition locator | Titan Books publisher |
| `literature:prh-autobiography-janeway` | [PRH/Titan Janeway](https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/) | title, author, ISBN, edition locator | Titan Books publisher |
| `literature:proposed-lit-picard-second-self` | [S&S Second Self](https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781982194833) | title, author, ISBN, edition locator | S&S publisher surface |
| `literature:proposed-lit-snw-high-country` | [S&S High Country](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-The-High-Country/John-Jackson-Miller/Star-Trek-Strange-New-Worlds/9781668002391) | title, author, ISBN, edition locator | S&S publisher surface |
| `lead:0000` | [Paramount+ The Doomsday Machine](https://www.paramountplus.com/shows/video/1226106142/) | title | TOS S2E6, Oct 20 1967 |
| `lead:0001` | [Paramount+ The Trouble with Tribbles](https://www.paramountplus.com/shows/video/1226188697/) | title | TOS S2E15, Dec 29 1967 |
| `lead:0002` | [Paramount+ The Corbomite Maneuver](https://www.paramountplus.com/shows/video/788561887/) | title | TOS S1E11, Nov 10 1966 |

PRH pages are distributor listings for Titan Books; they do not count as independent Titan plus PRH corroboration. `paramount`, `paramountplus.com`, and `startrek.com` source groups share `paramount_corporate_publisher_family`. Wikidata's discovery row and Paramount's separately consulted TOS episode page are kept as **distinct provenance families**; a Paramount URL is not silently substituted for the original Wikidata locator.

The **three episode synopses** are short original paraphrase drafts based only on the official site's brief descriptions. They are **not summaries derived from full episodes**; human review is pending. The other **1,211 synopsis fields are explicitly missing**. Memory Alpha may be used later for *secondary discovery/crosswalk* only; no Memory Alpha page was verified or admitted in this batch.

## Coverage and duplicate accounting

- `1,214` source-local rows in ledger; `8` rendered metadata rechecks; `1,206` rows still require primary metadata rechecks.
- `5` literary edition-related checks and `3` official episode title/slot page checks.
- `25` normalized duplicate-signature groups containing `50` original rows; all raw rows preserved. Duplicates do not add independent corroboration.
- `0` raw publisher page-body byte snapshots pinned by this batch; `0` governed Works/Evidence/Assertions admitted; `0` complete episode or book reads.
- The 1,214 rows are a **source-local observation count**, **not** a defensible count of unique Star Trek works, episodes, fully researched items, or completed synopses.

## Deterministic rebuild

```bash
python3 tools/build_discovery_verification_ledger.py --check
python3 -m unittest tests/test_discovery_verification_ledger.py
python3 tools/build_discovery_verification_ledger.py --queue-next 16
```

`--check` reconstructs every field and compares the committed `ledger.json` byte-for-byte. It does **not** re-fetch remote sources or verify that these web observations are authenticated; it validates only their consistency and recorded fields against the accepted source-local directory. `source_rechecks.json` and `episode_rechecks.json` are reviewable declared observations, not proof of remote source custody.

`--queue-next 16` prints a deterministic next 16-row JSON work queue, beginning with remaining Wikidata episode leads `lead:0003` onward. It performs **no remote fetching or verification**, records `processed:0`, and carries exact row title/context/locator and per-row requirements. Workers may append source-bound observations only after their own actual source reads and review; the queue does not move coverage.

## Next verification frontier — bounded primary episode batches

1. Schedule deterministic batches of at most 16 as-yet-unchecked episode rows (prioritizing the initial Wikidata lead tranche). Record `row_id`, exact `title`, `context`, discovery URL, and expected source-family lineage in a queue manifest. Never count a shared episode-guide URL or an HTTP 200 response as a row-level match.
2. For each candidate, read a **specific official Paramount+ episode page**, with the title and `S# E#` appearing together in the episode heading or clearly delimited episode-card block. A season guide is acceptable only if an exact row-specific title/season/number triplet can be isolated without accidentally matching another card in the same document. Record canonical official URL, retrieval UTC date, independently confirmed title and slot. Compare slot only when source-row slot exists; otherwise mark `OBSERVED_OFFICIAL_PAGE_NO_SOURCE_ROW_COMPARISON`.
3. A source-retrieval worker should record an actually fetched UTF-8/HTML representation, byte length, SHA-256, acquisition URI/time, exact title/slot section locator and a short reproducible content fingerprint under a non-public raw-content custody scheme. No invented byte hashes; if the tool only provides rendered snippets, preserve `UNPINNED` as in B001.
4. From verified official brief descriptions, propose original short synopses with page grounding and explicit `BLURB_GROUNDED` status. Human review and any source-full close reading remain separate. Missing source descriptions remain `NOT_AUTHORED_SOURCE_NOT_READ`.
5. Reject mismatched titles, wrong episode numbers, multiple ambiguous card hits, cross-series collisions, stale pages, claimed corroboration from Paramount aliases, and unsupported promotion to `SOURCE_BOUND`, `CLOSE_READ`, or `AUDITED`. Add test fixtures for those adversarial cases before admitting the batch.
6. Append a versioned observation batch and regenerate this ledger. Only independently reviewed metadata fields advance; unresolved entries retain the exact reason. Work identity/reconciliation and coverage remain governed by their separate accepted ledgers.

No public-domain or copyrighted source text has been copied into this proposal; it contains factual bibliographic/episode metadata and original brief paraphrases only.
