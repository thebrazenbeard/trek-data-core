# Director Synchronization — 2026-08-17

Role: DIRECTOR  
Authority: coordination proposal only  
Accepted state: `main` @ `007641c57933dda222489fff56555f6968ff2a53`

## Accepted state

Accepted `main` remains authoritative. It still contains only the skeletal accepted Trek repository state plus the unresolved one-byte top-level path `x` added by commit `007641c57933dda222489fff56555f6968ff2a53`.

`x` is tracked as accepted-state drift under issue #90. It has no assigned Trek corpus, governance, schema, registry, coverage, or research meaning. No deletion/revert is authorized here.

No proposal becomes accepted because it exists, is complete, has been audited, or has green CI.

## Governance

PR #4 remains the open governance-only proposal for the four Project-supplied root governance files:
- `TREK_RESEARCH_METHOD.md`;
- `TREK_REPO_PROTOCOL.md`;
- `TREK_ROLE_CATALOG.md`;
- `CHAT_STARTERS.md`.

Head: `6019ff5b96feaf4a1ca4a1d3f0ea95b5ea979b95`.

Prior Director/Auditor custody work supports exact supplied bytes. Governance acceptance/merge remains a protected effect requiring Patrick's explicit authorization.

Closed PR #92 remains preservation/alignment history only and is not an architecture acceptance path.

## Architecture / integrated Consolidator

PR #82 is the sole active integrated architecture implementation surface after topology normalization.

Current exact head: `407ee4ca59101bdacfad0e4a1c2097687f848555`.  
Current recorded workflow: `32078324682` = SUCCESS.

That green run demonstrates substantial implementation progress, but **the current head is not Director-cleared foundation state** because later contract reviews exposed additional requirements that are not in those bytes.

### Substantially implemented on #82

The integrated branch materially implements:
- schema-aware admission validation and typed record references;
- assertion/reconciliation supersession checks;
- separate assertion disposition vs projection epistemic status machinery;
- canonical eight-output logical projection;
- source/evidence/work/entity provenance and lineage;
- governed semantic diff machinery substantially correcting original AUD-ARCH-004 defects;
- shared projection-bundle verification and verified SQLite/PostgreSQL/graph-search consumers;
- synthetic adversarial #43 tests for Source-lineage DAGs/cycles, local-name collision without merge, testimony framing, and input-order determinism.

The original bootstrap defects AUD-ARCH-001..004 were materially remediated on the Auditor's previously tested scope. Later Director refinements below are **new/reopened foundation gates**, not a claim that the original work vanished.

### Current architecture blockers after later Director review

#### #72 historical projection-status semantics
A valid accepted `ASSERTION_PROJECTION_STATUS` decision does not become retroactively invalid merely because a later Assertion explicitly supersedes its target.

Required current rule:
- preserve the historical decision in reconciliation history;
- make it inactive for current projection once the predecessor Assertion is no longer eligible;
- build succeeds with both histories preserved and only the successor active.

The older green oracle expected build rejection and therefore remains contract-wrong until corrected.

#### #55 predicate governance beyond usage-level syntax
Separate PR #152 implements explicit usage contexts, but full #55 closure still requires:
- machine-readable examples that actually satisfy current Assertion subject/object domains;
- direct compiler enforcement of predicate lifecycle + projection eligibility as well as usage context;
- strict metadata coherence for ACCEPTED non-research predicates;
- reproducible historical DEPRECATED predicate readability using admission-time predicate-registry version/hash and batch attribution;
- actual EXTERNAL_CROSSWALK execution only after canonical #65 integration.

#### #61 identity-relation cardinality / scope values
V0.1 Director rule:
- default ENTITY_LINK active identity is the full edge `(subject_type, subject_id, relation_predicate, target_type, target_id)`;
- do not infer max-one-target semantics from predicate spelling;
- explicit predicate metadata may later govern stricter cardinality;
- ENTITY_LINK supersession compatibility is distinct from active conflict-key identity;
- current scope keys `CONTINUITY_SCOPE`, `TIMELINE_SCOPE`, `NARRATIVE_FRAME`, and `TEMPORAL_SCOPE` accept non-empty string `resolution` values in v0.1, not arbitrary JSON.

