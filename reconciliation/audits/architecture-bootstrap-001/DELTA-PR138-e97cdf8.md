# Auditor review — coverage ledger PR #138 @ `e97cdf8`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #138 `architecture/coverage-ledger-v0.1`
Audited head: `e97cdf8722c4f0928e83e70efd2583012bdd27df`
Base proposal: PR #82 integrated architecture
CI: `validate-core` run `32078800275` — SUCCESS
Director contract: #40

## Disposition

**CONTESTED / REWRITE REQUIRED BEFORE COVERAGE INFRASTRUCTURE ACCEPTANCE.**

The branch correctly keeps coverage append-only/proposal-only and attempts to fail closed around missing Source↔Work binding. It also proves useful negative cases such as staging reads not entering accepted numerators and producer-role mismatch not automatically becoming AUDITED.

However, Director exact-head review at predecessor `34343b5...` correctly found that the implementation model itself conflicts with #40 by rebuilding a universal Work-centric ladder. The current `e97cdf...` successor is only two commits later and does not implement that required rewrite. The same architecture-level blockers remain current.

This Auditor record treats the Director's ten findings as upstream review rather than independent corroboration and records additional second-order safety/currentness defects visible on the current exact head.

No coverage event, denominator, Source/Work/binding state, merge, or protected effect is accepted/performed by this audit.

## Director blockers still current on `e97cdf8`

The current code still:
- duplicates DISCOVERED and SOURCE_BOUND as coverage events instead of deriving them from accepted Work/binding owner records;
- uses an ordinal universal `PREDECESSOR` ladder across dimensions with different native units;
- requires `work_id` as universal event subject;
- conflates event lifecycle with semantic effect and lets REJECTED successor suppress prior accepted event;
- uses untyped arbitrary-string basis/producer/integration/audit refs;
- models FULL_TEXT / STRUCTURAL / CLOSE_READ / SEMANTIC through one Work/source ladder rather than native binding/representation/Work units;
- derives one runtime Work denominator instead of accepted content-addressed per-dimension denominator snapshots;
- hardcodes provisional binding-field interpretation;
- trusts caller-supplied producer_role rather than repository/path ownership;
- remains a separate stacked draft while #82/#125 are converging.

Those ten issues require the rewrite described by the Director comment on PR #138 / issue #40.

## Additional Auditor findings

### COV-AUD-001 — CRITICAL — report path publishes coverage from unvalidated records

`coverage_report(records, works=None)` does not call `validate_coverage()` and does not consume a validated state object.

The CLI `report` command likewise calls `coverage_report(records)` directly. The GitHub workflow happens to run `coverage_ledger.py validate` before `coverage_ledger.py report`, so that one shell sequence fails closed. The reporting API/CLI itself does not.

Consequences: a caller can supply an `ACCEPTED` event that has forged producer role, dangling basis refs, invalid schema fields, missing prerequisites, invalid binding/currentness, or other validation failures and still receive it in `active_accepted_event_count` / state counts if the basic status/work fields happen to line up.

Coverage reporting is an accepted-state claim. It must be derived from validated active coverage state, not depend on every caller remembering to run another command first.

**Required correction:** make validation part of report construction, or produce a validated immutable state object that both validation/reporting consume. Invalid records must make report generation fail closed rather than return numerators.

Add regression: invalid ACCEPTED AUDITED event with forged/missing basis cannot be reported even when `coverage_report()` is invoked directly.

### COV-AUD-002 — CRITICAL — SOURCE_BOUND checks raw binding lifecycle, not current active binding state

Current SOURCE_BOUND validation accepts a referenced binding when:
- binding exists;
- `lifecycle == ACCEPTED`;
- `mapping_role == EVIDENCE_BEARING`;
- source/work IDs match.

It does not determine whether that binding is still the **active current** accepted binding after supersession/correction, nor whether an active incompatible CONTESTED binding leaves the mapping unresolved.

PR #125 is already being corrected precisely because raw `lifecycle=ACCEPTED` is insufficient current-state semantics.

Coverage must consume the canonical active Librarian binding-state function/snapshot from the corrected #65 implementation. It must not independently reinterpret raw binding rows.

Otherwise an accepted-but-superseded binding can continue justifying SOURCE_BOUND indefinitely, or an unresolved contested mapping can still appear settled.

### COV-AUD-003 — HIGH — coverage supersession can cross unrelated source/scope contexts

Current supersession validation requires only same `work_id` and same `coverage_state`.

For source-native states, successor/source context is not required to match predecessor/source context. A correction for `FULL_TEXT_AVAILABLE` or `CLOSE_READ` on Source B can supersede an event for Source A so long as Work/state match.

That can silently deactivate unrelated valid coverage when active-event suppression is computed globally by predecessor ID.

Director already requires a semantic active key `(dimension, subject_type, subject_id, canonical_scope_key)` in the rewrite. Supersession must preserve that semantic key/domain unless a separately governed re-scoping operation explicitly says otherwise.

Add regression: correction for binding/representation B cannot supersede A solely because both concern the same Work and dimension.

### COV-AUD-004 — HIGH — prerequisite references are not generally referentially validated

The code checks duplicate prerequisite IDs and later searches active prerequisites only when a dimension has an ordinal predecessor.

It does **not** require every `prerequisite_event_id` to exist.

Examples:
- a DISCOVERED event can carry arbitrary dangling prerequisite IDs and validate because DISCOVERED has no predecessor-state check;
- an event may contain one valid required predecessor plus additional nonexistent prerequisite IDs, and the dangling extras are silently ignored;
- no general prerequisite DAG/cycle validation exists beyond the separate supersession chain.

