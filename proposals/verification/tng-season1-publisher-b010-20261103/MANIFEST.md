# TNG season-one B010 — first-party publisher card recheck (held proposal)

**Scope:** Ten source-local Paramount season-one slots: `legacy:s1:tng:000`–`007`, `009`–`010`. The missing `008` is the *Hide and "Q"* title already included as the Wikidata-derived TNG overlap in accepted B004; the two source-local lines are not merged or counted as independent witnesses. Baseline accepted `main` at discovery: `1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b`.

**First-party source actually read on 2026-11-03:** [Paramount+ Star Trek: The Next Generation — Season 1 Episode Guide](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/1/), complete rendered guide section and raw HTML card metadata. Ten selected cards were individually examined for official title, publisher season/episode slot, description, and the HTML `<img src>` URL lead. The copyrighted descriptions are not copied into the repository. Each source card's description text has a SHA-256 fingerprint of its Unicode HTML-decoded, whitespace-trimmed text; this is a verification lead, not a preserved original HTML snapshot. This batch does **not** claim archived raw HTML bytes or full audiovisual source viewing.

**Evidence discipline:** The prior `legacy-paramount-season1` discovery listing and this reread derive from the **same Paramount publisher lineage**. Ten separately read cards are ten card observations, **not ten independent corroborating organizations**. The observations retain the exact accepted discovery row IDs/locators. Short original synopsis paraphrases are *publisher-description frames* only; their fidelity still requires editorial/human review. Literal character and organization mentions are source-relative strings, not globally resolved entities or assertions of what happened in the fictional world.

| Source-local row | Publisher guide card | Card status |
| --- | --- | --- |
| `legacy:s1:tng:000` | Encounter At Farpoint Part 1 and 2 — S1E1 | **Combined-card/part-identity hold**; no split inferred |
| `legacy:s1:tng:001` | The Naked Now — S1E3 | Title/slot reread |
| `legacy:s1:tng:002` | Code of Honor — S1E4 | Title/slot reread |
| `legacy:s1:tng:003` | The Last Outpost — S1E5 | Title/slot reread |
| `legacy:s1:tng:004` | Where No One Has Gone Before — S1E6 | Title/slot reread |
| `legacy:s1:tng:005` | Lonely Among Us — S1E7 | Title/slot reread |
| `legacy:s1:tng:006` | Justice — S1E8 | Title/slot reread |
| `legacy:s1:tng:007` | The Battle — S1E9 | Title/slot reread |
| `legacy:s1:tng:009` | Haven — S1E11 | Title/slot reread |
| `legacy:s1:tng:010` | The Big Goodbye — S1E12 | Title/slot reread |

**Art:** Ten `thumbnails.cbsig.net` asset *locator strings* were present in the official publisher card HTML. They are held in `records.json` as leads only. No image bytes downloaded into this repository, image license/reuse adjudicated, Explorer thumbnail changed, or artwork publication authorized. This is not a claim that thumbnails can legally or technically be hotlinked for display.

**Strict result:** 10 card reads, 10 description fingerprints, 10 original draft paraphrases held, 10 artwork URL leads held, 1 combined-card identity hold, **zero** full episodes/transcripts viewed, **zero** governed research admission, **zero** approved/public synopsis or artwork, **zero** Explorer population. Existing discovery statuses remain unchanged. This proposal is not a substitute for the Consolidator's accepted evidence/reconciliation projection work.

Build/validate without network:

```bash
python3 tools/build_tng_publisher_cards_b010.py --check
python3 -m unittest tests.test_tng_publisher_cards_b010
```

The deterministic compiler binds every row to the accepted 1,214-row discovery snapshot, rejects source-title/ordinal/fingerprint changes, **exact wrong-episode same-host thumbnail substitutions**, **invented character identity in literal publisher-description mentions**, source-family contamination, false AV viewing/custody claims, false part splitting, and accidental synopsis/art admission. Each thumbnail URL is pinned to its exact independently observed publisher card; a valid CBS URL for another episode does not pass. In *The Big Goodbye* the source says only "the Captain", so `Captain Picard` is deliberately **not** claimed as a literal source mention; the original synopsis draft similarly avoids inferring that identity. Source retrieval correctness and paraphrase originality remain independently reviewable **human/model judgments**; the tests do not manufacture that assurance.

**Next frontier:** adjacent `legacy:s1:tng:011` onward, plus independent editorial verification of this tranche, followed by versioned reconciliation if warranted. Do not claim new global Works, accepted semantic coverage, or publicly released media from these records.