#### #78 cross-output referential verification
The shared verifier must additionally validate cross-output consistency:
- active assertions against assertion history;
- provenance assertion/evidence/source/work IDs and nested records;
- support sets and typed subject/object records;
- decision IDs against reconciliation history;
- relation endpoints / identity-link decision consistency;
- one non-conflicting canonical Source/Work/Evidence catalog reconstructed from nested provenance.

Perfect hashes over internally inconsistent records are not a verified bundle.

#### #65 / Librarian registry convergence
The architecture and Librarian cannot retain parallel Source/Work dialects.

Required foundation integration:
- one canonical Source schema enriched with lifecycle, provider metadata, content identity, variant/version, provenance-family/independence, and derivation fields;
- one canonical Work schema retaining broad `medium` plus optional structural `work_kind` and lifecycle/parent/component context;
- governed `source_work_binding`, `external_crosswalk`, `external_snapshot`, `external_observation`, and `analysis_pass` record surfaces;
- an authoritative Librarian registry root outside worker research partitions;
- Evidence requires `source_work_binding_id`; source_id/work_id remain validated redundant endpoints;
- projection manifest/input identity pins registry snapshot/head/hash;
- projection provenance stores the exact binding record/lineage used by Evidence.

#### Authority-file validation
A one-byte accidental `schema/coverage-event.schema.json` briefly existed on #82 while CI remained green. It was later removed, but the defect class remains: every governed schema artifact under the authority surface must parse/validate even when no tool imports that filename yet.

Add a negative regression so malformed/untyped schema files fail CI.

#### Documentation/methodology drift
Current #82 human-readable docs regressed despite green CI:
- `docs/architecture.md` again abbreviates the canonical flow to `SOURCE -> EVIDENCE -> ASSERTION`, omitting WORK and LOCAL ENTITY;
- `docs/research-methodology.md` omits `FULL_TEXT_AVAILABLE`;
- `research/README.md` omits the independent Short Treks lane;
- reconciliation docs do not clearly separate assertion disposition from projection status;
- worker/source wording predates the accepted-binding model.

Before foundation convergence restore the root-contract semantics and add contract-alignment regressions or derive repeated enumerations from a governed source so this cannot silently recur.

### Architecture topology normalization

Old development PR surfaces are now closed unmerged while every branch/history remains preserved:
- #1 bootstrap architecture;
- #8 projection input identity;
- #33 admission validator;
- #59 logical projection;
- #64 semantic diff;
- #68 SQLite;
- #71 PostgreSQL;
- #74 graph/search.

PR #82 is the sole active integrated implementation surface.

Final acceptance does **not** merge the historical stack sequentially. Director issue #151 defines a clean convergence candidate built from then-current accepted `main`, importing exact audited final blobs with provenance receipts.

## Predicate usage tranche — PR #152

PR #152 `Consolidator: govern predicate usage levels by context` is a bounded sibling proposal on #82.

Exact head: `803afa5e3bb527641211209115d05de383b9960e`.  
Workflow `32079180267`: SUCCESS.

Confirmed useful implementation:
- explicit contexts `RESEARCH_ASSERTION`, `RECONCILIATION_RELATION`, `EXTERNAL_CROSSWALK`, reserved `EVIDENCE_ANNOTATION`;
- MAPS_TO is crosswalk-only;
- current identity predicates are reconciliation-only while EXPERIMENTAL;
- assertion and ENTITY_LINK validators enforce context;
- compiler independently rechecks usage context;
- explicit multi-level behavior is tested.

Director routed this exact head to Auditor. Auditor disposition: usage-level mechanism is substantially implemented, with coherence follow-ups.

PR #152 is therefore an audited **partial #55 tranche**, not full #55 closure and not a merge candidate by itself.

Required successor #55 work:
- executable/machine-readable predicate examples valid under real Assertion domains;
- compiler lifecycle + projection-eligibility fail-closed checks;
- metadata coherence rules;
- historical DEPRECATED predicate admission/projection provenance using pinned registry identity and reconstructable registry history.

## Librarian Source / Work / binding

### PR #125 — implementation proposal exists, corrections required

