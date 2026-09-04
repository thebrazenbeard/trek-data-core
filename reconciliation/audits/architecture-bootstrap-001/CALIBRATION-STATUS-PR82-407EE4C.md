# Auditor calibration implementation status — PR #82 `407ee4c`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Integrated proposal: PR #82 head `407ee4ca59101bdacfad0e4a1c2097687f848555`
Calibration contract: Director #43

## Disposition

**SYNTHETIC SEED SUITE IMPLEMENTED / #43 CALIBRATION PROGRAM PARTIAL / REAL TREK FIXTURES CORRECTLY BLOCKED.**

PR #82 materially improves drift control beyond an empty-corpus build. It now runs synthetic adversarial tests alongside validator, reconciliation, projection, diff, provenance, and derived-consumer regressions.

That is meaningful implementation progress. It is not yet equivalent to the full #43 calibration contract.

No real Trek fixture is admitted by this review because accepted Source/Work/Evidence basis still does not exist on `main`.

## Current direct synthetic/adversarial file

`tools/test_adversarial_invariants.py` currently contains five tests:
1. Source-lineage diamond deduplicates without false cycle;
2. same display name does not merge Local Entities;
3. testimony framing survives and worker-proposed STABLE does not promote world-state;
4. input record order does not change logical projection;
5. true Source derivation cycle fails closed.

These are good structural invariants and should remain.

## #43 required synthetic-case coverage map

Status labels below distinguish **COVERED**, **PARTIAL**, and **ABSENT AS A #43 FIXTURE**. A behavior may have ordinary unit coverage without yet satisfying the calibration fixture contract.

### 1. Testimony is not world-state — PARTIAL

Current adversarial test preserves TESTIMONY frame/utterance and prevents worker-proposed STABLE from becoming canonical STABLE without reconciliation.

Missing #43 half: later direct depiction contradicting X and explicit preservation of both the utterance and the contradiction without promoting testimony to world-state.

### 2. Sensor/computer report can be wrong — ABSENT

No dedicated synthetic fixture currently models a sensor/computer report X followed by incompatible direct depiction Y while preserving report provenance.

### 3. Duplicate-source pseudo-corroboration — PARTIAL

Source-lineage diamond test proves transitive lineage deduplication and true-cycle rejection.

It does not explicitly test the epistemic consequence: two downstream Sources from one upstream witness must not count as two independent corroborating witnesses. No witness-count/independence-group fixture currently asserts that distinction.

### 4. Same name, unresolved identity — COVERED

Two Local Entities with the same display label in different Works remain separate and acquire no identity links absent reconciliation.

### 5. Transport duplicate / fork — ABSENT

No synthetic branch/fork fixture currently represents one antecedent with two simultaneously represented continuants while forbidding forced original/fake or SAME_AS collapse.

### 6. Merge with asymmetric memories — ABSENT

No synthetic fixture independently varies biological/memory/social continuity for a merged result.

### 7. Erased alternate branch with retained memory — ABSENT

No synthetic fixture currently preserves retained branch memory without restoring the erased branch as baseline world-state or creating symmetric history.

### 8. Simulation with physical consequence — ABSENT

No synthetic fixture currently preserves simulated frame and baseline physical harm simultaneously.

### 9. Deliberately false institutional record — ABSENT

No synthetic fixture currently demonstrates a false official record producing a real institutional consequence while keeping false causal history false.

### 10. Source metadata/body mismatch — ABSENT IN INTEGRATED #82 SUITE

