# Explorer: accepted-but-HELD first-party episode-guide source shelf

**Branch base:** accepted `main` `b67155db5a35e788c555e6a5568b15739d385767`  
**Scope:** 20 exact source-local Paramount+ guide observations from **two series**; **zero** global Work admissions, completed episode reads, coverage changes, synopsis releases or artwork releases. This slice does not add to the 1,214 multimedia discovery records or 218 historical leads and does not replace the 39 ISBN or 13 film-page shelves.

## Input packets and custody

All four source packets already exist on accepted `main` and are read again for every compiler or query invocation. Original validators are invoked on the strictly duplicate-key-parsed packet, followed by exact source-file SHA and code-owned per-card evidence digest checks.

| Accepted source-local research packet | Included card positions | Exact original input SHA-256 |
| --- | --- | --- |
| `proposals/research/pic/picard-s1-first5-guide-cards-20261103/records.json` | *Picard* S1 E1–5 | `070dccdbda3b7a777e6f12201d725bd906610f4e1c5ee26e8c37c3a218c6829f` |
| `proposals/research/pic/picard-s1-last5-guide-cards-20261103/records.json` | *Picard* S1 E6–10 | `fe962cc235ffc84f5cff7a970a940419cf9a21dce72cd5844cae76ce89f9a9cc` |
| `proposals/research/snw/s3-publisher-first5-20261103/records.json` | *Strange New Worlds* S3 E1–5 | `89e816d651996405dce608fa3509b437178b0dcd635f2d8635962d0bd7acfe1c` |
| `proposals/research/snw/s3-publisher-last5-20261103/records.json` | *Strange New Worlds* S3 E6–10 | `b1daa95e849c61beb1011aabaebc06343589f29d0ec786e6359c07cb81137b2e` |

All four derive from **one publisher family**, `publisher:paramountplus.com`; they are *not independent source corroborations*. The guide HTML is dynamic, and source packet receipts do not constitute archived immutable full episode bodies. The SNW source-local `works` records are worker proposals with `canonical_work_id=null`, not accepted Work identities. The Picard guide records are similarly source-local. This compiler deliberately publishes no source `works` object.

## Deterministic output and public boundary

- Output: `explorer/episode-source-cards.json`, SHA-256 **`38dfde3c3a1cfe38e41bf6740327b070f7846e2dc7c6149b74f88db7b85186f6`**, code-pinned in `explorer/app.js`.
- Exactly 20 distinct source-local card IDs; source identity, exact series/season/episode/title, first-party guide locator, publisher utterance terms, source input receipt and held status.
- `publisher-utterance:*` tags are labels from accepted publisher-description research, **not** independently confirmed depicted beings, resolved global entities or fictional truth. An inferred editorial label such as “unnamed journalist” is explicitly omitted as a literal tag.
- No synopsis prose, guide blurb, episode stream URL, image URL, thumbnail, video, transcript, copyrighted long passage, global entity ID, full episode text or media asset is copied into this public shelf. The signed-in player/thumbnail URL candidates remain only in the accepted original research records and per-row evidence hashes.
- Every row marks `HELD_PUBLISHER_GUIDE_ONLY`, `SOURCE_LOCAL_CARD_NOT_ADMITTED_WORK`, and all Work, coverage, synopsis, artwork effects `NONE`. A future rights/admission review is a separate step.
- The code-owned card SHA binds the entire original card fragment—including nonpublic video/image references and evidence/utterance provenance—not just the subset rendered. Same-host video rebindings or held-status changes are not masked by preserved totals or an updated whole-packet source SHA.
- A **second, independent code-owned set of twenty SHA-256 pins in browser source** binds every complete published JSON row, including all label/tag pairs, title, source locator and held effects. Before anything is displayed, the browser canonicalizes each row and checks it with WebCrypto; no cards are visible until **all twenty** row pins and the enclosing sidecar SHA pass. A forged label *plus* forged matching facet tag *plus* repinned whole-file hash must still be withheld. Missing WebCrypto/TextEncoder is fail-closed.
- The Pages workflow calls all four original accepted validators, rebuilt deterministic sidecar and query CLI, then checks Git object fingerprints for exactly permitted Explorer artifacts. This is a **manual-release gate only**; merging does not deploy.

## Searches

The LCARS Explorer presents its own section with title, series, slot, HELD-source status, and publisher-utterance tag facets. It does not modify the governed Briefings, 218 prior leads, or the 1,214 directory count.

Callable local search (no network credentials, telemetry, or paid service):

```bash
python tools/build_episode_source_cards.py --check
python tools/query_episode_source_cards.py --validate-sources --series SNW --q Pike --limit 5
python tools/query_episode_source_cards.py --status HELD_PUBLISHER_GUIDE_ONLY --tag publisher-utterance:picard --limit 20
python tools/query_episode_source_cards.py --id pic-s1-e06-pplus-guide --facets
python tools/query_episode_source_cards.py --source-batch SNW-LAST5 --limit 2 --offset 2 --facets
```

`--validate-sources` is explicit for readability; source validation occurs **unconditionally** in the query command. Search is bounded to 160 query characters and twenty output rows. JSON query responses include source-local status and no admission/coverage effect.

Exact `--id` lookup accepts a **source-local card ID**, not an admitted Work ID. `--source-batch` selects an exact reviewed packet; `--offset` and `--limit` page stable sorted rows. `--facets` reports series, packet, held-source status, and *publisher-utterance label* counts across the matched source-local rows **before pagination**; it does not establish independent corroboration, verified depiction, or global entity identity. Responses include `identity_scope`, `next_offset`, and a zero-effects envelope. These additions affect query tooling only: no source data, Work records, search-catalog directory, artwork, synopsis, or deployment artifacts change.

## Hostile tests

`tests/test_episode_source_cards.py` exercises accepted source pinning, all four original validators, duplicate JSON keys, real full-source fragments, same-host video-link swaps under a forged full-file SHA, code-owned per-row source-evidence pins, *browser code-owned public-row digest pins*, public artifact status/rights/title/tag/URL poison, and query bounds. `tests/test_explorer.mjs` repeats malicious row changes after deliberately recomputing the **entire browser artifact hash**—including the paired publisher utterance label/tag attack—ensuring semantic fail-closed behavior beyond hash-only protection. `tests/test_explorer_accessibility.mjs` checks labels/status/UI; `tests/test_pages_artifact_scope.py` enforces Pages allowlist and mandatory original validators.

```bash
python -m unittest tests.test_episode_source_cards tests.test_pages_artifact_scope -q
node tests/test_explorer.mjs
node tests/test_explorer_accessibility.mjs
python -m unittest discover -s tests -p 'test_*.py' -q
python tools/build_episode_source_cards.py --check
python tools/query_episode_source_cards.py --validate-sources --limit 1
```

**Frontier:** independent exact-head hostile review of the branch before merge. Future rows from additional series/seasons require accepted original source packets, their validators, new code-owned digest pins and a separate review; merely having a discovery lead or publisher thumbnail URL is not enough.
