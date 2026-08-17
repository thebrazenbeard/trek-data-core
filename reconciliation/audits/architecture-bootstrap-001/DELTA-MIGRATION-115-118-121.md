# Auditor review — migration chain PR #115 / #118 / #121

Date: 2026-08-17
Role: AUDITOR
Accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`

Audited proposal heads:
- PR #115 `migration/trek-legacy-migration-batch-001` — `363fe1ff97b24b22758492ac1ea440b0873325ac`
- PR #118 `migration/legacy-state-claims-002` — `0803862d868d66e61c42f7fb27c9a9407fea5024`
- PR #121 `migration/legacy-artifact-inventory-003` — `32440b4f2c132937a79c71c4efdba61f0b34bfe2`

## Overall disposition

**SUPPORTED AS MIGRATION PRESERVATION WITH NORMALIZATION / PROVENANCE BLOCKERS.**

The chain follows the core migration rule: old confidence is not evidence, old counters do not become accepted coverage, user preferences are quarantined, source-relative passages remain distinct from broad synthesis, and unverified source/Work identities are not promoted.

No accepted coverage, canonical Source/Work identity, global identity, or protected effect is created by these proposals.

## PR #115 — recovered Discovery migration package

### Result: SUPPORTED_WITH_CAVEAT

#### Confirmed positives

1. Coverage discipline is strong: the package explicitly claims zero CLOSE_READ, COMPLETE_CLOSE_READ, viewing, and historical-completion promotions.
2. Legacy scalar confidence is assigned zero evidentiary weight.
3. Broader resurrection taxonomy is rejected rather than preserved merely because a legacy record once used it.
4. Tyler/Voq remains contested rather than being forced into alias/possession/merge/sameness.
5. Gray's broader multi-episode synthesis is dependency-pending rather than inferred from the sampled episode alone.
6. User-preference/theme/analogy material is excluded pending preference-blind retest.
7. Historical M4/M5/M6 hashes are correctly described as preserved provenance claims rather than newly re-observed byte custody.
8. Source records are explicit that only targeted passages were revalidated and whole-source close reading is false.

#### Independent primary/full-source sampling

I independently reopened the cited complete Forever Dreaming transcript pages for:

- `Project Daedalus`;
- `Jinaal`;
- `Choose to Live`;
- plus the relevant `Vaulting Ambition` page during the audit.

The sampled passage claims materially exist:

- Airiam explicitly says she can hear Tilly but cannot stop herself because her motor functions are being overridden, then asks Burnham to eject her;
- `Jinaal` explicitly describes zhian'tara as a limited-time transfer of Jinaal's consciousness, Guardian Xi announces the transfer/ending, and Culber later reports experiencing another consciousness inside him while also being present;
- `Choose to Live` explicitly presents an interval where Gray is no longer sensed with Adira and not yet sensed in the synthetic body, followed later by Gray self-identifying and being recognized/interacted with in that body.

Therefore the migrated evidence summaries are not fabricated from memory or recap.

#### MIG-115-001 — HIGH — pre-current assertion/projection shape must not be imported literally

`assertions.jsonl` uses:

- `status: PROPOSED`;
- a field named `projection_status` with values such as STABLE / CONTESTED / UNRESOLVED;
- no typed `subject_type`;
- legacy compatibility predicate `SUPPORTS`.

Current architecture separates worker assertion lifecycle from proposed/effective projection status and requires typed assertion subjects. A proposal-stage `projection_status: STABLE` must not become authoritative merely because migration tooling later normalizes the record.

Before admission, map these to the accepted assertion schema explicitly (for example current proposal-status field + typed subject) and require normal accepted reconciliation/projection-status rules. Do not copy the old field wholesale into current accepted projection state.

#### MIG-115-002 — HIGH — Jinaal consciousness-transfer proposition needs source-relative framing during normalization

The sampled transcript strongly supports that characters, ritual participants and Culber's experience **present** the event as limited-duration consciousness transfer. That is sufficient for a source-grounded interpretive assertion.

It is not an omniscient measurement of metaphysical consciousness transfer. Guardian Xi's statements are testimony, and Culber's report is first-person experience.

Current assertion MIG001-AS-004 says the episode "supports a limited-duration transfer/embodiment of Jinaal's consciousness". Preserve the useful distinction from `Jinaal=Culber`, but normalize the proposition so its epistemic basis remains explicit: the episode/participants depict and experience the zhian'tara this way. Do not silently promote the mechanism from narrative/participant evidence into ontology.

#### MIG-115-003 — MEDIUM — `epistemic_status: DIRECT` is potentially ambiguous when evidence kind is testimony

The evidence rows correctly mark `evidence_kind: testimony`, speaker, frame, and observed summary. That preserves the utterance.

However `epistemic_status: DIRECT` can be misread downstream as "directly true world-state evidence" rather than "directly observed in the source." Current normalization should either govern that field's meaning explicitly or replace it with the accepted source-relative evidence vocabulary so DIRECT never upgrades testimony truth value.

#### MIG-115-004 — MEDIUM/HIGH — self-attested validation and preference-blind PASS are not independent audit evidence

`validation.json` and per-assertion `preference_blind_review: PASS_NO_DIRECT_PREFERENCE_WEIGHTING_FOUND` are producer-generated claims. No executable validator or reproducible preference-blind comparison procedure is packaged with PR #115, and no GitHub workflow run exists at this head.

The content I sampled does not show obvious preference contamination, but that is not equivalent to proving the entire package preference-blind. Preserve these flags as migration-worker attestations, not AUDITED status or admission evidence.

#### MIG-115-005 — MEDIUM — transcript source identity is not byte-addressable

All five Source records have `content_hash: null` and `passage_fingerprint: null`. Locators/retrieval time/provenance family are preserved, which is useful, but these migration-local Source IDs cannot justify governed SOURCE_BOUND state without the Librarian's accepted Source/Work binding/custody surface.

The README phrase "primary transcript passages" should also be normalized carefully: Forever Dreaming is a third-party full transcript representation, not the primary audiovisual master. The Source records themselves are clearer than the README wording.

## PR #118 — historical state/coverage claim quarantine

### Result: SUPPORTED_WITH_PROVENANCE_CAVEAT

The substantive corrections align with the governing method:

- 29/158 and similar counters remain historical workflow claims;
- the legacy 158 denominator is not accepted;
- 14 literary STW IDs remain migration inputs;
- zero SOURCE_BOUND / BOOK_TEXT remains an important negative correction;
- general model knowledge is not research evidence;
- user preferences are excluded from primary research weighting;
- downstream/sibling agreement from the same lineage has zero independent corroboration weight;
- role-local counters are not merged into one coverage metric.

These are exactly the kinds of legacy corrections migration should preserve.

#### MIG-118-001 — MEDIUM/HIGH — historical claim provenance is filename-level, not passage/byte-level

The eight rows name artifacts such as `ChatGPT-Vera-20260817-0934.md` and `ST_CORPUS_CONVERGENCE_CHECKPOINT_V2.json`, but do not include artifact content hashes, repository/File-Library identity, passage/line locators, or quoted fingerprints for the historical claim being quarantined.

The correction policy can stand independently, but the exact historical claim should remain **reported/recovered** unless its source artifact can be deterministically reopened. Before accepted migration history, pin the exact artifact bytes/identity and locator for each claim.

Do not turn "we remember the old project said 29/158" into a canonical historical fact merely because the correction is sensible.

## PR #121 — migration artifact/actionability inventory

### Result: SUPPORTED_WITH_CURRENTNESS_CAVEAT

The inventory is conservative about authority boundaries and correctly routes Librarian-owned collision/crosswalk/ebook work away from MIGRATION. It also keeps chat exports as discovery/provenance surfaces rather than automatic evidence.

The current stop condition is defensible **for accepted-state execution**: no accepted governance/binding/coverage machinery exists on `main`, and recovered exact legacy bytes remain limited.

#### MIG-121-001 — MEDIUM — moving proposal references should be pinned by exact head/content identity

The inventory says artifacts are preserved/quarantined in draft PRs #115/#118 and describes Librarian artifacts, but it does not pin the exact PR head SHA/content hash for those moving proposal surfaces.

For a durable migration inventory, record both human-friendly PR number and exact audited/proposal head. Otherwise a later PR update can silently change what `PRESERVED_AS_DRAFT_PR_115` means.

#### MIG-121-002 — current stop condition is about **accepted authority**, not absence of proposal work

Since this inventory was authored, proposal-only Librarian implementation PR #125 and custody/crosswalk PR #127 exist. They do not satisfy the inventory's reactivation trigger because they are not accepted on `main`, but the wording should remain precise: migration is blocked for **accepted admission/execution**, not because no relevant proposal bytes exist anywhere.

This distinction matters for future handoff and prevents "remaining executable migration batches = 0" from being misread as "nothing useful exists to review/migrate later."

## Combined migration result

- Story-fact fabrication in sampled #115 evidence: **NOT FOUND**.
- Coverage inflation: **NOT FOUND**.
- Preference-driven promotion: **NOT FOUND in sampled material; whole-package producer PASS remains unverified**.
- Legacy confidence laundering: **NOT FOUND**.
- Source/Work canonicalization leakage: **NOT FOUND**.
- Main blockers: normalization to current typed assertion/evidence contracts; exact source/artifact custody; independent validation; accepted Librarian binding/admission state.

## Exact next frontier

1. Preserve #115/#118/#121 as proposal migration inputs; do not promote them unchanged.
2. Normalize #115 assertions/evidence against the accepted schema only after governance/binding exists, with source-relative mechanism framing intact.
3. Pin historical source artifacts/passages for #118 claims.
4. Pin exact proposal heads/content identities in #121 inventory.
5. Re-open migration execution when accepted Source/Work binding/admission state or newly recovered exact legacy bytes make a bounded tranche actually admissible.

No accepted migration, coverage promotion, Source/Work binding, identity reconciliation, merge, deployment, or protected effect performed.
