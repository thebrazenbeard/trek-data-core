# Discovery — official publisher Season 1 metadata observation, batch 001

**Status:** proposal only. **Mission:** `dis`. **Accepted main at orientation:** `c7a14ddb62dfa45d5d01855952d9e562c1af21de` (2026-11-02). No accepted nonfixture Discovery Work/Source/binding batch was found. This is NOT a source-bound or close-read audiovisual batch.

## Source observation

- Directly inspected the public publisher's *textual episode guide*: [Paramount+ Star Trek: Discovery Season 1](https://www.paramountplus.com/shows/star-trek-discovery/episodes/1/), rendered via a web retrieval tool on 2026-11-02. The retrieval tool reported its indexed crawl as **last week**, not a byte-exact current HTTP response. No response body, server timestamp, revision identifier, or response-byte SHA-256 was captured for this observation. The observation date is the **research reading date**.
- The guide explicitly lists the first five display entries, each with separate season/episode slots: S1E1 *The Vulcan Hello*; S1E2 *Battle at the Binary Stars*; S1E3 *Context Is For Kings*; S1E4 *The Butcher's Knife Cares Not for the Lamb's Cry*; S1E5 *Choose Your Pain*.
- [StarTrek.com publisher retrospective, September 18, 2017](https://www.startrek.com/news/watch-first-four-discovery-episode-titles-revealed) names the first four in the same order. That older page renders the third title *Context Is for Kings*; its casing differs from the current Paramount+ guide's *Context Is For Kings*. Treat this as source-specific display text; it does not warrant canonical title reconciliation.
- Both publisher surfaces belong to the Paramount corporate source family (`publisher:paramount`). They are NOT independent external corroboration.
- We read **publisher metadata**, not the complete episodes, a transcript, script, captions, audio or visual source. The publisher's descriptive plot blurbs were intentionally not coded as episode facts or research evidence.

## Preservation and boundaries

`roster.csv` stores the exact five displayed season/episode/title pairs. `observation_receipt.json` pins its byte digest; `bundle.json` is independently checked against the Mission registry and candidate-only roster schema. No source edition/custody binding, Work identity resolution, local entities, narrative Evidence or Assertions exist in this batch. The first five slots are a bounded sample; season completeness and total denominators remain **UNRESOLVED**. Unverified Wikidata candidate discovery in `proposals/discovery/wikidata-mission-samples-20261102/modern/proposals/dis.json` is neither imported as accepted fact nor treated as a second source witness.

The first two episodes are separate **publisher entries** here. Neither is collapsed into a combined streaming premiere, and no independent production/broadcast chronology is inferred from the listing.

## Validation

```bash
python3 -B tools/validate_publisher_episode_roster.py --input proposals/discovery/dis-publisher-s01-b001-20261102/bundle.json
python3 -B -m unittest tests.test_dis_publisher_batch -v
```

Admission: none. Coverage: none. Public release: none. The next substantive DIS research frontier is lawful acquisition/inspection of a **complete primary episode** and Librarian source binding under a reviewed custody process; these five metadata candidates alone cannot satisfy it.
