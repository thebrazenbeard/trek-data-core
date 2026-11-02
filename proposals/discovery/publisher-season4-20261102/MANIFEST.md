# Paramount+ Season 4 publisher page observations — candidate metadata

**Observed:** 2026-11-02. **State:** `DISCOVERY_ONLY`, not admitted evidence.
**Audience:** Librarian source/Work inventory; Consolidator-only directory projection.

The source-first processing of six official Paramount+ Season 4 guide pages
yielded **122 source-local episode-listing observations**. These are listing
cards, **not 122 independently verified, watched, read, researched or distinct
episodes**. Raw publisher HTML was captured by HTTPS and parsed offline; its
source-response SHA-256 and byte length, the exact normalized CSV SHA-256, and
listed-card count are recorded in [`index.json`](index.json). Raw copyrighted
page content is kept outside the public repository. The offline importer
rejects missing, duplicated, or unexpected HTML canonical URLs, including
duplicate `rel`/`href` attributes. This is a page-binding check, not a
cryptographic attestation of the publisher's identity.

| Series | Official publisher guide | Observed cards | Ordinal notes |
| --- | --- | ---: | --- |
| The Next Generation | https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/4/ | 26 | S4E1–S4E26 |
| Deep Space Nine | https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/4/ | 25 | S4E1, S4E3–S4E26; the missing E2 is not invented |
| Voyager | https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/ | 26 | S4E1–S4E26 |
| Enterprise | https://www.paramountplus.com/shows/enterprise/episodes/4/ | 22 | S4E1–S4E22 |
| Discovery | https://www.paramountplus.com/shows/star-trek-discovery/episodes/4/ | 13 | S4E1–S4E13 |
| Lower Decks | https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/4/ | 10 | S4E1–S4E10 |

The six URLs share a common Paramount/CBS provenance family. They are **not six
independent corroborations**. A local SHA-256 proves consistency with the
retained capture, **not publisher authentication or stable future availability**.
No full program audiovisual source was inspected, no text transcription was
read or published, no canonical Work identity was inferred, and no candidate
promoted to a Briefing. `accepted_work_effect`, `accepted_source_binding_effect`,
`coverage_effect`, and `denominator_effect` all remain `NONE`.

Reproduce committed candidate consistency:

```sh
python3 tools/build_publisher_s4_discovery.py --check
python3 -m unittest tests.test_publisher_s4_discovery -v
python3 tools/validate.py
```

For a fresh source capture, fetch the publisher HTML privately as
`<mission>-s4.html` for mission abbreviations `tng`, `ds9`, `voy`, `ent`, `dis`,
`ld`, compare the HTTPS response origin and page snapshot explicitly, then run:

```sh
python3 tools/build_publisher_s4_discovery.py --ingest-dir /path/to/private/html
```

This step regenerates the CSVs, source receipt index, and candidate bundles,
and should be audited against the exact raw responses before proposing an
updated receipt. Do not put raw HTML into Git. The validator does **not** make
multi-file updates transactionally atomic if ingestion is interrupted; rerun
`--check` and inspect the Git diff before publishing any proposal.

**Next frontier:** Librarian source-binding and edition/duplicate analysis;
Consolidator exact-main integration into *source-local* Universe Directory;
independent hostile replay of retained source captures. Neither step alone
advances `CLOSE_READ`, accepted Briefings, or the global denominator.
