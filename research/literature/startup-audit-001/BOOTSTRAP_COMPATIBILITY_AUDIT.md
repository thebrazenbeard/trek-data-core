# LIT bootstrap compatibility audit

Status: **proposal-only dependency audit; no literary coverage effect**

Scope is limited to whether the current `architecture/v0.1-bootstrap` proposal can support governed literary admission once actual Librarian Source/Work bindings exist. This file does not modify architecture, Source/Work registries, or global methodology.

Observed architecture proposal head during this audit: `4b771b28406e1b2f41d93f5787e1978e98c6e432`.

## Compatible elements already present

The proposed `docs/architecture.md` now states the canonical flow correctly as:

`SOURCE -> WORK -> LOCAL ENTITY -> EVIDENCE -> ASSERTION -> ACCEPTED RECONCILIATION -> DETERMINISTIC PROJECTION -> QUERY DATABASE`

It also explicitly distinguishes a concrete Source from a governed Work and warns against collapsing editions, releases, containers, conversions, or derivative representations simply because they appear to contain the same material. Those properties are necessary for literary ingest.

The proposed Source schema already carries useful source-level fields including:

- `source_id`;
- `source_kind`;
- `locator`;
- `content_hash`;
- `source_variant`;
- `provenance_family`;
- `derived_from`.

The proposed Work schema already carries:

- `work_id`;
- `title`;
- `medium`;
- `series`;
- `continuity_scope`;
- `parent_work_id`.

These are useful primitives, but they do not by themselves satisfy the literary admission gate below.

## LIT-critical unresolved bootstrap gaps

### 1. `FULL_TEXT_AVAILABLE` is still absent from the proposed processing ladder

Current `docs/research-methodology.md` says a work may be discovered, source-bound, structurally indexed, close-read, semantically analyzed, entity-linked, cross-referenced, and audited. It still omits the governed `FULL_TEXT_AVAILABLE` state required between `SOURCE_BOUND` and `STRUCTURALLY_INDEXED`.

For literature this omission is material. A Source can be correctly bound to a Work while its readable text is unavailable, partial, corrupted, encrypted, conversion-damaged, or otherwise unsuitable for complete reading. LIT must not infer structural indexing or close reading merely from binding.

Required accepted behavior:

`DISCOVERED -> SOURCE_BOUND -> FULL_TEXT_AVAILABLE -> STRUCTURALLY_INDEXED -> CLOSE_READ -> SEMANTICALLY_ANALYZED -> ENTITY_LINKED -> CROSS_REFERENCED -> AUDITED`

### 2. No explicit Librarian-owned Source<->Work binding record is present

The proposed tree contains independent Source and Work schemas but no explicit Source-to-Work binding schema/registry. Neither `source.schema.json` nor `work.schema.json` contains a required cross-reference establishing governed binding.

For LIT this is a hard blocker because:

- one Work may have multiple editions/source instances;
- one physical/container Source may contain multiple Works;
- a derivative OPF/TXT/HTML representation may descend from another Source while remaining a distinct source instance;
- a title match cannot substitute for governed binding;
- evidence records must not be the first place where Source<->Work identity is implicitly created.

The binding representation should remain Librarian-owned and exist independently of downstream evidence records.

### 3. Proposed research partition list still omits SHORT

Current `research/README.md` includes `literature` but omits the independent `short-treks` / SHORT lane required by the role catalog. This does not directly prevent LIT reading, but it remains evidence that the proposal has not yet reached the complete governing partition contract and therefore should not be treated as accepted infrastructure.

### 4. Current validator cannot enforce literary admission integrity

Direct inspection of proposed `tools/validate.py` confirms the limitation rather than relying only on coordination commentary.

The validator currently:

- parses JSON/JSONL;
- checks duplicate IDs for known record types;
- requires assertions to contain an `evidence` field;
- requires an accepted reconciliation decision to contain a method.

It does **not** currently:

- validate records against the repository JSON Schemas;
- verify that an Evidence `source_id` actually resolves to an existing Source;
- verify that an Evidence `work_id` actually resolves to an existing Work;
- verify a governed Source<->Work binding because no such independent binding record exists yet;
- validate predicates against the governed predicate registry;
- enforce worker partition boundaries;
- verify batch manifest/hash completeness;
- enforce legal coverage transitions such as `SOURCE_BOUND -> FULL_TEXT_AVAILABLE -> STRUCTURALLY_INDEXED -> CLOSE_READ`;
- distinguish proposal/legacy/discovery IDs from accepted Source/Work identity.

Therefore `VALIDATION PASSED` from the current script cannot by itself establish that a literary batch is admissible under the Project method.

Director issue #15 independently records the same broader requirement for stronger validation, calibration fixtures, and complete projection provenance identity.

For LIT specifically, a governed batch must fail closed if Source/Work references are dangling, if a source binding is proposal-only, or if an illegal coverage jump skips `FULL_TEXT_AVAILABLE` or `CLOSE_READ` requirements.

## LIT admission consequence

Even if a byte-backed literary Source appears before the bootstrap proposal is accepted, LIT may inspect dependency state but must not claim a governed accepted research batch from proposal infrastructure alone.

Even if the bootstrap becomes accepted before a byte-backed literary Source appears, LIT still cannot select a deep-reading batch without accepted Librarian Source/Work binding.

Both gates are independently necessary:

1. **accepted governed research infrastructure**, and
2. **accepted byte-backed Librarian literary Source/Work binding**.

Only after both gates pass may the LIT first-source admission checklist be applied to select and execute the first 1–3 substantial Works.
