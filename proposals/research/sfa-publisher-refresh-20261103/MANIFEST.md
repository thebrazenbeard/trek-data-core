# Starfleet Academy — pinned publisher metadata refresh and media-bucket holds

**Role:** SFA research worker. **Batch:** `SFA-PRESS-REFRESH-20261103-001`. **Disposition:** `PROPOSAL_ONLY_PUBLISHER_METADATA` — not an accepted Source↔Work binding, audiovisual close-read, episode denominator, Continuity Briefing, or artwork release.

Accepted baseline: `thebrazenbeard/trek-data-core` `main@d4ecd970bf28019696abd692011007d7d47f9ff8`. The accepted [SFA publisher roster](../../librarian/sfa-publisher-roster-20261102/bundle.json) already describes ten Season 1 metadata slots from Paramount+ and its Press Express pages, but no captured HTML response checksum. This batch repeats that listing against an actually retrieved HTML snapshot; it **does not add ten new Works or independent witnesses**.

## Source retrieval and processing performed

On 2026-11-03 UTC, I retrieved two publicly readable official publisher HTML pages with `curl --fail --location`, HTTP 200, `text/html; charset=UTF-8`:

| Source-local representation | Bytes actually received | SHA-256 of exact raw response |
| --- | ---: | --- |
| [Paramount+ Press Express episode listing](https://www.paramountpressexpress.com/paramount-plus/shows/star-trek-starfleet-academy/episodes/) | 144,050 | `379c67982b4d50664a09514e7723abd4bd4156ee3ce814df8b216dd81eafefc4` |
| [CBS Studios Press Express show page](https://www.paramountpressexpress.com/cbs-studios/shows/star-trek-starfleet-academy/) | 127,823 | `c5753b461be1739321643286a5d9c69666d2b67b94e0fa8ab549bed2db67f332` |

The post-retrieval UTC observation clock was `2026-11-03T01:23:34Z`. The pages belong to **one Paramount corporate publisher independence group**. They are metadata/promotion pages, not authenticated episode videos or a second independent corroborating witness. The raw HTML includes expiring AWS-signed photo thumbnail URLs; these hashes identify particular downloads rather than stable page revisions. The raw pages, signed URLs and photographs were **not committed**. Response custody after this temporary extraction is not durable, so independent replay currently requires a new retrieval and fresh digest.

I processed every row in the Press Express page's displayed listing in this snapshot: the ten Season 1 title/code pairs (HTML title physical lines 1028–1496), one Season 2 early-release media bucket (line 976) and a Season 1 early-release images bucket (line 1548). I also examined the studio show's source-local photo filename/caption metadata and recorded three bounded filename observations (lines 1079, 1112, 1145) without accessing image bytes. The public JSON preserves source-local entities, four source-specific evidence groups and three attributable assertions. No episode transcript, audiovisual stream, image, scene or fictional-world event was examined.

## New distinction worth preserving

The Press Express page itself uses an `Episodes` container for:

- `Season 2 - Early Release`, displayed with `Season 2` and `Ep. 200`, whose page card routes to photo assets and lacks an episode description in the retrieved HTML.
- `Early Release Images`, displayed as `Season 1` and `Ep. Multiple`.

Those labels are evidence about a **publisher webpage and publicity grouping**. They do not establish a work titled *Season 2 - Early Release*, an episode 200, a complete Season 2 roster, or the contents of any episode. The second entry is a useful internal falsifier for the assumption that every item under the website's `Episodes` heading is an audiovisual episode. The three `SFA_200_...` filenames observed on the CBS Studios page are only source-local publicity file labels. Their code prefix cannot be promoted into a Season 2 episode number.

The ten Season 1 titles/codes match the existing `SFA-PUBLISHER-ROSTER-20261102-001` observations. That agreement involves **dependent pages from the same source family**, not two independent attestations or an audit of their audiovisual works.

## Scope and negative controls

- No canonical Work, Source binding, global entity ID, timeline reconciliation or governed coverage event.
- No image URL, binary, signed CDN request, transcript, plot summary or public thumbnail sidecar.
- No `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED` **episode**, `CLOSE_READ` or `SEMANTICALLY_ANALYZED` coverage promotion. The structured object here is **publisher metadata only**.
- Unresolved: precise Season 2 episode roster; whether publisher release code `200` denotes a media package, production grouping or another publisher-internal scheme; edit/version identity of the changing Press Express pages; image rights; true S1 Work source binding.

> **Hostile check:** An automated crawler that emits one episode for every publisher card would invent a Season 2 episode `200` and a Season 1 episode `Multiple`. The proposal explicitly labels both as media buckets and its validator rejects converting them into episode-slot entities.

> **Provenance check:** Raw-page hashes cannot prove enduring page authenticity because expiring signed URLs affect the bytes. The exact raw snapshots are not committed and their source custody is incomplete; any future promotion requires an independently preserved and reviewed source representation.

## Reproducible proposal checks

Run from the repository root:

```bash
python3 proposals/research/sfa-publisher-refresh-20261103/validate.py
python3 proposals/research/sfa-publisher-refresh-20261103/test_validate.py
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_explorer.mjs
```

The first validator crosschecks the refreshed title/code pairs against the prior accepted publisher **proposal**, checks unique local identities, source family, rights/coverage fail-closed flags, evidence references and promotional bucket classification. Its adversarial tests attempt Work, S2 episode, coverage, source, independence and art-rights promotion. Neither test authenticates the remote HTML or grants episode source custody.

**Next frontier:** An SFA worker should retrieve full, authorized Season 2 episode-source inventory when publisher release pages become available, and an Auditor should inspect at least one primary audiovisual source or studio-authenticated script before treating any discovered title as source-bound narrative evidence. The Librarian owns eventual Work identity reconciliation.
