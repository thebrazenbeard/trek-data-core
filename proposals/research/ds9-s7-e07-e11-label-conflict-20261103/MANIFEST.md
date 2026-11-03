# DS9 Season 7 Episodes 7–11 — official-card source label audit

**DS9 worker**, local source-metadata proposal. **Base:** accepted `main@1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b`, observed 2026-11-03 UTC. **No Work identity, Source↔Work binding, approved synopsis, primary audiovisual read, script read, or governed coverage effect.**

## Bounded sources actually opened

The official [Paramount+ Deep Space Nine Season 7 Episode Guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/) displayed five consecutive title/slot/brief-description cards for **S7E7–E11**. The earlier accepted `publisher-season7-20261102/ds9.csv` shares the same upstream publisher guide, with historical CSV SHA-256 `1dbfe6a4b6af54a5eb2831108d358c8c3f984346b1b3a79de6301ccf2dc22aea` and separately recorded historical HTML response SHA-256 `23dcb2cc9d7baec5e13ee27f80054ee3dcf9f95ae86985f6ecaaf1303f946cf1`. No fresh raw HTML/body bytes were captured; the historical hash **does not** authenticate the current rendering.

| Publisher source-local row | Paramount+ currently displays | Source label status |
| --- | --- | --- |
| `publisher:s7:ds9:006` | S7E7 Once More Unto the Breach | Matches historical CSV |
| `publisher:s7:ds9:007` | S7E8 **The Siege of AR-555** | Same-family official label disagreement, unresolved |
| `publisher:s7:ds9:008` | S7E9 Covenant | Matches historical CSV |
| `publisher:s7:ds9:009` | S7E10 It's Only A Paper Moon | Matches historical CSV |
| `publisher:s7:ds9:010` | S7E11 Prodigal Daughter | Matches historical CSV |

**Material discrepancy, directly observed:** Paramount+'s S7E8 guide and [episode detail listing](https://www.paramountplus.com/shows/video/mIdm1LceoK_eeqSuaO8_jl7G_QNJuhi6/) label the card **“The Siege of AR-555.”** The first-party [StarTrek.com 2014 episode preview page](https://www.startrek.com/videos/episode-preview-the-siege-of-ar-558) labels it **“The Siege of AR-558”**; a [2023 StarTrek.com article](https://www.startrek.com/en-un/news/fan-favorite-deep-space-nine-quotes) also labels **“The Siege of AR-558,” Season 7, Episode 8**. These are first-party published labels from the **same Paramount/CBS corporate provenance family**, not independent primary audiovisual witnesses. This worker neither corrects the catalog nor chooses a canonical Work title. Both labels and their precise locators are preserved as source-local observations.

Only four original brief-description paraphrase drafts were prepared. The S7E8 synopsis draft is **withheld** because the title/version discrepancy requires investigation and a separate identity/edition decision. All four others are editorial candidates, not approved public synopses or fictional episode evidence. Actual episodes, scripts, screen recordings and media were not accessed.

## Hostile falsifiers

> **A title is not a Work identity.** The same publisher family displaying AR-555 on a stream catalog and AR-558 in editorial material does not prove that one surface is canonical or that a particular episode cut was viewed.

> **Repeated corporate surfaces are not independent witnesses.** Even agreement between a Paramount+ card, Paramount+ episode detail and StarTrek.com does not produce a second studio witness family.

> **A raw historical page hash is not a current episode hash.** The November 2 HTML capture receipt cannot establish November 3 page bytes, much less copyrighted audiovisual/script source fidelity.

> **No synopsis bypass.** A publisher blurb paraphrase is a draft description of publisher metadata. Unresolved source titles withhold drafts, and passed validation is not editorial approval.

[Director queue issue #23](https://github.com/thebrazenbeard/trek-data-core/issues/23) still restricts new primary episode close-reading. This batch is a source-local five-card catalog verification, not a full research batch. No external artwork, transcript or protected source content is committed.

## Reproduction and next frontier

```bash
python3 proposals/research/ds9-s7-e07-e11-label-conflict-20261103/validate.py
python3 -m unittest discover -s proposals/research/ds9-s7-e07-e11-label-conflict-20261103 -p 'test_*.py'
```

The validator must fail closed on changed directory/CSV receipts, misplaced guide slots, an altered conflict label or source URL, fake rights/source hashes, hidden full text/host paths, status promotion, missing null synopsis, and optimized-mode mutation. A separate Librarian/Director Source↔Work and source-edition process, plus independent review, is required before reconciling AR-555 versus AR-558.
