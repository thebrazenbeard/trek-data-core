# Auditor delta — PR #82 head `733e87c`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #82 `architecture/consolidator-v0.1-integration`
Previous audited head: `d822243bfcf991d56b8089cc1f97ebe1f6627701`
Current audited head: `733e87c4917cba5149109c381f2c63a2652e0d46`
Workflow: `validate-core` run `32076742200` — FAILURE

## Delta scope

Four commits after `d822243`, changing:

- `schema/projection-manifest.schema.json`
- `tools/build_projection.py`
- `tools/test_build_projection.py`
- `tools/test_contract_alignment.py`

This is substantive deterministic projection/compiler work. The validator implementation from `d822243` is unchanged in this delta.

## Confirmed compiler progress

### 1. Assertion disposition and projection status are now separate axes

The compiler derives effective assertion disposition independently from projection status. Only effectively ACCEPTED assertions enter active facts/contested/unresolved partitions. Missing projection status fails closed to UNRESOLVED. Worker-authored `proposed_projection_status` remains preserved but non-authoritative.

This materially implements Director #72's central distinction.

### 2. Typed scope decisions are applied without mutating worker scope

Assertion scope resolutions can coexist by governed key and are materialized as `resolved_scope` plus decision IDs while original worker `scope` remains intact. The updated tests now use actual governed IDs such as `CONTINUITY_SCOPE` and `TIMELINE_SCOPE`, resolving the previous test/registry mismatch.

### 3. Identity links are emitted as typed relations, not a generic resolved-global rewrite

Accepted executable ENTITY_LINK decisions require an ACCEPTED IDENTITY_RELATION predicate and produce traceable `projection_relation` rows plus decision IDs. The compiler does not currently collapse local entities into a single `resolved_entity` bucket. This is the correct non-merging direction under #61.

The current real registry has no ACCEPTED identity predicate, so the negative test correctly verifies that ACCEPTED SAME_AS using an EXPERIMENTAL predicate fails closed.

### 4. Canonical output set is now explicit and complete at the manifest level

The compiler deterministically emits all required #76 outputs:

- entities.jsonl
- facts.jsonl
- relations.jsonl
- contested.jsonl
- unresolved.jsonl
- provenance.jsonl
- assertion_history.jsonl
- reconciliation_history.jsonl

The projection-manifest schema requires each file and requires role/hash/count for each, with no undeclared output keys inside the canonical `outputs` object. Empty files are emitted rather than omitted.

### 5. Governing/input identity is substantially improved

Manifest/input identity now includes:

- research head
- reconciliation head
- schema version
- methodology version
- compiler commit
- predicate-registry hash
- scope-key-registry hash
- deterministic logical-input-records hash
- accepted reconciliation-history hash

`projection_hash` is derived from the hashes of the complete canonical output set rather than from raw database bytes or only active facts.

Source/Work/binding registry identity remains necessarily incomplete until #65 is implemented.

### 6. Provenance observability is substantially improved

For each assertion/evidence support edge the compiler preserves full assertion, evidence, Source and Work records; support set; source lineage records; Work parent lineage; subject/object referenced records where applicable; observer local-entity record; effective disposition; projection status; and relevant disposition/status/scope/entity-link decision IDs.

Because full Source/Evidence/Work records are embedded, changes to governed fields such as content hash, source variant, locator, observed payload, frame, epistemic fields, passage fingerprint, Work continuity metadata, etc. become projection-visible when present on the source records.

This is major progress toward AUD-ARCH-003 / Director #76.

## Blocking findings

### AUD-PROJ-EXPERIMENTAL-PROMOTION — CRITICAL

The validator's predicate lifecycle check is based on the **worker-authored assertion.status**, not the reconciled effective disposition.

An assertion using an EXPERIMENTAL predicate is valid while worker status is PROPOSED. An accepted ASSERTION_DISPOSITION can then promote that assertion to effective ACCEPTED. The compiler will place it in an active projection partition because `effective_disposition()` sees ACCEPTED, but neither validator nor compiler re-checks the predicate's projection eligibility against that effective disposition.

This violates #55: EXPERIMENTAL predicates may be collected on non-promoted assertions but must not become accepted/stable projection truth merely through a status change.

Required adversarial regression:

1. PROPOSED assertion using EXPERIMENTAL predicate;
2. accepted ASSERTION_DISPOSITION -> ACCEPTED;
3. optional STABLE projection-status decision;
4. validation/build must fail closed before active projection unless the predicate itself is governed for accepted use.

The same effective-lifecycle check should apply to any predicate whose current lifecycle/projection eligibility is incompatible with the reconciled assertion disposition.

### AUD-PROJ-ASSERTION-SUPERSESSION — HIGH

The compiler computes:

`superseded_assertions = {a.supersedes for every assertion carrying a predecessor}`

without considering the successor assertion's effective disposition.

