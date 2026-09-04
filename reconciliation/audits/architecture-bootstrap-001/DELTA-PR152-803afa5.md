# Auditor review — predicate usage-level PR #152 @ `803afa5`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #152 `architecture/predicate-usage-levels-v0.1`
Audited head: `803afa5e3bb527641211209115d05de383b9960e`
Base: PR #82 integrated architecture head `407ee4ca59101bdacfad0e4a1c2097687f848555`
CI: `validate-core` run `32079180267` — SUCCESS
Director contract: #55

## Disposition

**SUPPORTED / SUBSTANTIALLY IMPLEMENTS THE REMAINING PREDICATE USAGE-LEVEL GAP, WITH CONTRACT-COHERENCE FOLLOW-UPS.**

PR #152 adds an explicit `usage_levels` axis to every predicate and enforces the two currently executable contexts:
- `RESEARCH_ASSERTION` at assertion admission and active compiler projection;
- `RECONCILIATION_RELATION` for ENTITY_LINK identity semantics.

It also correctly moves accepted `MAPS_TO` to `EXTERNAL_CROSSWALK` with `CONTEXT_ONLY` projection eligibility rather than allowing it as an ordinary research assertion, and keeps all current identity predicates EXPERIMENTAL/reconciliation-only.

The core anti-leak tests are meaningful and the full integrated workflow is green on the exact audited head.

No predicate lifecycle promotion, crosswalk acceptance, reconciliation acceptance, merge, or protected effect is performed by this audit.

## Positive controls confirmed

### Context leakage is blocked

Current tests require:
- MAPS_TO rejected as a research assertion;
- SAME_AS rejected as a research assertion;
- CLAIMS rejected as an ENTITY_LINK predicate;
- an explicitly multi-level synthetic predicate can be valid in both declared contexts;
- direct compiler ENTITY_LINK validation rejects identity semantics lacking `RECONCILIATION_RELATION` usage.

The validator also rejects unknown/duplicate/empty/unsupported usage-level metadata and includes `usage_levels` in required predicate metadata.

### Registry identity is versioned

Predicate `registry_version` advances from `0.2.0` to `0.2.1`, and the existing canonical build identity already hashes the predicate registry. The context metadata therefore participates in deterministic input identity.

### Current crosswalk predicate no longer pretends to be a story assertion

`MAPS_TO` is now:
- semantic class `CROSSWALK_RELATION`;
- usage `EXTERNAL_CROSSWALK`;
- `CONTEXT_ONLY` projection eligibility;
- explicitly described as not an ordinary research assertion / not SAME_AS.

This is the correct direction for later #65 integration.

## PRED-USAGE-001 — HIGH — accepted predicate examples require an Assertion subject type the schema cannot represent

The governed Assertion schema permits only:
- SOURCE
- WORK
- LOCAL_ENTITY
- ASSERTION

as `subject_type`.

It does **not** permit EVIDENCE.

Several ACCEPTED predicates are nevertheless defined/exampled as relations whose subject is Evidence:
- `DEPICTS`: example says `Evidence depicts a referenced local entity.`
- `SUPPORTS`: example says `Evidence supports an assertion.`
- `CONTRADICTS`: example says `One evidence record contradicts an assertion.`

Their predicate metadata says `subject_types:["ANY"]`, but the Assertion record schema is the narrower executable domain. An Evidence-subject research assertion cannot be constructed without failing schema validation.

This is a contract-coherence problem, not merely documentation wording, because these predicates are ACCEPTED and `RESEARCH_ASSERTION`-scoped.

The project must choose one governed interpretation:
1. if Evidence really is allowed as an Assertion subject, explicitly revise #52/assertion schema and all reference/projection/diff rules; or
2. if evidence-to-assertion relations belong in a separate evidence-annotation/support structure, move those predicates to the appropriate usage level/record type and rewrite their examples/subject types; or
3. if ordinary research assertions are intended to *state that* evidence supports/depicts/contradicts something while using another allowed subject, rewrite definitions/examples so the executable record shape is unambiguous.

Do not leave accepted registry examples describing impossible records.

Required negative/positive fixture: every ACCEPTED predicate example should be mechanically representable by at least one schema-valid record in each declared executable usage level.

## PRED-USAGE-002 — MEDIUM/HIGH — EXTERNAL_CROSSWALK usage is governed metadata but not yet an executable context

PR #152 correctly prevents MAPS_TO from being used at the research-assertion layer, but the integrated PR #82 architecture still has no governed `external_crosswalk` record type/schema/validator path. PR #125 defines the future Librarian crosswalk surface separately and is still contested before integration.

Therefore `EXTERNAL_CROSSWALK` is currently a **declared context**, not an executable validated predicate context.