Proposal/audit candidates exist (#41 and PR #125 fixture material), but they are not yet a #43 synthetic fixture in the integrated suite.

A synthetic version can be implemented immediately without waiting for accepted Trek evidence.

### 11. Container versus contained Works — ABSENT IN INTEGRATED #82 SUITE

PR #125 proposal fixtures exercise Work components / Source cardinality, but the integrated calibration suite does not yet carry a synthetic container-vs-contained/derivative invariant.

### 12. Proposal coverage leakage — NOT ACCEPTANCE-GRADE / EXTERNAL PARTIAL

PR #138 contains a staging-read-does-not-count test, but PR #138's current coverage model is rejected for rewrite under #40 and is not part of the accepted/current integrated #82 calibration surface.

Keep the invariant; migrate it into the corrected coverage model rather than counting the current test as completed calibration.

### 13. Unknown predicate / ontology gap — PARTIAL MECHANIC, NO DEDICATED FIXTURE

The integrated validator/predicate registry fails closed on ungoverned predicate use and preserves CANDIDATE/EXPERIMENTAL lifecycle distinctions.

There is no dedicated #43 fixture proving that evidence requiring an unknown relation remains UNKNOWN/PROPOSED instead of being coerced into the nearest accepted predicate.

### 14. Structural paradox versus insufficient evidence — PARTIAL

Projection tests preserve `STRUCTURAL_PARADOX` as non-STABLE and preserve missing projection status as UNRESOLVED.

They do not supply the paired #43 fixture in which one evidence structure is genuinely incompatible under a pinned scope and another is merely insufficient, proving only the former may receive STRUCTURAL_PARADOX.

### 15. Reconciliation supersession — COVERED MECHANICALLY

Reconciliation/lineage tests exercise accepted decision/assertion supersession, immutable history, active successor application, and diff/history visibility.

This is strong deterministic coverage. It still lacks #43 fixture metadata/version packaging described below.

### 16. Provenance-only correction — COVERED MECHANICALLY

Projection/diff tests change Source provenance while keeping assertion value stable and require canonical provenance difference / `PROVENANCE_CHANGED` visibility.

Again, behavior is covered but not yet packaged as a governed calibration fixture.

## Fixture-governance layer is not implemented

#43 requires each calibration fixture to pin enough state to reproduce and audit it, including:
- fixture ID/version;
- purpose/invariant;
- synthetic vs accepted Trek basis;
- accepted Work/Source/Evidence IDs for real cases;
- schema version;
- methodology version;
- predicate-registry hash;
- compiler/validator version as applicable;
- expected **allowed result set**, not one magical confidence score;
- explicit forbidden outcomes;
- supersession relation when fixture expectations legitimately change.

Current synthetic tests are ordinary Python unit-test functions with hard-coded records. They do not have this separately versioned fixture metadata/manifest layer.

Consequences:
- a test rename/edit can change the oracle without an explicit fixture supersession record;
- schema/method/predicate dependency is inherited implicitly from branch code rather than pinned per fixture;
- expected allowed-result sets and forbidden outcomes are encoded only in test assertions/prose, not inspectable data;
- fixed-real and synthetic fixture governance cannot yet share one reproducible catalog/report.

A calibration system should not require reading Python source to discover what evidence/method/version its oracle assumes.

## Blindness / anti-overfitting status

Positive:
- input-order reversal explicitly tests one irrelevant-detail variation;
- synthetic records use generic fixture identifiers rather than Trek names;
- real Trek candidates have not been frozen prematurely.

Still needed:
- vary irrelevant IDs/names/order/content across more synthetic structural cases;
- separate fixture data from expected oracle metadata where practical;
- for future real Trek fixtures, preserve an Auditor blind evidence-first classification step before comparing expected result;
- explicitly separate source independence group from analysis-pass identity in overlap/drift fixtures, as Director comment on #43 requires.

## Fixed Trek fixture layer

Current candidate real-case sources (#41 DS9 metadata/body, #45 Prodigy segmentation, #47 SFA repeated-analysis independence, plus other proposal candidates listed by #43) remain **candidates only**.

That is correct because accepted `main` still lacks the Source/Work/Evidence records required to pin them.

Do not use proposal titles/transcripts/audit conclusions as the canonical expected oracle merely because they are already available on branches.

The fixed-real layer re-opens only after corrected #65 Librarian state is accepted and exact accepted evidence IDs exist.

## Current #43 status

- synthetic drift testing exists: **YES**;
- full sixteen-case synthetic matrix: **NO**;
- versioned fixture catalog/manifest: **NO**;
- anti-overfitting variation: **PARTIAL**;
- source-independence vs analysis-pass drift fixture: **NO**;
- fixed accepted Trek fixtures: **CORRECTLY BLOCKED**;
- architecture should claim #43 complete: **NO**.

## Exact next frontier

1. Create a versioned synthetic fixture catalog/manifest rather than only Python test functions.
2. Implement the absent/partial #43 cases, prioritizing frame/ontology structures not already exercised by ordinary unit tests:
   sensor fallibility, transport fork, asymmetric merge, erased-branch memory, simulation+physical consequence, false institutional record, metadata/body mismatch, container/contained, unknown predicate, paradox-vs-insufficient, source-independence vs analysis-pass.
3. Keep proposal coverage-leakage fixture on the corrected #40 successor, not the rejected PR #138 v0.1 model.
4. Add a calibration report that shows fixture version, dependencies, expected allowed set/forbidden outcomes, and pass/fail without collapsing semantic ambiguity into one label.
5. Admit fixed Trek cases only after accepted Source/Work/Evidence exists and Auditor performs source-grounded freeze.

No semantic fixture truth, accepted Work/Source/Evidence, merge, or protected effect is created by this audit.
