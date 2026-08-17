# Star Trek: Prodigy worker-staging proposal index

Status: **PROPOSAL / STAGING ONLY — NOT ACCEPTED COVERAGE**  
Lane: **PRO**  
Synchronized against accepted `main`: `007641c57933dda222489fff56555f6968ff2a53`  
Synchronization date: 2026-08-17

## Purpose

This index is the operational handoff for the Prodigy research lane. It records what this worker actually full-source processed and where the proposal artifacts live. It does not promote proposal branches into accepted state, mint canonical Source/Work IDs, reconcile global identities, or claim downstream coverage tiers that have not occurred.

Accepted `main` still does not contain the proposed research architecture, an accepted Librarian-owned Prodigy Source/Work registry, a governed predicate registry, a Prodigy coverage ledger, or an accepted PRO batch. Therefore every item below remains staging/proposal research.

## Current released-work denominator checked

Current official StarTrek.com material lists **2 seasons** of `Star Trek: Prodigy`. The official Season 2 release contains 20 episodes. Combined with the official Season 1 numbered inventory, the current released audiovisual denominator is **40 numbered episodes**.

No released Season 3 work was found in the current official series inventory at this synchronization checkpoint.

Important: this denominator is used only to describe worker-staging source-read completeness. It is not a substitute for the Librarian's future accepted WORK registry.

## Worker-staging source-read status

### Season 1 — all 20 numbered episodes source-read

The opening source has a real segmentation disagreement: some complete transcript providers expose `Lost & Found (Part 1, Part 2)` as one combined source page while other inventories expose separate 1x01/1x02 records. The research packet preserves this instead of selecting a canonical Work split.

| Worker packet | Numbered episode coverage represented | Source-read result | Proposal |
|---|---|---|---|
| S1 B001 | 1x01-1x06, represented by five titled transcript pages because the premiere is combined | COMPLETE at worker-staging close-read level; premiere segmentation UNRESOLVED | PR #117 |
| S1 B002 | 1x07-1x11 | COMPLETE; former `Asylum` source blocker resolved by later complete transcript retrieval | PR #93 |
| S1 B003 | 1x12-1x16 | COMPLETE | PR #109 |
| S1 B004 | 1x17-1x20 | COMPLETE | PR #110 |

Historical provenance: closed PR #11 is the original opening-five proposal from an older `main` base. Its exact 339-line research README blob was reused byte-for-byte in B001 (`d749e0098ac76a42157b2a0262d6e8db22f41645`) rather than rewritten. PR #11 remains closed/unmerged and is not a second independent research batch.

### Season 2 — all 20 official works source-read

Official Work titles follow StarTrek.com rather than subtitle-upload filenames. Alternate source labels are preserved as source-variant metadata only.

| Worker packet | Official works | Source-read result | Proposal |
|---|---|---|---|
| S2 B001 | 2x01-2x05 | COMPLETE | PR #111 |
| S2 B002 | 2x06-2x10 | COMPLETE | PR #112 |
| S2 B003 | 2x11-2x15 | COMPLETE | PR #113 |
| S2 B004 | 2x16-2x20 | COMPLETE | PR #114 |

Notable filename/title variants preserved include `The Mystery Spiral` / `Observer's Paradox`, `The Race` / `The Fast and the Curious`, `Veritas` / `Is There in Beauty No Truth?`, `The Time Devouring Scavengers` / `The Devourer of All Things`, `A Tribble Called Bridule` / `A Tribble Called Quest`, `The Mirror Universe` / `Cracked Mirror`, `The Ascent` / `Ascension`, `On the Brink` / `Brink`, and `Behind Enemy Lines` / `Touch of Grey`.

## Proposal branch heads at synchronization checkpoint

- `research/pro/pro-s01-b001-staging` — `080bb0c2ff7e3b1f304705c2171fadb1f01c1f2e` — PR #117
- `research/pro/pro-s01-b002-staging` — `cd259fb61c51a2803ce76d8bd6d18e2d8024f827` — PR #93
- `research/pro/pro-s01-b003-staging` — `2d4df887da490384a8c3c2675371fb3ee42efb92` at PR creation; subsequent PRO-only provenance/PR-scope housekeeping exists on the same branch and must be read from the branch head before admission — PR #109
- `research/pro/pro-s01-b004-staging` — `032a6aed68f849809b257d538bc954dfe5d39c93` — PR #110
- `research/pro/pro-s02-b001-staging` — `7daa23c4c52fa1bb76e0f982326f452c285942cd` — PR #111
- `research/pro/pro-s02-b002-staging` — `bdaefbc1eb77151a3de89e0b4e3c64f2e9ee2b6c` — PR #112
- `research/pro/pro-s02-b003-staging` — `07cfebdac57bf3a50d8f17412a6233e756b448d2` — PR #113
- `research/pro/pro-s02-b004-staging` — `1f0aaa9ec0abf00208d7aecf8421f0a4fce34fd4` — PR #114

