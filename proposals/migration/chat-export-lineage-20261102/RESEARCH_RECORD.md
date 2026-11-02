# Chat-export provenance and legacy-work lineage — 2026-11-02

**Role:** MIGRATION. **Status:** PROPOSAL ONLY; no accepted episode evidence or coverage effect.

## Exact supplied artifact

| Property | Observed value |
| --- | --- |
| Local owner-supplied ZIP | `Trek Data Core.zip` |
| ZIP byte length | `2663954` |
| ZIP SHA-256 | `c6f9018ab748a3b53ba968ba5c4225681df9759ee748dd73679df42fbc49b2d6` |
| Member 1 | `Trek Data Core.html` — 128,726 uncompressed bytes |
| Member 2 | `images/file_00000000b8e881f5a977eeab7f220a5a.png` — 2,534,888 uncompressed bytes |
| ZIP integrity | `unzip -t`: both entries OK |
| Observed HTML messages | 22 user, 37 assistant; 59 total |
| Conversation's visible date range | 2026-11-02, approximately 05:44–12:51 (displayed local times) |
| Accepted `main` inspected | `c7a14ddb62dfa45d5d01855952d9e562c1af21de` |

The archive was inspected as a read-only ZIP: bounded archive size, two explicitly listed regular members, no extraction and no execution of embedded HTML or scripts. Neither the HTML conversation nor the PNG is a full audiovisual/literary primary Star Trek source. This proposal does not reproduce the copyrighted image or export the conversation into the public corpus.

## What the export actually establishes

The export is a record of a **single same-day repository-building conversation**, not an archive of earlier full-show close reads. Its messages primarily concern the README artwork and wording, Mission/Mission Briefing terminology, branch topology, GitHub Pages Explorer, metadata lead ingestion, admission safeguards, and OPF intake tooling. It **does not contain complete episode viewings, timecoded first-party episode notes, or detailed local Entity → Evidence → Assertion records for every show**.

The table distinguishes statements **made inside an exported conversation** from repository state independently inspected at the specified `main` head. An assistant's report inside a chat is not itself source or runtime verification.

| Exported statement, summarized | Evidence class | Independent local cross-check | Safe conclusion |
| --- | --- | --- | --- |
| Branches were highly converged; 190 branch names and 132 accessible historical PR heads; many past `research/` paths | Chat assistant report; repo report | `reports/branch-census-2026-11-02.json` has `summary.total_branches_including_main=190`, `accessible_pr_head_refs=132`, `research_paths_in_pr_heads=398` (report built against earlier `4681b637...`, not today's immutable re-enumeration) | A substantial **historical recovery lead** exists. Counts of paths and refs are **not** counts of completed/source-read episodes. |
| Episode discovery proposals added Wikidata-derived candidate leads across Missions | Chat assistant report | Current `git log` includes candidate importer `#161`, 180-lead proposal `#169`, and 218-lead integration `#185`; accepted current-readiness tool reports 0 admitted nonfixture episode Works | Discovery metadata exists; it does not prove full episode ingestion. |
| A public Explorer renders Missions separately from admitted Briefings and unverified research leads | Chat assistant report | Current repository includes Explorer code, tests and README; release state requires a separate live-system probe | Source supports an implemented interface, but the export alone is not proof of the live release. |
| OPF intake processed 347 files with 15 XML cases flagged | Chat assistant runtime claim | Accepted `main` has private OPF ingestion tools, tests and merged `#173`/literary follow-ups; private original ebook files and run outputs are absent from this ZIP | Preserve **reported historical intake** as a lead. Do not treat reported 347 as independently replayed or books close-read. |
| 218 candidate leads and **0 admitted Mission Briefings** | Chat assistant report | Accepted `main` candidate/index code and `tools/check_episode_pilot_readiness.py`: 0 accepted nonfixture episode Works and no approved projection hashes at this checkpoint | Current **admission** is blocked, but historic research may still be recoverable in PR heads. |
| Source-review packet workflow was merged as `#188` | Chat assistant report | `git log` contains `ec12836 feat: introduce fail-closed episode research review packets (#188)` | A review tool exists; it is not an admission or proof of completed source reading. |

## Falsifiers, gaps, and reconciliation holds

> **Hostile review:** The archive contains confident assistant progress reports, not independent primary-source evidence of full-series close readings. In particular, `218 research leads`, `398 historical research paths`, or `347 OPF records` cannot be promoted into episode semantic coverage by counting them.

> **Separate hostile review:** Conversely, the absence of close reads **in this exported conversation**, or the current zero-admission readiness state, does not show that earlier research never occurred. Historical PR-head files and independently stored work may contain substantive research. Rejecting them without inspection would risk destructive history loss.

Patrick's current report that every show was analyzed/ingested earlier is an **owner-supplied historical claim to investigate**; it is not contradicted merely by the latest accepted coverage ledger. The export itself is not the earlier research, and its scope is too narrow to confirm or refute that claim per show.

The 2026-11-02 branch-census JSON's `historical_research_paths_by_lane` records a particularly large number of TNG paths, plus DS9, Prodigy, Starfleet Academy, Short Treks and other lanes; the lane distribution is uneven and may reflect staging/directory paths rather than unique analyzed works. The independent PR-head artifact census and content-quality sampling must distinguish these possibilities.

## Migration handoff

1. Match chat-mentioned PRs `#156`, `#161`, `#169`, `#175`, `#178`, `#185`, `#188`, `#189` to actual immutable Git commits/PR-head blobs (never infer accepted evidence from PR title).
2. Have the branch/PR-head recovery lane identify actual retrievable per-show files and their SHA-1 Git blob IDs. The accepted branch-census snapshot is a **lead**, not current complete content inventory.
3. Have the separate content-quality lane sample full historical research files, recording actual source locators, evidence frames, unsupported synthesis, source access and preference contamination; quarantine fabricated/recap-only legacy work rather than deleting it.
4. Rebind genuine recoverable observations into `Source → Work → Local Entity → Evidence → Assertion`, with explicit exact-edition access/custody and an independent admission decision. Keep existing accepted coverage at zero until all gates pass.

No source works, global identity state, accepted records, coverage counters, commits, branches, PRs, deployments, or credentials were changed by this migration witness.
