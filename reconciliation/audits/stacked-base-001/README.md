# Stacked research-base topology audit 001

Role: AUDITOR  
Disposition: **CONFLICT — preserve proposal branches, do not integrate research through the architecture base**

This audit concerns PR topology, not the semantic quality of the staged research.

## Observed proposal graph

The following open **research** PRs currently declare `architecture/v0.1-bootstrap` as their base branch rather than accepted `main`:

- DS9 #2
- DS9 #9
- Enterprise #10
- DS9 #20
- DS9 #30
- DS9 #35
- DS9 #39
- DS9 #42
- DS9 #46
- DS9 #48
- DS9 #50
- DS9 #51

Infrastructure hardening PRs #8 and #33 are also stacked on `architecture/v0.1-bootstrap`, but that is appropriate to their architecture/consolidator scope and is not the subject of this finding.

## Finding

### AUD-TOPO-001 — merging a research PR into its declared architecture base would contaminate the architecture proposal

**Verdict:** CONFIRMED  
**Severity:** CRITICAL for integration

PR #1 is intended to be a bounded architecture foundation proposal. A research PR whose GitHub base is `architecture/v0.1-bootstrap` is asking GitHub to integrate its research commit(s) into that architecture branch.

If such a research PR were merged into its declared base:

1. the architecture branch would acquire `research/...` staging bytes;
2. PR #1's effective diff against `main` would expand beyond architecture/foundation scope;
3. later acceptance of PR #1 could unintentionally carry corpus staging with it;
4. architecture review/CI would no longer have a clean foundation-only input set;
5. research and infrastructure acceptance histories would become coupled despite different ownership and admission requirements.

This is a topology/integration hazard even though all affected research PRs currently remain unmerged proposals.

## Why the current research bytes are not rejected

The proposal research should be preserved. The defect is the integration target, not necessarily the work product.

Several of these PRs correctly state that they are proposal-only, advance no accepted coverage, invent no canonical Source/Work IDs, and are blocked on architecture/Librarian admission. Those boundaries remain useful.

However, `proposal-only` does not neutralize the declared Git merge target.

## Required integration invariant

Research proposals must not be merged into an architecture proposal branch merely to preserve dependency context.

Before any eventual admission/integration action, an authorized integration owner should choose a path that preserves:

- accepted `main` as the authority baseline;
- architecture acceptance separately from research acceptance;
- research lane ownership;
- exact research proposal provenance/commit identity;
- no silent history rewrite or force push;
- no coverage advancement until Source/Work/schema/admission conditions are met.

Possible implementation strategies belong to Director/Consolidator governance; the Auditor does not prescribe or perform a retarget/rebase/merge here.

## Currentness complication

The architecture base branch itself has advanced over time. Older research branches can therefore be simultaneously:

- based on an older architecture commit;
- behind the current architecture proposal;
- targeting the moving architecture branch in GitHub.

That makes branch ancestry unsuitable as evidence that a research packet was validated against the current architecture semantics. Exact commit/schema dependency must be recorded explicitly.

## Protected-effect boundary

This audit does **not**:
- retarget any PR;
- rebase any branch;
- merge any PR;
- close any proposal;
- delete staging work;
- modify the architecture branch.

Those are integration/protected effects requiring the appropriate owner and, where applicable, Patrick's exact authorization.

## Exact next frontier

Re-audit only when an integration/retarget/normalization proposal is made. Verify that architecture-only acceptance cannot accidentally import research staging and that research proposal provenance survives any authorized topology correction.
