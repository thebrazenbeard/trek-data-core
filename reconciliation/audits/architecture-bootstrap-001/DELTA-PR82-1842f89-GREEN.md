# Auditor acceptance delta — PR #82 head `1842f89`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `e61dc464d28819fb9ff43ce59ece2b4bb6e51204`
Current audited head: `1842f89c0362bb2866d1963620e91f1692379a42`
Workflow: `validate-core` run `32077893803` — **SUCCESS**

## Delta scope

Two commits change only:

- `.github/workflows/validate.yml`
- `tools/test_build_projection.py`

Production validator/compiler/diff/verifier/derived adapter code is unchanged from the audited preceding implementation heads.

## Confirmed integration-gate progress

The workflow now exercises the actual repository stack end-to-end rather than relying only on handcrafted projection fixtures:

1. run all `tools/test_*.py` regressions;
2. run repository admission validation;
3. build the canonical projection twice using the real compiler;
4. verify both exact compiler-produced directories with the shared verifier;
5. require identical verification receipts and byte-identical canonical bundles;
6. require zero semantic diff for identical projections;
7. build two SQLite databases from the verified canonical output and compare deterministic query snapshots plus receipt/builder/schema metadata;
8. generate and byte-compare two PostgreSQL bundles;
9. generate and byte-compare two graph/search bundles;
10. change research-head input identity while leaving logical corpus bytes unchanged and require input_hash change, projection_hash stability, and zero semantic diff.

This closes the earlier compiler->verifier->derived-adapter integration-test gap at the empty accepted-corpus state. The successful run is meaningful mechanical/reproducibility evidence.

## Test correction confirmed

The provenance test now uses the compiler's governed `subject_record` shape rather than the obsolete `local_entity_record` expectation. The prior intra-suite field mismatch is resolved.

## Acceptance blockers deliberately not closed by this green run

### 1. PROPOSED/REJECTED successor suppression remains untested and production logic is unchanged

The supersession fixture creates `successor = dict(predecessor)` and changes ID/object/supersedes only. Because the predecessor status is ACCEPTED, the successor remains ACCEPTED. Therefore the test proves only that an accepted successor can replace a predecessor.

It does not cover the independently reproduced defect:

- A = ACCEPTED;
- B = PROPOSED or REJECTED, `B.supersedes=A`;
- current compiler/validator still place A in the generic `superseded_assertions` set and suppress A.

Green CI cannot close a case the oracle never constructs.

### 2. Effective EXPERIMENTAL-predicate promotion remains untested and production logic is unchanged

The disposition-promotion fixture uses ordinary accepted `CLAIMS` semantics. It does not create a worker-PROPOSED assertion under an EXPERIMENTAL predicate and then reconcile disposition to ACCEPTED.

The previously reproduced lifecycle hole therefore remains: effective promotion can make experimental semantics active without rechecking predicate eligibility against effective disposition.

### 3. ENTITY_LINK cardinality remains untested

The test suite only checks that an ACCEPTED decision using the repository's EXPERIMENTAL SAME_AS predicate fails. It still does not exercise two distinct targets under one valid identity predicate or a governed predicate cardinality declaration. The current active-decision key remains singleton by implementation rather than contract.

### 4. Work-scope materialization remains untested

Scope tests cover ASSERTION subjects only. There is no fixture proving an accepted Work-targeted scope resolution remains materialized in current canonical state when no active assertion uses that Work as subject.

### 5. First-green diff findings remain untested/unchanged

No `diff_projection.py` production change occurred in this delta. The following remain open:

- provenance-diff non-orthogonality;
- conflict disappearance incorrectly implying CONFLICT_RESOLVED;
- proposition-key-changing explicit supersession aborting instead of conservative remove+add;
- inactive assertion-history changes lacking a representable canonical diff event.

### 6. Verifier cross-record consistency / derived identity dependencies remain open

No verifier or adapter code changed here. Prior findings remain:

- embedded provenance/reference identities are not cross-checked strongly enough;
- derived builder identity does not hash verifier schema dependencies;
- graph relation mapping contract version is hard-coded rather than content-pinned;
- PostgreSQL/graph output directory stale-file hygiene remains weaker than SQLite.

## CI interpretation

Run `32077893803` is the strongest producer CI evidence observed so far and should be retained. It proves the current implementation is internally deterministic and interoperable on the accepted repository's currently empty semantic corpus plus the existing fixture suite.

It does **not** prove semantic correctness for adversarial states absent from that suite.

## Disposition

**CONTESTED / NOT ACCEPTANCE-READY.**

Mechanical integration has advanced from red prototypes to an end-to-end green stack. The remaining blockers are now predominantly semantic/adversarial contract gaps rather than basic plumbing.

## Exact next frontier

Add red regressions for the independently reproduced semantic holes before changing implementation:

1. PROPOSED and REJECTED successor must not deactivate accepted predecessor;
2. EXPERIMENTAL predicate + disposition promotion must fail closed;
3. identity-link multi-target/cardinality behavior must follow an explicit predicate contract;
4. Work-targeted scope resolution must have guaranteed materialized current-state effect;
5. pure status/value/scope/link changes must not manufacture PROVENANCE_CHANGED;
6. contradiction disappearance without explicit governed resolution must not claim CONFLICT_RESOLVED;
7. verifier cross-record identity/support invariants must fail closed.

Then re-run the full end-to-end workflow and independently re-audit the exact successor bytes.

No merge, acceptance decision, predicate promotion, reconciliation acceptance, deployment, database execution, accepted-state mutation, or protected effect performed.
