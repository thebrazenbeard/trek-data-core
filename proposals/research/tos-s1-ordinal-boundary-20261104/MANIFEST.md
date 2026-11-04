# TOS Season 1 source-local ordinal boundary — HELD metadata check

**Role:** TOS. **Base accepted main:** `3028765359001b90bc3e6b5c1835ee283b326e91`.
**Status:** proposal only, held under Director [issue #23](https://github.com/thebrazenbeard/trek-data-core/issues/23).
**Batch type:** public publisher metadata consistency audit, **not** episode close-read, screenplay research, Source↔Work admission, synopsis approval, coverage, reconciliation, or publication.

## New direct publisher observation

On 2026-11-04 I read the complete **publicly rendered episode guide text** at the publisher's [Paramount+ TOS Season 1 guide](https://www.paramountplus.com/shows/star_trek/episodes/1/). The five consecutive guide-card headings and ordinal fields observed were:

| Publisher-local slot | Publisher heading |
| --- | --- |
| S1E1 | *The Cage* |
| S1E2 | *The Man Trap* |
| S1E3 | *Charlie "X"* |
| S1E4 | *Where No Man Has Gone Before* |
| S1E5 | *The Naked Time* |

`RECEIPT.json` gives exact heading/slot locators. The guide's original episode-description text was read but **not** copied to this repository; zero new synopses were produced because existing held proposal [#273](https://github.com/thebrazenbeard/trek-data-core/pull/273) already covers guide-card synopsis drafts. **No raw publisher HTML bytes were retained**, no response SHA-256 is claimed, no copyright clearance or audiovisual viewing was performed, and the live rendered page can change. The source URL is one corporate publisher witness, not a new independent corroborator of the older Paramount+ receipt.

## Exact accepted-main comparison and protected differences

The validator checks four frozen accepted-main blobs (full Git blob SHA-1 verified, not new web source hashes):

| Accepted-main candidate artifact | Git blob SHA-1 | Comparison |
| --- | --- | --- |
| `proposals/discovery/legacy-paramount-season1-20261102/tos.csv` | `bb87f91381098420986b94097072a30ef0e5074b` | Fresh five slots match accepted **publisher** discovery rows. |
| `proposals/discovery/tos-publisher-s01-b001-20261102/paramountplus.json` | `9743f66a30520aa5007865c6ade3e163702161e5` | Exact same five source-local titles and ordinals. |
| `proposals/discovery/tos-publisher-s01-b001-20261102/plutotv.json` | `faccc37c28e2d9784c57f98c56891e23e07bf08a` | Pluto's own S1E1–E5 omit the publisher's *Cage* slot and align by title to Paramount+ S1E2–E6. **No global episode-ordinal conversion inferred.** Both count as corporate `publisher:paramount`, not two independent corroborators. |
| `proposals/research/tos-charlie-x-derivative-close-read-20261103/MANIFEST.json` | `f195efb96f1b704ab991d16980eec7f46dbb9458` | Derivative *Charlie X* image-caption ordinal **Season 1 episode 2** differs from official Paramount+ publisher S1E3. Retain both source-specific labels; this third-party derivative is not authenticated primary. |

The check fails closed on slot/title mutation, punctuation simplification, false independent publisher claim, primary-source upgrade, silent derivative-ordinal collapse, Source↔Work assignment, coverage promotion, missing guide-card receipt, or changed accepted input blobs. **Two difference classes preserved:** Paramount+ vs Pluto pilot-inclusive publisher indexing; Paramount+ vs TVMEG source-local *Charlie X* numbering. None proves a canonical Work mapping.

## Reproduce on a repository checkout

```bash
python3 proposals/research/tos-s1-ordinal-boundary-20261104/validate.py
python3 -m unittest discover -s proposals/research/tos-s1-ordinal-boundary-20261104 -p 'test_*.py' -v
python3 tools/validate.py
```

An independent source recheck, Librarian rights-valid complete representation and source binding, Auditor review, and explicit research admission are still required by #23. This packet has **zero** admitted Briefings, coverage events, Source↔Work bindings, approved synopses, identity decisions or Explorer effects. Existing proposals [#488](https://github.com/thebrazenbeard/trek-data-core/pull/488) and [#493](https://github.com/thebrazenbeard/trek-data-core/pull/493) cover overlapping source-card/QID checks; this packet instead pins the cross-roster discrepancy invariant.
