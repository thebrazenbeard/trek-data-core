# TNG Season 2 B014–B015 — publisher episode cards E6–E22 (HELD)

**Role:** TNG. **Accepted baseline:** `main@3028765359001b90bc3e6b5c1835ee283b326e91`. **Date:** 2026-11-04 UTC.

**Source:** [Official Paramount+ TNG Season 2 guide](https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/2/), a single corporate-publisher source family. The full rendered guide, comprising all **22 episode cards**, was accessed and read again. **Seventeen existing source-local rows** were enriched in contiguous sub-batches B014 (E6–E10) and B015 (E11–E22). The first five cards are separately proposed in **draft PR #538**, not accepted as source or Work state. This proposal is accepted-main-based and does not depend on or duplicate that draft's five records.

| Existing local discovery ID | Publisher displayed card | Distinct source-relative synopsis focus |
| --- | --- | --- |
| `legacy:s2:tng:005` | *The Schizoid Man*, S2E6 | Publisher's attempted mind transfer into Data |
| `legacy:s2:tng:006` | *Unnatural Selection*, S2E7 | Publisher's rapid-aging disease premise |
| `legacy:s2:tng:007` | *A Matter of Honor*, S2E8 | Publisher's Riker/Klingon-ship loyalty conflict |
| `legacy:s2:tng:008` | *The Measure of a Man*, S2E9 | Publisher's refusal, disassembly proposal, courtroom framing |
| `legacy:s2:tng:009` | *The Dauphin*, S2E10 | Publisher's Wesley/ruler/potential-power premise |
| `legacy:s2:tng:010` | *Contagion*, S2E11 | Ship's electronic-virus threat |
| `legacy:s2:tng:011` | *The Royale*, S2E12 | An Air Force artifact and a fictional hotel |
| `legacy:s2:tng:012` | *Time Squared*, S2E13 | Picard's apparent future double |
| `legacy:s2:tng:013` | *The Icarus Factor*, S2E14 | Riker's father amid a command prospect |
| `legacy:s2:tng:014` | *Pen Pals*, S2E15 | Data and a threatened young alien |
| `legacy:s2:tng:015` | *Q-Who?*, S2E16 | Q sends the crew toward the Borg |
| `legacy:s2:tng:016` | *Samaritan Snare*, S2E17 | Picard's surgery and Geordi's captivity |
| `legacy:s2:tng:017` | *Up the Long Ladder*, S2E18 | A missing colony and clone civilization |
| `legacy:s2:tng:018` | *Manhunt*, S2E19 | Troi's mother's visit and Picard |
| `legacy:s2:tng:019` | *The Emissary*, S2E20 | Worf's previous partner as mediator |
| `legacy:s2:tng:020` | *Peak Performance*, S2E21 | A war-game overtaken by ambush |
| `legacy:s2:tng:021` | *Shades of Gray*, S2E22 | Riker's neurological infection |

The source card is located by exact guide URL, title and displayed S2E ordinal. Its SHA-256 fingerprint is of the **web-reader-rendered, trimmed UTF-8/NFC description**, not raw HTML or an authenticated studio/source-edition digest. The publisher source was accessible in the web reader, but an independent direct Lappy HTTP request for the guide returned HTTP 406 in this session; raw webpage bytes were not archived or republished. No copyrighted descriptions, transcripts, images or episode stills are included. All seventeen one-sentence synopsis drafts are original, held descriptions of the publisher's promotional account.

## Source and continuity caveats

- E9 overlaps accepted-main **TNG *The Measure of a Man*** derivative-transcript research. Its original Springfield text extraction is a distinct, unauthenticated derivative source, deliberately selected as a topical case study. Its manifest is byte-pinned here solely to preserve the known overlap. This does **not** establish independent corroboration of an episode's events or authenticated footage; the candidate Work link remains unresolved.
- The two source-relative references in the E9 publisher text establish that the publisher says Data refuses disassembly and Picard is asked to defend rights; the records do not promote legal status or fictional truth beyond that short description.
- An unnamed scientist in E6, young ruler in E10, young alien in E15, and Worf's former partner in E20 are not globally identified from familiar episode lore. Literal mention lists follow names available in the publisher descriptions.
- The S2E13 description of Picard's apparent future double and S2E12 description of a fictional hotel are **promotional statements**; no alternate-timeline, causal, memory or nested-fiction ontology is settled here.
- The current Paramount episode-guide ordinal is a streaming-listing observation. Broadcast, syndicated, restored or production edition equivalence remains open.
- Personal preference was not a selection criterion. These are the next contiguous seventeen cards after E1–E5, and no theme-based sampling weight is inferred.

**Admission/coverage:** No new Source↔Work binding, new global Work, audiovisual or script read in this batch, public synopsis clearance, image license, canonical assertion, coverage event or denominator change. Every record remains `HELD_SOURCE_LOCAL_PUBLISHER_METADATA`; issue #23's primary-source close-read hold still applies.

> **Hostile challenge:** Two title-matching source surfaces, one publisher synopsis and one unauthenticated script mirror, do not prove they represent the same exact cut. A matching title and ordinal are metadata, not an approved reconciliation or a close-read receipt.

## Deterministic validation

```bash
python3 proposals/research/tng-s2-remaining17-publisher-20261104/validate.py --check
python3 -m unittest discover -s proposals/research/tng-s2-remaining17-publisher-20261104 -p 'test_*.py'
python3 tools/validate.py
```

The validator pins accepted-main discovery/CSV/source-bundle bytes and the earlier *Measure of a Man* derivative manifest SHA-256. It rejects title, ordinal, source-local ID, publisher-description fingerprint, mentions, original paraphrase, derivative-overlap relationship and admission/custody/coverage drift. With pending draft PR #538 and this draft, all 22 **Season 2 publisher listing cards** have proposed source-local paraphrases, but **zero** are thereby admitted as an authenticated episode read. The next independent publisher metadata frontier is TNG **Season 3**, unless an audited episode/script source-custody lead is available first. Actual episode/script close reading requires independent source custody and review before any governed coverage claim.
