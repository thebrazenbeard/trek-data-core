# Prodigy Season 1 — five source-local distributor display entries

**Worker:** PRO / *Star Trek: Prodigy* audiovisual lane. **Observed:** 2026-11-02. **Accepted `main`:** `c7a14ddb62dfa45d5d01855952d9e562c1af21de`.

**Status:** `CANDIDATE_METADATA_ONLY` / `DISCOVERED`. No full episode media was read, no canonical Work/Source was admitted, and no source-binding or coverage status changed.

## Direct primary listing observation

The [Apple TV US Prodigy series listing](https://tv.apple.com/us/show/star-trek-prodigy/umc.cmc.1zqk40gcoayvwt9tai2555wkp) is a **first-party distributor catalog**. Its visible Season 1 entries on the inspected public page list:

| Display position | Apple TV's Season 1 ordinal | Apple TV title |
| --- | --- | --- |
| 1 | E1 | Lost & Found, Pt. 1 |
| 2 | E3 | Starstruck |
| 3 | E4 | Dreamcatcher |
| 4 | E5 | Terror Firma |
| 5 | E6 | Kobayashi |

The first entry is labeled "Pt. 1" on the distributor page but has a **46-minute displayed duration** and the listing skips ordinal E2. **Do not infer that E2 does not exist** or treat E1 as a canonical single-part Work. The official [StarTrek.com premiere announcement](https://www.startrek.com/news/how-to-watch-star-trek-prodigy) described its original October 28, 2021 release as a one-hour premiere, which is consistent with—but does not on its own prove—the interpretation that this 46-minute Apple listing packages two broadcast portions. The [Google Play distributor catalog](https://play.google.com/store/tv/show?cdid=tvseason-IVMVVNG-9Uc.P&gdid=tvepisode-h0wvFXP0Bs4.P&id=r3JzXJmWKtY.P) separately displays E1 "Lost & Found Part 1" and E2 "Lost & Found Part 2"; this is a **cross-distributor catalog discrepancy**, not a reconciliation vote. Google Play's later S1 metadata also contains a duplicate "All The World's A Stage" at E6 and E13, so its ordinal series requires further source review.

The official [StarTrek.com Prodigy show page](https://www.startrek.com/en-un/series/star-trek-prodigy) currently identifies Netflix and SkyShowtime as availability venues, which explains why a Paramount+ episode guide was not assumed to be present. **Publisher vs rights-holder are distinct:** Apple TV controls this observed distributor listing, while the listing credits Viacom as the studio/copyright holder. Neither fact establishes who supplied Apple's episode-metadata feed. The receipt therefore marks `independence_group: INDEPENDENCE_UNRESOLVED`; do **not** count Apple, Google Play, and StarTrek.com as independent evidence for narrative claims until their actual upstream content lineage is authenticated.

This five-slot batch is neither a season-completeness count nor evidence of the actual narrative. Episode summaries were not copied or transformed into story assertions. `roster.csv` holds exactly the observed title/slot pairs; its SHA-256 in `observation_receipt.json` authenticates **our CSV bytes**, not any publisher HTML. The observed page was read as a public web rendition, with no locally owned raw publisher-byte digest. Full-source inspection, local entities, source-relative evidence, neutral assertions, and higher coverage levels remain pending.

## Reproduction

```sh
python3 -B tools/normalize_episode_roster.py --csv proposals/discovery/pro-publisher-s01-b001-20261102/roster.csv --receipt proposals/discovery/pro-publisher-s01-b001-20261102/observation_receipt.json --output proposals/discovery/pro-publisher-s01-b001-20261102/bundle.json --check
python3 -B tools/validate_publisher_episode_roster.py --input proposals/discovery/pro-publisher-s01-b001-20261102/bundle.json
python3 -B -m unittest discover -s tests -p 'test_pro_publisher_batch.py' -v
```

**Next:** Librarian review of publisher catalog variant, combined/separate premiere identity, raw-source custody and permissioned full-episode access; only then can the PRO lane conduct the substantive close-read required for episode-level research.
