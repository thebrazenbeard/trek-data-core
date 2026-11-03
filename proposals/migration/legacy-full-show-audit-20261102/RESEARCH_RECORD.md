# Legacy Star Trek research recovery — ref/tree inventory (2026-11-02)

**Role:** MIGRATION. **Status:** PROPOSAL ONLY / UNTRUSTED HISTORICAL WORK.
**Accepted `main`:** `c7a14ddb62dfa45d5d01855952d9e562c1af21de`.
**Effect:** No accepted Source, Work, evidence, assertion, reconciliation, coverage, denominator, or public projection changes.

## Why this audit exists

Patrick reports that *every Star Trek show* was previously researched and ingested. This is a report of historical work, not automatically evidence of present accepted coverage. Equally, the absence of admitted Briefings on today's `main` does **not** establish that earlier work never existed. The migration job is to find its surviving artifacts, distinguish content from progress claims, and preserve useful research for source-neutral revalidation.

## Live Git object census

Captured anonymous GitHub refs in a **disposable, no-checkout partial clone** at `/workspace/scratch/2644a2e09e43/trek-data-core-history-audit`. No historical code, task, hook, or editor workspace was run. Exact remote ref populations were fetched to disjoint `refs/trek-audit/branch-heads/*` and `refs/trek-audit/pr-heads/*`. The repository's `tools/audit_git_topology.py` reported:

- **169 accessible PR head refs** (vs. 132 in the accepted 2026-11-02 earlier census); **193 non-main branch refs**.
- **397 actual nested historical research paths** in the strict governed inventory; the broader topology census additionally counts the shared `research/README.md` landing document, yielding **398 raw paths**. All current accepted `main` paths under `research/` are absent in the audited main tree.
- **740 distinct historical paths** in all PR heads, **59 contested paths** across *all* path types. This is **not** the count of analyzed episodes.
- Current nested research proposal paths have **397 distinct Git path/object variants, 0 conflicts among those 397 path versions, 0 matching byte-identical paths on current `main`**. No unsafe object modes among those nested research paths. This only checks Git trees; the blobs have not all been inspected for source quality.

**Corrected strict inventory now passes.** Initially `tools/inventory_historical_research.py` rejected a legitimate top-level `research/README.md` present in 37 PR-head trees. The migration tooling has since been corrected to recognize that document as a non-lane landing page without treating it as research content. Re-running the **unmodified CLI** on the pinned audit clone with all 169 PR refs succeeds: **397 nested research paths, 397 object variants, zero contested or unsafe variants**. Reproducible strict manifest SHA-256: `5e8797303f6234477c279043ba8c0c38fed7f1cecab9ed83219492bb9375e360`. The earlier read-only exclusion diagnostic produced the same digest but is superseded by the corrected strict run.

## Recoverable paths by lane (PR-head tree evidence)

| Lane | Distinct `research/` paths | PR heads containing them | Observed path type |
| --- | ---: | --- | --- |
| TNG | 297 | #3, #12, #21, #36, #44, #49, #54, #58, #62, #69, #75, #80, #84, #86–89, #128–137, #139–150 | 285 staging files, plus a 12-file S1 batch including 9 structured record JSONs, manifest, coverage claim and validation artifact |
| DS9 | 33 | #2, #9, #20, #30, #35, #39, #42, #46, #48, #50–51, #56–57, #60, #63, #66, #70, #73, #77, #79, #81, #83, #85, #101–103, #105–106, #120, #122–124, #126 | Mostly staged batch `README.md` files; substantive content must be inspected |
| Prodigy | 21 | #11, #93, #109–114, #117, #119 | Staging proposals and validation/index notes |
| Starfleet Academy | 18 | #6, #18, #22, #34, #37 | Staged per-installment reports and status files |
| Short Treks | 13 | #7 | Staged individual reports, manifest and status |
| Enterprise | 4 | #10, #94, #100 | Staged named-episode reports |
| TOS | 3 | #17, #99 | Startup/source-lane notes |
| Literature | 5 | #16, #98 | Startup audit/admission/frontier documents |
| Discovery | 1 | #96 | Lane sync note |
| TAS | 1 | #97 | Lane sync note |
| Films | 1 | #13 | Startup audit note |
| Voyager, Picard, Lower Decks, Strange New Worlds | **0 nested paths in current reachable PR-head trees** | Not established by this tree census | Their named branches can exist without unique surviving per-episode tree files; inspect branch history, non-`research/` paths, chat exports and other custody before declaring legacy work absent |

