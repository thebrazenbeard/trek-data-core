# Three publisher-edition and description observations — LIT

**State:** PROPOSAL_ONLY / source-local HELD; **role:** LIT; **observed:** 2026-11-03 UTC.

**Accepted `main` baseline:** `f4ea65391cf1543a55bf19dfcf3ed776dd80ab04`.

I opened and read the **official publisher product details and About the Book descriptions** for three exact editions. These are three **edition-page observations**, three **original publisher-description paraphrases**, and one dependent publisher lineage—not three full books read, three new admitted Works, independent corroboration, or accepted canonical plot events.

| Publisher-page candidate | Exact edition page read | Edition claim on page | Evidence boundary |
|---|---|---|---|
| *The Antares Maelstrom* — Greg Cox | [ISBN 9781982113209](https://www.simonandschuster.com/books/The-Antares-Maelstrom/Greg-Cox/Star-Trek-The-Original-Series/9781982113209) | Trade paperback, Pocket Books/Star Trek, August 13, 2019, 368 pages | Publisher describes Kirk, Baldur-3, resource prospectors, and the Antares Maelstrom; not a direct novel close-read |
| *The Unsettling Stars* — Alan Dean Foster | [ISBN 9781982140601](https://www.simonandschuster.com/books/The-Unsettling-Stars/Alan-Dean-Foster/Star-Trek/9781982140601) | Trade paperback, Pocket Books/Star Trek, April 14, 2020, 304 pages | Publisher **claims** a Kelvin alternate-timeline setting involving Kirk and Perenorean refugees; timeline identity remains unreconciled |
| *Star Trek: The Original Series: Devil's Bargain* — Tony Daniel | [ISBN 9781476700472](https://www.simonandschuster.com/books/Star-Trek-The-Original-Series-Devils-Bargain/Tony-Daniel/Star-Trek-The-Original-Series/9781476700472) | Mass-market paperback, Pocket Books/Star Trek, February 26, 2013, 320 pages | Publisher describes Kirk and Spock handling a resisted evacuation at Vesbius; a page excerpt exists but no complete novel was read |

The three publisher descriptions were **actually read** and newly paraphrased in `observations.json` without including the publisher's text. The evidence and typed assertions are **source-relative**: they establish the publisher's description, not the described fictional events as independently verified world-state. Other retailer formats linked on the pages were not independently verified and must not be counted as editions in this batch.

## Collision, custody, and coverage controls

- Before drafting, I searched accepted `proposals`, `explorer`, and `registry` for all three titles and these edition identifiers; no accepted matches were found at the pinned head. Open literary draft PRs #212, #216, #222, #330, and #378 have distinct stated scopes; final reconciliation still requires exact-head collision recheck.
- `observations.json` records three local entities, two source-relative evidence records per entity (product details and publisher description), and one typed publisher-claim assertion per entity. No global Work identity is resolved.
- No complete book source bytes, authenticated raw publisher HTML, artwork bytes, or copyrighted long passages were committed. A publisher page's presence of a cover-image link is **not** a license to display it.
- Accepted SOURCE↔WORK binding, FULL_TEXT_AVAILABLE, STRUCTURALLY_INDEXED, CLOSE_READ, SEMANTICALLY_ANALYZED, ENTITY_LINKED, CROSS_REFERENCED, and AUDITED coverage: **unchanged / not claimed**. Public Explorer: **unchanged**.
- The private archive's edition/text equivalence is `UNRESOLVED`; no OPF/ebook custody is claimed.
- Machine validation pins the observations SHA-256, ISBN check digits, publisher URL paths, known bibliographic fields, lineage, description anchors, evidence/claim links, unreviewed-property rejection, and no-public-effect invariants.

## Exact batch boundary

`observations.json` SHA-256: `54872dfb1e9fd1040e52dc4ef644a267ab3a13f5c45fe1d253331b451ec89159`.

Run `python proposals/research/lit-sns-antares-unsettling-devils-20261103/validate.py` and `python -m unittest tests.test_lit_sns_antares_unsettling_devils`.

**Next:** Independent publisher-page and collision audit; Librarian source-binding consideration; only then may the Consolidator decide whether to expose explicitly held edition candidates in a deterministic Explorer projection. No automatic promotion.
