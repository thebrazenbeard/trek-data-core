# Voyager S1: first five publisher-listed episode slots — proposal

Observation date: **2026-11-02**. Mission: `voy` (*Star Trek: Voyager*). Status: **CANDIDATE_METADATA_ONLY**.

## Source observations

The [Paramount+ Season 1 episode guide](https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/) directly displayed these five **listed entries in sequence**. The episode numbers are the publisher's displayed slots, **not a newly inferred contiguous count**.

| Listed position | Paramount+ displayed slot | Publisher heading |
| --- | --- | --- |
| 1 | S1E1 | Caretaker, Part 1 & 2 |
| 2 | S1E3 | Parallax |
| 3 | S1E4 | Time And Again |
| 4 | S1E5 | Phage |
| 5 | S1E6 | The Cloud |

Primary page: `https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/` (observed through a web-rendered publisher page, not a retained response-byte capture).

Same-family editorial checks:

1. [StarTrek.com, “Star Trek: Voyager — Communication”](https://www.startrek.com/videos/star-trek-voyager-communication) expressly labels *Caretaker* “Season 1, Episodes 1 & 2” (published 2020-12-10). This supports a *two-installment identification*, while the Paramount+ platform currently displays **one combined playback listing at E1**. The absent standalone E2 listing in that guide is not proof that no E2 installment exists.
2. [StarTrek.com, “20 Years Ago Today... Voyager Debuted With 'Caretaker'”](https://www.startrek.com/news/20-years-ago-today-voyager-debuted-with-caretaker) states that the **two-hour premiere** aired **1995-01-16**. The Paramount+ season guide's search-indexed metadata dated the combined listing **1995-01-17**; the individual Paramount+ video result exposed a differing **1995-01-16**. These are **publisher-display date disagreements**, not reconciled release facts. This batch deliberately does not encode a canonical airdate.
3. [StarTrek.com, “The Unique Experience of Motherhood in the Delta Quadrant”](https://www.startrek.com/news/the-unique-experience-of-motherhood-in-the-delta-quadrant-0) refers to *The Cloud* as **Season 1, Episode 6** (published 2021-05-09), matching the displayed Paramount+ slot.

All named pages are within the **Paramount/Star Trek franchise publishing family**; they do **not** amount to independent upstream corroboration. A separate indexed Australian Paramount+ result appeared to have distinct *Caretaker, Part 1* treatment, but directly opening that international page redirected to a generic landing page. The divergent indexing is only a discovery lead and is not admitted as a directly verified regional catalog record.

## Internal hostile challenges (not an independent review)

> **Challenge 1 — unit ambiguity:** A 91-minute platform asset at E1, a two-hour premiere, and a franchise article calling it Episodes 1 & 2 do not establish whether a future canonical Work registry should represent one feature-length Work, two episode Works, or a containing broadcast unit plus contained parts. The Librarian/Consolidator must settle this with versioned source and unit evidence; this worker does not make the reconciliation.
>
> **Challenge 2 — freshness and independence:** A web-rendered episode guide can be localized, reordered or revised without an immutable publisher-byte capture. The franchise editorial checks have shared ownership and cannot transform the proposal into independent corroboration. A CSV digest authenticates only the local transcription, not the remote page.
>
> **Challenge 3 — date contradiction:** A one-day difference cannot be assumed to mean a time-zone conversion. Other causes include catalog errors or edition-specific dates. Treat the dated fields as separate attributed displays pending a primary broadcast-source review.

## Scope, exclusions and unresolved questions

- **RETRIEVED / metadata:** Five episode title/slot pairs visible in the official US publisher's Season 1 guide, in the order above. These are **five displayed listings**, not a claim that Season 1 contains five episodes or that every episode was inspected.
- **UNRESOLVED / editorial vs streaming unit:** A two-part/two-hour broadcast pilot may be treated as two episode ordinals but one combined streaming asset. Preserve `S1E1` and `S1E3` exactly as displayed; **do not silently create E2** in this publisher roster, and do not collapse the two editorial installments into one canonical Work.
- **UNRESOLVED / dates:** Indexing and publisher pages disagree by a day around the premiere. Resolve by original broadcast records and edition/time-zone history before any accepted date assertion.
- **NOT PERFORMED:** No stream, audiovisual bytes, complete script, subtitles, transcript or book text were viewed/read. No source HTTP response was retained, so `response_sha256` and publisher revision stay null. The receipt hash covers **only** the committed local CSV bytes.
- **NO ACCEPTED EFFECTS:** No canonical Source, Work, local entity, narrative Evidence, continuity Assertion, source↔work binding, coverage event, accepted denominator or reconciliation decision was created. Candidate metadata cannot advance research coverage.

## Reproduction and next frontier

```sh
python3 tools/normalize_episode_roster.py --csv proposals/discovery/voy-publisher-s01-b001-20261102/observed_slots.csv --receipt proposals/discovery/voy-publisher-s01-b001-20261102/observation.json --output proposals/discovery/voy-publisher-s01-b001-20261102/bundle.json --check
python3 tools/validate_publisher_episode_roster.py --input proposals/discovery/voy-publisher-s01-b001-20261102/bundle.json
```

Next: independent source/crosswalk review of *Caretaker*'s original broadcast unit against streaming editions, lawful full-content access and exact source binding. Only then can a separately accepted audiovisual research batch begin. There is **no approved source-content frontier** in this proposal.