`research/tng/batches/tng-s01-b001/` on PR #3 is a particularly concrete recovery target: `records/01-encounter-at-farpoint.json`, `02-the-naked-now.json`, `03-code-of-honor.json`, `04-the-last-outpost.json`, five structured files for `05-where-no-one-has-gone-before`, plus `manifest.json`, `coverage_update.json`, and `validation.json`. **These are extant Git objects, not a verified finding that source episodes were actually processed.**

## Inert historical blob sampling (internal migration review)

Two separate migration reviewers subsequently read historical Git blobs as **data** (no old code execution). Their observations substantiate *real authored source-relative work* in several lanes beyond branch names. They do **not** independently authenticate the old external transcript bytes or show that the original audiovisual editions were watched. Concrete recovery anchors:

| PR | Git blob / path | Historical content observed | Outstanding source/admission limit |
| --- | --- | --- | --- |
| #3 TNG | `61159536b7a1e0cca85112a00d5b211b55e9c150` — `research/tng/batches/tng-s01-b001/manifest.json`; `dab9822a52ff9ed5045d0a783ee21ba486151b7d` — `records/02-the-naked-now.json` | Manifest *claims* five third-party transcript-derived installment reads, 58 line-located observations/evidence, 31 supported assertions and 69 local entities; sampled `The Naked Now` record actually contains 12 granular observations and 6 support-linked assertions. | Transcript content SHA absent; original AV not verified, claims in manifest still need independent review. |
| #2 DS9 | `5ece6c5cdb6fa0f35dd651d9261561cdedd53091` — `research/ds9/staging/ds9-s1-opening-five/README.md` | Substantial five-episode structured transcript-relative notes, with URLs and explicitly recorded source/header-body offset issue. | No preserved raw source digest or accepted binding. |
| #11 Prodigy | `d749e0098ac76a42157b2a0262d6e8db22f41645` — `research/pro/staging/pro-s1-opening-five/README.md` | Five installment source-relative notes and segmentation uncertainty with named external transcript services. | Primary AV and raw-byte custody unverified. |
| #18 Starfleet Academy | `81b8ac10d0958b09e7f5faceeefd66d2428a0398` — staging `README.md`; `b3f9d672392ea045a9bc2dbec47ca492dd9ef9aa` — `KIDS_THESE_DAYS.md` | Claims five close-read installments; sampled episode note includes around 30 labeled observations and 15 assertions. | Some evidence lacks individual line locators; no raw-source/AV digest. |
| #94 Enterprise | `720ad093090e352f076cf23244330d063fc6b0c6` — `research/enterprise/staging/ent-s1-strange-new-world/README.md` | Detailed, transcript-derived close read with evidence, assertions and counterevidence. | Chakoteya third-party transcript source; no recorded source SHA or AV verification. |
| #96 Discovery | `01e124a0998094d881eee25afb42029e0e51afcd` — `research/dis/staging/DISCOVERY_LANE_SYNC.md` | Lane sync enumerates 25 prior proposed source-read installment receipts in five tranches (S1–S2). | Sync is a retrospective claim/locator, not itself the underlying 25 source observations or source custody. |
| #97 TAS | `ad1cd17c0935cb88fa6cadf0ca4952798e0390d2` — `research/tas/staging/TAS_LANE_SYNC.md` | Enumerates 22 proposed source-relative Works, 177 entities, 160 evidence, 119 assertions across five historical branches. | Historical counts must be reconstructed from original records; no accepted binding or AV hashes. |
| #100 Enterprise | `28bb3b93e383a2124e8d35906b315abaaf076051` — `research/enterprise/sync/ENT_LANE_SYNC.md` | Lists seven distinct staged Works and notes duplicate historical branch variants. | Work identity/editions and actual source bytes need revalidation. |
| #99 TOS | `45fc16337f1a17793231d7350daf7e1cf79cbbd0` — TOS sync note | Explicitly reports **no completed TOS close-read** at that checkpoint despite earlier lane titles. | This is a useful falsifier of a universal completed-content claim for that exact historical checkpoint, not proof no later/other TOS work existed. |
| #137 TNG | `e03bafdfd798bb75e81db923fbb9cbbf5e45be49` — `05-the-inner-light.md`; `13f04167dfbdf6681fcbbca3668b7449e4118d44` — associated `validation.json` | Numbered external-transcript-relative locators and observations; local validation claims 50 evidence and 25 assertions. | Local self-validation is not independent source authentication or admission. |

