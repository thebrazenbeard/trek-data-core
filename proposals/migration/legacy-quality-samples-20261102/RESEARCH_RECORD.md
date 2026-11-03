# Legacy Trek content-quality sampling: historical PR heads #1–90

Status: **MIGRATION PROPOSAL / READ-ONLY HISTORICAL INSPECTION**
Lane: `MIGRATION`
Date: 2026-11-02
Accepted baseline: `main` at `c7a14ddb62dfa45d5d01855952d9e562c1af21de` at inspection time.

## Question and method

Patrick reports that every Star Trek show was previously analyzed and ingested. Does retrievable historical repository content substantiate earlier per-episode analysis, or do its completion labels stand alone? This is a **sample of actual historical Git blobs**, not a fresh source-read, a complete portfolio census, or admission to the current evidence ledger.

I used the isolated read-only Git refs `refs/trek-audit/pr-heads/<N>` from public GitHub PR head objects and inspected selected *file contents*, not merely branch names. The sample covers DS9, TNG, Prodigy, and Starfleet Academy, primarily PRs #1–90. Other migration work separately owns the full ref/path census. The recorded OIDs are Git SHA-1 object identities, **not** content hashes of external copyrighted episode sources.

## Exact retrievable samples and quality assessment

| PR head | Historical path (relative to PR tree) | Blob Git OID | Observed contents | Migration classification |
|---|---|---|---|---|
| #3 `0695fb2d36870e9c156ce7acd16f00f70103b19e` | `research/tng/batches/tng-s01-b001/manifest.json` | `61159536b7a1e0cca85112a00d5b211b55e9c150` | Manifest identifies five episode transcripts, provider URLs and transcript line extents; declares 58 evidence / 31 assertions / 69 local entities; explicit unverified audiovisual/source-binding limits. | Structured legacy research candidate; counts are historical author declarations. |
| #3 same | `research/tng/batches/tng-s01-b001/records/02-the-naked-now.json` | `dab9822a52ff9ed5045d0a783ee21ba486151b7d` | Directly inspected and independently parsed JSON: 12 distinct source-aliased evidence observations (all with transcript line-range locators), six evidence-linked assertions, and 12 work-local entities; impaired Data testimony is not silently turned into physiological fact. | Strongest sampled migration candidate for structured evidence, pending source reacquisition and independent inspection. |
| #12 `e4c891b26622ae08eac346a55059a58f687d064c` | `research/tng/staging/tng-s01-b002/01-lonely-among-us.md` | `43c84929a0c3c24eb005f037f10a198fcdfcf595` | Ten numbered, line-located evidence observations and five support-linked staging assertions; cited Springfield transcript and Chakoteya crosscheck, clearly distinguished testimony/memory and transporter continuity ambiguity. | Detailed source-relative staging, not accepted canonical evidence. |
| #2 `114d96b41865eff37a309fea747e8a6404c3a512` | `research/ds9/staging/ds9-s1-opening-five/README.md` | `5ece6c5cdb6fa0f35dd651d9261561cdedd53091` | Five substantial episode-level source-relative research sections; exact Springfield script URLs; documented systematic mismatch between script page header and actual body around feature-length *Emissary*. Explicitly says raw bytes and primary audiovisual not verified. | Recoverable close-read notes with a known source-to-work ambiguity; must not trust page headers. |
| #85 `341686699413f4e1fe4602bfa61c1c3aa1efb02c` | `research/ds9/staging/ds9-s05-b023/README.md` | `81c9f2866a1b479a8272b59c0169a4b287e7cce2` | Five episode-level source-relative note sets, numbered observations and interpretations; two earlier source gaps claimed closed using Forever Dreaming. No per-observation transcript line locators in this sampled packet. | Substantive but weaker independently replayable locators; source re-read and detailed evidence references required. |
| #11 `04c39135a1db7506277a8516bbb0beaf32d40c8d` | `research/pro/staging/pro-s1-opening-five/README.md` | `d749e0098ac76a42157b2a0262d6e8db22f41645` | Five titled, purported full-transcript reads from Springfield and Forever Dreaming with explicit URLs, many labelled evidence and linked provisional assertions; combined *Lost & Found* premiere and split subtitle variants held unresolved. | Genuine authored source-oriented notes, but unverified source bytes, segmentation and external transcript rights. |
| #18 `281550c47f77b18d8fffaba74c83e2d0518d5889` | `research/starfleet-academy/staging/sfa-s01-b001/README.md` | `81b8ac10d0958b09e7f5faceeefd66d2428a0398` | Five purported full-transcript episode passes plus provisional cross-work hypotheses, official-metadata title variant held. | Recoverable staging overview; not proof of actual source retrieval. |
| #18 same | `research/starfleet-academy/staging/sfa-s01-b001/KIDS_THESE_DAYS.md` | `b3f9d672392ea045a9bc2dbec47ca492dd9ef9aa` | Thirty labelled, source-relative observations and fifteen proposed assertions, including sensor deception, simulation, and database-absence epistemic distinctions; only approximate overall transcript extent, not line locator per observation. | Detailed candidate notes requiring new source-relative locators and custody before admission. |

