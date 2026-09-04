# Auditor delta — PR #82 graph/search and provenance-schema successor

Date: 2026-08-17  
Role: AUDITOR  
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`  
Integrated proposal: PR #82 @ `1507db0b3f4ba98255b26fb3a6a80d30028c72b5`  
CI: `validate-core` run `32077506091` — **FAIL** (`70` tests; `10` errors)

## Findings

- four upgraded graph/search tests now expect verified receipt/history/provenance/governed-relation behavior, but builder still stops on its stale `no governed relation row schema exists` guard;
- this head adds a projection-relation schema, so builder/verifier wiring now needs to catch up rather than deleting the fail-closed test surface;
- projection provenance validation is strengthened, but one supposedly-valid verifier fixture is stale and lacks newly required provenance fields; rebuild fixture rather than weaken schema;
- SQLite five-test arity blocker persists unchanged (11 table columns, 12 inserted values);
- PostgreSQL verified-consumer tests remain green.

## #78 status

- shared verifier: strengthened; stale valid fixture needs repair;
- PostgreSQL: supported under current regressions;
- SQLite: mechanical arity blocker;
- graph/search: stronger tests/schema, implementation mapping/verifier wiring still open.

Original AUD-ARCH-001..004 remain resolved.

No implementation mutation, merge, accepted-state mutation, reconciliation acceptance, coverage promotion, deployment, or protected effect performed.
