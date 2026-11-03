# B006 — Deep Space Nine / Voyager official episode-guide metadata rechecks

**Status: source-local proposal only.** These records do not establish complete episodes read, admitted Works, corpus evidence, independent corroboration, synopsis publication authorization, or governed coverage advancement.

The exact bounded frontier is 16 original `wikidata:wdqs` discovery entries `lead:0067`–`lead:0082` in the pinned `explorer/discovery-catalog.json` (three Deep Space Nine and thirteen Voyager). Source titles and source-local identities are preserved. Primary publisher guide cards were read on **2026-11-03** from Paramount+:

- [DS9 Season 6](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/6/) and [Season 7](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/).
- Voyager [Season 1](https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/), [Season 2](https://www.paramountplus.com/shows/star_trek_voyager/episodes/2/), [Season 3](https://www.paramountplus.com/shows/star_trek_voyager/episodes/3/), [Season 4](https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/), [Season 5](https://www.paramountplus.com/shows/star_trek_voyager/episodes/5/), [Season 6](https://www.paramountplus.com/shows/star_trek_voyager/episodes/6/), and [Season 7](https://www.paramountplus.com/shows/star_trek_voyager/episodes/7/).

Each `observations.json` row declares its source-local ID, series, publisher episode slot and exact official card title, unresolved title state, and original one-sentence synopsis draft. The deterministic `records.json` compiler derives source and official URL locators, observed date, separate upstream source families, and fail-closed non-admission fields. Publisher page HTML bytes were not captured or pinned, so all publisher raw body digests remain `null`; a rendered card observation must never be treated as cryptographic source custody.

**Identity hold:** Voyager's source-local `lead:0074` title *Caretaker* points to a single official S1E1 episode-guide card **Caretaker, Part 1 & 2**, which is a combined multipart listing. We have **not** resolved the source-local Work identity or assumed one or two canonical Works. The episode synopsis draft is therefore `null`, with `COMBINED_MULTIPART_LISTING_UNRESOLVED` and a withheld-synopsis state.

**Publisher title variants held unresolved:** `lead:0069` *Favor the Bold* versus *Favor The Bold*; `lead:0073` *Time and Again* versus *Time And Again*. No automatic global alias decision is made. The other 13 episode titles match literally.

**B006 proposal counts:** 16 official publisher cards read, 13 literal matches, two unresolved capitalization variants, one combined multipart listing, 15 original source-description-grounded synopsis drafts pending human review, zero public synopsis approvals, zero source-body hashes, zero admitted evidence or Works, and zero governed coverage events. All publisher observations share **one Paramount corporate upstream lineage**; they are not 16 independent corroborating sources. No copyrighted transcripts, media, or publisher blurb copies are included.

**Denominator discipline:** Before accepting this tranche, accepted B001–B005 comprise 72 distinct source-local directory recheck IDs / 1,214 (including 67/218 Research Leads and 5/9 literary rows), **not** canonical Work or close-read coverage. If B006 is accepted, this would increase to 88 / 1,214 source-local directory rechecks, 83 / 218 original Research Leads and 5 / 9 literary rows, all still `NOT_ADMITTED` for governed research coverage.

Reproduce with `python3 tools/build_episode_guide_rechecks_b006.py --check` and `python3 -m unittest discover -s tests -p 'test_episode_guide_rechecks_b006.py' -v`. The generated `records.json` file is an exact derivative and must be regenerated if its pinned 1,214-row source directory changes.
