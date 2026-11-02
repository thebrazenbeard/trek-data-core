# Paramount+ Season 5 episode-guide observations — source-local metadata

**Observed:** 2026-11-02. **Status:** `DISCOVERY_ONLY`; **admission:** `NONE`.

Five separately retrieved official Paramount+ Season 5 guide pages yielded **97 publisher-listed episode-card observations**. The original HTTPS response bodies remain private, outside Git; [index.json](index.json) records each response's byte size and SHA-256, the corresponding source-local CSV's SHA-256, the official page URL, and the observed card count. The CSVs and bundles can be regenerated and verified deterministically from the same captured response bytes.

| Publisher series | Source | Observed cards | Source-local ordinal notes |
| --- | --- | ---: | --- |
| The Next Generation | https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/5/ | 26 | S5E1–S5E26 |
| Deep Space Nine | https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/5/ | 26 | S5E1–S5E26 |
| Voyager | https://www.paramountplus.com/shows/star_trek_voyager/episodes/5/ | 25 | S5E1–S5E15, S5E17–S5E26. **E16 is absent from this page's listed cards and is not inferred.** |
| Discovery | https://www.paramountplus.com/shows/star-trek-discovery/episodes/5/ | 10 | S5E1–S5E10 |
| Lower Decks | https://www.paramountplus.com/shows/star-trek-lower-decks/episodes/5/ | 10 | S5E1–S5E10 |

No Enterprise Season 5 guide exists in this batch; no missing entry or ordinal is invented. One card does not necessarily equal one distinct aired Work, especially for combined or multipart installments. These five Paramount+ pages belong to the **same publisher/corporate provenance family**, not five independent corroborations. A retained local capture SHA-256 authenticates only the captured bytes against the submitted receipt; it is **not** a publisher signature or verification against the audiovisual work.

The records have `accepted_work_effect=NONE`, `accepted_source_binding_effect=NONE`, `coverage_effect=NONE`, and `denominator_effect=NONE`. The batch **does not** assert 97 researched/viewed episodes, canonical identity, `CLOSE_READ` coverage, any admitted Briefing, or global series completeness. No full HTML/transcript/media is committed. The raw response bodies were consulted only for listing titles, season/episode labels, and publisher locators.

Offline validation:

```sh
python3 tools/build_publisher_s5_discovery.py --check
python3 -m unittest tests.test_publisher_s5_discovery -v
python3 tools/validate.py
```

For a new source acquisition, retrieve official HTML privately as `<mission>-s5.html` with mission IDs `tng`, `ds9`, `voy`, `dis`, `ld`; then run `python3 tools/build_publisher_s5_discovery.py --ingest-dir /private/source/dir`. The script verifies bounded regular-file inputs and safe no-follow output paths, but multi-file ingestion is **not transactionally atomic**; a partial failure requires a fresh `--check` and diff audit.

**Next:** independent adversarial source-replay of the five exact private responses, Librarian source-binding/duplicate review, then Consolidator-only deterministic integration from an accepted base. None of those acts by itself admits facts or increases researched-episode coverage.
