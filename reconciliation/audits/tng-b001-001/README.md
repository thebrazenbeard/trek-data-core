# TNG proposal batch audit — tng-s01-b001

Role: AUDITOR  
Accepted base at audit branch creation: current `main`  
Proposal audited: PR #3, head `0695fb2d36870e9c156ce7acd16f00f70103b19e`  
Disposition: **SUPPORTED_WITH_CAVEAT — preserve research effort; do not promote coverage vector unchanged**

This audit does not merge or rewrite TNG research. It performs deterministic integrity checks plus adversarial semantic sampling of the proposal.

## Proposal boundary confirmed

The batch manifest explicitly states:
- schema `TREK_RESEARCH_METHOD_V1_PROVISIONAL`;
- status `PROPOSAL_VALIDATED`;
- accepted main had no Librarian-owned Source/Work registry;
- `SOURCE_BOUND` therefore cannot be claimed;
- primary audiovisual media was not directly verified;
- transcript-provider lineage independence is `UNKNOWN`;
- local work references are provisional;
- no global identity/reconciliation state was mutated.

Those limitations are materially preserved rather than hidden.

## Deterministic integrity checks

The manifest records Git blob identities for the record artifacts. Direct GitHub tree inspection at the exact proposal head confirms the declared blob identities for the record set and top-level coverage/validation artifacts examined, including the split `Where No One Has Gone Before` files.

The worker validation reports 17/17 checks passing, including local-only entities, internal reference resolution, unique IDs, lane confinement and record counts `69 local entities / 58 evidence / 31 assertions / 5 works`.

This is useful proposal-integrity evidence, but the validator is self-defined under a provisional schema and is not equivalent to the future accepted repository admission validator.

## Findings

### AUD-TNG-B001-001 — governed coverage dependency order is violated by the proposed state vector

**Verdict:** CONFIRMED  
**Severity:** HIGH for promotion; LOW for preservation as worker-effort metadata

For all five works, `coverage_update.json` proposes:

- `DISCOVERED = true`
- `SOURCE_BOUND = false`
- `FULL_TEXT_AVAILABLE = true`
- `STRUCTURALLY_INDEXED = true`
- `CLOSE_READ = true`
- `SEMANTICALLY_ANALYZED = true`

The file carefully qualifies that the later states describe completed proposal work over complete third-party transcript representations and that `SOURCE_BOUND` remains false because the Librarian registry does not exist.

That explanation makes the worker effort honest, but it does not make the vector a legal governed coverage transition. The Project method's depth ladder is ordered:

`DISCOVERED -> SOURCE_BOUND -> FULL_TEXT_AVAILABLE -> STRUCTURALLY_INDEXED -> CLOSE_READ -> SEMANTICALLY_ANALYZED -> ENTITY_LINKED -> CROSS_REFERENCED -> AUDITED`.

A governed projection therefore must not directly import this boolean vector with downstream states true across a false `SOURCE_BOUND` gate.

**Recommended resolution:** preserve these booleans, if useful, as proposal/worker-processing observations. After Librarian Work/Source binding exists, recompute the governed coverage transitions from accepted evidence instead of promoting this vector wholesale.

---

### AUD-TNG-B001-002 — adversarial semantic sample preserves source-relative framing and identity uncertainty

**Verdict:** CONFIRMED  
**Severity:** POSITIVE CONTROL

Blind/high-risk sampling focused on cases that commonly produce ontology leakage:

#### Encounter at Farpoint

The batch separates:
- Q's accusations and courtroom claims from objective world-state truth;
- holodeck presentation/materiality from a universal holodeck ontology;
- the Farpoint station/lifeform explanation as an episode-local interpretive inference supported by converging evidence;
- initial vessel classification from later epistemic revision.

No global identity merge is attempted.

#### Code of Honor

The batch separates:
- the holodeck opponent's explicit simulated/nonliving status;
- Picard/Data's Prime Directive and cultural analysis as their institutional reasoning;
- Crusher's reported observation of Yareena's death/restoration;
- the local legal consequence Picard argues follows from death;
- metaphysical personal continuity after revival, which remains `UNRESOLVED`.

This is exactly the sort of distinction the Project method requires rather than converting legal/medical dialogue into an omniscient identity verdict.

#### Where No One Has Gone Before

The batch separates:
- the Traveler's causal role as an episode-local interpretive attribution rather than unquestioned mechanism;
- thought/reality coupling as an altered-reality frame;
- Picard's deceased mother as a manifestation rather than resurrection evidence;
- the Traveler's post-return existence as `UNRESOLVED`;
- the Traveler's temporal origin as `UNRESOLVED`.

Independent transcript readback materially supported these sampled representations. No sampled assertion required rejection for world-state, simulation, identity or testimony leakage.

**Sampling limitation:** three high-risk works/cases were semantically audited, not every one of the 58 evidence records. This is an adversarial sample and is not a population error-rate estimate.

---

### AUD-TNG-B001-003 — source-provider crosscheck must not become pseudo-corroboration

**Verdict:** CONFIRMED  
**Severity:** HIGH if promoted incorrectly

The manifest lists Springfield! Springfield as the complete transcript provider and Chakoteya as a crosscheck provider while explicitly recording `lineage_independence = UNKNOWN` and `primary_audiovisual_verified = false`.

That is the correct current classification. A later normalizer must not turn the two provider names into two independent witnesses unless the Librarian establishes independent provenance families.

**Recommended resolution:** bind exact transcript source variants and lineage through the Librarian. Until then, provider crosschecking supports routing/consistency checks but carries no independent-corroboration multiplier.

---

### AUD-TNG-B001-004 — provisional numbering ambiguity is preserved rather than silently canonicalized

**Verdict:** CONFIRMED  
**Severity:** POSITIVE CONTROL

The batch records differing conventions around the feature-length premiere and uses local aired-title sequence references while preserving provider transcript indexes and production-code crosschecks. It explicitly refuses to claim a global canonical numbering resolution.

This is suitable staging behavior pending Librarian Work identities.

## Admission disposition

**Preserve the proposal bytes. Do not promote this batch directly into accepted governed coverage.**

Before governed conversion:
1. accepted architecture/schema/validator state must exist;
2. Librarian must bind the five Work identities and transcript Source variants/provenance families;
3. the worker records must be normalized against that accepted schema;
4. coverage transitions must be recomputed with `SOURCE_BOUND` as an actual prerequisite;
5. accepted validation must run over the normalized records;
6. only then should coverage advancement be proposed.

The sampled semantic work is strong enough to justify preservation and later normalization. The current blocker is governance/source binding, not a demonstrated need to redo the sampled close reading.

## Exact next frontier

For TNG PR #3, no further audit is high-value until either:
- the proposal head changes materially;
- Librarian bindings appear;
- architecture admission rules become accepted; or
- a normalization/promotion successor is proposed.

Repository-wide Auditor priority should move to a distinct unresolved risk archetype rather than repeatedly auditing staging packets with the same blocker.
