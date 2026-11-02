# Paramount+ Season 7 publisher page observations — candidate metadata

**Observed:** 2026-11-02. **State:** `DISCOVERY_ONLY`, not admitted evidence.
**Audience:** Librarian source/Work inventory and Consolidator-only source-local directory projection.

Three directly retrieved official Paramount+ Season 7 episode-guide responses
yielded **74 source-local episode-listing cards**. They are **not 74 distinct,
verified, watched, read or researched episodes**. The raw HTML is held only in
temporary private custody; nothing resembling a full publisher page or episode
transcript is committed. [`index.json`](index.json) records each response's
SHA-256 and byte length, the deterministic CSV SHA-256, the exact URL, and
observed card count.

| Series | Publisher URL | Observed listings | Ordinal scope |
| --- | --- | ---: | --- |
| The Next Generation | https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/7/ | 25 | S7E1–S7E25 |
| Deep Space Nine | https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/7/ | 25 | S7E1–S7E25 |
| Voyager | https://www.paramountplus.com/shows/star_trek_voyager/episodes/7/ | 24 | S7E1–S7E9 and E11–E25; S7E10 is absent from this page and must not be invented |

The missing Voyager E10 may reflect a combined multipart publisher package;
the page itself does **not** justify inventing a separate card, asserting
completeness, or deciding the underlying Work structure. All three sources
belong to the same Paramount/CBS provenance family, so three site pages are
not independent corroboration. Their local SHA-256 receipts establish only
capture consistency, not publisher-signed authenticity. The parser explicitly
rejects missing, mismatched, duplicated, or ambiguous page-canonical tags,
including duplicate `rel` or `href` attributes.

No audiovisual source was watched, complete transcript read, edition identity
reconciled, or factual canon admitted. All accepted Work, source-binding,
coverage, and denominator effects remain `NONE`; zero Briefings are created.

Check the committed bounded source observations without private HTML:

```sh
python3 tools/build_publisher_s7_discovery.py --check
python3 -m unittest tests.test_publisher_s7_discovery -v
python3 tools/validate.py
```

To reproduce a source capture privately, retrieve the three publisher guide
pages into a non-repository directory as `tng-s7.html`, `ds9-s7.html`, and
`voy-s7.html`; compare response origin/canonical to expected locators, then
run `python3 tools/build_publisher_s7_discovery.py --ingest-dir /private/html`.
The importer is fail-closed on source attribution and refuses unsafe output
links, but a multi-file batch is not transactionally atomic across interruption;
rerun `--check` and inspect the Git diff before publication.

**Next frontier:** independent hostile raw-source replay; Librarian source and
Work binding; Consolidator integration of source-local discovery metadata
without global identity promotion or accepted research coverage changes.