Therefore a merely PROPOSED or REJECTED successor can suppress an ACCEPTED predecessor from active projection. The new projection test covers only an ACCEPTED successor and therefore does not detect this failure.

Required regression: accepted A + proposed B supersedes A must not deactivate A solely because B exists. Define and test the exact governed condition under which an effective successor becomes the active replacement.

This mirrors the validator finding at `d822243`; the defect now exists in both validation eligibility and projection semantics.

### AUD-PROJ-ENTITY-CARDINALITY — HIGH

The compiler inherits the validator's ENTITY_LINK active key:

`(ENTITY_LINK, subject_type, subject_id, relation_predicate)`

so one subject cannot have two active targets under the same relation predicate.

#61 does not define singleton target cardinality, and predicate metadata has no cardinality contract. Do not make this a universal identity invariant. A relation such as a future MERGED_FROM can naturally require multiple targets.

This finding remains open from `d822243` and now constrains compiler execution as well.

### AUD-PROJ-WORK-SCOPE-EFFECT — HIGH

#61 permits SCOPE_RESOLUTION subjects of WORK, LOCAL_ENTITY, or ASSERTION.

The compiler materializes:
- LOCAL_ENTITY scopes on `entities.jsonl`;
- ASSERTION scopes on active assertion rows;
- subject scopes on an active assertion when that assertion's subject happens to be the scoped Work/Local Entity.

But there is no canonical Work-state output row. A valid accepted scope resolution targeting a Work can therefore have no materialized current-state effect if no active assertion uses that Work as its subject. It survives only in reconciliation history/input identity.

That is insufficient for an accepted executable reconciliation decision whose semantic effect is supposed to be observable. Either materialize governed Work projection state or explicitly define how every Work scope decision is represented in canonical current-state/provenance output.

Required regression: a Work-targeted accepted scope resolution with no Work-subject assertion must still alter an appropriate current-state canonical output, not merely history.

### AUD-PROJ-PREDICATE-USELEVEL — HIGH / inherited

The compiler now creates `ASSERTION_PREDICATE` relation rows for every active typed-reference assertion. The registry has semantic_class but still lacks #55's explicit predicate use-level/scope contract distinguishing research assertion, evidence-description, reconciliation relation, or governed multi-level use.

Until that field/contract exists, the compiler should not infer that all typed-reference assertions belong in the same canonical relation surface merely because the object is referential. This is especially important where a predicate may be valid as an assertion descriptor but not as a first-class domain relation.

### AUD-PROJ-BINDING-PROVENANCE — BLOCKED, not implementation fault yet

#76 requires Source↔Work binding provenance once #65 exists. No Librarian-owned binding implementation exists, so the compiler cannot yet include it. AUD-ARCH-003 cannot be fully closed until that dependency lands and projection provenance includes binding identity/scope/status/supersession.

## Test/CI observations

- Contract tests now use governed scope keys, which is correct.
- `test_build_projection.py` still contains a provenance assertion for `p['local_entity_record']`, while the compiler exposes the assertion subject as `subject_record` and observer separately as `observer_local_entity_record`. The contract-alignment test uses `subject_record`. This intra-suite naming mismatch is one likely red-test source and should be normalized to the governed provenance shape rather than patched inconsistently.
- Local clone/test execution was attempted independently but the execution environment has no outbound DNS/network access to GitHub, so exact branch test reproduction outside GitHub Actions was unavailable. The GitHub Actions run itself is confirmed failed.

## Original finding status at this head

- **AUD-ARCH-001 validation:** PARTIAL, materially improved; inherited cardinality/supersession/predicate-effective-lifecycle findings remain.
- **AUD-ARCH-002 reconciliation application:** **PARTIAL / major progress**, no longer the original no-op compiler. Still blocked by effective predicate lifecycle, supersession semantics, ENTITY_LINK cardinality, and Work scope observability.
- **AUD-ARCH-003 canonical provenance/manifest:** **PARTIAL / near structural closure absent #65**, with required output/hash/count/pins and rich provenance now present. Binding provenance remains blocked; semantic gaps above also affect projection correctness.
- **AUD-ARCH-004 semantic diff:** OPEN; diff implementation did not change in this tranche.
- Derived database/search trust chain remains downstream of a verified canonical bundle and current diff semantics.

## Exact next frontier

1. Close effective predicate-lifecycle promotion hole.
2. Correct assertion-supersession activation semantics in validator and compiler.
3. Govern/fix identity relation cardinality.
4. Ensure Work-targeted scope decisions always materialize semantically.
5. Resolve predicate use-level typing before treating all typed objects as canonical relations.
6. Normalize the provenance test field mismatch.
7. Then move semantic diff and canonical-bundle verifier/derived consumers; rerun full integrated CI and re-audit the exact green head.

No merge, assertion acceptance, predicate acceptance, identity reconciliation, accepted-state mutation, or protected effect performed.
