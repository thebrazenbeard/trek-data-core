# Starfleet Academy staging convergence audit 001

Role: AUDITOR  
Primary proposal audited: PR #37 @ `7addd7ea5413e986500147f8a24241c891876923`  
Related overlap proposals: PR #18, #22, #34  
Disposition: **SUPPORTED_WITH_CAVEAT / STOP CONDITION CONFIRMED**

This audit does not establish an accepted SFA denominator or accepted coverage.

## Accepted-state and queue boundary

PR #37 correctly records accepted `main` as having no Work objects, no SFA Source bindings, and no advanceable accepted SFA coverage. Its staging snapshot treats external release counts as discovery metadata only.

Director issue #23 remains open and explicitly pauses new close-read tranches until governance, usable schema/predicate admission, Librarian Work/Source binding, and governed coverage/admission exist. Its enforcement update specifically confirms SFA proposal expansion after the hold and instructs workers to preserve completed checkpoints without starting additional tranches.

Therefore PR #37's stop condition is currently supported: SFA has no legitimate new source-reading assignment under accepted project authority.

## Findings

### AUD-SFA-001 — current external inventory is discovery metadata, not accepted denominator

**Verdict:** CONFIRMED  
**Severity:** HIGH if mis-promoted

The current staging snapshot records ten released Season 1 entries from Paramount+ discovery and no announced Season 2 premiere date. That information is useful for discovery/currentness, but no accepted Work registry exists.

The worker correctly refuses to convert `10 external entries` into `10 accepted Works` or accepted coverage.

Any later denominator must be rebuilt from the Librarian-owned Work registry, not inherited from this staging table.

---

### AUD-SFA-002 — final-title discrepancy is a real provenance conflict, not a typo to normalize away

**Verdict:** CONFIRMED  
**Severity:** HIGH for Source↔Work binding

Current official-facing Paramount+ material renders the Season 1 finale title as `Rubincon`. Springfield's S01E10 transcript page renders the page title as `Rubicon`, while the transcript body itself contains Rubincon/Rubicon wordplay.

These are distinct evidence channels:
- official release/title metadata;
- third-party provider displayed title;
- body text containing terms used inside the work.

A Librarian binding must preserve the provider-displayed title and official-title crosswalk separately. The occurrence of `Rubicon` in body wordplay does not make the third-party heading authoritative, and the official title does not justify silently rewriting the source's observed heading.

---

### AUD-SFA-003 — overlapping proposal passes are not independent source corroboration

**Verdict:** CONFIRMED  
**Severity:** CRITICAL for evidence weighting

PR #37 explicitly identifies overlap:
- `Beta Test`: PR #18 + PR #22;
- `Vitus Reflux`: PR #18 + PR #34;
- `Vox in Excelso`: PR #18 + PR #34;
- `Series Acclimation Mil`: PR #18 + PR #34.

Those passes use the same Springfield transcript representations/upstream provider.

Therefore their source-evidence corroboration weight relative to one another is **zero**. Multiple workers/passes may later be useful for measuring classification drift or analytical reproducibility, but only if pass identity is tracked separately from witness/source independence.

A future normalizer must not count `two proposal packets agree` as `two textual witnesses agree`.

---

### AUD-SFA-004 — current proposal overlap should remain unresolved rather than selecting a winner

**Verdict:** CONFIRMED  
**Severity:** MEDIUM

PR #37 does not choose one overlapping packet as canonical research and does not silently deduplicate conclusions. That is correct while accepted Source/Work identities and an admission schema are absent.

Future normalization should compare overlapping passes record-by-record after source identity is known, preserving analytical disagreements rather than selecting by branch age, PR number, or apparent completeness.

---

### AUD-SFA-005 — queue stop is current, but its accepted-head note is historically stale

**Verdict:** SUPPORTED_WITH_CAVEAT  
**Severity:** MEDIUM

Issue #23 is still open and its hold conditions remain operative. Its enforcement comment names accepted head `694cb833...`, but accepted `main` later advanced to `007641c...` by adding root file `x`.

That head-staleness does not satisfy any resume condition: current `main` still lacks accepted governance/schema/Work/Source/admission infrastructure. The hold therefore remains substantively active.

Currentness should be evaluated from live accepted state and issue state, not frozen head text inside the comment.

## Blind-spot result

This SFA proposal cluster demonstrates that research independence and source independence are different axes.

Two independent reasoning passes over one source can help estimate interpretation/classification drift, while contributing only one source witness. Conversely, two distinct source representations can still be one provenance family and therefore fail to provide independent corroboration.

The corpus needs both:
- `analysis/pass provenance`;
- `source/witness independence provenance`.

Collapsing those dimensions creates pseudo-corroboration.

## Admission disposition

Preserve PR #37 and the overlapping staging packets. Do not advance accepted coverage or begin additional SFA close reading under the current hold.

## Exact next frontier

SFA Auditor work is blocked until one of these materially changes:
1. Librarian proposes accepted-bound SFA Works/Sources;
2. issue #23 is superseded/closed by valid resume conditions;
3. a normalization proposal reconciles the overlapping passes;
4. title/source crosswalk records are proposed.

Repository-wide Auditor priority returns to infrastructure/admission, specifically Consolidator PR #33, which issue #23 identifies as current validator-hardening progress.
