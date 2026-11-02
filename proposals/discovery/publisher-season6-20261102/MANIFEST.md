# Paramount+ Season 6 publisher page observations — candidate metadata

**Observed:** 2026-11-02. **State:** `DISCOVERY_ONLY`; no episode research
or canonical admission. **Owner:** Librarian source/Work inventory proposal.

The source-first inspection of three HTTPS official Paramount+ Season 6 guide
pages yielded **78 source-local episode-listing observations**. These are
publisher cards, **not 78 independently verified, watched, close-read,
researched, or distinct canonical episodes**. Raw responses were captured
privately, then parsed using exact single publisher `<link rel="canonical">`
binding; missing, forged, duplicated, or ambiguous rel/href attributes fail
closed. Each captured response SHA-256, byte count, normalized CSV hash, and
card count is retained in [index.json](index.json). These local digests verify
reproducibility of a captured response, **not its cryptographic authenticity**.

| Series | Official publisher page | Listed source-local cards | Ordinal observations |
| --- | --- | ---: | --- |
| The Next Generation | https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/6/ | 26 | S6E1–E26 |
| Deep Space Nine | https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/6/ | 26 | S6E1–E26 |
| Voyager | https://www.paramountplus.com/shows/star_trek_voyager/episodes/6/ | 26 | S6E1–E26 |
| **Total** | | **78** | No gaps in captured numeric card sequences |

All three guides belong to the **same Paramount/CBS provenance family** and
do not provide three independent confirmations. Source roster completeness,
edition/variant identity, global entity reconciliation, and source binding
remain unresolved. The captured pages do not establish the franchise-wide
episode denominator or guarantee equivalence with original broadcasts.
No full scripts, licensed text, audiovisual files, or HTML page bodies are
committed; source bytes stay in a private temporary capture.

For exact offline replay against the committed candidate CSVs, bundles and
source receipts:

```sh
python3 tools/build_publisher_s6_discovery.py --check
python3 -m unittest tests.test_publisher_s6_discovery -v
python3 tools/validate.py
```

For fresh source capture, privately retrieve the three official season-guide
pages as `tng-s6.html`, `ds9-s6.html`, `voy-s6.html`, verify HTTPS origin and
raw response identity, then run:

```sh
python3 tools/build_publisher_s6_discovery.py --ingest-dir /path/to/private/html
```

The importer checks canonical URLs strictly but is **not** a cryptographic
publisher attestation. The multi-file atomic writer prevents symlink-follow
and half-file output but does not offer all-or-nothing transaction rollback
across the batch; rerun `--check` after interruption.

**Next frontier:** source-binding, identity/edition reconciliation, and
Consolidator-only deterministic candidate directory integration. No accepted
`SOURCE_BOUND`, `CLOSE_READ`, `ENTITY_LINKED`, audited episode coverage or
Briefing count is increased by this metadata tranche.