Because repository state can move, these SHAs are checkpoint identities, not eternal aliases. Admission tooling should inspect actual PR/branch heads rather than assume this file is newer than Git.

## High-value identity/frame regressions now represented in PRO staging

The close-read corpus deliberately preserves at least these cases for later reconciliation/audit:

1. Hologram Janeway versus physically present Vice Admiral Janeway.
2. Hologram Janeway inherited biography/institutional knowledge versus lived autobiographical experience.
3. Construct-compromised Hologram Janeway agency versus enduring program/personality state.
4. Season 1 failed Janeway portable-copy attempt versus Season 2 successful full-program EMH-backup copy.
5. Preserved full-memory Hologram Janeway backup versus reset historical Protostar Janeway instance.
6. Holodeck legacy-character simulations versus physical legacy-character occurrences.
7. Holographic duplicate youths versus simultaneously existing physical originals.
8. Holo-Gwyn's Loom trauma/memory versus physical Gwyn's evidence stream.
9. Zero versus Zero's containment suit/interface presentation.
10. Zero under temporary Borg collective domination versus later self-directed agency.
11. Zero's noncorporeal existence, temporary Ovidian organic embodiment, loss of that body, and later Jankom-designed replacement embodiment.
12. Dal/Admiral Janeway neural-pattern/body swap and later restoration.
13. Murf metamorphic body states with continuing local relational identity.
14. Dal's engineered hybrid origin and temporary epigenetic trait expression without serial person replacement.
15. Planet-generated desire/lure representations versus the persons/objects represented.
16. Recorded/archival Chakotay versus physically present Chakotay.
17. Future-origin Chakotay recording versus present physical actor.
18. Earlier Ilthuran versus later Diviner worldline states.
19. Younger Asencia versus future-origin Vindicator occurrence and public/covert role states.
20. Mission names/titles such as Diviner/Vindicator as role identities rather than automatic person replacement.
21. Temporal phase-relative deaths in `Time Amok` versus globally final death/resurrection.
22. Present peaceful Solum versus future-war Solum.
23. Altered-history Gwyn superposition/displacement and temporary stabilizer dependence.
24. Loom erasure that changes records/memory versus ordinary death.
25. Protected witnesses retaining evidence from rewritten history.
26. Alternate-reality deaths and world states versus prime-history facts.
27. Mirror counterparts versus prime persons.
28. Dal's deliberately placed combadge and returned Protostar as loop-closing causal artifacts.
29. Enderprizian stage/cultural Starfleet representations versus historical Starfleet events/institutional sameness.
30. Starfleet status transitions: asylum request, training/warrant-officer path, probation/assignment, and later field commission as ensigns.

These are research fixtures/candidates, not accepted global reconciliation outcomes.

## Source/provenance limits that remain

- Complete third-party transcript/subtitle bodies were used for close reading; primary audiovisual media was not directly verified by this worker.
- Canonical source hashes, editions/variants, retrieval snapshots and independence groups remain Librarian responsibilities.
- Multiple transcript/subtitle providers may share upstream lineage; repeated wording was not treated as independent corroboration.
- The Season 1 premiere segmentation remains unresolved at the canonical WORK level.
- Some Season 2 uploaded subtitle filenames do not match official titles; the mismatch is preserved rather than normalized away without provenance.
- No full copyrighted transcript/subtitle body has been committed to the public repository.

## What is complete versus not complete

### Complete at PRO worker-staging level

- current released two-season inventory checked against official StarTrek.com material;
- all 40 numbered episodes processed from complete transcript/subtitle bodies;
- local entity/state candidates recorded;
- source-relative evidence notes recorded;
- candidate assertions linked conceptually to evidence inside each packet;
- explicit counterevidence/uncertainty recorded;
- proposal branches created;
- manual staging validation performed;
- draft PRs opened/reopened for every active current-main-based packet;
- original opening packet provenance synchronized without rewriting its research blob.

### Explicitly NOT complete / not owned by this worker

- accepted Librarian Source/Work binding and source hashes;
- governed JSONL record conversion under accepted schemas/predicate registry;
- batch manifests under accepted tooling;
- accepted coverage transitions on `main`;
- global identity reconciliation;
- deterministic projection/database integration;
- cross-work/global audit and acceptance;
- merge or other protected effects.

## Exact downstream frontier

There is no further released Prodigy primary-source episode left for this PRO worker to close-read under the currently verified official two-season inventory.

The next valid work becomes available only when one of the following changes:

1. the Librarian supplies accepted Prodigy Work/Source bindings and hashes, enabling deterministic conversion of these staging packets into governed research records;
2. accepted schemas/predicate registry/tooling land on `main`, enabling validation/manifests and an honest coverage transition proposal;
3. a new official Prodigy audiovisual work is released/entered into the accepted Work registry;
4. an Auditor/Consolidator returns a specific PRO-lane correction requiring source reopening.

Until then, claiming further PRO research progress would mean inventing work or trespassing into another role.
