# Legacy Migration Startup Readiness 001

Role: MIGRATION
Status: PROPOSAL / BLOCKED_FOR_GOVERNED_MIGRATION
Observed accepted main: `d58359a207da89e812d0a0330558c66774ed1241`
Recorded: 2026-08-14

## Accepted-state inspection

At the observed accepted `main`, the repository contains only `README.md`. There is no accepted migration ledger, Source/Work registry, research schema, predicate registry, worker contract, validation tooling, or accepted legacy migration batch.

Therefore accepted legacy migration coverage is **zero governed batches**. No historical chat counter or prior synthesis is promoted into accepted coverage.

## Proposal-state inspection

Open PR #1 (`architecture/v0.1-bootstrap`) proposes the governing research architecture, including:

- Source, Work, Local Entity, Evidence, Assertion schemas;
- batch and reconciliation schemas;
- predicate registry;
- worker/source/methodology documentation;
- deterministic validation/projection tooling;
- `migrations/README.md`, which states that legacy research is migrated in bounded batches and must not silently upgrade old conclusions into current accepted truth.

PR #1 is not accepted state and is not treated as authority for a governed migration batch.

At the latest refresh PR #1 remains open, mergeable, and unmerged. Its head is `4b771b28406e1b2f41d93f5787e1978e98c6e432`, with two commits and 24 changed files. This movement does not change accepted `main`.

## Repository-visible candidate inventory

A bounded search for legacy/migration material inside `trek-data-core` found no repository file matching the legacy-migration search terms outside this readiness proposal. A search of repositories owned by `thebrazenbeard` for Trek material found only `thebrazenbeard/trek-data-core`.

Repository-visible unaccepted research proposals/branches do exist, including current lanes for DIS, DS9, LD, PIC, SNW, TNG, TOS, and VOY. These are **not classified as legacy migration inputs merely because they are unaccepted**. They are current worker proposals and remain under their originating research lanes unless an accepted decision explicitly routes them through MIGRATION.

Open PRs visible during the refresh include:

- PR #1, architecture bootstrap;
- PR #2, DS9 opening-five staging pending source binding;
- PR #3, TNG initial five-title batch.

These are proposal-state dependencies or current research proposals, not accepted legacy artifacts.

## Candidate-selection result

Result: `NO_REPOSITORY_VISIBLE_LEGACY_TRANCHE`

No bounded legacy artifact tranche can presently be selected from GitHub evidence alone. The absence of a repository-visible artifact is not evidence that historical Trek research does not exist elsewhere; it means its durable location/provenance has not yet been established in accepted repository state or another accessible project source.

This prevents the migration worker from fabricating a source path, reconstructing legacy research from chat summaries, or misclassifying current proposal branches as legacy input.

## Migration gate result

Result: `BLOCKED_FOR_GOVERNED_MIGRATION`

A governed legacy tranche cannot yet be emitted because the accepted repository lacks the schema/methodology/registry state required to validate the canonical records that a migration batch must contain.

This block is methodological, not evidence-erasing. Existing legacy material may still be inventoried and staged, but it must remain explicitly non-accepted and must not advance coverage until the governing architecture is accepted or an equivalent accepted contract exists.

## Next migration frontier

The next executable frontier is dependency-driven:

1. detect acceptance of a governing schema/methodology/predicate-registry foundation on `main`;
2. locate a durable legacy artifact source through project-accessible evidence rather than old chat completion claims;
3. inventory that artifact without treating filenames or summaries as evidence of source reading;
4. choose one bounded tranche whose original source provenance can be checked;
5. verify whether source content was actually read;
6. separate source-grounded evidence from preference-influenced or unsupported synthesis;
7. generate current-model records plus validation and a batch manifest;
8. leave unresolved provenance, identity, or factual conflicts unresolved rather than manufacturing certainty.

Until both the governance gate and artifact-location gate change, no migration coverage advancement is justified.
