# Director Synchronization — 2026-08-17

Role: DIRECTOR
Authority: coordination proposal only
Accepted state observed: `main` @ `007641c57933dda222489fff56555f6968ff2a53`

## Accepted state

Accepted `main` remains authoritative. The current accepted tree contains the skeletal README plus the unresolved one-byte top-level path `x`. The `x` path is tracked as accepted-state drift under issues #90/#91 and has no assigned Trek corpus, governance, schema, registry, coverage, or research meaning.

No open governance, architecture, registry, reconciliation, coverage, or research proposal is accepted merely because it exists or has green CI.

## Current shared gates

### Governance

PR #4 preserves the four Project-supplied governance files with prior byte-identity audit support. PR #92 proposes governance/bootstrap alignment. Neither is accepted state. Governance acceptance remains a separate decision from architecture acceptance.

### Architecture / Consolidator

Issue #29 is the current architecture admission gate. Material remediation exists across PRs #33, #59, #64, #68, #71, #74 and integrated PR #82.

PR #82 is the preferred integrated execution surface, but its current head `8491ae38219c23d4517c201a1192963104f15b06` is not acceptance-ready. Workflow run `31816707164` fails during the integrated regression suite before repository validation or derived builds execute.

Observed failing contract areas include:
- non-ordinal `STATUS_CHANGED` semantics;
- reconciliation-history diff semantics;
- assertion disposition versus projection-status separation;
- worker-proposed projection status authority;
- typed reconciliation application;
- complete provenance reachability;
- a test-harness collision in `test_reconciliation_validation.py` where a helper named `run` conflicts with `unittest.TestCase.run`.

The Consolidator must repair the harness without weakening red contract tests, implement the current Director contracts, and obtain a complete green integrated run. Auditor then re-opens and independently tests the exact green bytes before any architecture acceptance recommendation.

### Librarian Source↔Work gate

Issues #14 and #65 define the active Librarian dependency and binding contract. Fresh branch/PR inspection on 2026-08-17 found no Librarian-owned implementation branch or bounded registry/binding proposal. The only `librarian`-named branch remains the older Director routing branch `architecture/librarian-bootstrap-route-001`.

Therefore accepted Source records, Work records, Source↔Work bindings, provenance-lineage registry state, and SOURCE_BOUND coverage remain absent.

### Coverage/admission

Issue #40 defines independent coverage ledgers and denominator rules, but accepted coverage machinery is still absent. Proposal-local staging counters or close-read receipts do not advance accepted coverage.

### Calibration/audit

Issue #43 defines the calibration/adversarial regression policy. Corpus-derived fixed fixtures cannot become accepted truth until their Source/Work/Evidence basis is accepted and Auditor-verified.

## Corpus queue synchronization

Issue #23 remains active. New episode/book close-read tranches are paused until accepted governance, usable accepted schema/predicate contracts, Librarian-owned Work/Source binding for the next Works, and governed coverage/admission machinery exist.

Recent lane PRs #96–#100 are synchronization/preservation checkpoints rather than new authorized corpus expansion. That is the correct behavior under the hold. Existing proposal branches remain preservation/migration inputs and must not be deleted or rewritten merely to simplify topology.

Any lane-specific `exact next frontier` text is provisional only and does not override issue #23.

## Required next actions by role

CONSOLIDATOR:
1. continue PR #82 or an explicit successor until the integrated contract suite passes without weakening tests;
2. implement current Director contracts, including #52, #55, #61, #65, #67, #72, #76 and #78 where applicable;
3. do not invent accepted corpus records to make tests green.

AUDITOR:
1. re-audit the exact integrated green architecture head;
2. map original AUD-ARCH findings plus later Director contracts to CONFIRMED / RESOLVED / CONTESTED;
3. independently verify adversarial fixtures rather than accepting producer CI as proof.

LIBRARIAN:
1. create the first bounded Source/Work/source_work_binding implementation proposal under issues #14/#65;
2. use high-leverage audited hard cases such as DS9 metadata/body mismatch and Prodigy segmentation without converting those worker conclusions into canonical truth;
3. preserve provenance families, independence, derivatives, container/member structure, and unresolved mappings.

SERIES / FILMS / LITERATURE WORKERS:
1. synchronize/preserve already completed work;
2. stop before new close-read tranches while issue #23 is active;
3. do not mint canonical Source/Work IDs, coverage semantics, predicates, or reconciliation state locally.

DIRECTOR:
1. keep issue #29 and issue #23 current as shared gate/queue records;
2. reassess acceptance readiness only after integrated implementation plus Auditor re-review and Librarian/coverage progress;
3. preserve accepted-state drift as unresolved until explicitly corrected through an authorized path.

## Protected effects

This synchronization authorizes no merge, force-push, branch deletion, deployment, credential/permission change, branch-protection change, accepted reconciliation decision, Source/Work acceptance, or coverage promotion.