This sampled material materially changes the migration priority: **recover and revalidate existing authored episode observations first**, rather than rebuilding every series from a blank slate. No review upgrades an old claimed completion counter into an accepted coverage event.

## Other available history and its limits

- Current Git branch names explicitly span additional lanes and batches (e.g., VOY, PIC, LD, SNW, TAS). Many present heads resolve to the same consolidated commit, so names alone cannot recover the old branch-tip payload or certify historical source reads. PR-head objects are a stronger but incomplete recovery path.
- The supplied `Trek Data Core.zip` (`SHA-256 c6f9018ab748a3b53ba968ba5c4225681df9759ee748dd73679df42fbc49b2d6`) contains a 128,726-byte HTML ChatGPT conversation export and a 2,534,888-byte PNG. A separate migration crosswalk in `proposals/migration/chat-export-lineage-20261102/RESEARCH_RECORD.md` identifies 59 messages from November 2. They describe architecture, candidate indexing and admission, but do **not** themselves contain complete per-show close reads; this ZIP is **not** a complete export of all prior source research. Do not transmute chat progress claims into ledger facts.
- `reports/branch-census-2026-11-02.json` was collected at earlier main `4681b637ec9052b704283a83ec5d8d07d3fa6a79` with 132 accessible PR heads and 398 raw `research/` paths, including the landing README. The refreshed live strict count is 397 *nested* research paths across 169 PR heads; these denominators are not competing claims.

## Migration frontier and falsifiers

1. Expand the already-started **inert-data blob sampling** to an exact manifest of every recoverable record, starting with PR #3 TNG structured batch and representative DS9/PRO/SFA staged reports. Preserve the Git blob OID, original path, PR number, source/edition locator, raw evidence vs interpretation, asserted source-access basis, and correction history. Do not run any old repository code or tasks.
2. Seek original full-source/edition custody outside the public repository. An episode title, summary, transcript reference, invented episode-confidence score, or prior completion claim is not proof of actual source inspection.
3. Compare staged records with current schema and neutral coding. Retain independent contradictory variants, fake/synthetic markers, and preferences contamination; propose explicit migrations and crosswalk decisions under versioned review.
4. Search historical branches *by commit graph and non-`research/` files*, and recover older chat exports/host artifacts if actually accessible. **Unknown** whether the all-shows historical work remains accessible from the Git refs inspected here.
5. Keep the now-corrected strict-inventory parser and its adversarial top-level README regression under CI; treat the reproducible manifest as a **historical proposal inventory**, never as independently admitted source evidence.

> **Hostile challenge:** A high file count or a rich-sounding batch name can hide metadata-only, speculative, derivative, fabricated, or preferences-driven entries. Even real authored files do not prove complete episode inspection. Conversely, missing Git PR-head files do not prove earlier work was never done. Both directions must be tested against actual source-edition evidence and custody.

### Verification commands (read-only)

```bash
python3 tools/audit_git_topology.py --repo /workspace/scratch/2644a2e09e43/trek-data-core-history-audit
python3 tools/inventory_historical_research.py --repo /workspace/scratch/2644a2e09e43/trek-data-core-history-audit --expected-main-sha c7a14ddb62dfa45d5d01855952d9e562c1af21de
git -C /workspace/scratch/2644a2e09e43/trek-data-core-history-audit ls-tree -r --name-only refs/trek-audit/pr-heads/3 research/tng/batches
git -C /workspace/scratch/2644a2e09e43/trek-data-core-history-audit ls-tree -r --name-only main research
```

Some historical blob content was **internally sampled and classified**; independent source-edition custody, full-source verification and admission remain **NOT_PERFORMED**. No GitHub mutations or local canonical research edits were made.
