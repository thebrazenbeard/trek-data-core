# TOS script archives: five episode-level source locators

**Disposition:** archival catalog metadata only; `PROPOSAL_ONLY`, **no source text read**, no source-to-Work admission, no episode evidence or assertions, and no research coverage event. Accepted baseline: `5127598af7e7c9a1148b11bb15863643f2914dfc`.

This TOS research-frontier batch crosswalks five already catalogued Paramount+ *Season 1* heading observations with a separate institutional library catalog of physical Star Trek production scripts. The five candidates come from the accepted [Librarian lead-selection artifact](../../librarian/lead-qualification-tos-s1-20261103/selection.json). This is not a new series denominator and the matched strings are **candidate**, not reconciled, Work identities.

| Episode title (candidate) | Paramount+ S1 heading ordinal | Lilly script-list no. | Lilly catalog writer credit |
| --- | ---: | ---: | --- |
| The Man Trap | 2 | 1 | George Clayton Johnson |
| The Corbomite Maneuver | 11 | 10 | Jerry Sohl |
| The Devil in the Dark | 26 | 25 | Gene L. Coon |
| The Conscience of the King | 14 | 13 | Barry Trivers |
| The Naked Time | 5 | 4 | John D. F. Black |

## Source custody and precise locators

1. **Indiana University Bloomington Lilly Library**, [*Star trek : scripts, 1966–1969*](https://iucat.iu.edu/lilly/19297540), call no. `PN6120.S48 S795`. Its catalog *Contents* section lists all five title strings, the script-entry numbers above, and the writer credits; its *Notes* discuss drafts and revisions. The collection covers both final/revised scripts and *The Cage*, and says that some numbering does not follow broadcast order. Its holding is **by appointment**; copying requires copyright-holder permission. **Observed** via public catalog page on 2026-11-03. Source bytes were not independently archived; no archive-script page was requested, photographed or read.
2. **University of Kansas Spencer Research Library**, [Barbara Bohm's scripts, MS 374](https://archives.lib.ku.edu/repositories/3/resources/5928). The finding aid describes TOS season 1–2 scripts plus a TAS script. It reports no general access restrictions but permits staff to restrict use due to physical condition. **Collection-level lead only:** individual episode entries were not observed here.
3. **CSU Fullerton**, [Willis McNelly collection](https://libraryguides.fullerton.edu/visiting/sciencefiction). The institutional guide reports draft scripts for 78 of 79 produced episodes, alongside a pitch and writer's guide. **Collection-level lead only:** no case for any of these five exact script variants is established by the guide.
4. **Writers Guild Foundation**, [60 Years of Star Trek library holdings](https://www.wgfoundation.org/blog/2026/9/1/read-it-in-the-wgf-library-60-years-of-star-trek). Its library describes almost every TOS script plus early production guides. **Collection-level lead only:** not an index of individual draft versions or permission to publish them.

These four institutions describe distinct collection custody, **not four independent readings** or corroborations of episode events. The Paramount+ guide and physical script catalog use differing numbering schemes and must not be collapsed. Distinct drafts may vary from the broadcast cut. Title concordance licenses a *retrieval candidate*, not script↔broadcast content equivalence.

## Reproducibility and boundaries

`observations.json` preserves all source-local ordinals, catalog credits, original URLs and unresolved identities. It deliberately has no assertion/evidence records because the research worker did not access a complete primary script or broadcast source. The institutional catalog itself was read, not the catalogued underlying script.

```bash
python3 -m unittest discover -s tests -p 'test_tos_script_archive_locators.py' -v
python3 tools/validate.py
```

Next research gate: use the Lilly call number to obtain lawful access to a named physical script draft, retain a source/edition hash and page locators outside the public repo, and then read it in full. A separate audiovisual source is needed to test script-to-screen deviations. No copyrighted script content or image is committed.