## Supporting observations, falsifiers, and limitations

1. **The historical content is substantive:** episode-specific observations and linked assertions were actually present in inspected Git blobs. Patrick's report of prior research should not be dismissed because modern `main` has zero accepted Briefings.
2. **Historical author claims are not independent verification:** a manifest declaring `SOURCE_RETRIEVED=true`, `CONTENT_ACTUALLY_READ_PROCESSED=true`, or `STAGING_CLOSE_READ_COMPLETE` cannot by itself prove that a complete transcript was read. This sampling establishes *saved research structure and claims*, not the act of past source inspection. Original source response bytes and their acquisition chain were not preserved in these sampled files.
3. **Most samples cite nonofficial full transcript representations, not audiovisual masters:** Springfield! Springfield, Chakoteya, and Forever Dreaming. These are far more informative than recaps, but external providers may share upstream transcripts; no independent corroboration should be counted merely from two provider names.
4. **Source identity pitfalls are concrete:** the DS9 `s01e02` script page was reported to contain *Emissary* despite a different header; Prodigy's combined premiere differs from subtitle split counting. Neither can be flattened into an unreviewed canonical episode ordinal.
5. **Evidence granularity varies materially:** TNG JSON/line-located records are more directly reusable than DS9 and SFA broad staging notes. A single reported batch count must not equate all records to the same evidence tier.
6. **Counterevidence and uncertainty are preserved in several samples:** altered memories, sensor reports, testimony, simulations, holographic representations, and identity claims are generally treated as evidence of what is said/shown, not automatically objective universe-wide truth. This is a positive migration signal, not proof of correctness.
7. **No preference-neutral blind recoding or content revalidation performed:** this is a structural/semantic sample, and source facts could be wrong. These historical artifacts remain proposals until independently re-checked, structurally migrated, and admitted by the appropriate roles.
8. **No complete copyrighted transcript bodies** were copied into this review report. Prior file OIDs and source locators are sufficient to retrieve the authored notes for governed migration.

## Exact recommended migration frontier

1. **TNG PR #3:** retrieve the exact five listed transcript representations (or a rights-compliant source edition), verify provider page/body matches and accessible byte custody, re-evaluate the 12 evidence observations and six assertions from *The Naked Now* as a bounded pilot; map source-relative locators before admitting any record. Recover the other four episode records only after the pilot passes.
2. **TNG PR #12:** migrate one line-located work *Lonely Among Us* with adversarial review of transporter/energy-entity testimony versus depicted events.
3. **DS9 PR #2:** resolve source-page header/body mismatches before converting any provisional work ID. No automatic +1 offset from mere conjecture.
4. **Prodigy PR #11:** record source-page and media-work segmentation variants for the combined premiere before local Work binding.
5. **SFA PR #18 and DS9 PR #85:** re-read legal source representations and add missing fine-grained locators as a prerequisite for evidence admission. Preserve original notes as proposed prior analysis.

No new accepted Source, Work, local entity, evidence, assertion, coverage event, reconciliation, or projection was created. No commits, pushes, merges, or deployment occurred in this inspection.