PR #125 `Librarian: propose Source/Work binding and provenance registry surface` is the correct first implementation proposal.

Exact head: `4ccc10b84e2a9896f80fa4822cf67d9c709335b9`.  
Base: accepted `main@007641c...`.  
Draft/open; no accepted IDs/bindings created.

Director + Auditor agree it is a strong partial implementation with blockers.

Required corrections before a clean Auditor successor handoff include:
- ACCEPTED binding requires accepted governed Source + Work endpoints;
- SOURCE_BOUND derives from **active** accepted evidence-bearing bindings, excluding accepted predecessors superseded by accepted successors while retaining history;
- explicit non-empty binding supersession/correction reason;
- exclusive-source-scope collision identity cannot be bypassed by arbitrary caller labels;
- deterministic Work parent-cycle rejection;
- analysis-pass record/schema/ID/reference integrity;
- accepted external crosswalk requires accepted endpoint;
- binding scope/basis schema execution rather than handwritten loose dict checks;
- canonical #65 schema convergence with #82 instead of a parallel Librarian dialect;
- Evidence `source_work_binding_id` integration;
- deterministic CI receipt on the proposal.

Actual literary binding remains separately blocked because the reported ebook ZIPs are not byte-addressable to the Librarian in this environment.

### External snapshot / observation provenance

Auditor #127 showed that aggregator pages can flatten layered values. Director #65 now requires reproducible row-level external provenance:
- concrete `external_snapshot` with exact locator/query, retrieval/version identity, hash/fingerprint, lineage and independence;
- atomic `external_observation` rows preserving displayed/direct/quoted/derived/editorial values separately;
- explicit upstream attribution/derivation rather than treating provider name as independent corroboration;
- external_crosswalk bases itself on observation IDs.

PR #127 remains proposal/migration custody evidence, not governed ingestion. Historical collision counts 84/121/41 remain reported migration metrics until exact byte-addressable membership evidence exists.

## Coverage / denominators

Accepted `main` still has no coverage ledger.

Director #40 now has an implementation-ready native-unit model:
- DISCOVERED derives from accepted Work registry state; no duplicate coverage event;
- SOURCE_BOUND derives from active accepted #65 evidence-bearing binding; no duplicate coverage event;
- later completion uses immutable `coverage_event` records with typed subject, dimension, lifecycle, semantic effect (`ATTAINED | REVOKED | BLOCKED`), typed basis, explicit scope, method/provenance, and supersession;
- active event key is `(dimension, subject_type, subject_id, canonical_scope_key)`;
- dimensions use native units rather than one Work-level ladder;
- coverage denominators are versioned `coverage_denominator_snapshot` inputs; `DENOMINATOR_UNRESOLVED` emits no percentage;
- coverage report is a deterministic verified projection with its own receipt/hash;
- coverage semantic diff is separate from fact-projection #67 classes.

### PR #138 — green against rejected model; rewrite required

PR #138 current head: `e97cdf8722c4f0928e83e70efd2583012bdd27df`.  
Workflow `32078800275`: SUCCESS.

Director + Auditor disposition: mechanically green, **CONTESTED / REWRITE REQUIRED**.

Current implementation still:
- creates duplicate DISCOVERED/SOURCE_BOUND events;
- restores a universal predecessor ladder;
- uses Work as universal subject;
- conflates lifecycle and semantic effect;
- trusts opaque producer/basis/integration/audit strings;
- derives one runtime Work denominator rather than accepted scoped denominator snapshots;
- can ingest accepted-looking events from non-authoritative staging/migration paths;
- reconstructs binding validity from loose fields rather than canonical #65 state;
- exposes reporting as a potential validation bypass.

Preserve useful append-only/history/fail-closed ideas, but rewrite against #40 after #82/#125 contracts converge. Do not normalize staging counters into the rejected schema.

## Calibration

Issue #43 remains the calibration/adversarial contract.

Synthetic adversarial fixtures are legitimate before corpus admission. Real Trek fixed fixtures require accepted Source/Work/binding/Evidence provenance before becoming canonical regression truth. Proposal staging/audit findings may nominate candidates but do not become an oracle by repetition.