Coverage provenance must not contain decorative references. Every prerequisite ID must resolve and belong to a dimension/subject/scope relation allowed by the dimension-specific rule.

The rewrite's typed-basis model should include prerequisite references in the same deterministic referential-validation surface.

### COV-AUD-005 — HIGH — correction reason may be empty

For ACCEPTED/REJECTED successor events the validator checks only `isinstance(reason, str)`.

`reason=""` therefore satisfies the correction requirement. The schema also permits empty reason strings.

#40 requires enough identity to reconstruct why coverage changed. A correction/revocation without a nonempty rationale is not reconstructable.

Require `minLength: 1` / nonblank normalized reason on any accepted semantic correction/revocation/supersession that changes current coverage effect.

### COV-AUD-006 — CRITICAL — denominator treats every Work record as accepted inventory

`coverage_report()` builds its denominator with `index_records(records, 'work', 'work_id')` and marks the denominator RESOLVED whenever that dictionary is nonempty.

It does not filter Work lifecycle/status to accepted current registry state.

Once PR #125-style Work records are present, PROPOSED or SUPERSEDED Work candidates can therefore make `denominator_status='RESOLVED'` and inflate `work_denominator` even when no accepted Work registry snapshot exists.

This is a concrete manifestation of the Director's broader denominator-snapshot finding.

Required regression before rewrite acceptance: only PROPOSED Work records present -> `DENOMINATOR_UNRESOLVED`, never RESOLVED count N.

### COV-AUD-007 — HIGH — accepted event authority can be forged by string fields

Director already notes path ownership, but the bypass deserves an explicit adversarial fixture.

Current validator accepts event ownership from caller-supplied strings:
- `producer_role='AUDITOR'` plus any nonempty `audit_ref` can satisfy AUDITED role checks;
- `producer_role='CONSOLIDATOR'` plus any nonempty `integration_ref` can satisfy ENTITY_LINKED/CROSS_REFERENCED ownership checks;
- `basis_refs` are arbitrary strings and are never resolved.

The existing test proves a TNG event cannot self-label AUDITED **while still saying role=TNG**. It does not test the trivial forged-role case.

Required rewrite fixture: a record physically/provenancially owned by a research lane that claims `producer_role='AUDITOR'` must fail even with fake audit_ref. Authority must derive from governed typed provenance/path/accepted audit record, not self-description.

### COV-AUD-008 — HIGH — report/validator do not pin accepted denominator/current registry identity

`registry_head` is optional on events and `coverage_report()` emits no registry/research/reconciliation snapshot identity.

#40 requires every denominator report to identify the accepted registry/head/snapshot that supplied the denominator, and per-dimension snapshots may differ.

Even aside from the universal-denominator model flaw, the current report is not reproducible from its JSON output alone: consumers cannot know which Work registry state produced `work_denominator`.

The Director's required `coverage_denominator_snapshot` must be mandatory input to resolved reports, content-addressed, and included in report identity/output.

### COV-AUD-009 — HIGH — standalone coverage surface is outside common repository admission/projection/diff semantics

The branch adds a separate coverage schema/tool/workflow step rather than integrating `coverage_event` / denominator snapshot records into the common v0.2 record admission and provenance architecture.

That separation is reasonable while the model is still being rewritten, but acceptance-grade coverage eventually needs:
- common schema/path ownership enforcement;
- typed reference resolution against Librarian/research/reconciliation/audit records;
- append/supersede history integrity under the integrated validator;
- deterministic content identity for coverage snapshots/reports;
- semantic diff/currentness visibility for coverage-only corrections.

Coverage need not become a story-fact projection, but it must not remain a validator island whose accepted-state semantics are invisible to the repository's common provenance/diff machinery.

## Positive controls preserved

Useful ideas worth retaining in the rewrite:
- explicit proposal/accepted/rejected history rather than one mutable `done` bit;
- no implicit later-state promotion in reporting;
- SOURCE_BOUND fail-closed when the Librarian binding surface is absent;
- representation type/completeness fields for full-source availability;
- research-role distinction for close read/semantic analysis;
- Consolidator/Auditor ownership intent for integration/audit dimensions;
- separate history count from active accepted current count;
- explicit DENOMINATOR_UNRESOLVED result instead of guessed percentages;
- no accepted coverage events in this proposal.

## Current exact-head result

- #40 conceptual goal: **SUPPORTED**.
- current event schema/native-unit model: **REJECTED / REWRITE REQUIRED**.
- current report numerators safe if API called directly: **NO**.
- current denominator semantics: **UNSAFE**.
- current binding currentness semantics: **UNSAFE / dependent on corrected #65 active state**.
- current CI: **GREEN for rejected model**, not acceptance evidence.
- accepted coverage effect: **NONE**.

## Exact next frontier

Implement the Director rewrite first:
1. derive DISCOVERED from accepted Work snapshot and SOURCE_BOUND from corrected active binding state;
2. use dimension-native typed subjects/scopes instead of universal Work/source ladder;
3. separate lifecycle from ATTAINED/REVOKED/BLOCKED semantic effect;
4. typed/referential producer+basis provenance with path ownership;
5. dimension-specific prerequisite rules and full reference validation;
6. content-addressed denominator snapshots by dimension;
7. make reporting consume validated accepted state only;
8. integrate the corrected coverage records/snapshots into the common v0.2 admission/provenance/diff surface;
9. rerun the Director regression matrix plus the additional Auditor negative fixtures above.

Do not normalize existing staging worker counters into this rejected v0.1 coverage-event model.

No merge, coverage promotion, denominator acceptance, or protected effect performed.
