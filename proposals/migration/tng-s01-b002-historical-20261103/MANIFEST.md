# TNG historical staging migration: Season 1 titles 6–10

**Role:** MIGRATION

**Candidate base:** accepted `main@d4ecd970bf28019696abd692011007d7d47f9ff8`

**Historical source:** [PR #12](https://github.com/thebrazenbeard/trek-data-core/pull/12), immutable head `e4c891b26622ae08eac346a55059a58f687d064c`
**Effect:** `proposal_only`, `accepted_corpus_effect=NONE`, `accepted_coverage_effect=NONE`, `source_work_binding=NOT_ADMITTED`

## Actual work performed

Inspected the historical overview, validation and metadata portions of the five episode files as inert Git blob content; this was **not** a fresh full semantic reading of those historical research files. Verified the eight blob IDs against the historical commit and independently calculated SHA-256 hashes of all eight historical files. Recovered **five candidate episode metadata rows** with provisional aired-title ordering, production codes, transcript-index locators, historical line extents, metadata crosschecks, and source provenance limits. The `records.json` file retains reported historical aggregates of 50 evidence and 25 assertion records as **unadmitted counts**, not as migrated accepted evidence. The original historical paraphrase records remain at their immutable Git paths and are not duplicated as current source-grounded assertions.

Crosswalked the five titles against the separately accepted-as-discovery-only Paramount+ Season 1 `tng.csv` snapshot, pinned by SHA-256. The publisher episode ordinals are **7–11**, while the historical local sequence is **6–10**, because the premiere's multipart numbering convention differs. The publisher labels `Hide and "Q"`; the old proposal has `Hide and Q`, retained as a title variant requiring review. These candidate matches do **not** settle canonical Work identity.

## Evidence classes and exclusions

- **Git object inspection:** eight historical files verified by both Git blob identity and content SHA-256.
- **Historical claim:** the earlier worker reported reading five complete third-party Springfield! Springfield! transcript pages. This migration did not retrieve or independently authenticate those page bytes, their completeness, or their relation to an audiovisual release.
- **Metadata source:** the already captured Paramount+ index is a publisher listing and discovery reference, not a watched episode, transcript content, or independently accepted Source↔Work binding.
- **Unknown lineage:** the Springfield! Springfield!/Chakoteya relationship is unresolved; a crosscheck URL does not establish independent corroboration.
- **Rights:** no complete transcript, script, video, still or ebook content is copied into this proposal.
- **Research scope:** no new local entity, primary-source evidence, assertion, global identity, `SOURCE_BOUND`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED` or `AUDITED` record is admitted.

> **Hostile challenge:** The historical `validation.json` reports local consistency, but this does not authenticate source reads or prove the 50 paraphrased evidence records are faithful to a licensed version of the episodes. Its green result cannot be replayed as a current independent semantic audit.

## Reproduction

From the repository root:

```bash
python3 proposals/migration/tng-s01-b002-historical-20261103/validate.py
python3 proposals/migration/tng-s01-b002-historical-20261103/validate.py --historical-repo .
```

The second command requires the exact old PR #12 Git objects to be fetched into a read-only audit object store; it performs no checkout or historical code execution and fails closed if those objects are absent. Both commands check the accepted discovery CSV hash. `records.json` contains the eight original Git object IDs plus SHA-256 receipts and the five metadata rows.

## Exact next frontier

The TNG researcher and Librarian must independently qualify edition-specific full-source evidence and an accepted Source↔Work roster, then re-code the historical observations into the current typed model, with explicit counterevidence and a fresh Auditor review. The next *unrecovered* historical TNG tranche would need separate immutable-path and source-lineage review; do not treat an old PR number or staging title as completed coverage.
