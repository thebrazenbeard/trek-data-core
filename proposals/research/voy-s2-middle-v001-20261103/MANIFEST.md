# VOY V001 — Season 2 official guide, episodes 6–15

**Role:** VOY publisher metadata research worker. **Accepted main checked at selection:** `2070b0153228272b5dd667b0a23465ff49a95a5f` (2026-11-03 UTC). **Status:** unaccepted source-relative candidate evidence only. No admitted Source↔Work relationship, global identity, complete audiovisual/script source, approved synopsis, artwork license, database admission or coverage event.

## Direct first-party page read

I freshly opened and read the visible `S2 E#` display positions and titles on Paramount+'s official [*Star Trek: Voyager* Season 2 episode guide](https://www.paramountplus.com/shows/star_trek_voyager/episodes/2/), specifically the ten contiguous cards **S2E6–S2E15**. Descriptions appeared below the cards but **no source description or original paraphrase is stored**; no episode video, transcript, raw current HTML bytes, authenticated page DOM, image asset URL, image bytes, or rights grant was obtained.

| Unadmitted discovery row | Current publisher guide title/position |
| --- | --- |
| `legacy:s2:voy:005` | S2E6 — *Twisted* |
| `legacy:s2:voy:006` | S2E7 — *Parturition* |
| `legacy:s2:voy:007` | S2E8 — *Persistence of Vision* |
| `legacy:s2:voy:008` | S2E9 — *Tattoo* |
| `legacy:s2:voy:009` | S2E10 — *Cold Fire* |
| `legacy:s2:voy:010` | S2E11 — *Maneuvers* |
| `legacy:s2:voy:011` | S2E12 — *Resistance* |
| `legacy:s2:voy:012` | S2E13 — *Prototype* |
| `legacy:s2:voy:013` | S2E14 — *Alliances* |
| `legacy:s2:voy:014` | S2E15 — *Threshold* |

Each record has its own **local source-card entity**, **source-relative evidence ID**, literal current guide title, displayed slot and locator. Evidence kind is `PUBLISHER_GUIDE_CARD_DISPLAY` and evidence scope is `TITLE_AND_SLOT_ONLY`; the source does not support claims of episode events, objective fictional truth, source-body text, scene order, characters' internal states, broadcast chronology, or physical edition identity. The underlying directory calls these rows `UNVERIFIED_METADATA`, not accepted Works.

## Provenance, overlap, held publication

The accepted discovery directory SHA-256 is `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`. The older Paramount Season 2 discovery CSV SHA-256 is `192a970935739a618b68609598532443da8fb9de2529d1d53399b323245c0a97`. Those input receipts establish **repository provenance**, not newly captured webpage bytes. The source family of the CSV and current first-party guide is **the same Paramount corporate publisher lineage**, not independent corroboration.

The accepted Voyager B006 verification observations SHA-256 is `3b55fcf2b9a9aab7a02293400e4ccac1f62d0ad097ffb2ff057f02fa305b8080`. Its two Season 2 title/slot observations concern *Initiations* **S2E2** (`lead:0076`) and *Investigations* **S2E20** (`lead:0077`), neither in this tranche. Active Draft PR #290 proposes a B006 DS9/Voyager mixed guide check of the same Wikidata-lead partition and is not an accepted new research tranche. The accepted Voyager region-split hold discusses S5 and S7 presentation variants, not S2E6–E15. The metadata directory already contains these ten entries; current publisher checking must not create duplicate Work identities.

The episode-guide page serves as a **candidate starting point for future artwork discovery only**. The text-oriented retrieval did not authenticate any specific thumbnail URL, asset, file hash, license or reuse right, so each record holds `artwork_candidate_page_url` at the official guide, `artwork_asset_url:null`, and `artwork_rights_status:UNKNOWN_HELD`. Similarly every synopsis is `HELD_NO_PUBLIC_TEXT_OR_PARAPHRASE`. There are **zero public synopsis or artwork effects** and no image hotlinking or copying.

> **Hostile challenge:** A first-party streaming metadata card is neither a fully viewed production nor a reliable proof of a uniquely reconciled episode edition. Same-publisher agreement with the previous CSV is dependent evidence, and apparent card descriptions could be wrongly associated with titles. No narrative paraphrase is admitted on that basis.

> **Artwork falsifier:** The guide is an address for an investigator, not a licensed image asset. A URL found in page markup would still need ownership, rights, derivative origin and reuse permission checked before publication; no artwork is presently approved.

## Reproducibility and next frontier

`observations.json` contains ten scoped source-local evidence cards; `validate.py` pins the accepted directory, prior VOY B006 source checks and historical Paramount CSV by SHA-256, checks exact current title/slot locators, rejects duplicate JSON keys and all unknown authenticity/coverage/rights fields, and forbids public release or Work promotion. Adversarial regression probes run under ordinary and optimized Python, including false artwork licensing, falsified HTML/body availability, reinserted previously rechecked S2E2, and duplicate-key provenance tricks.

```bash
python3 proposals/research/voy-s2-middle-v001-20261103/validate.py
python3 -m unittest discover -s tests -p 'test_voy_s2_v001.py'
python3 tools/validate.py
```

**Next Voyager source-card frontier:** Remaining publisher guide spans outside S2E6–E15 can receive similarly bounded metadata rechecks if absent from accepted and draft work. Full audiovisual/semantic reading, source authenticity, Work mapping, and artwork licensing remain independent admissions requiring rights and source custody; this tranche changes none of their coverage ledgers.
