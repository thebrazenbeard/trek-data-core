# DS9 B012 — Season 6 five un-rechecked publisher cards, E1–E4 and E26

**Role:** DS9 source-relative publisher research. **Selection base:** accepted `main@f4ea65391cf1543a55bf19dfcf3ed776dd80ab04` checked 2026-11-03 UTC. **Disposition:** source-local, unadmitted **proposal**. No full episode/video/script read, Source↔Work authentication, new Work admission, global entity resolution, public synopsis release or research coverage effect.

## Source actually read

On 2026-11-03 UTC I opened the first-party [Paramount+ Deep Space Nine Season 6 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/6/) and read the visible titles, displayed S6 E# ordinals, and adjacent description blocks for **E1 A Time To Stand, E2 Rocks And Shoals, E3 Sons And Daughters, E4 Behind The Lines, E26 Tears Of The Prophets**. Each was compared against the already accepted publisher Season 6 CSV and 1,214-row source-local discovery directory. These are **five same-publisher rechecks**, not five independent witnesses or newly discovered episodes. The description drafts in `observations.json` are fresh **original paraphrases of distributor claims**, not findings from viewing the fiction. They remain `HELD_PENDING_INDEPENDENT_EDITORIAL_REVIEW` and are **not approved public synopses**.

This work fills the five remaining source-local Season 6 title/slot-card recheck gaps relative to accepted B006 (E5 and E20), B010 (E6–E15), and B011 (E16–E19, E21–E25). It does **not** resolve the Wikidata-to-Paramount candidate identity crosswalk, and the simultaneously open Draft [PR #290](https://github.com/thebrazenbeard/trek-data-core/pull/290) is unaccepted, not a corroborating source. All 26 Season 6 publisher-directory rows already existed in the discovery projection; this proposal does not inflate its denominator or update the Explorer.

| Source-local row | First-party guide card read | Editorial state |
| --- | --- | --- |
| `publisher:s6:ds9:000` | S6E1 *A Time To Stand* | HELD original distributor-claim paraphrase |
| `publisher:s6:ds9:001` | S6E2 *Rocks And Shoals* | HELD original distributor-claim paraphrase |
| `publisher:s6:ds9:002` | S6E3 *Sons And Daughters* | HELD original distributor-claim paraphrase |
| `publisher:s6:ds9:003` | S6E4 *Behind The Lines* | HELD original distributor-claim paraphrase |
| `publisher:s6:ds9:025` | S6E26 *Tears Of The Prophets* | HELD original distributor-claim paraphrase |

## Provenance and hostile review

The historical CSV and 1,214-row directory have SHA-256 `328e2df32a5492249a756a23a22eb641d135877cfca930ffc444b005c04b9ef8` and `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`, respectively. Accepted B006, B010 and B011 `observations.json` hashes are pinned in the JSON bundle and validator. These authenticate **already accepted repository input bytes** only. I did not capture the current guide response body; `current_raw_html_sha256=null` and `current_raw_html_captured=false` are deliberate. No full audiovisual or script content was accessible or read.

> **A distributor's description is promotional testimony.** It is not direct evidence that the fictional events occurred as described. Draft editorial paraphrases stay held even if the metadata validator passes.

> **Same-family agreement is not independent corroboration.** The live Paramount+ card, earlier Paramount+ CSV and Explorer directory lineage are one publisher family plus a derived projection. They do not establish a unique episode cut or Source↔Work admission.

> **Completing one source-card recheck layer is not primary research completion.** The [Director's source-admission hold](https://github.com/thebrazenbeard/trek-data-core/issues/23) remains. No CLOSE_READ, SEMANTICALLY_ANALYZED or source-authenticated Work coverage increments are claimed.

## Validation and exact next frontier

`validate.py` pins the 5 explicit card slots, expected original paraphrases, accepted directory/CSV/B006/B010/B011 input hashes, source lineage, strict duplicate-key parser and closed research/coverage gates. `tests/test_ds9_s6_b012.py` attacks forged Work admission, source captures, overlapping cards, description promotion, directory drift, and duplicate-key laundering in normal and optimized mode.

```bash
python3 proposals/research/ds9-s6-gaps-b012-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_ds9_s6_b012.py'
python3 tools/validate.py
```

**Next DS9 frontier:** Independently review the five original publisher-claim paraphrases; investigate edition-specific, rights-authorized audiovisual or script custody with the Librarian and Director; resolve Source↔Work binding without conflating publisher row IDs and Wikidata seeds. Season 6's visible title/slot guide is now rechecked in source-local proposals, not fully read as episodes.
