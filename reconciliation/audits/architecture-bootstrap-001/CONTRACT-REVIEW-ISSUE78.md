# Auditor contract review — Director issue #78

Date: 2026-08-17
Role: AUDITOR
Contract: Director #78 — verified derived-projection consumers
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`

## Disposition

**CONFIRMED / IMPLEMENTATION PENDING.**

Issue #78 correctly formalizes the trust-boundary defects independently found in Auditor reviews of SQLite PR #68, PostgreSQL PR #71, and graph/search PR #74.

The contract's central rule is necessary: deterministic derived output is not trustworthy if the adapter merely copies `manifest.projection_hash` from an unverified directory. A shared verifier must establish that the exact canonical JSONL bytes, declared hashes/counts, partition/status invariants, and aggregate projection hash agree before any derived backend consumes them.

## Mapping to prior Auditor findings

The contract directly closes design ambiguity around these previously observed defects:
- arbitrary claimed projection hash accepted over unrelated/tampered files;
- missing per-output hash/count verification;
- facts/contested/unresolved partition labels trusted without status validation;
- derived builder identity conflated with upstream compiler identity;
- no exact derivation receipt for imported canonical bytes;
- SQLite replacing/deleting prior target before a new build is fully validated;
- PostgreSQL literal/session behavior insufficiently specified for hostile strings;
- graph/search consuming an unverified canonical directory;
- adapters silently representing only a subset of canonical outputs without a versioned imported-surface contract.

These are one shared architectural problem, not independent backend quirks.

## Positive contract properties

#78 correctly requires:
- one shared deterministic verifier instead of divergent backend copies;
- manifest-schema validation;
- complete #76 output-set verification;
- exact file hash + record-count recomputation;
- governed aggregate projection-hash recomputation;
- partition/status invariants;
- fail-closed malformed/duplicate/contradictory structural input handling;
- separate derived-tool/schema identity;
- verified derivation receipts;
- versioned imported-surface declarations;
- SQLite atomic replacement after success;
- PostgreSQL file generation separated from execution;
- structural-only graph/search semantics and no downstream semantic repair.

This is consistent with the Project rule that the evidence ledger/canonical logical projection is authoritative and all database/search forms are rebuildable outputs.

## Current implementation search

Fresh repository search on 2026-08-17 found no shared `verify_projection` or equivalent verified-upstream implementation. Current PRs #68/#71/#74 therefore remain useful prototypes but do not satisfy #78.

They should not each independently invent a verifier. Implement the shared verifier after #76 canonical manifest/provenance semantics are corrected, then make all derived consumers depend on the same verified contract.

## Required Auditor re-open trigger

Re-audit when a proposal adds the shared verifier or when PR #82/successor integrates #76/#78. Tests must include #78's hostile/tampered input cases and prove failed SQLite rebuild preserves a prior known-good target.

No backend execution, deployment, merge, or protected effect performed.
