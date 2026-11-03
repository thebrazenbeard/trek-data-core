# Scouts Holodeck Rescues #6–#9 — four publisher-description proposals; #10 held

- Version: `trek-scouts-holodeck-06to09-publisher-description-v1` (2026-11-03 UTC)
- Partition: `SHORT_FORM` / `SOURCE_LOCAL` discovery candidates, not admitted Works
- Primary retrieved evidence **class**: official YouTube video *search-result* `Description` fields, first episode-specific paragraph, publisher `Blaze and the Monster Machines`. **Not** directly opened video-page body or video playback.
- Corporate upstream source family: one (`publisher:paramount-nickelodeon-youtube`). Derivative TV directories copy this description text and do **not** count as independent witnesses.
- Pinned source observations: [`observations.json`](observations.json), SHA-256 `8610b331dc882c1aed933e0ae46a5469666cc7f61e45045222d94f754ec1b116`.
- Proposed statements: four original `PUBLISHER_DESCRIPTION_PARAPHRASE` strings, one NULL held-following row; no canonical fictional plot or watched-episode claim.
- Effect: **NONE** on accepted source/work bindings, evidence ledger, coverage, artwork or public Explorer synopsis release.

| Source-local row | Exact official video ID | Publisher display date | What the publisher Description permits |
| --- | --- | --- | --- |
| Holodeck #6 | [-m7ISEuAhac](https://www.youtube.com/watch?v=-m7ISEuAhac) | 2026-02-14 | Disputing robots, pogo stick, threatened moonchuck home |
| Holodeck #7 | [cYRzkzu_zhg](https://www.youtube.com/watch?v=cYRzkzu_zhg) | 2026-02-28 | Shadowtrix, baby chameleon, lost camouflage, Zips and phaser |
| Holodeck #8 | [O5wUrGB_6qw](https://www.youtube.com/watch?v=O5wUrGB_6qw) | 2026-03-07 | Moon alien forced to mine rocks, bionic arm and astro boots |
| Holodeck #9 | [TbZFOtuHpxk](https://www.youtube.com/watch?v=TbZFOtuHpxk) | 2026-03-16 | Underwater alien planet mission and giant crab; the *video title* additionally mentions a whirlpool |
| Holodeck #10 | [vlez2Dtu95E](https://youtu.be/vlez2Dtu95E) | **Unverified here** | **HOLD:** derivative directories contain a copied description, but the direct first-party YouTube result was not retrieved. No synopsis proposed. |

The publisher search-result video titles and the discovery directory titles are deliberately maintained as **separate source-relative observations**. For #9, the publisher video title mentions an underwater whirlpool, but its description paragraph does not; the paraphrase uses the described *giant crab*, not an unwitnessed whirlpool outcome. For #10, do not promote syndication into first-party metadata, or infer that a farmer/tribbles scene was audiovisually witnessed.

## Validation

```bash
python3 proposals/research/short/scouts-holodeck-06to09-descriptions-20261103/validate.py
python3 -O proposals/research/short/scouts-holodeck-06to09-descriptions-20261103/validate.py
python3 -m unittest discover -s tests -p test_scouts_holodeck_06to09_descriptions.py -v
python3 tools/validate.py
```

Required next step: independent human/model reading of the four official search-result Description fields, identification of material falsifiers and exact-head review. This proposal is **not** public synopsis admission or verified close-read coverage. Holodeck #10 requires its own first-party source observation or explicit independent evidence qualification before its NULL is replaced.
