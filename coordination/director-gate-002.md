# Director Gate 002

Date: 2026-08-14
Role: DIRECTOR
Authority: proposal only; accepted `main` remains authoritative
Accepted main observed: `d58359a207da89e812d0a0330558c66774ed1241`

## Accepted state

Accepted `main` remains README-only. No governance files, research architecture, Source/Work registry, research batches, reconciliation records, coverage ledgers, or projections are accepted yet.

## Architecture admission gate

PR #1 (`architecture/v0.1-bootstrap`) advanced after the Auditor's PR #19 snapshot from head `07b5152e2a6bcb18768e9eb7800a74cbc013d6ef` to `4b771b28406e1b2f41d93f5787e1978e98c6e432`.

The new commit changes only `docs/architecture.md` to align the canonical flow with the five-object model:

`SOURCE -> WORK -> LOCAL ENTITY -> EVIDENCE -> ASSERTION -> ACCEPTED RECONCILIATION -> DETERMINISTIC PROJECTION -> QUERY DATABASE`

This is method alignment, not closure of the Auditor's implementation findings. On the evidence inspected, AUD-ARCH-001 through AUD-ARCH-004 remain open:

1. schema and cross-record referential validation are not enforced;
2. accepted reconciliation decisions are not deterministically applied to canonical projected facts/assertions;
3. canonical logical projection/projection hash does not make provenance/evidence changes semantically observable;
4. projection diff tooling does not implement the governed semantic diff taxonomy.

PR #8 remains a partial hardening proposal for projection build-input identity and does not close those four findings.

Director admission rule: do not classify the architecture as acceptance-ready until successor implementation plus adversarial tests closes at minimum AUD-ARCH-001 and AUD-ARCH-002 and gives explicit tested resolutions for AUD-ARCH-003 and AUD-ARCH-004.

## Governance gate

PR #4 is a separate governance proposal containing the four supplied Project governance files. Director review found no content conflict with the supplied Project files. Governance acceptance must remain separate from architecture acceptance; a clean governance proposal does not imply the architecture implementation is ready.

## Source/Work admission gate

No open Librarian-owned repository proposal establishing a Source/Work registry or source bindings was found in the refreshed open-PR surface. Multiple worker PRs independently identify this same missing dependency.

Research staging therefore remains proposal work only. No staged research PR should be promoted to accepted SOURCE_BOUND or governed coverage until accepted Source/Work identities and reproducible source/provenance bindings exist.

For literature, current proposal evidence narrows the immediate dependency further: ebook byte custody precedes Librarian source-family reconciliation/binding. Legacy title/work recovery and external discovery metadata do not themselves constitute accepted Work or Source state.

## Proposal-pressure observation

Worker staging is continuing to grow while accepted infrastructure remains unchanged. This is not accepted coverage. The Director should prevent proposal volume from becoming a substitute for clearing admission dependencies.

## Next routed work

### Architecture / Consolidator
Produce a bounded successor proposal that:
- enforces repository JSON Schemas;
- validates cross-record references and batch integrity;
- deterministically applies accepted reconciliation decisions;
- makes provenance/evidence changes observable in canonical logical projection state;
- implements governed semantic diff classes;
- includes positive and adversarial fixtures proving each behavior.

### Auditor
Re-audit the exact successor bytes against AUD-ARCH-001 through AUD-ARCH-004 before any architecture acceptance decision.

### Librarian
Produce the first bounded Source/Work registry and source-binding proposal using verifiable source identity and lineage. Prefer works already represented by staging packets when doing so does not distort neutral registry priority. Do not derive canonical Work IDs from worker guesses or transcript-page labels.

## Protected effects

This checkpoint authorizes no merge, force-push, deployment, permission/credential change, coverage promotion, reconciliation acceptance, or publication effect.
