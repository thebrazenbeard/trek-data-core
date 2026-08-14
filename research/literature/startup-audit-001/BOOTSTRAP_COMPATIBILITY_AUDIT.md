# LIT bootstrap compatibility audit

Status: **proposal-only dependency audit; no literary coverage effect**

Scope is limited to whether current architecture/admission proposals can support governed literary admission once actual Librarian Source/Work bindings exist. This file does not modify architecture, Source/Work registries, validation contracts, coverage semantics, or global methodology.

Current architecture proposal head observed: `a26b444cd64be25c34cdb46c76721da7aeb777a2` (PR #1).
Current admission-validation successor observed: `ec25f6525255fe019b4a51652d353eeb6ecd4844` (PR #33), stacked on PR #1.

## Compatible elements already present

The proposed architecture states the canonical flow correctly as:

`SOURCE -> WORK -> LOCAL ENTITY -> EVIDENCE -> ASSERTION -> ACCEPTED RECONCILIATION -> DETERMINISTIC PROJECTION -> QUERY DATABASE`

It distinguishes a concrete Source from a governed Work and warns against collapsing editions, releases, containers, conversions, or derivative representations simply because they appear to contain the same material.

The proposed Source schema carries useful source-level fields including `source_id`, `source_kind`, `locator`, `content_hash`, `source_variant`, `provenance_family`, and `derived_from`.

The proposed Work schema carries `work_id`, `title`, `medium`, `series`, `continuity_scope`, and `parent_work_id`.

## LIT-critical unresolved bootstrap gaps

### 1. `FULL_TEXT_AVAILABLE` remains absent

At the current PR #1 head, `docs/research-methodology.md` still moves from source-bound directly to structurally indexed. It omits the governed `FULL_TEXT_AVAILABLE` state required by the Project method.

For literature this is material because a correctly bound Source can still be partial, unreadable, encrypted, corrupted, truncated, or conversion-damaged. Binding alone cannot justify structural indexing or close reading.

### 2. No explicit Librarian-owned Source<->Work binding record is present

The proposed architecture still has independent Source and Work schemas but no explicit Source-to-Work binding schema/registry.

That remains a hard literary dependency because one Work may have multiple editions/source instances, one container Source may contain multiple Works, and derivative OPF/TXT/HTML representations must remain distinct lineage-linked Sources rather than implicit independent witnesses.

### 3. Proposed partition declaration remains incomplete

At current PR #1 head, `research/README.md` includes `literature` but still omits the independent `short-treks` / SHORT lane required by the governing role catalog. This does not directly block book reading but confirms the proposal has not yet reached the complete governing partition contract.

### 4. PR #33 materially improves deterministic admission validation

Direct inspection of PR #33 at `ec25f6525255fe019b4a51652d353eeb6ecd4844` confirms it now performs:

- repository schema-subset validation;
- unknown-record rejection;
- duplicate-ID detection;
- Source `derived_from` reference checks;
- Work `parent_work_id` checks;
- Local Entity → Work checks;
- Evidence → Source / Work / observer checks;
- Assertion → Evidence / supersession checks;
- reconciliation evidence/supersession checks;
- governed predicate membership checks;
- batch-manifest hash verification using canonicalized manifest-plus-record material;
- declared record-count verification;
- manifest Work-reference validation;
- manifest source-hash validation against known Source content hashes.

Its current regression suite includes explicit rejection tests for a schema-invalid Source, dangling Assertion evidence, an unregistered predicate, and a bad batch hash. The `validate-core` workflow at this head completed successfully.

This materially reduces the original validator defect. It does **not** close the LIT admission gate because PR #33 remains proposal-only and still does not provide:

- an independent Librarian Source<->Work binding record;
- `FULL_TEXT_AVAILABLE` or governed coverage-transition enforcement;
- byte custody or source-completeness semantics;
- container/contained-work or derivative-family reconciliation;
- resolution of Auditor PR #19's separate deterministic reconciliation-application, provenance-projection, and governed semantic-diff findings.

### 5. Ordered coverage remains a separate admission constraint

Auditor PR #38 records that proposal worker effort can have downstream processing flags while `SOURCE_BOUND=false`, but that vector cannot be imported unchanged into the governed ordered coverage ladder.

For LIT this reinforces the existing distinction between work actually performed and accepted coverage state. A later migrated close read must still be normalized against accepted Source binding and legal coverage transitions.

## Queue control

Director issue #23 is currently open and explicitly pauses new episode/book close-read tranches until the shared admission bottleneck clears. It says workers with no admitted frontier should remain at startup/blocker state and prohibits creating worker-local canonical Source/Work identities, predicate standards, coverage semantics, or validation contracts merely to stay busy.

Issue #14 remains the Librarian-owned dependency-clearing queue. Its latest Director refresh reports no Librarian/source-binding implementation branch or PR and recommends first defining the binding shape, then validating a small hard-case fixture set including literary derivative/container distinctions before broader binding expansion.

This LIT audit therefore stops at dependency verification and preservation. It does not become a substitute architecture or Librarian registry.

## LIT admission consequence

A byte-backed literary Source alone is insufficient while governed infrastructure remains unaccepted.

Accepted infrastructure alone is insufficient while byte-backed Librarian Source/Work binding and complete readable text remain absent.

The first LIT deep batch may begin only after accepted `main` supplies the required governance/schema/coverage mechanism and a Librarian-owned literary Work/Source binding sufficient to establish full readable source availability.
