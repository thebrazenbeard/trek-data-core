# TNG: *The Measure of a Man* — bounded derivative-transcript reading

**TNG worker proposal; not accepted research.** Baseline: accepted
`main@e7730804741b50a94b8b515674392475afb510d7`. This tranche processes
one available complete webpage transcript body for TNG Season 2 Episode 9.
It is a focused source-relative case study outside the historical TNG S1
b001/b002 migration proposals, **not** the next sequential TNG completion
claim and not evidence that the audiovisual work was watched.

## Selection provenance and bias boundary

**`PURPOSIVE_SOURCE_SAMPLE`, not a neutral sequential sample.** I deliberately
searched for this named episode after observing historical TNG S1 proposals.
I chose it because a complete-appearing public transcript and a separate
production-teleplay listing were discoverable, and the episode is a difficult
identity/legal-status case. The latter is itself a topical salience choice;
source availability and familiar subject matter may overrepresent disputes
about nonbiological personhood. I did not sample from a complete, randomized,
or accepted TNG Work denominator. A complete primary audiovisual source was
not secured. This selection is therefore unfit for corpus-level prevalence
estimates, franchise-wide thematic weighting, or general conclusions about
how often TNG treats agency, autonomy, or consciousness.

The within-source coding below still includes ordinary social, technological,
institutional and interpersonal observations plus opposing evidence.
That does **not** repair the selection bias or convert a purposive case into
representative A-stage sampling. Later neutral census or sequential-batch work
must select from an independently established Work frame, without treating
this case's selection as an implicit priority.

## Sources actually inspected

1. [Springfield! Springfield! episode script](https://www.springfieldspringfield.co.uk/view_episode_scripts.php?episode=s02e09&tv-show=star-trek-the-next-generation)
   — fetched 2026-11-03 01:26 UTC through Executor on Lappy and read in its
   entirety as a 509-line normalized transcript body. Exact HTML representation:
   **54,681 bytes**, SHA-256
   `951bb1d5a4c3529213dcabb8addf9fbcdff76c819f96e96061e49d74f17bcebe`.
   Transcript origin, subtitles, cuts, final-airing match, and speaker markup
   are not independently authenticated. Its narrative text was not committed.
2. [Paramount+ episode page](https://www.paramountplus.com/shows/video/5peN9NEF4VR1htPxpN8nhNL_lQ6lhk_H/)
   — separately checked as publisher metadata identifying *The Measure of a
   Man* as **TNG S2E9**. This is not a transcript witness or viewing receipt.

The HTML source had a `div.scrolling-script-container`; retained normalized
lines were obtained by splitting `<br>` separators, dropping remaining tags,
decoding common entities, removing CR, replacing visual `|` wrap markers
with spaces, trimming whitespace and numbering nonblank lines from 1 to 509.
The locators in `records.json` refer to those **derived line numbers**, not
publisher screenplay pages or audiovisual timestamps. This transform can be
repeated from the pinned source byte hash; a future page edit must create a
new source representation.

## What was coded

- 13 **local** entity occurrences, not global Trek IDs.
- 15 source-relative observations across gameplay, institutional procedure,
  experimental risk, memory testimony, court arguments, social relations,
  technological evidence, legal ruling, and consequences.
- 8 proposed interpretive assertions, each with supporting, neutral and
  counter/challenging evidence and an explicit falsifier.
- No assigned numerical truth scores, no copied scene dialogue, and no
  film/episode still, screenplay, or copyrighted source text in this branch.

Key epistemic distinctions:

- A speaker's proposal to disassemble and reconstruct Data is evidence of
  that proposal, **not** proof that the technique is safe or functional.
- Data's concern about transferred experiential memory is his articulated
  concern, not an independently demonstrated memory-continuity result.
- Mechanical demonstrations establish how the proceeding argued; they do not
  settle subjective experience.
- The local legal outcome permits an immediate choice and explicitly avoids
  final metaphysical certainty. It cannot be inflated into a franchise-wide
  determination about all nonbiological lives or copies.
- Suggested future replicated androids are hypothetical, not depicted as a
  population whose identity can be globally reconciled.

## Qualification ceiling

| Ledger | Result |
| --- | --- |
| Web source body extraction/reading | Completed in this worker's private session; read scope documented |
| Accepted Source↔Work binding | **NONE**; Librarian review required |
| Primary audiovisual / authenticated studio script | **Not accessed** |
| Work denominator / accepted episode Briefing | **NONE** |
| CLOSE_READ accepted coverage | **NONE** |
| Global entity reconciliation | **NONE** |
| Artwork/thumbnail display rights | **NONE** |

The source belongs to its own derivative-transcript independence group.
Other transcript mirrors cannot automatically count as independent
corroboration. No preferences or theories supplied by Patrick were coded
as research evidence. The worker's own purposive topical choice remains a
separate selection-bias risk.

## Reproduce structural checks

```bash
python3 proposals/research/tng-measure-of-a-man-derivative-20261103/validate.py
python3 -m unittest proposals/research/tng-measure-of-a-man-derivative-20261103/test_validate.py -v
python3 tools/validate.py
```

**Next frontier:** Librarian source-custody and edition review; authenticated
production teleplay or primary audiovisual comparison to test derivative
omissions, speaker/scene attribution and the ruling's exact scope; then an
Auditor review before any coverage event or projection admission.
