# Preservation Receipt — TREK_LEGACY_MIGRATION_BATCH_001

Status: **PROPOSAL STAGING ONLY — NOT ACCEPTED CORPUS STATE**

Preserved on branch: `migration/trek-legacy-migration-batch-001`
Current accepted base observed at preservation: `007641c57933dda222489fff56555f6968ff2a53`

## Provenance

This directory reconstructs the durable File Library package `TREK_LEGACY_MIGRATION_BATCH_001` generated on 2026-08-14. The original package manifest is preserved unchanged, including its historical observation of accepted `main` at `d58359a207da89e812d0a0330558c66774ed1241` and its recorded SHA-256 values for the package files and M4/M5/M6 legacy artifacts.

The package content surfaced through File Library retrieval and was copied into this proposal branch. The historical M4/M5/M6 `/mnt/data/...` paths named by the manifest are provenance references only; those historical local bytes were not re-exposed during this preservation pass.

## Current-state correction

The original README's statement that accepted `main` contained only the repository README was accurate to the package's recorded generation context, not to the preservation-time repository state. At preservation time, accepted `main` is `007641c57933dda222489fff56555f6968ff2a53` and contains `README.md` plus the unresolved one-byte top-level file `x`.

Earlier migration readiness work that reported no durable legacy tranche is superseded by this File Library recovery. The recovered batch is migration input, not accepted research state.

## Preserved record surface

- Works: 5
- Sources: 5
- Local entities: 19
- Evidence records: 14
- Assertions: 5
- Migration adjudications: 7
- Coverage promotions: 0
- Whole-source close-read promotions: 0
- Audiovisual viewing claims: 0

## Integrity interpretation

The original manifest's SHA-256 values are preserved as historical integrity claims from the source package. This preservation pass verified the recovered record counts, IDs, reference structure, and explicit zero-coverage semantics against the surfaced package content. It did not independently re-open the historical M4/M5/M6 local byte paths, and therefore does not upgrade their historical hashes into newly observed byte custody.

## Admission blockers

This staging package must not be treated as accepted corpus truth until accepted `main` supplies the governing method/schema/predicate contract, Librarian-owned Source/Work bindings, and governed coverage/admission representation. The Director queue hold remains applicable.
