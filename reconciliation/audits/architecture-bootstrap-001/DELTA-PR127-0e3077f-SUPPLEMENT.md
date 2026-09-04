# Auditor supplement — PR #127 external-source verification

Date: 2026-08-17
Role: AUDITOR
Proposal head: `0e3077f0a0fc16237b9fd08f2e515a6942ef76ba`
Companion audit: `DELTA-PR127-0e3077f.md`

## Scope

This append-only supplement does not repeat the companion audit's blocking findings on crosswalk snapshot identity, aggregator subsource provenance, row-specific lineage, historical collision-count recoverability, or missing deterministic PR validation.

It records independent positive source checks performed after that audit and updates the PR #125 coordination state.

## SUP-XWALK-001 — rtrek binary target identity independently confirmed

PR #127 currentness record names:
- repository: CRAN mirror `cran/rtrek`;
- commit: `b0583ee4b204457bfe1020564aad0d7acf7146a4`;
- path: `data/stBooks.rda`;
- Git blob: `ea0a3c4dafdcc2e857edec38b6231bc9acd75a25`;
- size: 77,722 bytes;
- package version context: 0.5.2.

Independent GitHub checks confirm:
- commit `b0583ee4...` is the CRAN mirror commit `version 0.5.2`;
- its exact recursive tree contains `data/stBooks.rda` at blob `ea0a3c4...`, size 77,722;
- `man/stBooks.Rd` at the same commit documents `stBooks` as 783 rows × 11 columns, largely complete through end of 2017 but explicitly non-comprehensive and potentially irregular.

Therefore the preserved binary intake target is reproducibly identified even though its RDA contents are not decoded here.

## SUP-XWALK-002 — current decoder blocker reproduced in Auditor runtime

At audit time:
- `Rscript` is not installed on the execution PATH;
- Python module `pyreadr` is unavailable;
- Python module `rdata` is unavailable;
- GitHub connector attempt to fetch the binary `stBooks.rda` directly fails because the connector accepts UTF-8 text rather than arbitrary binary content.

Thus `LOCATED_BUT_NOT_DECODABLE_IN_CURRENT_RUNTIME` is independently supported for this runtime.

This is a runtime/capability observation, not a permanent property of the file. If a decoder/export route becomes available, re-evaluate from the same pinned blob rather than copying documentation rows as if they were decoded data.

## SUP-XWALK-003 — Worlds Volume Three ISBN disagreement independently reproduced

Independent reopening of the current cited external pages supports the proposal's decision to preserve the 2010 reprint ISBN conflict:
- Memory Alpha currently exposes reprint ISBN `1451613421`;
- Memory Beta currently exposes reprint ISBN `1451613423`.

The candidate crosswalk correctly keeps the conflict unresolved.

This verifies the conflict-preservation behavior only. It does not decide which ISBN is correct and does not promote the legacy `STW-*` identity.

## SUP-XWALK-004 — Ghost Ship eBook manifestation independently supported by publisher metadata

Current Simon & Schuster publisher metadata for Diane Carey's `Ghost Ship` exposes:
- eBook format;
- Pocket Books/Star Trek;
- publication May 23, 2000;
- 258 pages;
- ISBN13 `9780743412131`.

That independently supports PR #127's decision to keep the later eBook manifestation distinct from paperback edition/source-instance metadata and from the unresolved legacy LIT-derived representation.

It does not establish preferred Source quality; the legacy Ghost Ship LZX/body-extraction warning still requires byte comparison before source preference.

## SUP-XWALK-005 — PR #125 current state has advanced beyond the Director-only correction comment

`ST_LIBRARIAN_CURRENTNESS_SYNC_V2.json` is already correctly treated as historical by the companion Director comment.

Current coordination state is now further advanced:
- PR #125 exact head `4ccc10b...` has been Auditor-reviewed as well as Director-reviewed;
- durable Auditor record: `DELTA-PR125-4ccc10b.md`;
- result: strong bounded Source/Work/binding model, still CONTESTED before integration/acceptance with additional findings on active CONTESTED state, cross-domain supersession, multi-parent independence, executable schema, SOURCE_BOUND derivation boundary, common v0.2 integration, and contested/superseded rationale.

Future currentness artifacts should point to both Director and Auditor successor records rather than treating `PROPOSAL_READY_FOR_AUDITOR_REVIEW` as current.

## Result

These checks strengthen PR #127 as **legacy/candidate migration evidence** but do not change the companion audit's disposition: the rows are not yet acceptable governed crosswalk records without normalization into the corrected #125 successor contract.

No Source/Work/crosswalk acceptance, ebook custody promotion, collision membership recovery, or protected effect performed.
