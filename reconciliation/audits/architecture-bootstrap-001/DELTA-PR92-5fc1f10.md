# Auditor delta — PR #92 governance alignment head `5fc1f10`

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #92 `architecture/governance-alignment-001`
Audited head: `5fc1f103e4407233b52da62f82276b3153355600`

## Disposition

**SUPPORTED FOR GOVERNANCE BYTE CUSTODY / CONTESTED AS AN INTEGRATED GOVERNANCE+ARCHITECTURE ACCEPTANCE CANDIDATE.**

PR #92 successfully combines the exact four Project governance files with a bootstrap architecture proposal without mutating accepted `main`. The root governance bytes are the same bytes previously custody-audited in PR #27/#4.

However, the branch's own authority intent says implementation documents, schemas, registry, and tools must conform to the root `TREK_*` governance files rather than become a competing methodology. That condition is not currently met.

No merge, governance acceptance, accepted-state mutation, coverage advancement, or protected effect is performed by this audit.

## Positive deterministic controls

Exact root Git blobs at PR #92:
- `TREK_RESEARCH_METHOD.md` — `d30eb5bfd8012cf7a53af233b4bc5f5bf07ab368`
- `TREK_REPO_PROTOCOL.md` — `781032ab0786730eaede9e27b2b0aae0318a60a0`
- `TREK_ROLE_CATALOG.md` — `d5a005fe3ce8250ee95f5d0a2f1223474bef0e19`
- `CHAT_STARTERS.md` — `ba68d4eccedbb0160fd57097d6432dc70f459636`

These exactly match the previously audited governance proposal blobs. Governance custody itself is confirmed.

`validate-core` run `31846756062` is green on the audited PR #92 head. That validates the branch's current, older bootstrap test surface only; it does not demonstrate compliance with later Director contracts or repair previously audited semantic gaps.

## GOV-ALIGN-001 — HIGH — duplicate methodology omits FULL_TEXT_AVAILABLE

Root `TREK_RESEARCH_METHOD.md` defines the coverage ladder:

`DISCOVERED -> SOURCE_BOUND -> FULL_TEXT_AVAILABLE -> STRUCTURALLY_INDEXED -> CLOSE_READ -> SEMANTICALLY_ANALYZED -> ENTITY_LINKED -> CROSS_REFERENCED -> AUDITED`

Bundled `docs/research-methodology.md` instead says a work may be discovered, source-bound, structurally indexed, close-read, semantically analyzed, entity-linked, cross-referenced, and audited. It omits `FULL_TEXT_AVAILABLE`.

This is not harmless abbreviation because coverage contract #40 and the root method require availability to remain independent from binding and close reading. The implementation document therefore contradicts the authority file on a load-bearing coverage state.

**Required resolution:** bring the duplicate implementation methodology into exact semantic alignment or reduce it to a non-authoritative pointer so there is only one governing coverage ladder.

## GOV-ALIGN-002 — HIGH — research partition README omits Short Treks

Root `TREK_ROLE_CATALOG.md` explicitly defines lane `SHORT` for Short Treks. Bundled `research/README.md` lists suggested top-level lanes but omits `short-treks`.

This already caused a historical validator-routing mismatch before later validation work added `SHORT` explicitly. The integrated governance branch should not preserve that known partition drift.

**Required resolution:** include the Short Treks partition consistently across role catalog, worker routing, repository layout guidance, and validator ownership maps.

## GOV-ALIGN-003 — CRITICAL — bootstrap implementation is stale relative to current architecture contracts

PR #92 bundles the earlier v0.1 bootstrap architecture/tooling rather than the later integrated validator/projection work now under PR #82. The older stack retains findings already recorded in Auditor PR #19, including inadequate admission validation, raw/untyped reconciliation semantics, incomplete provenance projection, and coarse semantic diff behavior.

Since PR #92 explicitly claims to integrate governance with architecture, acceptance of this branch now would install governance beside an architecture implementation already known to violate both the root method and Director contracts #52/#55/#61/#67/#72/#76.

The current green CI does not cure this because it validates the old test oracle/empty accepted corpus, not the current contract surface.

**Required resolution:** governance alignment should be re-based/reconstructed on a semantically corrected integrated architecture successor after PR #82's oracle/validator/compiler/provenance/diff findings are repaired. Do not independently fork a second architecture lineage merely to keep this PR green.

## GOV-ALIGN-004 — HIGH — root protocol diff taxonomy is older than current proposed corrections

`TREK_REPO_PROTOCOL.md` correctly preserves the original governed semantic diff classes, but Director #67 later identified cases that cannot honestly be represented by those classes (non-STABLE STATUS_CHANGED, reconciliation history, entity lifecycle, relation lifecycle) and explicitly keeps those extensions proposed until governance accepts them.

This is not a reason to silently edit the root protocol in an Auditor branch. It is a governance-alignment requirement: either formally accept/version the taxonomy extensions through the governance process or keep implementations on an explicit provisional/diagnostic channel. PR #92 currently does neither because it predates those contracts.

## Closure

- Governance byte identity: **CONFIRMED**.
- Root files as Project operating contract: **SUPPORTED**.
- Internal docs semantically aligned with roots: **NO**.
- Architecture implementation aligned with current contracts: **NO**.
- PR #92 acceptance-ready as integrated governance+architecture: **NO / CONTESTED**.

Exact next governance frontier: preserve the four root bytes, repair/retire contradictory duplicate docs, and integrate them with the corrected successor of PR #82 rather than the stale bootstrap stack.