## Corpus queue hold — #23

Issue #23 remains ACTIVE and accepted `main` still does not satisfy resume conditions.

New source-reading batches remain paused. Preservation, synchronization, migration, and exact-byte restaging may remain open when they do not create new source-reading throughput or accepted coverage.

This Director execution closed the newly surfaced TNG close-read convoy unmerged while preserving every branch/commit:
- #128–#137;
- #139–#150.

Earlier DS9/TNG overrun cleanups remain preserved as well. No current open PR titled `Stage TNG` remained after the cleanup scan.

Prodigy #117 is exact-byte restaging/preservation; #119 is a synchronization index, not authorization for new source reading. Migration #121 records its current stop condition.

Accepted coverage remains zero for all preserved staging packets.

## Auditor

PR #19 remains the durable audit surface, current head `a1c6402ec3320a31b2a33e498cad0f5701f248e8`.

Its body still records the original AUD-ARCH-001..004 findings as resolved on the previously tested integrated scope. Director later reopened **foundation readiness** for post-audit contracts (#55/#61/#65/#72/#78, authority-file validation, documentation drift, coverage integration and clean convergence).

#152 exact head has now been independently reviewed: usage-context mechanism supported; follow-up lifecycle/coherence work remains.

Auditor should re-open exact successor bytes only when the relevant proposal head materially changes. Do not repeatedly audit unchanged green heads.

## Clean foundation convergence — #151

Do not merge #82's historical development stack as the final foundation.

After the architecture, canonical Librarian schema boundary, and any selected coverage tooling are independently audited:
1. re-pin then-current accepted `main`;
2. create a new clean proposal branch from that accepted head;
3. import exact audited final file blobs only;
4. record source PR/head, blob SHA, audit disposition, versions/hashes, generated/source classification and expected paths;
5. preserve accepted-main files including unresolved `x` unless separately authorized;
6. prove full validation/deterministic/audit equivalence on the clean candidate;
7. obtain Patrick's explicit authorization before merge.

PR #4 governance remains a separate protected acceptance decision unless Patrick explicitly authorizes combining effects.

## Current next actions by role

### Consolidator
- produce bounded successor(s) for #61 cardinality/scope-value rules, #72 historical status semantics, #78 cross-output referential verification, authority-file validation, and #55 lifecycle/provenance follow-up;
- update current #82 docs/methodology alignment before foundation convergence;
- do not treat PR #138's current coverage model as accepted contract;
- keep actual corpus records out of architecture tests except explicit synthetic fixtures.

### Librarian
- harden #125 against Director/Auditor findings;
- converge on the canonical #65 Source/Work/binding schemas rather than a parallel dialect;
- add exact external snapshot/observation provenance;
- keep real ebook binding blocked until bytes are actually available;
- route corrected exact successor bytes to Director/Auditor.

### Auditor
- #152 usage-level exact head has been reviewed;
- re-audit only substantive successors for #82/#125/#138/#55 follow-up or clean #151 convergence;
- preserve the distinction between original bootstrap finding closure and later reopened foundation contracts.

### Series / Films / Literature
- preserve/synchronize already completed proposal bytes only;
- do not begin new close-read tranches while #23 is active;
- do not mint canonical Source/Work/binding, coverage, predicate, or reconciliation authority locally.

### Director
- maintain #29/#14/#23/#40/#55/#61/#65/#72/#76/#78/#151 only on substantive state changes;
- use this PR #104 as the durable coordination surface rather than spawning redundant checkpoint PRs;
- enforce queue hold without deleting proposal history;
- reassess foundation only after successor implementations and audit actually change the evidence.

## Protected effects / remaining Patrick decisions

This synchronization authorizes no:
- merge;
- force-push or history rewrite;
- branch deletion;
- deployment;
- credential/permission/branch-protection change;
- accepted Source/Work/binding/crosswalk record;
- accepted reconciliation decision;
- coverage promotion;
- cleanup/revert of accepted top-level `x`.

The only current Director-cleared protected proposal decision remains governance PR #4, which still requires Patrick's explicit authorization if it is to be merged. All other foundation work remains proposal/audit/dependency state.
