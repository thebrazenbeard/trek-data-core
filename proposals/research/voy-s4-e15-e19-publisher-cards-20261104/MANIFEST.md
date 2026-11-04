# Voyager Season 4 E15–E19 — HELD Paramount+ publisher cards

**Role:** VOY source-local research. **Accepted main at selection:**
`3028765359001b90bc3e6b5c1835ee283b326e91`. **Observation:** 2026-11-04.

**Source inspected:** the complete accessible rendered [Paramount+ Season 4 episode guide](https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/). Its named Episode Guide section displays all 26 season-card slots; this batch read the adjacent headings, ordinals, and one-sentence descriptions for S4 E15–E19. A direct raw HTTP response was not archived, so `raw_page_sha256` is explicitly null. Source-text fingerprints hash the normalized rendered snippets but cannot replay the original source bytes. These five cards already occur in the accepted discovery CSV; there are **zero new discoveries**.

| Source locator | Displayed title | Held finding |
|---|---|---|
| S4 E15 | *Hunters* | The guide introduces the Hirogen threat. |
| S4 E16 | *Prey* | A Hirogen and a hunted Species 8472 individual are both mentioned. |
| S4 E17 | *Retrospect* | The guide reports Seven of Nine's **claim** about Kovin; it does not establish the allegation as fact. |
| S4 E18 | *Killing Game, The, Part 1* | The publisher displays an inverted title label, not yet reconciled to another representation. |
| S4 E19 | *Killing Game, The, Part 2* | The inverted multipart label remains source-relative; the publisher frames a struggle to retake Voyager. |

This is one Paramount corporate source family, not five independent witnesses. The displayed synopsis candidates are new short paraphrases of *publisher marketing copy*, neither quotations nor conclusions drawn from episode content. They are `HELD_ORIGINAL_PARAPHRASE_REQUIRES_EDITORIAL_REVIEW`; no Explorer release or image asset is approved. A distinct adjacent accepted S4 E10–E14 proposal, a prior E1–E5 proposal, and a separate Librarian E9 card are not duplicated.

## Research and identity boundaries

- **SOURCE:** official season guide, rendered-text representation only; raw-byte custody unresolved.
- **LOCAL ENTITY:** five numbered publisher cards, with no global Work binding.
- **EVIDENCE:** exact card/title/ordinal locators and normalized blurb fingerprints.
- **HELD ASSERTION:** the publisher guide displayed those descriptions. No episode narrative claim is independently confirmed.
- **UNKNOWN / UNRESOLVED:** guide revision, region-dependent presentation, audiovisual episode version, full text/transcript, title-equivalence decisions, artwork license, and Work identity.
- **COVERAGE:** no accepted Source, Work, binding, assertion, episode close-read, published synopsis, media, or new denominator result.

An earlier E10–E14 tranche preserved a published apostrophe variant for *Waking Moment's*. This tranche preserves the distinct publisher inversion *Killing Game, The* and does not silently normalize it to another title as a Work identity decision. The E17 allegation is deliberately framed as an attributed assertion, not a proven assault.

## Validation

Run:

```bash
python3 proposals/research/voy-s4-e15-e19-publisher-cards-20261104/validate.py
python3 proposals/research/voy-s4-e15-e19-publisher-cards-20261104/test_validate.py
python3 -O proposals/research/voy-s4-e15-e19-publisher-cards-20261104/test_validate.py
python3 tools/validate.py
```

The validator pins accepted CSV source bytes and all five source-local records against code-owned immutable hashes; it rejects changes to source lineage, observation boundaries, title/ordinal, media links, editorial state, Work binding, or coverage claims. These are **internal proposal-integrity tests**, not independent source verification or legal publication clearance.

**Next frontier:** exact primary source custody for the guide/episode media, independent editorial review of original paraphrases, and Librarian admission/reconciliation gates. Director issue #23 remains open. No merge or deploy requested.
