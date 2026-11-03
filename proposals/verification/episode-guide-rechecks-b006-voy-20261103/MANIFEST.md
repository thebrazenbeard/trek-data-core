# B006-VOY: 13 Voyager official publisher guide-card rechecks

**LIBRARIAN source-relative proposal only** · accepted `main@5ea4a8d562e76931218329b8386e363e3c40845f` · observed 2026-11-03 UTC.

This bounded tranche covers precisely **`lead:0070`–`lead:0082`** in the accepted 1,214-row source-local discovery directory; every originating row is a Wikidata-derived Voyager episode lead, not an admitted Work. The adjacent **`lead:0067`–`lead:0069` Deep Space Nine cards are reserved for the DS9 worker**. Do not combine these into a 16-row B006 count without separate Consolidator review, identity checks and source manifests.

### Actual official rendered reads

Thirteen episode title/season/slot/short-description **cards were individually read** from Paramount+ U.S. official *Star Trek: Voyager* season guides: [S1](https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/), [S2](https://www.paramountplus.com/shows/star_trek_voyager/episodes/2/), [S3](https://www.paramountplus.com/shows/star_trek_voyager/episodes/3/), [S4](https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/), [S5](https://www.paramountplus.com/shows/star_trek_voyager/episodes/5/), [S6](https://www.paramountplus.com/shows/star_trek_voyager/episodes/6/) and [S7](https://www.paramountplus.com/shows/star_trek_voyager/episodes/7/). `observations.json` pins the source-local IDs, exact rendered card titles, official season/episode slots, and read-state; `records.json` deterministically attaches each source-local Wikidata QID locator, publisher-guide URL, card section locator and distinct provenance groups.

The publisher guide excerpt is **not the audiovisual episode** and was not hashed as raw HTTP bytes. The short descriptions were examined to identify cards; no blurb text, synopsis paraphrase, dialogue, image, cover, audio or video is published. The branch neither changes `explorer/metadata-rechecks.json` nor marks these as approved or accepted research.

### Two explicit unresolved cases

| Source-local lead | Indexed title | Publisher card | Status |
| --- | --- | --- | --- |
| `lead:0073` | *Time and Again* | *Time And Again* (S1E4) | Case difference; `CASE_VARIANT_UNRESOLVED` |
| `lead:0074` | *Caretaker* | *Caretaker, Part 1 & 2* (combined publisher S1E1 card) | Multipart title/scope ambiguity; `MULTIPART_TITLE_SCOPE_UNRESOLVED` |

The other **11** cards match the source-local titles exactly. A combined publisher display card does not prove one versus two canonical episode Works or identify an edition/source body. Both unresolved cases require reviewed binding decisions, not string normalization.

> **Hostile challenge:** The original Wikidata lead QIDs and the Paramount guide cards are not two independent narrative readings; neither supplies complete episode content. Card count, title, blurb and slot do not prove canon, full-text availability, SOURCE_BOUND/CLOSE_READ coverage, a global Work identity or licensed media reuse. An official metadata page can also misassociate a description with an adjacent card, as observed in the earlier B005 DS9 tranche; this proposal uses no publisher blurb as narrative evidence.

### Accounting and reproduction

- New source-local rendered metadata checks: **13** (11 exact; two unresolved); public synopsis approvals: **0**; accepted Source/Work/coverage effects: **0**.
- The accepted B001–B004 Explorer metadata display is **56/1,214** and B005 separately proposes 16 DS9 cards; this branch makes no accepted denominator or display-change claim. A reviewable source-relative combined candidate census is not a governed corpus denominator.
- Source lineage: Wikidata-derived discovery rows `wikidata_collaborative_derivative` ↔ official publisher guide cards from **one Paramount corporate publisher family**; no independent narrative corroboration is claimed. Memory Alpha and its descendants remain external discovery sources, not additional witnesses.
- Regenerate with `python3 tools/build_episode_guide_rechecks_b006.py`; verify with `python3 tools/build_episode_guide_rechecks_b006.py --check` and `python3 -m unittest tests.test_episode_guide_rechecks_b006 -v`. The compiler pins the exact catalog SHA and observed title/slot/status mapping; all protected effects fail closed.
