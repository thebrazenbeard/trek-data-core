# TOS first full-source pilot — blocked at source access, metadata preserved

**Role:** TOS research worker. **Snapshot:** accepted `main` SHA `c7a14ddb62dfa45d5d01855952d9e562c1af21de`, inspected 2026-11-02 UTC. **Candidate Mission Briefing:** *The Cage* (the original Pike-led pilot). **Result:** `BLOCKED_BEFORE_COMPLETE_SOURCE_EXTRACTION`; no complete primary episode representation was inspected, though one bounded frame of *The Man Trap* streamed in the free Pluto browser player. This is deliberately kept in **`proposals/`**, outside the governed `research/` record scan; its packet and metadata context are not governed research record types.

## What was actually read

I read the public text views of these publisher pages on 2026-11-02:

| Page | Scope actually inspected | Limits |
| --- | --- | --- |
| [Paramount+ S1 episode guide](https://www.paramountplus.com/shows/star_trek/episodes/1/) | Catalog title and displayed slot *The Cage* S1E1; its blurb identifies Capt. Pike and Jeffrey Hunter; *The Man Trap* S1E2 | Publisher listing, **not** episode media; no captured publisher response bytes, edition checksum or media timestamp observations |
| [Paramount+ Star Trek Day editorial](https://www.paramountplus.com/sneak-peak/star-trek-day/) | Publisher calls *The Cage* the first unaired pilot; calls *Where No Man Has Gone Before* the second pilot; describes *The Man Trap* as the first NBC broadcast on 1966-09-08 | Historical publisher claims, **not** a full episode witness or independent production archive |
| [Pluto TV S1 guide](https://pluto.tv/us/shows/star-trek-the-original-series/season/1/) | Catalog places *The Man Trap* at S1E1 and advertises a free playback option | Catalog roster alone is not an episode witness |
| [Pluto TV actual *The Man Trap* free player](https://pluto.tv/us/shows/2140877/episode/63641f361ac5b40013b2bb17/) | Browser Play S1E1 opened a live player with **00:10 / 50:26**, playback controls, and a visible frame showing a starship near a planet, without signing in | **One transient visual frame only.** Audio/dialogue not processed; no sequential/full content review, no captured media bytes, edition hash or source version receipt. The frame is not stored in this repository |
| [Paramount+ *The Cage* playback landing](https://www.paramountplus.com/shows/video/vnDpwO4ZpMxZzKbgJUmXIGhESkEKD6mD/) | Search-visible landing advertises full episode under streaming signup | The web reader's page open returned HTTP 500; no logged-in playback, direct episode bytes or verifiable rights/access basis obtained |

Exactly **zero complete minutes** of *The Cage* or *The Man Trap* were sequentially analyzed as audiovisual episode content. The Pluto UI did render one frame at the approximately 10-second player mark; that is a genuine, **partial visual playback observation** but cannot authenticate an entire media edition or support general episode plot assertions. I did not listen to dialogue or record scene notes over a bounded continuous span. Publisher guides are separately useful but cannot establish what happens within a timestamped scene. Any synopsis is a publisher assertion, not a researcher-observed depiction. No DRM/subscription barrier was bypassed.

## Source-relative chronology (separate dimensions)

The seven short, publisher-attributed metadata statements in [`source-relative-context.json`](source-relative-context.json) deliberately separate:

1. **Production/pilot status:** *The Cage* was Paramount's original initially unaired Pike-led pilot; *Where No Man Has Gone Before* was a subsequent pilot.
2. **Initial television broadcast:** Paramount reports *The Man Trap* as the first NBC installment on **1966-09-08**.
3. **Present platform presentation:** Paramount+ lists *The Cage* S1E1 and *The Man Trap* S1E2, while Pluto TV lists *The Man Trap* S1E1. These labels are independently scoped to their catalogs and are **not** universal episode IDs or historical transmission dates.

**Important anomaly:** Paramount's listing renders a date of 1966-09-08 for *The Cage* despite Paramount's editorial description of that episode as initially unaired. A catalog display date must not silently override the publisher's distinct historical broadcast claim. The discrepancy is preserved as unresolved presentation semantics, **not** forced into a chronology correction.

These statements are research leads, not canonical episode assertions, and they create no global entity identities or new accepted predicates. Publisher sites may share a common lineage and should not be counted as independent episode witnesses. Patrick's correction agrees with publisher metadata, but the user's statement was not used as independent source evidence.

## Exact gates and rights status

| Batch condition | Verified outcome |
| --- | --- |
| Full episode source retrieved | **NO** — public metadata read and a partial free playback frame displayed; no complete source retained/processed |
| Lawful episode viewing/inspection | **PARTIAL ONLY** — Pluto publicly streamed one visible frame without sign-in; no sustained, complete edition read or audio processing |
| Actual episode byte SHA-256 | **NULL** — no source content bytes to hash |
| Source response/version SHA-256 | **NULL** — no fixed raw publisher response preserved |
| Source/content edition | **UNKNOWN** — remastered/current pages do not authenticate the media edition |
| Episode content read/processed | **NOT COMPLETE** — one transient frame visible, zero fully processed episode minutes |
| Timestamped content evidence records | **0** |
| Content-sourced assertions | **0** |
| Source↔Work binding | **NONE**, must be separately reviewed by Librarian |
| Coverage/denominator/projection effect | **NONE** |

The metadata-only [`episode-review-input.json`](episode-review-input.json) is a valid **proposal-only** input for the repository's offline review-packet tool. Its `inspection: NOT_INSPECTED`, `PUBLISHER_METADATA`, `content_sha256: null`, empty observations/assertions are intentional. This is **not a completed research batch**, Source-bound episode, `CLOSE_READ` event, accepted Work, or claim to have watched anything.

## Next exact frontier

Pluto TV now has a verified no-sign-in **playback route** for *The Man Trap*, but this session has not completed 50:26 of source inspection and cannot obtain an authenticated exact media digest via its browser UI. Use that legitimate free playback (or an authorized, stably accessible edition of *The Cage*) for a complete, reproducible review. Outside the public repository, retain its identity/edition, exact inspected-media SHA-256, access and rights basis, and enough access context for an independent Librarian to verify. Only then read the full episode and create a small bounded, original, timecoded observation set, source-relative local entities and assertions for review. The source/Work, rights, reviewer, coverage and projection admissions are distinct subsequent decisions; this worker cannot self-promote them.

## Reproducibility

```sh
python3 tools/prepare_episode_review_packet.py --input proposals/research/tos-source-pilot-20261102/episode-review-input.json
python3 -m unittest discover -s tests -p 'test_tos_source_pilot.py' -v
python3 tools/check_episode_pilot_readiness.py
```

All commands are read-only. See `docs/EPISODE_REVIEW_PACKET.md` and `docs/FIRST_NONFIXTURE_EPISODE_PILOT.md` for admission boundaries.
