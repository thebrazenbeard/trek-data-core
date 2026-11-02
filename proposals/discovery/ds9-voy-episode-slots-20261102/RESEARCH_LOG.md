# DS9 / Voyager publisher episode-slot discovery — 2026-11-02

Status: PROPOSED — pending independent admission review; no accepted Work, source binding, episode count, or denominator effects.

## Frozen research plan (before source collection)

Question: Can current first-party publisher episode guides supply bounded, source-attributed *Deep Space Nine* and *Voyager* episode-title and season-slot discovery proposals without conflating platform numbering with canonical Work identity?

- H1: At least one accessible primary publisher streaming listing identifies five ordered, titled S1 installment slots per series. Falsifier: the official listings cannot be accessed or do not expose five titles and local ordinals.
- H2: The existing `normalize_episode_roster.py` and `validate_publisher_episode_roster.py` can encode both source-local mini-batches with zero admission effects. Falsifier: either batch fails the canonical validation or requires a change to canonical registries.
- H3: The official guides establish a single canonical total for every installment. Falsifier: differences between platform presentations, specials, or metadata unit definitions. H3 is expected to remain unsupported; do not derive an episode denominator.

Methods:

- C1 confirmatory: Search/retrieve Paramount+ or other first-party official season guides for *Deep Space Nine* and *Voyager*; record precise URLs, observed titles, source-specific ordinal labels and timestamp. Do not copy scripts, synopses, media, or extensive descriptions.
- C2 confirmatory: Feed bounded two-series CSV observations to existing offline normalizer and validator; record hashes, commands, outputs and negative assertions.
- E1 exploratory: Compare official show/season presentation conventions, and record any source-specific caveats or unresolved completeness issues.

Stop conditions: Two five-slot candidates pass local validation OR official sources are inaccessible; report other sources as research paths, not accepted metadata. Preserve contradictions and do not promote a source-specific slot into a canonical identity. A research verdict requires separate reviewer; do not self-declare independently confirmed.

## Evidence log

Evidence IDs below refer to the public web-reader views inspected on 2026-11-02.
The source pages were NOT downloaded as fixed raw bytes; these locators and
brief observations are consequently **not cryptographically authenticated
publisher snapshots**. Linked page text may subsequently change.

| ID | Source | Observation and decisive source-local facts |
| --- | --- | --- |
| E-DS9-1 | [Paramount+ DS9 S1 episode guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/1/) | Publisher display has *The Emissary, Parts I and II* at S1E1, *Past Prologue* at S1E3, followed by E4 *A Man Alone*, E5 *Babel*, E6 *Captive Pursuit*. No E2 standalone card appears in this view. |
| E-VOY-1 | [Paramount+ Voyager S1 episode guide](https://www.paramountplus.com/shows/star_trek_voyager/episodes/1/) | Publisher display has combined *Caretaker, Part 1 & 2* at S1E1, then *Parallax* at E3, *Time And Again* E4, *Phage* E5, *The Cloud* E6. No E2 standalone card appears in this view. |
| E-TAS-1 | [Paramount+ The Animated Series S1 guide](https://www.paramountplus.com/shows/star_trek_animated/episodes/1/) | The first five displayed local slots are E1 *Beyond the Farthest Star*, E2 *Yesteryear*, E3 *One of Our Planets is Missing*, E4 *The Lorelei Signal*, E5 *More Tribbles, More Troubles*. |
| E-DS9-2 | [StarTrek.com DS9 series landing](https://www.startrek.com/series/deep-space-nine) | Publisher-level presentation says seven seasons and 176 episodes, but is not itself a numbered episode-by-episode roster. |
| E-VOY-2 | [StarTrek.com Voyager series landing](https://www.startrek.com/series/star-trek-voyager) | Publisher-level presentation says seven seasons and 172 episodes, not independently verified canonical Work units. |
| E-TAS-2 | [StarTrek.com TAS series landing](https://www.startrek.com/series/star-trek-the-animated-series) | Publisher-level presentation says two seasons and 22 episodes. |
| E-SHORT-1 | [Paramount+ Short Treks program](https://www.paramountplus.com/shows/star-trek-short-treks/) | Separately published *Star Trek: Short Treks* anthology is not one of the 12 series on the franchise landing-page directory. It needs its own proposed Work/container identity rather than being silently folded into *Discovery*. |
| E-VERYSHORT-1 | [Official Animated Celebration](https://www.startrek.com/animated-celebration) | Publisher explicitly describes **five very Short Treks** shorts. This distinct format is also missing from the 12-series directory and requires governed category assignment. |
| E-TOS-EXISTING | [`official-tos-roster-scope-20261102` existing repository proposal](../official-tos-roster-scope-20261102/RESEARCH_RECORD.md) | A separate preexisting proposal already records incompatible Paramount+/Pluto TOS S1 numbering, including *The Cage* treatment. This batch does not duplicate or overrule that comparison. |

## Execution record

- C1 confirmatory retrieval: **met** for DS9, Voyager. Five publisher-labeled slots per series were exposed in web-reader snapshots at E-DS9-1 / E-VOY-1. No original audiovisual episode, script, or caption was inspected.
- E1 exploratory expansion: **animated metadata source also available**, E-TAS-1. Added third bounded 5-slot candidate for a non-live-action series; this was not part of frozen C1 and is classified exploratory.
- E1 exploratory shorts: **separate program identity gap**, E-SHORT-1 and E-VERYSHORT-1; no attempt to force these sources into the 12-Mission catalog.
- C2 confirmatory local run: `python3 tools/normalize_episode_roster.py --csv proposals/discovery/ds9-voy-episode-slots-20261102/<series>-observed-slots.csv --receipt proposals/discovery/ds9-voy-episode-slots-20261102/<series>-observation.json --output proposals/discovery/ds9-voy-episode-slots-20261102/<series>/bundle.json`, once for each of `ds9`, `voy`, `tas`. Exit **0** in all three, output `ROSTER_NORMALIZATION_CANDIDATE`, exactly **5 slots** and `accepted_effect: NONE` each. Input SHA-256 values are present in receipts and covered by offline tests. Existing tools already enforce no canonical-Work and no accepted coverage effects.

## Interpretation and independent-review gate

H1: supported by public publisher presentation for DS9 and Voyager, subject to mutable web-reader snapshot limits.
H2: passed local validator/normalizer tests; proves internal candidate-shape consistency, not publisher authenticity.
H3: **rejected as an inference from these pages.** The combined two-part premiere is one displayed item spanning two ordinal positions, and StarTrek.com series totals do not resolve the counting unit. No global denominator claim is justified.

**Independent evidence review remains pending.** These 15 rows are proposed
publisher display positions, not 15 independently verified distinct narrative
Works, not accepted Briefings, and not analysis of Star Trek scenes.
