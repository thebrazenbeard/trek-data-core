# LIT — *Emissary* private TXT deep read (proposed)

**Lane:** LIT only. **Batch:** `LIT-DS9-EMISSARY-TXT-20261103`. **Status:** draft research proposal; no accepted registry, reconciliation, database, media, or coverage mutation. **Base accepted head:** `69f0a5c46e78b9d034ff168d969374892fc997e0`, 2026-11-03.

## Direct source and provenance

- First-hand input was the exact owner-held, private TXT member already fingerprinted as `txt-local:0001` under accepted Librarian receipt `proposals/librarian/private-ds9-txt50-20261103/observations.json`.
- Opened the ZIP entry **in memory**, without extracting or publishing book text. SHA-256 of the uncompressed member matches the accepted receipt: `fb80998ce09f42b096d97cbffda446eb68f1b022d6c8f344d665bc1cf54f5f3e` (363,543 bytes). Archive hash: `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac`.
- UTF-8 decoding produced no U+FFFD replacement characters. The text has **12 sequential `Chapter N` headings, 2,092 nonempty lines, approximately 63,192 regex word matches**, an opening scene and a concluding scene. All 12 chapters were read in sequence privately. The local record is a prose narrative with multiple third-person focalizations, **not an episode screenplay transcript**.
- The [official publisher product page](https://www.simonandschuster.com/books/Emissary/J-M-Dillard/Star-Trek-Deep-Space-Nine/9780743412209) lists *Emissary* by J.M. Dillard as *Star Trek: Deep Space Nine* book #1, eBook ISBN 9780743412209. **Inference:** source content and title strongly fit a prose novelization/adaptation candidate. A matching publisher page **does not** prove this owner-held TXT is that exact edition, an unmodified edition, or complete.
- Full source bytes, exact private ZIP member path, substantive quotations, and artwork are **not** included here. No copyright claim or republication permission is inferred.

## Chapter-level original structural reading

| Chapter | Neutral content synopsis from private text |
|---|---|
| 1 | Wolf 359 loss is narrated through Sisko's command duties, rescue attempt, and desperate separation from his family. |
| 2 | Sisko and Jake arrive at the damaged station; the narrative develops O'Brien's welcome, Kira's political objections, and the uncertain significance of a religious encounter. |
| 3 | A juvenile theft and Quark's impending departure become a negotiation; Sisko and Picard confront conflicting memories of the Borg, with Picard's private reaction rendered in prose. |
| 4 | Sisko secures Quark's continued presence; Kira balances skepticism with spiritual expectation; Opaka gives Sisko an orb, whose experience is framed by the memory of meeting Jennifer. |
| 5 | The O'Brien family changes home; Jake privately resents the transfer; O'Brien relives Setlik, then Dax and Bashir arrive and confront personal and intercultural assumptions. |
| 6 | An orb encounter evokes a joining memory for Dax; external data and Dukat's presence redirect inquiry toward the Denorios Belt. Jake and Nog form an uneasy rapport. |
| 7 | A diversionary operation permits the runabout's launch. A passage leads to a distant starfield and to a site perceived differently by the two investigators. |
| 8 | Dax reappears while Sisko communicates with interlocutors in familiar guises; the station crew considers moving the installation to the newly observed passage. |
| 9 | The encounter examines sequential time through memory and loss while the station undertakes a risky relocation and Dukat enters the passage. |
| 10 | The station confronts Cardassian coercion. Sisko comes to recognize that his experiential return to a specific traumatic moment has persisted beyond the event itself. |
| 11 | Under attack, several characters act across initial hostility: Jake and Nog rescue an adult, Odo and Bashir tend the wounded, Kira and O'Brien defend the station. Sisko returns, negotiates and revisits his interaction with Picard. |
| 12 | The O'Brien family decides how to live on the station; Sisko returns the orb to Opaka, who declines a direct account of the entities and renews her expectation of his continued journey. |

## Local evidence and interpretive limits

`records.json` uses **13 local occurrences**, **15 source-relative observations**, **6 explicitly interpretive assertions**, and **5 unresolved questions**. Locators are `chapter` plus the **zero-based index of nonempty text lines within the chapter**, matching `CHAPTER_INDEX.json`. The chapter heading itself counts as line 0. Since the TXT is a conversion with no trusted page or publisher paragraph IDs, these are **conversion-local locators**, not print-edition citations.

Evidence kinds separate narrated events, dialogue, memory, altered experience, and subjective perception. For example, the wormhole encounter uses faces and places familiar to Sisko; the presented forms are **not silently reconciled** to living people. Dax's joined self-description and the memoir-like Setlik flashback are **this prose source's** claims, not an automatic update to audiovisual or global Trek canon.

### Corrective semantic review — counterevidence

Independent hostile review of the first draft found five invalid `counterweight` references: `as-02 → ev-14`, `as-03 → ev-12`, `as-04 → ev-12`, `as-05 → ev-08`, `as-06 → ev-02`. These observations concern different people, frames, or claims; they **do not disconfirm** the associated interpretation merely because they appear elsewhere in the same book. I also removed `as-01 → ev-12/ev-14`: subsequent cooperation or reframing does not logically disconfirm the interpretation that grief was experienced as arrested time. Their use as counterweights was a methodological error, not additional source evidence.

All six assertions now explicitly record `counterweight: []` and `counterevidence_status: UNKNOWN`. An empty list means **no genuinely relevant counterevidence is indexed in this batch**, **not** that none exists in the book or wider corpus, and **not** that an exhaustive counterevidence search passed. The supporting observations and their source-relative locators remain unchanged. Validator and adversarial tests reject any unsupported counterweight (even a valid-but-irrelevant evidence ID) or a fabricated certainty such as `NONE_FOUND`. New disconfirming or neutral evidence requires a fresh source-relative observation, explicit relation/rationale, and independent semantic review before being represented as a counterweight.

> **Hostile challenge — edition:** An internally complete-looking 12-chapter TXT could omit publisher front matter, undergo fan editing, contain transcription errors, or differ from the published J.M. Dillard novelization. The matching title, plot, and publisher description are inadequate to establish edition identity or exact completeness. Require independent title/copyright-page evidence or edition-to-edition collation before admitting `SOURCE_BOUND` at the Work level.

> **Hostile challenge — cross-continuity:** Prose additions to interiority and remembered events may conflict with screen narratives or later lore. No identity assertion should be promoted until a separate cross-work analysis finds supporting **and disconfirming** evidence with genuinely independent source lineage.

> **Hostile challenge — semantic classification:** A narrated vision cannot by itself prove time travel, and a figure taking a person's form is not that person. The original research records preserve the encounter's narrative frame rather than manufacturing an objective history.

**Completion claim:** Full read of the **private hash-verified TXT artifact** and local structured/semantic analysis are performed for this single candidate, but the accepted *Work's* `CLOSE_READ` / `SEMANTICALLY_ANALYZED` counters remain unchanged pending Librarian edition binding, audit and acceptance. `accepted_source_binding_effect=NONE`, `accepted_work_effect=NONE`, `coverage_effect=NONE`.

**Validation:** run `python proposals/research/lit/ds9-emissary-private-20261103/validate.py` and `python -m unittest discover -s proposals/research/lit/ds9-emissary-private-20261103 -p 'test_*.py'`. These checks validate public metadata invariants and accepted-Librarian source SHA; they do **not** reread the private book in GitHub CI.
