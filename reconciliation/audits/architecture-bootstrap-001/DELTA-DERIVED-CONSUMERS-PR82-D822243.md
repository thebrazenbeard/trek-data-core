# Auditor delta — PR #82 derived consumers

Date: 2026-08-17  
Role: AUDITOR  
Proposal: PR #82 @ `d822243bfcf991d56b8089cc1f97ebe1f6627701`

## Disposition

**DIRECTOR CONTRACT #78 OPEN.** Derived adapters are deterministic prototypes, not verified consumers of canonical projection bytes.

## Findings

1. SQLite/PostgreSQL/graph-search each trust manifest `projection_hash`; no shared verifier recomputes output hashes/counts/aggregate projection identity.
2. Missing canonical files are treated as empty lists rather than failing closed.
3. Consumers do not validate manifest schema, complete required output set, imported-output contract/version, or retain a verified upstream hash/count receipt.
4. Partition/status invariants are not comprehensively verified.
5. SQLite unlinks the existing target database before successful build/validation, so a failed rebuild destroys the prior known-good target instead of atomically replacing it after success.
6. Derived builder identity is not independently pinned from upstream compiler identity.
7. Imported history/query surface is incomplete without an explicit versioned omission contract.
8. PostgreSQL input is unverified and required hostile literal/session regressions are not yet proven.
9. Graph/search fail-closed relation behavior and structural conflict checks are useful but do not verify upstream canonical bytes.

## Required closure direction

Implement one shared deterministic projection-bundle verifier; require all adapters to call it before output mutation; pin derived-tool/schema/import identities and verified upstream receipt; make SQLite build/validate temporary output then atomically replace; execute #78's full regression set.

No backend execution/deployment, merge, implementation mutation, or protected effect performed.
