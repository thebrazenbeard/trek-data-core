# DS9 Season 7 publisher card recheck, five bounded observations

**Role:** DS9 research worker. **Selected accepted base:** `main@8a89b16e96220188d200b6ff9300fb90fa137627`, checked 2026-11-03 UTC. **Disposition:** source-local publisher metadata proposal; no governed Source↔Work binding, Work admission, episode body reading, public synopsis release or coverage effect.

## Source authenticity and version custody

The accepted earlier [publisher Season 7 discovery](../../discovery/publisher-season7-20261102/MANIFEST.md) has a **historical capture-process receipt, not publisher-signed authenticity proof**, from 2026-11-02: `ds9.csv` SHA-256 `1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea` and recorded HTML response SHA-256 `23dcb2cc9d7baec5e13ee27f80054ee3dcf9f95ae86985f6ecaaf1303f946cf1` (length recorded as 314,706 bytes). The historical HTML itself was not re-obtained or inspected here. These hashes pin **historical separate observations**, not the current web rendering.

On 2026-11-03 UTC I opened and read the current public [Paramount+ DS9 Season 7 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/) as rendered text. Current raw HTML was not captured; its body hash is deliberately `null`. The five title/slot/short-description blocks were checked in order, after S7E1 *Image in the Sand* was separately rechecked in DS9 B006. The independent `explorer/discovery-catalog.json` directory is a projection of the prior publisher CSV, **not a second source witness**.

| Source-local directory row | Publisher card directly read | Title/slot comparison |
| --- | --- | --- |
| `publisher:s7:ds9:001` | *Shadows and Symbols* — S7E2 | Exact agreement |
| `publisher:s7:ds9:002` | *Afterimage* — S7E3 | Exact agreement |
| `publisher:s7:ds9:003` | *Take Me Out to the Holosuite* — S7E4 | Exact agreement |
| `publisher:s7:ds9:004` | *Chrysalis* — S7E5 | Exact agreement |
| `publisher:s7:ds9:005` | *Treachery, Faith, and the Great River* — S7E6 | Exact agreement |

`observations.json` includes five source-local record IDs and short **original paraphrases of publisher card descriptions**; all five drafts remain `PENDING_HUMAN_REVIEW` and unapproved for public display. `assertions.json` has one unresolved provenance assertion with its supporting source-card IDs and a falsifier. Neither the historical CSV nor present guide card confirms a particular broadcast or streaming cut, script draft, scene, character motive, title ontology or distinct governed Work.

## Hostile findings and limits

> **Source-family dependence:** The current Paramount+ guide and November 2 Paramount+ CSV share the same corporate upstream. Their title/slot agreement is a same-source recheck, not two independent primary witnesses.

> **Current source-byte gap:** The new rendered text is not a reproducible raw HTML capture. The historical source-body hash may not be reused as if it covered the current page or episode audiovisual content.

> **A distributor synopsis is not source-relative narrative evidence.** These are only original paraphrase *drafts of promotional metadata*, pending editorial review. They must not become approved synopses, local fictional entities, corpus evidence, or close-read coverage via a data projection.

The [Director issue #23 hold](https://github.com/thebrazenbeard/trek-data-core/issues/23) continues to prohibit new primary episode close-reading without accepted Source↔Work and admission infrastructure. All such effects are `NONE` in this proposal.

## Deterministic verification and next frontier

```bash
python3 proposals/research/ds9-s7-publisher-card-recheck-20261103/validate.py
python3 -m unittest discover -s proposals/research/ds9-s7-publisher-card-recheck-20261103 -p 'test_*.py'
```

The validator uses the exact accepted publisher Season 7 CSV and `index.json`, the 1,214-row directory, closed fields/roles, exact five chronological card rows, stable rendered-card labels and pinned observation fingerprints. Tests must reject fabricated Work IDs, URL/cut hashes, unexpected fields, forged titles, case drift, changed publisher capture claims, prose substitution, and admission/coverage promotion, including in optimized Python mode.

**Next source-only frontier:** S7E7 onward, in a separate bounded publisher-card observation. The five draft descriptions require independent editorial review and should not be inserted into public synopsis projections merely because this manifest passes code tests. No source-body or Work denominator is claimed.
