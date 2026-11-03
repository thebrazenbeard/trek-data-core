# DS9 publisher Season 1: first five displayed episode entries

**Role:** DS9 audiovisual worker. **Observation date:** 2026-11-02.
**Status:** `CANDIDATE_METADATA_ONLY` / `DISCOVERED` publisher listing. Not an accepted research batch or episode-content witness.

## Observed publisher metadata

The public [Paramount+ Season 1 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/1/) displayed these *first five entries*, with source-local season and episode labels:

| Display position | Publisher label | Publisher title |
| --- | --- | --- |
| 1 | S1 E1 | The Emissary, Parts I and II |
| 2 | S1 E3 | Past Prologue |
| 3 | S1 E4 | A Man Alone |
| 4 | S1 E5 | Babel |
| 5 | S1 E6 | Captive Pursuit |

These are five **display positions**, not an assertion of five sequential numerical episode slots: Paramount+ shows the combined-length premiere as E1, followed immediately by E3. The missing **E2 label is not a missing observed title**, nor is an E2 record invented in this batch. The titles and labels above were observed from the publisher page using a public web-reader view, not inferred from a fan database, recap, transcript, or filename.

The related [StarTrek.com publisher retrospective on “Emissary”](https://www.startrek.com/news/ds9-premiere-emissary-aired-22-years-ago-this-week) reports the original January 3, 1993 two-hour broadcast and says the later March 1993 syndicated repeat separated the pilot into *Part I* (#401) and *Part II* (#402), after an original media schedule called it #721. This is publisher-authored **context for representation/ordinal ambiguity**, not proof that any proposed streamable item equals either syndicated half. The article and Paramount+ episode guide belong to the same underlying Paramount publisher family and **are not independent content corroboration**.

## Exact scope, limitations, and reproducibility

- `roster.csv` preserves only the five publisher-listed titles and source-local numbered slots. `observation_receipt.json` captures the observed page locator, same-publisher crosscheck, observation date, and SHA-256 of **our local CSV bytes**; it does **not** claim a publisher HTML response hash.
- `bundle.json` was produced by the repository's offline `tools/normalize_episode_roster.py` and validated by `tools/validate_publisher_episode_roster.py`. It deliberately has no canonical Work IDs, source-binding IDs, accepted registry mutation, coverage effect, denominator effect, or completeness claim.
- No audiovisual media, captions, full scripts, complete transcripts, or literary primary texts were retrieved or read. The publicly visible publisher listing and publisher retrospective do not satisfy the full-source research method. Therefore **no** `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, `CROSS_REFERENCED`, or `AUDITED` state is asserted.
- A full Season 1 count is **not** derived by extrapolating these five entries, by interpreting pilot halves, or by accepting any publisher display numbering as a canonical identity policy.
- No proprietary episode synopses, source page bodies, media, or passage excerpts are reproduced here. Publisher site revision and response SHA-256 remain `null`; current page content could change.

**Accepted baseline:** On `main@c7a14ddb62dfa45d5d01855952d9e562c1af21de`, the nonfixture pilot-readiness audit reported `accepted_nonfixture_episode_works = 0` and `TECHNICAL_PREREQUISITES_BLOCKED`. This proposal does not advance that count.

## Offline checks

```sh
python3 tools/validate_publisher_episode_roster.py --input proposals/discovery/ds9-publisher-s01-b001-20261102/bundle.json
python3 -m unittest discover -s tests -p 'test_ds9_publisher_batch.py' -v
```

**Exact next frontier:** The Librarian must admit a source and choose/verify scoped Work identity and pilot presentation variants; DS9 audiovisual research then needs permissioned access to and actual processing of a complete primary episode representation before creating source-relative evidence and semantic assertions. Until then this remains five publisher-discovery entries, not five episodes researched.
