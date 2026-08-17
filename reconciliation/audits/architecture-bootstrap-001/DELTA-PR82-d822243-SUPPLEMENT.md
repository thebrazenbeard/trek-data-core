# Auditor supplement — PR #82 head `d822243`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Audited head: `d822243bfcf991d56b8089cc1f97ebe1f6627701`
Companion audit: `DELTA-PR82-d822243.md`

## Scope

This is an append-only supplement to the concurrently created primary successor audit. It does not repeat that file's confirmed findings on ENTITY_LINK cardinality, inactive-successor assertion suppression, predicate use-level metadata, governed scope-key fixture drift, or current architecture closure state.

It records additional issues found in the same exact head.

## SUP-PR82-001 — HIGH — DEPRECATED predicates cannot remain historically readable

Director #55 requires DEPRECATED/SUPERSEDED predicate historical use to remain readable while new assertions use the successor. Compiler/migration must not silently rewrite historical predicate identity.

Current `validate_predicate_assertion()` rejects every assertion whose current registry entry is DEPRECATED with the rule that deprecated predicates may not be used for new assertion admission.

The repository validator has no deterministic distinction between:
- a new assertion attempting to use a deprecated predicate; and
- an immutable historical accepted assertion that was valid under an earlier predicate-registry state.

Therefore a future registry transition ACCEPTED -> DEPRECATED can make previously valid repository history fail current CI unless historical records are rewritten, which #55 forbids.

`batch-manifest.schema.json` currently pins only generic `schema_version`; it does not pin predicate-registry version/hash or an equivalent admission/migration receipt sufficient to reconstruct predicate validity at acceptance time.

**Required correction:** define historical-validation context. A versioned batch/admission receipt, explicit migration context, or equivalent deterministic mechanism must preserve old predicate identity/readability while rejecting genuinely new use after deprecation.

## SUP-PR82-002 — HIGH — accepted semantic decisions do not generally require rationale

Director #61 says every ACCEPTED semantic reconciliation decision must remain traceable to evidence/provenance and method and states that empty reason/method or untraceable semantic changes are invalid.

Current schema requires nonempty `method` and nonempty evidence support, but `reason` remains optional. The validator requires nonempty reason only when an ACCEPTED decision supersedes another decision.

A first accepted ENTITY_LINK / ASSERTION_DISPOSITION / ASSERTION_PROJECTION_STATUS / SCOPE_RESOLUTION can therefore be admitted with no reason/rationale field.

**Required correction:** either require nonempty `reason` (or a separately governed rationale field) for every ACCEPTED semantic decision, or explicitly supersede the current #61 rationale requirement. Do not infer rationale from payload values.

## SUP-PR82-003 — HIGH — scope key is governed, resolution value is not

`registry/scope_keys.json` correctly governs key names and subject domains, but each `payload.resolution` remains unconstrained JSON. Director #61 requires deterministic typed semantic decisions; moving free-form semantics from `resolution_key` into `resolution` does not close that requirement.

An accepted TIMELINE_SCOPE, CONTINUITY_SCOPE, NARRATIVE_FRAME, or TEMPORAL_SCOPE decision can currently carry arbitrary object/string/list meaning with no key-specific validation contract.

This independently agrees with the Director implementation delta already appended to #61.

**Required correction:** each governed scope key needs a canonical value contract sufficient for deterministic validation and projection: enum/schema, literal/reference mode, allowed typed-reference domain, or equivalent.

## SUP-PR82-004 — CRITICAL TEST ORACLE SPLIT — legacy projection suite certifies superseded compiler semantics

`tools/test_build_projection.py` remains fully green in run `32076498604`, but it is a regression oracle for the old compiler contract. It still constructs/expects:
- assertion records without required `subject_type`;
- worker `projection_status` as authoritative;
- raw reconciliation `value`;
- obsolete `ASSERTION_STATUS`;
- generic ENTITY_LINK -> global `resolved_entity` collapse;
- opaque whole-scope replacement;
- accepted OTHER history.

The newer contract-alignment tests simultaneously require the incompatible #61/#72 model.

This creates two executable semantic authorities on one branch. A correct compiler rewrite cannot satisfy both.

**Required correction:** migrate or retire the legacy semantic expectations during the compiler rewrite. Retain only still-valid invariants such as determinism, worker-record immutability, and fail-closed partitioning. Do not weaken the corrected contract tests to preserve obsolete behavior.

## SUP-PR82-005 — LOW/MEDIUM — legacy validator tests are stale after correct hardening

Current CI contains three failures that do not indicate missing validator enforcement:

1. `test_batch_hash_and_valid` builds an assertion without the now-required `subject_type`; its supposedly valid fixture is invalid and its precomputed batch hash must be recomputed after correction.
2. `test_worker_cannot_own_source_work` likewise contains the stale assertion and expects the old batch-local error phrase, while current validator correctly emits partition-wide authoritative Source/Work ownership errors.
3. `test_cross_subject_supersession_is_rejected` correctly receives validation failure for a different active key but asserts the older substring `different subject`.

**Required correction:** update fixtures/assertions, recompute hashes, and assert semantic invariants rather than obsolete wording.

## Existing companion findings endorsed

The companion `DELTA-PR82-d822243.md` correctly identifies additional current blockers:
- ENTITY_LINK one-target-per-predicate cardinality is invented, not governed;
- any assertion successor currently suppresses its predecessor for projection eligibility regardless of successor effective disposition;
- predicate usage-level/scope metadata remains absent;
- the direct compiler scope fixture still uses ungoverned key `continuity` rather than `CONTINUITY_SCOPE`;
- Librarian positive Source/Work ownership surface still does not exist.

The assertion-supersession case is especially important: a PROPOSED or REJECTED successor must not automatically deactivate an ACCEPTED predecessor merely because it carries a lineage pointer, absent an explicit governed rule establishing that effect.

## Current interpretation of run 32076498604

The branch is red for useful reasons. Most original catastrophic admission-validation holes are now closed; red contract tests mainly expose the unchanged compiler/provenance/diff stack. The stale legacy tests above should be repaired so red/green state maps cleanly to actual contract compliance.

No merge, accepted-state mutation, predicate lifecycle change, reconciliation acceptance, or protected effect is performed by this supplement.
