# DS9 B006 publisher-guide tail: source-local cards only

**Role:** DS9 series worker. **Accepted base checked:** `5ea4a8d562e76931218329b8386e363e3c40845f`, 2026-11-03 UTC. **Status:** proposal only; zero accepted Source↔Work, close-read, public synopsis, identity reconciliation or coverage effects.

## Exact scoped frontier

The accepted B005 recheck covered directory leads `lead:0051`–`lead:0066`. The next three and final contiguous **DS9 entries in this particular Wikidata-derived 218-row Research Leads discovery partition** are `lead:0067`–`lead:0069`. The next entry, `lead:0070`, belongs to VOY and is **outside** this DS9 worker's remit. This is not an overall DS9 installment count or a governed Work denominator.

These three source-local candidate episode titles were checked against the public, rendered [Paramount+ Season 7 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/) and [Season 6 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/6/). The displayed guide titles, slots and short descriptions were read; **no episode audiovisual source, full script, raw publisher page byte snapshot or edition/cut was read or captured**.

| Source-local seed | Official rendered card locator | Title result |
| --- | --- | --- |
| `lead:0067` Image in the Sand | Season 7, Episode 1 | Exact literal title |
| `lead:0068` His Way | Season 6, Episode 20 | Exact literal title |
| `lead:0069` Favor the Bold | Season 6, Episode 5, publisher *Favor The Bold* | Case variant; unresolved |

`observations.json` preserves the Wikidata seed locator separately from the Paramount+ corporate publisher family. The three one-sentence, original **publisher-card description paraphrases** are editorial candidates pending separate review, not observations from an actual episode viewing, approved public synopses, or claims of fictional objective reality. `assertions.json` contains one source-local unresolved capitalization observation, with a falsifier and no global identity effect.

## Source and identity limits

The episode catalog displays publisher metadata, not a primary audiovisual performance. It does not prove a broadcast date, edit, runtime, region, script draft, scene, character's inner state, or that two similarly named entries are governed identical Works. Previous B005 had an apparent publisher-blurb association conflict for *The Visitor*; therefore no publisher description is automatically treated as authoritative source-body fidelity. These three descriptions appeared aligned with their adjacent displayed titles and slots, **but were not cross-validated against a full episode**.

`observations.json` contains no media or copyrighted transcript. No auto-generated public projection was altered. The accepted [Director issue #23 hold](https://github.com/thebrazenbeard/trek-data-core/issues/23) applies throughout.

> **Hostile challenge:** A title and card blurb on a distributor page are not a viewed episode, and agreement with a Wikidata label does not constitute independent Work authentication.

> **Hostile challenge:** A source-family self-description and a derivative Wikidata seed are separate evidence classes; neither can establish canonical episode identity or independent scene evidence.

## Reproducibility and next gate

The validator compares the exact 1,214-row discovery directory SHA-256, closed record schema, three pinned source-local IDs/locators, guide slots, title-case classification, source-relative observation and original paraphrase fingerprints. It fails closed on extra keys, forged paths, admissions, missing/extra rows, duplicate JSON keys, spurious script/AV evidence, and altered synopsis statuses. Tests exercise these mutations in both normal and optimized Python.

```bash
python3 proposals/research/ds9-publisher-guide-tail-b006-20261103/validate.py
python3 -m unittest discover -s proposals/research/ds9-publisher-guide-tail-b006-20261103 -p 'test_*.py'
```

**Next permitted DS9 action:** Seek an authenticated, rights-authorized byte-addressable source and a governed Source↔Work proposal through the Librarian/Director. A later close-read requires Director hold release plus actual full primary-source access. This catalog-only B006 tranche cannot self-promote.
