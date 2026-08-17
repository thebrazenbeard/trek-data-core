# Auditor review — PR #127 legacy custody / external crosswalk intake

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`
Proposal: PR #127 `external/librarian/crosswalk-intake-v1`
Audited head: `0e3077f0a0fc16237b9fd08f2e515a6942ef76ba`
GitHub workflow runs at head: none

## Disposition

**SUPPORTED AS PROPOSAL PRESERVATION / INSUFFICIENT PROVENANCE FOR GOVERNED CROSSWALK INGESTION.**

The branch is appropriately cautious about not converting legacy IDs, unexposed ebook containers, external bibliographic pages, or aggregate collision counts into accepted Trek registry state. Its conceptual lineage/container/edition discipline is useful migration evidence.

The external-crosswalk tranches are not yet reproducible enough to become governed accepted crosswalk records under the repository protocol and #65-style provenance expectations.

## Confirmed strengths

1. Legacy `STW-*` IDs remain explicitly migration evidence, not accepted `trek-data-core` Work identity.
2. The two ebook ZIP containers remain reported-but-not-byte-exposed; no Source IDs/hashes are fabricated.
3. Container, contained Work, edition/release and physical-source identity are kept distinct.
4. LIT/TXT/OPF/HTML derivative representations are explicitly assigned zero additional corroboration weight rather than being treated as independent witnesses.
5. Aggregate collision counts 84 / 121 / 41 are preserved while exact membership is explicitly marked unrecovered.
6. Currentness sync correctly preserves the historical branch base and separately records current `main@007641...` plus the unexplained `x` drift instead of rewriting historical artifacts to look newly generated.
7. rtrek binary intake is correctly blocked rather than synthesizing rows from documentation counts alone.
8. External metadata conflicts and edition differences are generally preserved instead of averaged away.

## Blocking findings

### AUD-XWALK-001 — HIGH — external observations are not reproducibly snapshotted

Tranche 001 includes page URLs, but does not preserve per-observation retrieval time, page/content snapshot hash, revision/version identifier, or content fingerprint.

Tranche 002 is weaker: its individual Memory Alpha / Memory Beta / Simon & Schuster observations generally do not include external locators at all. They are keyed only by `system` plus copied metadata.

Mutable wiki/publisher pages can change. An accepted external crosswalk record needs enough source identity to reconstruct which observation was actually used: locator + retrieval/version/snapshot identity + lineage/independence group + mapping status. A global tranche timestamp or source-system name is not equivalent.

Disposition: retain these rows as migration/candidate notes only until each external observation is source-bound reproducibly.

### AUD-XWALK-002 — HIGH — layered/derived values inside one external page are flattened into source-specific scalars

Independent reopening of Memory Beta's `Incident at Arbuk` page demonstrates the risk.

The page currently displays chronology stardate `48531.6`, but its Background explicitly states that **the book gives 48135.6** and that **The Star Trek Fiction Timeline adjusts it to 48531.6** for compatibility.

PR #127 tranche 001 records Memory Beta simply as `stardate: 48531.6` and then represents the issue as a Memory Alpha `48135.6` versus Memory Beta `48531.6` source conflict.

That flattens three different provenance layers:
- value stated by the underlying book;
- value chosen/displayed by Memory Beta's chronology field;
- adjustment derived from another timeline source.

The correct external evidence model must be source-relative even *inside* an external aggregator page. Preserve original reported value, derived/adjusted value, derivation source, and page display separately. Do not turn a wiki's synthesis into one atomic witness value.

### AUD-XWALK-003 — HIGH — external observation lineage is mostly tranche-global, not row-specific

The adapter assessment has good conceptual independence rules, but the candidate rows do not consistently carry per-observation provenance family / independence group / upstream derivation / retrieval identity / mapping status fields that can be consumed deterministically by the proposed #125 contract.

For example, a Memory Beta field may itself derive from a book, a timeline project, a wiki editor synthesis, or another listed external source. `external_system: Memory Beta` alone is insufficient to determine witness independence.

Before governed ingestion, bind each candidate observation to the actual external Source/snapshot and preserve its internal/upstream lineage where known.

### AUD-XWALK-004 — MEDIUM/HIGH — historical collision counts have no recoverable source artifact in this proposal

The branch carefully labels 84 high-confidence LIT↔TXT candidates, 121 title-overlap groups and 41 suspicious short conversions as historical aggregate counts with exact memberships unrecovered.

That honesty is good. But the proposal does not preserve a byte-addressable report, manifest, query output, commit, or other durable artifact from which those counts can be independently regenerated.

Therefore they are **reported historical migration metrics**, not accepted collision statistics, denominators, or evidence of individual duplicate relationships. Keep them quarantined from coverage/inventory arithmetic until the underlying membership artifact is recovered.

### AUD-XWALK-005 — MEDIUM — no deterministic PR validation / CI receipt

No GitHub Actions workflow run is associated with head `0e3077f...`. The branch is primarily preserved JSON/Markdown rather than executable schema work, but acceptance-grade migration intake should still have deterministic validation for parseability, required proposal-only flags, no accidental canonical Source/Work IDs, locator/provenance requirements, and crosswalk row uniqueness.

This becomes more important if these files are later consumed automatically by migration tooling.

## Independent external checks

### `Incident at Arbuk`

Memory Beta independently confirms the basic bibliographic identity used by the candidate row: Voyager/Pocket VOY No. 5, John Gregory Betancourt, November 1995, 214 pages, ISBN 0671520482. Its displayed chronology is 48531.6 while Background says the book itself gives 48135.6 and the Fiction Timeline adjusts that value.

Result: **bibliographic crosswalk candidate supported; stardate provenance in PR #127 is oversimplified.**

### `Seven of Nine`

Simon & Schuster's current official page independently supports the candidate Work/edition distinction: Christie Golden, Star Trek: Voyager #16, eBook, ISBN13 9780743453820. That supports preserving the publisher eBook as distinct release metadata rather than collapsing it into the 1998 paperback Source instance.

Result: **edition-separation reasoning supported.**

## Interaction with PR #125

PR #125 is the correct place to govern Source/Work/binding/crosswalk record semantics. PR #127 should remain migration/candidate evidence and should not bypass #125 validation by later being copied wholesale into accepted external records.

Once #125 is hardened, migrate these observations one external Source/snapshot at a time through the governed schema, preserving page-level and subsource derivation.

## Exact next frontier

1. Add reproducible external observation identity: locator + retrieval/version/snapshot/fingerprint per candidate source observation.
2. Preserve subsource/derived-field provenance within aggregator pages rather than flattening to one source scalar.
3. Attach row-specific provenance family / independence group / mapping status compatible with the hardened #125 contract.
4. Recover byte-addressable collision membership evidence before using 84/121/41 as anything beyond historical reported metrics.
5. Add deterministic validation/CI for the proposal intake surface.

No Source/Work/crosswalk acceptance, collision reconciliation, coverage promotion, merge, deployment, or accepted-state mutation performed.
