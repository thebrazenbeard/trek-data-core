# LIT bootstrap compatibility audit

Status: **proposal-only dependency audit; no literary coverage effect**

Scope is limited to whether the current architecture/admission proposals can support governed literary admission once actual Librarian Source/Work bindings exist. This file does not modify architecture, Source/Work registries, or global methodology.

Current architecture proposal head observed during the latest refresh: `a26b444cd64be25c34cdb46c76721da7aeb777a2` (PR #1).
Current admission-validation successor observed: `1bf5eedb9bebfc5a3c96300263bc7fdc643d1363` (PR #33), stacked on PR #1.

## Compatible elements already present

The proposed `docs/architecture.md` states the canonical flow correctly as:

`SOURCE -> WORK -> LOCAL ENTITY -> EVIDENCE -> ASSERTION -> ACCEPTED RECONCILIATION -> DETERMINISTIC PROJECTION -> QUERY DATABASE`

It explicitly distinguishes a concrete Source from a governed Work and warns against collapsing editions, releases, containers, conversions, or derivative representations simply because they appear to contain the same material. Those properties are necessary for literary ingest.

The proposed Source schema carries useful source-level fields including:

- `source_id`;
- `source_kind`;
- `locator`;
- `content_hash`;
- `source_variant`;
- `provenance_family`;
- `derived_from`.

The proposed Work schema carries:

- `work_id`;
- `title`;
- `medium`;
- `series`;
- `continuity_scope`;
- `parent_work_id`.

These are useful primitives, but they do not by themselves satisfy the literary admission gate below.

## LIT-critical unresolved bootstrap gaps

### 1. `FULL_TEXT_AVAILABLE` is still absent from the proposed processing ladder

At current PR #1 head, `docs/research-methodology.md` still says a work may be discovered, source-bound, structurally indexed, close-read, semantically analyzed, entity-linked, cross-referenced, and audited. It omits the governed `FULL_TEXT_AVAILABLE` state required between `SOURCE_BOUND` and `STRUCTURALLY_INDEXED`.

For literature this omission is material. A Source can be correctly bound to a Work while its readable text is unavailable, partial, corrupted, encrypted, conversion-damaged, or otherwise unsuitable for complete reading. LIT must not infer structural indexing or close reading merely from binding.

Required accepted behavior:

`DISCOVERED -> SOURCE_BOUND -> FULL_TEXT_AVAILABLE -> STRUCTURALLY_INDEXED -> CLOSE_READ -> SEMANTICALLY_ANALYZED -> ENTITY_LINKED -> CROSS_REFERENCED -> AUDITED`

### 2. No explicit Librarian-owned Source<->Work binding record is present

The proposed architecture tree contains independent Source and Work schemas but no explicit Source-to-Work binding schema/registry. Neither `source.schema.json` nor `work.schema.json` contains a required cross-reference establishing governed binding.

For LIT this remains a hard blocker because:

- one Work may have multiple editions/source instances;
- one physical/container Source may contain multiple Works;
- a derivative OPF/TXT/HTML representation may descend from another Source while remaining a distinct source instance;
- a title match cannot substitute for governed binding;
- evidence records must not be the first place where Source<->Work identity is implicitly created.

The binding representation should remain Librarian-owned and exist independently of downstream evidence records.

### 3. Proposed research partition list still omits SHORT

At current PR #1 head, `research/README.md` includes `literature` but still omits the independent `short-treks` / SHORT lane required by the role catalog. This does not directly prevent LIT reading, but it confirms PR #1 has not yet reached the complete governing partition contract.

### 4. Admission validation is partially hardened in PR #33, but remains proposal state and incomplete for LIT

The original PR #1 validator was too weak for governed literary admission. PR #33 materially improves that situation.

Direct inspection of current PR #33 `tools/validate.py` confirms it now:

- validates records against the repository's current JSON-Schema subset;
- rejects unknown record types;
- detects duplicate IDs;
- checks Source `derived_from` references;
- checks Work `parent_work_id` references;
- checks Local Entity → Work references;
- checks Evidence → Source and Evidence → Work references;
- checks Evidence observer-local-entity references;
- checks Assertion → Evidence and supersession references;
- checks reconciliation evidence/supersession references;
- rejects unregistered assertion predicates.

Its regression suite directly tests at least:

- schema-invalid Source rejection;
- dangling Assertion evidence-reference rejection;
- unregistered predicate rejection.

Current PR #33 CI at head `1bf5eedb9bebfc5a3c96300263bc7fdc643d1363` reports success.

This **reduces** the validation blocker, but does not close the LIT admission gate because PR #33:

- is still stacked proposal state, not accepted `main` infrastructure;
- cannot verify a governed Source<->Work binding because no independent binding record/schema exists yet;
- does not implement or enforce the missing `FULL_TEXT_AVAILABLE` coverage tier;
- does not enforce legal coverage-state transitions;
- does not yet establish byte custody, source completeness, container/contained-work correctness, or derivative-family semantics;
- does not by itself close Auditor PR #19's separate reconciliation-application, provenance-projection, and semantic-diff findings.

Therefore a passing PR #33 validator is valuable evidence of implementation progress, but it is not sufficient by itself to admit a literary research batch.

## LIT admission consequence

Even if a byte-backed literary Source appears before corrected infrastructure is accepted, LIT may inspect dependency state but must not claim a governed accepted research batch from proposal infrastructure alone.

Even if corrected infrastructure becomes accepted before a byte-backed literary Source appears, LIT still cannot select a deep-reading batch without accepted Librarian Source/Work binding and complete readable text.

Both gates are independently necessary:

1. **accepted governed research infrastructure**, and
2. **accepted byte-backed Librarian literary Source/Work binding with `FULL_TEXT_AVAILABLE` actually supported**.

Only after both gates pass may the LIT first-source admission checklist be applied to select and execute the first 1–3 substantial Works.
