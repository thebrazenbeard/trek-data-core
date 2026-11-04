# Enterprise Season 2 — official publisher guide E01–E05 (HELD)

**Scope:** First five complete publisher-description *proposals*, derived from the actual official Paramount+ Season 2 guide. Not a complete episode video/audio/script read; not accepted Work, Source binding, reconciliation, governed coverage, Explorer publication or deployment.

## Provenance and full source observation

- Authoritative accepted `main` reviewed: `3028765359001b90bc3e6b5c1835ee283b326e91` (GitHub API rechecked 2026-11-04).
- Accepted-main discovery context: `proposals/discovery/legacy-paramount-season2-20261102/ent/bundle.json`, SHA-256 `b3ba6c175202d0bd55b711a850a939af6aee2786d0900bc1365cbd109086ef84`, 26 `CANDIDATE_METADATA_ONLY` entries. Not 26 admitted Works or episode close reads.
- Official first-party guide: https://www.paramountplus.com/shows/enterprise/episodes/2/
- HTTP 200; response Date `Wed, 04 Nov 2026 22:48:50 GMT`; observation `2026-11-04T22:48:51.067817+00:00`.
- Full HTML read and parsed in memory: **312,754 bytes**, raw SHA-256 `860df3bd8d3c3e91727ab71c712cd60718da0bddf63fcd5bd5914b83358d9cdd`.
- All **26** source-local cards structurally parsed for title, season/episode badge, analytics ordinal, publisher datetime, response-local lines, description length/hash and route strings. Exact title/number match to all 26 accepted discovery candidates; this is the same Paramount publisher lineage, not independent corroboration.
- Only E01–E05 full publisher descriptions read, **1,184 source characters** in all; five independent *original paraphrases* drafted and fingerprinted, one per local evidence/assertion chain. Source prose and complete raw HTML remain outside the repository.
- Extractor `source_probe.py` uses the S2-specific `Star Trek: Enterprise - ` analytics field prefix observed on this page, which differs from the S4 guide's `Enterprise - ` prefix.

| Source-local card | Publisher guide title | HTML anchor / paragraph line | Paragraph SHA-256 |
| --- | --- | ---: | --- |
| S2 E01 | Shockwave Part II | 1482 / 1500 | `002d314336f29209603e9dc4ff30820ff37ccc87bc9d393460aa1412b9d6970e` |
| S2 E02 | Carbon Creek | 1510 / 1528 | `8cd473070d262c6a33a51eec0ea7d83be938dd82a414b4daa415b33fa0e8b4de` |
| S2 E03 | Minefield | 1538 / 1556 | `df06736f37dd8fafdff4f0a57d9f6cdb0c1f566e39ef5462ab261a3e87896c4c` |
| S2 E04 | Dead Stop | 1566 / 1584 | `5dd65d877019abd6af5d949684675f3db1e2bd5b49b1fba54787940fd3bbb563` |
| S2 E05 | A Night in Sickbay | 1594 / 1612 | `35a16decfa3813aaa532b342574231ede51a5d4a0c162d924eb22aad0abdeedc` |

## Source-relative uncertainty and adversarial findings

1. **Publisher date/order conflict:** The source lists E01 with publisher datetime `2002-09-24T21:00:00-07:00` but E02 with `2002-09-17T21:00:00-07:00`; likewise E04 `2002-10-15T21:00:00-07:00` versus E05 `2002-10-08T21:00:00-07:00`. Both adjacent intervals descend despite ascending episode badges. Preserve raw publisher values. No broadcast-order correction, chronology assertion or date promotion.
2. **Nested account versus event:** The E02 description reports T'Pol telling an account of Vulcan contact. Our paraphrase identifies the narration as *her story*, not verified objective historical truth. Source-relative `PUBLISHER_DESCRIBES` assertion with a `CHARACTER_REPORTED_ACCOUNT_NOT_OBJECTIVE_EVENT` limitation.
3. **No episode content witnessed:** Printed route paths are HTML metadata, not evidence that any linked video, audio, subtitles, artwork or screenplay was fetched.
4. **Potential S1 duplication avoided:** Accepted-main ENT Season 1 already contains held publisher guide research (b001–b003), specifically referenced by open held sidecar PR #558. This S2 first-five lane is separate. Open PR review found no conflicting ENT S2 publisher-description tranche at the time of this work.

## Batch completion semantics and next frontier

`SOURCE RETRIEVED → FIVE PUBLISHER DESCRIPTIONS ACTUALLY READ → FIVE SOURCE-RELATIVE PARAPHRASE/EVIDENCE/ASSERTION RECORDS → VALIDATION → MANIFEST`.

The publisher-guide description tranche is **5/26 HELD**, with 21 source descriptions not yet processed. **Zero accepted episode Work or CLOSE_READ/coverage gain.** No full copyrighted source prose, transcripts, video, audio, images, or guide HTML committed; no push/merge/deploy.

**Next exact frontier:** Enterprise S2 E06–E10 full first-party publisher descriptions, as a new nonoverlapping HELD batch dependent on this source receipt, with special attention to source datetime drift and repeated-source lineage. Later, a separate rights-aware primary audiovisual CLOSE_READ would still be needed.
