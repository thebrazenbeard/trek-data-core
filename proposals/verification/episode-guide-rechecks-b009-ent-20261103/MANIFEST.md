# B009 Enterprise publisher card checks — proposal, not admission

- Source-local scope: Wikidata-derived `lead:0099` through `lead:0107` in the accepted 1,214-row discovery snapshot.
- Read: [Paramount+ Enterprise season 1 guide](https://www.paramountplus.com/shows/enterprise/episodes/1/) and [season 4 guide](https://www.paramountplus.com/shows/enterprise/episodes/4/) on 2026-11-03, including all nine selected cards and their short descriptions. Read surface: official rendered guide text, not episode streams/transcripts.
- Source family: one Paramount corporate publisher lineage. Wikidata IDs are source-local discovery crosswalks, **not** a second independent witness or canonical Work IDs.
- Exact first-party card titles: `0099` Sleeping Dogs (S1E14), `0100` Desert Crossing (S1E24), `0101` Oasis (S1E20). Three original short publisher-description paraphrases remain *held for editorial review*.
- Title/slot holds: `0102` *In A Mirror, Darkly, Pt 2* vs Wikidata *In a Mirror, Darkly, Part II*; `0103`–`0104` *Storm Front, Pt. 1/2* vs *Part I/II*; `0105` *Shockwave Part I* punctuation; `0106`–`0107` two Wikidata *Broken Bow* part rows versus **one combined official S1E1 “Broken Bow - Part 1 and 2” card**. No split identity, date, or distinct-Work conclusion follows.
- No source bytes captured; no artwork, episode video, transcripts, full-work reading, semantic analysis, global identity resolution, approved public synopsis, governed coverage, or Explorer publication. Evidence is publisher *description* text and card title/slot only.
- Build: `python3 tools/build_episode_guide_rechecks_b009_ent.py --check`; tests: `python3 -m unittest tests.test_episode_guide_rechecks_b009_ent`.

Material ambiguity is preserved as `PART_NUMERAL_STYLE_UNRESOLVED`, `PUNCTUATION_STYLE_UNRESOLVED`, and `COMBINED_CARD_SPLIT_UNRESOLVED`, not silently normalized.
