# SFA Proposal Staging Snapshot

Snapshot basis: 2026-08-14 final execution checkpoint.
Authority: `PROPOSAL_ONLY`.

## Accepted state

Latest accepted `main` observed: `007641c57933dda222489fff56555f6968ff2a53`.
Latest root inspection contains only:
- `README.md`
- one-byte root file `x`

Accepted Work objects: **absent**.
Accepted SFA Source bindings: **absent**.
Accepted SFA research coverage: **undefined / not advanceable**.

The source-page counts below are staging/discovery facts only and must never be substituted for accepted corpus coverage.

## Current external release discovery

Current Paramount+ discovery exposes one released season with ten episode entries. Paramount+'s April 21, 2026 Season 2 update says filming has wrapped but no Season 2 premiere date has been announced.

This external release inventory is discovery metadata, not an accepted Work denominator.

## Proposal staging map and overlap

| Provisional source position | Source-page title | End-to-end transcript close read | Proposal locations |
|---|---|---|---|
| S01E01 | Kids These Days | staged | PR #18 / `research/sfa/sfa-s01-b001-staging` |
| S01E02 | Beta Test | staged | PR #18 **and** PR #22 |
| S01E03 | Vitus Reflux | staged | PR #18 **and** PR #34 |
| S01E04 | Vox in Excelso | staged | PR #18 **and** PR #34 |
| S01E05 | Series Acclimation Mil | staged | PR #18 **and** PR #34 |
| S01E06 | Come, Let's Away | staged | PR #34 |
| S01E07 | Ko'Zeine | staged | PR #37 / `research/sfa/sfa-s01-b004-staging` |
| S01E08 | The Life of the Stars | staged | PR #37 / `research/sfa/sfa-s01-b004-staging` |
| S01E09 | 300th Night | staged | PR #37 / `research/sfa/sfa-s01-b004-staging` |
| S01E10 | Springfield page: Rubicon | staged | PR #37 / `research/sfa/sfa-s01-b004-staging` |

### Overlap discipline

PR #18 was expanded by another SFA proposal path after earlier packets were created and now contains opening-five files for `Kids These Days`, `Beta Test`, `Vitus Reflux`, `Vox in Excelso`, and `Series Acclimation Mil`.

Therefore:
- E02 overlaps PR #22;
- E03–E05 overlap PR #34;
- these overlaps use the same Springfield transcript representations/upstream provider and **must not be counted as independent source corroboration**;
- the overlapping research may later be useful for classification-drift comparison, but only after source identity and worker/pass provenance are explicitly tracked;
- no attempt is made here to choose a winning proposal or silently deduplicate research conclusions. That is future normalization/audit work after accepted infrastructure exists.

## Director workload hold

Open issue #23, `Director queue hold: pause new corpus staging until admission bottleneck clears`, directs corpus workers not to begin additional close-read tranches while governance/admission and Librarian Source↔Work dependencies remain unresolved. It permits already-in-progress bounded work to reach a clean preservation checkpoint.

The E07–E10 transcript reads preserved in PR #37 were already completed/in progress before this final handoff reconciliation. PR #37 is the clean preservation checkpoint for that work. **No further SFA source-reading tranche should begin while issue #23 remains active**, irrespective of future discovery-only metadata, unless Patrick provides a newer explicit project direction that supersedes the hold.

## Outstanding source/provenance issues

- no Librarian-owned Work identity exists for any entry;
- no accepted Source identity/provenance family exists;
- stable byte hashes for third-party transcript representations are not bound;
- transcript-provider upstream lineage/independence remains unresolved;
- primary audiovisual media has not been directly verified by this worker;
- final-title discrepancy remains unresolved (`Rubincon` on current Paramount+ versus Springfield page title `Rubicon`);
- no global identity reconciliation has been performed for legacy characters/institutions/technologies or for Sam's post-Kasq continuity;
- overlapping proposal passes are not independent corroboration.

## Current stop condition

There is currently no legitimate additional SFA corpus-reading action for this worker:

1. all ten currently released Season 1 entries in the external official discovery inventory have at least one complete transcript close-read preserved in proposal staging;
2. Season 2 has no announced premiere date and supplies no released episode corpus to read;
3. Director issue #23 explicitly pauses new corpus staging;
4. accepted `main` still has no Work/Source/admission infrastructure enabling normalization or governed promotion;
5. merge, acceptance, global reconciliation, Librarian binding, and infrastructure repair are owned elsewhere or require protected authorization.

Next SFA execution begins only after the queue hold/resume conditions or accepted state materially change. At that point, recalculate from accepted `main`; do not continue from this provisional numbering as if it were canonical.