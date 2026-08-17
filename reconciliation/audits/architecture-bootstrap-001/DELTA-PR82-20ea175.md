# Auditor delta — PR #82 head `20ea175`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `205544bd93d18815bd56f347c413b972c9d3ee36`
Current audited head: `20ea17557fc2839e75f96900be3e084d77b56536`
Workflow: `validate-core` run `32077162357` — SUCCESS

## Delta scope

Two commits after the first green integrated head add only:

- `tools/projection_bundle.py`
- `tools/test_projection_bundle.py`

No canonical compiler, validator, semantic diff, SQLite/PostgreSQL/graph/search consumer, or workflow integration code changed in this delta.

## Confirmed progress toward Director #78

The new shared verifier is a strong deterministic primitive. It:

- validates manifest structure against `projection-manifest.schema.json`;
- requires exactly the eight #76 canonical outputs in manifest metadata;
- verifies required output files exist and rejects unexpected JSONL files;
- parses every output as canonical object JSONL;
- rejects duplicate stable IDs per output;
- recomputes exact per-file byte hashes and counts;
- recomputes aggregate `projection_hash` from verified output hashes;
- verifies required governance/input pins are present and SHA-256-shaped where applicable;
- enforces facts=STABLE, unresolved=UNRESOLVED, contested={CONTESTED,STRUCTURAL_PARADOX};
- requires active assertion rows to be effectively ACCEPTED and prevents duplicate active assertion IDs across partitions;
- validates basic relation/provenance row types;
- returns a deterministic verified receipt including the exact required-output hash/count set and imported-output contract.

The test suite covers arbitrary aggregate hash, file-hash mismatch, count mismatch, missing output, wrong partition status, stale manifest after output change, and unexpected JSONL output.

This directly addresses much of the previously open shared-verifier contract rather than duplicating trust logic in each backend.

## Blocking findings

### AUD-BUNDLE-001 — CRITICAL — verifier rejects the current compiler's own projection directory

Current `build_projection.py` at the inherited `733e87c` implementation deliberately writes two temporary compatibility aliases into the projection output directory:

- `accepted_reconciliation.jsonl`
- `accepted_assertions.jsonl`

They are explicitly described by the compiler as non-canonical aliases and are not present in manifest `outputs`.

The new verifier computes all `*.jsonl` names in the directory and requires that set to be **exactly** the eight canonical outputs. Therefore the exact directory produced by the current compiler contains two unexpected JSONL files and fails verification.

The verifier tests construct synthetic directories containing only the eight canonical files, so producer CI does not exercise compiler -> verifier interoperability.

Required integration regression:

1. run `build_projection.py` into a fresh directory;
2. immediately call `verify_projection()` on that exact directory;
3. require success.

Resolution options must preserve #78 fail-closed semantics. Prefer removing/moving the compatibility aliases rather than teaching the verifier to ignore arbitrary extra JSONL. If legacy adapters still need aliases, generate them outside the canonical bundle or explicitly version a non-canonical compatibility surface.

### AUD-BUNDLE-002 — CRITICAL — shared verifier is not yet consumed by derived builders

This delta adds the verifier library and tests only. SQLite, PostgreSQL, graph/search builders did not change and therefore still retain their previously audited independent trust behavior.

Director #78 requires one shared verifier **used by all derived consumers**. Existence of a good utility is not the trust boundary until each consumer calls it before importing any projection row.

Required regressions per backend should demonstrate malformed/stale bundles are rejected through the actual builder entry point, not only through direct verifier unit tests.

### AUD-BUNDLE-003 — HIGH — verifier/imported-output contract currently conflates verification with adapter import surface

The receipt sets `imported_output_contract` to all eight REQUIRED_OUTPUTS. That accurately describes what the verifier authenticated, but it does not prove that a particular derived adapter actually imports/materializes all eight surfaces.

#78 requires each adapter to explicitly version/list **its own imported surface**, including intentional omissions. Keep the verifier receipt as a verified-upstream contract, but require backend-specific import-contract metadata rather than allowing every consumer to inherit an implied all-eight import claim.

### AUD-BUNDLE-004 — MEDIUM — builder identity remains external to verifier receipt by design, but must be enforced downstream

The shared receipt pins upstream logical compiler identity. It does not and should not pretend to identify SQLite/PostgreSQL/graph/search transformation code.

This is not a verifier defect, but #78 remains open until each derived artifact records its own adapter schema/version and builder/tool identity alongside this verified upstream receipt.

## Inherited acceptance blockers remain

Nothing in this delta changes the first-green-head findings:

- effective EXPERIMENTAL predicate promotion hole;
- inactive assertion successor suppression;
- ENTITY_LINK cardinality invention;
- Work-scope materialization gap;
- predicate use-level gap;
- provenance-diff orthogonality defects;
- conflict-resolution overclaim;
- supersession fallback and inactive-history diff gaps;
- #65 binding provenance dependency.

## Status update

- **#78 shared verifier primitive:** STRONG PARTIAL.
- **#78 actual derived-consumer trust boundary:** OPEN until all adapters consume it and retain backend-specific build/import receipts.
- **PR #82 overall:** CONTESTED despite green CI.

## Exact next frontier

1. Make canonical compiler output pass the verifier on its exact emitted directory.
2. Wire verifier into SQLite/PostgreSQL/graph/search entry points before any row import.
3. Add backend-specific imported-output contract, adapter version, builder identity, and verified-upstream receipt.
4. Preserve the green verifier adversarial suite while adding compiler->verifier and verifier->backend integration tests.
5. Continue closing the independent semantic findings from `DELTA-PR82-205544b-GREEN.md`.

No merge, database execution, deployment, accepted-state mutation, or protected effect performed.
