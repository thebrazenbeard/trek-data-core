# Star Trek autobiographies: publisher/distributor source inventory

Role: **LIBRARIAN**, candidate-only source and edition inventory, 2026-11-03.

The official Penguin Random House [Star Trek Autobiographies series](https://www.penguinrandomhouse.com/series/0PT/star-trek-autobiographies-series/) page identifies **five titles** (raw HTTP body: 183,841 bytes, SHA-256 `bd1e729a07c7a1714c0bde2a9da384f97259c87a928d899c1c43d7637a2a31fd`). Five individual product pages were also **actually fetched as full HTML bodies**, read via their embedded `schema.org` JSON-LD `Book` metadata, and hashed as raw downloaded bytes. The printed `mainEntity` fields were checked against the series listing. PRH distributes the editions published by Titan Books; these pages form **one publisher/distributor independence group**, not seven independent witnesses.

| Source-relative Work candidate | Edition ISBN | Full source bytes | Full raw HTML SHA-256 |
| --- | --- | ---: | --- |
| [James T. Kirk](https://www.penguinrandomhouse.com/books/250795/the-autobiography-of-james-t-kirk-by-david-a-goodman/) | 9781783297481 | 257,913 | `5acfa401c5ee942e185c308ded5ff264972b7a013852961aad8b2757083684af` |
| [Jean-Luc Picard](https://www.penguinrandomhouse.com/books/555327/the-autobiography-of-jean-luc-picard-by-david-a-goodman/) | 9781785659409 | 230,973 | `119eddb5ca3d8d1b76bdd9d0b411f5d16e3a470b62507796e053301c37c51b26` |
| [Kathryn Janeway](https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/) | 9781789095333 | 262,319 | `fa8dbce6950678405dfe4615a0e26782406af0b73acf0ad7409aaed991ac49ca` |
| [Mr. Spock](https://www.penguinrandomhouse.com/books/577045/the-autobiography-of-mr-spock-by-una-mccormack/) | 9781785659416 | 258,759 | `1c54fd926d0641d98fb41d827e9c999bb56e24fd11fae97ee4d304f4fbca8510` |
| [Benjamin Sisko](https://www.penguinrandomhouse.com/books/737400/the-autobiography-of-benjamin-sisko-by-derek-tyler-attico/) | 9781803366258 | 261,970 | `9fe73b190eec8fe1bb3209d1d58c2c4dadd404b336ece66e6dfab22bb43e9d42` |

The publisher separately sells [*Star Trek Captains — The Autobiographies*](https://www.penguinrandomhouse.com/books/715915/star-trek-captains---the-autobiographies-by-una-mccormack-david-a-goodman/) as boxed set ISBN 9781803362168 (raw HTTP body 215,042 bytes, SHA-256 `77e22a9bdf9c290bc9b7d1e6e21aa734321fc3bcbedbfd13030ab64d51086f36`). It contains Kirk/Picard/Janeway editions and is **not** counted as a sixth original literary Work. The five individual memoirs are *fictional in-universe autobiographies*, not historical nonfiction and not evidence of canonical character biography.

## Evidence and rights boundary

- Direct full HTML captures were downloaded on the authorized owner host into its temporary directory; they are **not committed** and temp files may be removed by the host. Checksums describe the observed bytes on 2026-11-03, not a promised immutable URL version. A future source refresh must re-fetch and compare raw bytes before claiming byte-identical reproduction.
- `bundle.json` contains only source-relative bibliographic JSON-LD observations and full-body hash/length receipts. `records.json` is deterministic output from `tools/build_prh_autobiography_candidates.py`; it creates five proposed Work IDs, five edition candidates, five proposed metadata-only Source bindings, and a non-Work boxed-set relationship.
- Publisher image URLs in the proposal are **locators only**. No artwork binary or license has been acquired or published; cover-image use remains unresolved. No book text, scans, or large quotes are published.
- Coverage, canonical Work admission, binding admission, full-text available, close-read, semantic analysis, and the Briefings counter all remain **unchanged** (`NONE`). Four different editions of the existing *Ring of Fire* observation still represent **one** separate proposed literary Work.
- This five-title tranche is intentionally bounded and not exhaustive. PRH's series listing count of five is a denominator for **that particular series page only**, not for Star Trek literature. Simon & Schuster's search listing shows over a thousand **product results** including non-prose, formats, and duplicates; it cannot be treated as the number of distinct literary Works.

Rebuild: `python3 tools/build_prh_autobiography_candidates.py --check` and `python3 tools/build_unified_discovery.py --check`; test the adversarial file/identity/ISBN/rights gates before any accepted integration.
