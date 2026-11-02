# TNG Paramount+ episode-slot observations — proposal only

Batch family: `TNG-PARAMOUNT-20261102`. Observation date: 2026-11-02.

This records **five publisher-listed metadata slots**, not a complete season,
an accepted Mission Briefing corpus, or an audiovisual inspection. Three
separate bundles make each slot traceable to the actual Paramount+ season page
used for the observation. The source pages were examined through public page
renderings; raw HTTP response bytes, page revisions, signed snapshots, and
source-content digests were **not** retained or attested.

| Bundle | Mission Briefing identity candidates | Primary source |
| --- | --- | --- |
| `season-1/bundle.json` | S1E10 *Hide and "Q"*; S1E23 *Skin of Evil*; S1E26 *The Neutral Zone* | [Paramount+ Season 1](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/) |
| `season-4/bundle.json` | S4E3 *Brothers* | [Paramount+ Season 4](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/4/) |
| `season-5/bundle.json` | S5E10 *New Ground* | [Paramount+ Season 5](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/5/) |

The `crosscheck_locator` on each bundle is a **related page**, not an
independent corroborating publisher or a verification of every bundled row:

- Season 1: [StarTrek.com *The Neutral Zone* page](https://www.startrek.com/videos/star-trek-the-next-generation-the-neutral-zone) also displays that *one* S1E26 slot, not the other two.
- Season 4: [StarTrek.com Picard watch guide](https://www.startrek.com/news/your-ultimate-star-trek-picard-watch-guide) mentions *Brothers* as TNG, but provides no episode ordinal.
- Season 5: [StarTrek.com *New Ground* page](https://www.startrek.com/videos/watch-star-trek-the-next-generation-new-ground) also displays S5E10.

All sources belong to the same **Paramount publisher family**. Separate domain
names, websites, video pages, previews and editorial posts do not create
independent rights-holder witnesses. They are episode identity metadata,
not evidence that the full episodes were accessed or reviewed.

## Unresolved source differences

1. **Title formatting:** Paramount+ displays `Hide and "Q"`, whereas the
   existing TNG Librarian proposal uses `Hide and Q`. The proposed link is
   plausible, but a verified external crosswalk and canonical title have not
   been approved.
2. **Date:** A [StarTrek.com retrospective](https://www.startrek.com/news/a-look-back-at-skin-of-evil)
   says *Skin of Evil* premiered April 25, 1988; Paramount+'s season-one
   listing labels April 26, 1988. These may refer to different broadcast and
   platform conventions. Neither date is accepted as the sole authoritative
   series chronology.
3. **Multipart counting:** Paramount+ lists *Encounter at Farpoint Part 1 and
   2* under S1E1 and continues with S1E3. A streaming listing row must not be
   mistaken for one uniform underlying episode component or counted as a
   season denominator.
4. **Subscription counts:** Publisher pages expose different
   subscription-availability totals (176 versus 178). These are service-facing
   availability claims, not independently reconciled Work counts.

## No admission effect

Every bundle is `CANDIDATE_METADATA_ONLY`, with `roster_completeness:
UNRESOLVED`; every row has `canonical_work_id: null` and
`source_binding_id: null`. All accepted-Work, binding, coverage and
denominator effects are `NONE`. No videos, transcripts, scripts, plot prose,
or publisher page bodies are stored here.

The next reviewer must verify a dated page representation, inspect title/slot
mapping and multipart rules, reconcile existing candidate crosswalks, and
obtain separate authorized episode-content evidence before any
`EVIDENCE_BEARING` Source↔Work binding or continuity claim.

Check the bounded JSON contract:

```sh
python3 tools/validate_publisher_episode_roster.py --input proposals/discovery/tng-paramount-season-slots-20261102/season-1/bundle.json
python3 tools/validate_publisher_episode_roster.py --input proposals/discovery/tng-paramount-season-slots-20261102/season-4/bundle.json
python3 tools/validate_publisher_episode_roster.py --input proposals/discovery/tng-paramount-season-slots-20261102/season-5/bundle.json
python3 -m unittest discover -s tests -p 'test_tng_paramount_season_slots.py' -v
```

This proposal supplements, but does not edit or supersede,
`proposals/librarian/tng-official-metadata-20261102/`.
