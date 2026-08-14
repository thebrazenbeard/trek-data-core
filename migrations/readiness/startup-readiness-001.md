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

## Migration gate result

Result: `BLOCKED_FOR_GOVERNED_MIGRATION`

A governed legacy tranche cannot yet be emitted because the accepted repository lacks the schema/methodology/registry state required to validate the canonical records that a migration batch must contain.

This block is methodological, not evidence-erasing. Existing legacy material may still be inventoried and staged, but it must remain explicitly non-accepted and must not advance coverage until the governing architecture is accepted or an equivalent accepted contract exists.

## Next migration frontier

After an accepted schema/methodology/predicate-registry foundation exists:

1. inventory candidate legacy Trek research artifacts without treating filenames or old completion claims as evidence;
2. choose one bounded tranche whose original source provenance can be checked;
3. verify whether source content was actually read;
4. separate source-grounded evidence from preference-influenced or unsupported synthesis;
5. generate current-model records plus validation and a batch manifest;
6. leave unresolved provenance, identity, or factual conflicts unresolved rather than manufacturing certainty.

Until that gate changes, no migration coverage advancement is justified.
