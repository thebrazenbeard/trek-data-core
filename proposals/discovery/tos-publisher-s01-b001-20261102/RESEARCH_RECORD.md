# TOS publisher Season 1, first five positions — machine-readable comparison

Status: **candidate proposal only**. Observation: 2026-11-02 UTC.

This is a five-position follow-up to the [official roster scope comparison](../official-tos-roster-scope-20261102/RESEARCH_RECORD.md). The two validated JSON bundles deliberately retain **source-local** ordinals. They do not create canonical episode identities, accepted Work or Source records, source bindings, coverage events, episode denominators, or viewed-episode evidence.

| Publisher listing | Exact first-five position evidence | Proposed bundle |
| --- | --- | --- |
| [Paramount+ Season 1](https://www.paramountplus.com/shows/star_trek/episodes/1/) | S1E1 *The Cage*, E2 *The Man Trap*, E3 *Charlie "X"*, E4 *Where No Man Has Gone Before*, E5 *The Naked Time* | [`paramountplus.json`](paramountplus.json) |
| [Pluto TV Season 1](https://pluto.tv/us/shows/star-trek-the-original-series/season/1/) | S1E1 *The Man Trap*, E2 *Charlie "X"*, E3 *Where No Man Has Gone Before*, E4 *The Naked Time*, E5 *The Enemy Within* | [`plutotv.json`](plutotv.json) |

The franchise [StarTrek.com series page](https://www.startrek.com/en-un/series/star-trek-the-original-series) lists 79 episodes across three seasons; that page does **not** resolve the streaming roster's extra *The Cage* entry or certify a globally complete identity denominator. These platform listings are not independent audiovisual witnesses. Both bundles use `publisher:paramount` as the same independence group.

**Pilot and chronology distinction (Patrick's correction, supported by [Paramount+'s Star Trek Day explainer](https://www.paramountplus.com/sneak-peak/star-trek-day/)):** *The Cage* was the original, initially unaired Pike-led pilot; *Where No Man Has Gone Before* was the second pilot with Kirk; and *The Man Trap* was the first episode actually broadcast. Paramount+ includes *The Cage* as its streaming S1E1, while Pluto begins with *The Man Trap*. The research model must not equate a publisher's current streaming slot with an original broadcast ordinal, filming/production order, pilot status, or canonical Work identity. Those are separate, source-attributed properties requiring explicit reconciliation.

## Evidence and limits

- The titles and ordinal labels were inspected in the public web-reader views of the linked pages on 2026-11-02. No raw publisher response bytes were retained or independently hashed: `response_sha256: null` is intentional, as is `publisher_revision: null`.
- These are *only the first five positions shown by each platform*, not five independently resolved Work identities, a complete season roster, or a canonical broadcast order. A title appearing in both is a potential string crosswalk, **not** an automatic identity binding.
- The publisher's short title/ordinal facts are retained; no page body, episode media, scripts, transcripts, subtitles, synopsis, stills, user account tokens or streaming access details are copied.
- For any later accepted work, an independent Librarian must choose an explicitly scoped episode unit (original broadcast, streamable presentation, edition, etc.) and verify the raw source/version, identity, two-part boundaries and rights. A researcher's title comparison cannot create content coverage.

## Offline check

```sh
python3 tools/validate_publisher_episode_roster.py --input proposals/discovery/tos-publisher-s01-b001-20261102/paramountplus.json
python3 tools/validate_publisher_episode_roster.py --input proposals/discovery/tos-publisher-s01-b001-20261102/plutotv.json
python3 -m unittest discover -s tests -p 'test_tos_official_batch.py' -v
```

Result remains `PUBLISHER_ROSTER_CANDIDATE`, with `UNRESOLVED` completeness and `NONE` acceptance/coverage effect.