This is acceptable as staged governance if described accurately. It is not yet evidence that crosswalk-level predicate usage is enforced end-to-end.

When corrected PR #125/successor is integrated:
- external-crosswalk records using predicate semantics must validate `EXTERNAL_CROSSWALK` usage explicitly;
- research assertions must remain unable to consume MAPS_TO merely because the predicate is ACCEPTED;
- crosswalk lineage/status/candidate semantics remain separate from assertion projection.

Until then, #152 closes the research/reconciliation leakage gap but only prepares the crosswalk side.

## PRED-USAGE-003 — HIGH — direct compiler assertion path checks usage level but not predicate lifecycle/projection eligibility

`build_logical_projection()` now independently checks active assertions have a predicate declaring `RESEARCH_ASSERTION` usage.

It does **not** independently require that active assertion predicate be lifecycle `ACCEPTED` / projection-eligible.

Example bypass for an unvalidated direct caller:
- assertion immutable status = ACCEPTED;
- predicate = current EXPERIMENTAL `CAUSES`;
- CAUSES declares `RESEARCH_ASSERTION` usage;
- the new direct compiler usage check passes;
- direct build can therefore partition/project the assertion even though repository admission validation would correctly reject an ACCEPTED assertion using the EXPERIMENTAL predicate.

The CLI path is currently safe because `build_projection.py` runs repository admission validation before compiling. The pure compiler function is weaker than the accepted semantic contract and is used directly by tests/other Python consumers.

#55 says experimental predicates must not silently become accepted projected semantics. The compiler's independent fail-closed check should therefore validate both:
- allowed usage level; and
- lifecycle/projection eligibility appropriate to the effective assertion state.

Add direct-function regression: an effectively ACCEPTED assertion using EXPERIMENTAL CAUSES raises, even if caller bypasses repository validator.

## PRED-USAGE-004 — MEDIUM — registry validation permits incoherent projection eligibility for non-research predicates

For an ACCEPTED predicate without `RESEARCH_ASSERTION` usage, registry validation currently permits either:
- `CONTEXT_ONLY`; or
- `ACCEPTED_ASSERTION_ALLOWED`.

Assertion admission separately prevents non-research predicates from being used as assertions, so current MAPS_TO is safe because it uses `CONTEXT_ONLY`.

The metadata rule is nevertheless internally permissive: a future EXTERNAL_CROSSWALK-only predicate can declare `ACCEPTED_ASSERTION_ALLOWED` without the registry loader treating that as inconsistent.

Unless a separately governed meaning for `ACCEPTED_ASSERTION_ALLOWED` outside research assertions is introduced, non-research-only accepted predicates should require context-only/non-assertion projection eligibility.

This keeps registry metadata self-consistent rather than relying on a later validator to make contradictory fields harmless.

## PRED-USAGE-005 — EXTERNAL / still open — historical DEPRECATED readability is not solved by #152

This PR intentionally addresses usage-level governance and should not be faulted for not redesigning predicate migration history.

However, the separate #55 Auditor finding remains open: the current repository validator rejects any assertion whose **current** registry entry is DEPRECATED, with no admission-time registry/migration context to distinguish a historical valid assertion from a new forbidden use.

Do not mark the entire #55 predicate-governance program complete solely because the usage-level field has landed. Historical predicate readability still needs a deterministic version/migration/admission receipt mechanism before any ACCEPTED predicate is actually deprecated.

## Current exact-head result

- explicit usage-level metadata: **CONFIRMED**;
- research assertion vs reconciliation identity leakage: **BLOCKED correctly**;
- MAPS_TO ordinary research leakage: **BLOCKED correctly**;
- current CI: **GREEN**;
- usage-level gap from prior Auditor review: **SUBSTANTIALLY RESOLVED**;
- accepted predicate/schema example coherence: **OPEN**;
- external-crosswalk execution context: **PREPARED, not integrated**;
- direct compiler lifecycle fail-closed behavior: **OPEN**;
- historical DEPRECATED readability: **SEPARATE #55 blocker still open**.

## Exact next frontier

1. Reconcile ACCEPTED predicate examples/subject domains with the governed assertion/evidence record model.
2. Add lifecycle/projection-eligibility checks to the pure compiler path for effectively active research assertions.
3. Tighten non-research predicate projection-eligibility metadata coherence.
4. Integrate EXTERNAL_CROSSWALK enforcement only with the corrected #125/successor Librarian contract.
5. Keep historical deprecation/migration context as a separate required #55 follow-up.
6. Re-audit exact successor bytes; do not promote any current EXPERIMENTAL identity predicate merely to demonstrate the new context machinery.

No accepted Trek assertion, identity relation, crosswalk, or protected effect is created by this audit.
