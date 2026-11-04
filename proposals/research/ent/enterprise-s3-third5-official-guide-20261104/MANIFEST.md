# Enterprise Season 3 — E11–E15 first-party guide, held research

**Batch:** `ENT.PPLUS.S3.THIRD5.GUIDE.20261104`

**Disposition:** `HELD_OFFICIAL_PUBLISHER_GUIDE_SOURCE_RELATIVE`

**Branch dependency:** New isolated local branch `research/ent-s3-e11-e15-20261104` is explicitly based on the two prior ENT Season 3 held commits (`67e997fe4db0eaa20a96b311c91006520c767848`, `865291996cf0c16286f1aea05fe562c354a83408`), themselves based on accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91`. This is **not** accepted main or an Explorer update.

## Exact complete source retrieval

- Official first-party source: [Paramount+ *Enterprise* Season 3 episode guide](https://www.paramountplus.com/shows/enterprise/episodes/3/).
- Fresh read-only **HTTP 200** full HTML response; Date `Wed, 04 Nov 2026 21:36:32 GMT`; observed `2026-11-04T21:36:32.669611+00:00`.
- Retrieved **308,190 raw bytes**, SHA-256 `3a970117c2e224b998be2b223e4f2ee925c41acb8c0c79eca34f4588d89d06c9`.
- The same structural parser inspected all 24 visible guide cards and their description strings in memory, checking title, season and episode badge, analytics ordinal, video-route path, `datetime`, HTML locator and source-description SHA-256. Their 24 normalized metadata and description fingerprints exactly matched **both** previous source reads, despite distinct raw whole-page response digests.
- The E11–E15 publisher-description texts were actually read to author five concise original paraphrases: **957 characters** of publisher text processed. Full source paragraphs and raw HTML were not copied to the repository. No video, soundtrack, closed captions, screenplay or image was retrieved.

| Source-local episode | Official card title | HTML description line | Publisher-description SHA-256 |
|---|---|---:|---|
| E11 | Carpenter Street | 1780 | `d4ae4a81b47e18f99f6f11f49770ae36cdd9eeceb31fdef1bdadf2582f24eaec` |
| E12 | Chosen Realm | 1808 | `7102998269532aee2e019d5118093a6933c5b0e58633c5307ae9b99c126e2c59` |
| E13 | Proving Ground | 1836 | `2e5062a9c9591dbd0ffd3fbea9f2fc70e9f37df8bc2447da3fe9d2ace0894340` |
| E14 | Strategem | 1864 | `1f8253ca8affbe9098730f499b4b34188dc28520acfd769b1a012ab7df977ef7` |
| E15 | Harbinger | 1892 | `cb5fdbad86dbb29369ec7340bfafebf12168f8a0c2c10230722fa105d4d40029` |

HTML line numbers are relative to the specific retrieved dynamic response. `records.json` contains all exact card metadata and original source-relative paraphrases. The indexed 24-card *title roster* is previously accepted discovery, not 24 fresh Work analyses.

## No accidental double count or semantic promotion

Prior E01–E05 records SHA-256: `05e7375949b0facdbda22bc2e0a3ff8ec6a46c9cdb901a34ac5fd4e98d837f27`.

Prior E06–E10 records SHA-256: `54e50b5e169a961912f2cde1d1a19bdf8eabfc704bd5b216b40902df9ff302d7`.

All three separately held batches derive from the same `publisher:paramountplus.com` source lineage, so repeat GETs are **not independent corroboration**. The E11–E15 local entity, evidence and assertion IDs do not overlap the first ten. The typed predicate `PUBLISHER_DESCRIBES` asserts only the publisher's editorial description, not objective event truth.

> **Hostile challenge:** A dated publisher synopsis can be misleading or incomplete. Agreement between three separate HTML retrievals does not prove the described episode events occur onscreen, license video or image reuse, resolve a canonical Work, or qualify audiovisual `CLOSE_READ`.

All protected effects are `NONE`: accepted Source binding, global Work, reconciliation, coverage, denominator and public Explorer synopsis release. No copyrighted episode content or thumbnail was accessed or published.

## Reproducible checks

```bash
python3 proposals/research/ent/enterprise-s3-third5-official-guide-20261104/validate.py
python3 -m unittest discover -s proposals/research/ent/enterprise-s3-third5-official-guide-20261104 -p test_validate.py
python3 proposals/research/ent/enterprise-s3-last5-official-guide-20261104/validate.py
python3 proposals/research/ent/enterprise-s3-first5-official-guide-20261104/validate.py
python3 tools/validate.py
python3 -m unittest discover -s tests
git diff --check
```

The validator pins two prior records by exact SHA, commit and source receipt, checks all three disjoint local episode ranges, enforces E11–E15 guide-card order, exact fingerprints and source lines, and rejects fabricated audiovisual coverage, canonical Work binding or false independent lineage. `source_probe.py` reuses the exact structural parser in the first-five packet; it performs a new read-only guide GET and hashes all 24 cards. Its optional private-prose flag is solely for internal source reading.

**Exact next frontier:** E16–E20 original publisher-description paraphrases in a separately held packet with new full source receipt, or acquisition of an authenticated, rights-compatible audiovisual/transcript evidence source before making any CLOSE_READ claim. No merge, push or deployment was performed.
