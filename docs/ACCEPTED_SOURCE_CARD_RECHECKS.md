# Accepted publisher-card rechecks: additive source-local Explorer sidecar

The previous `explorer/metadata-rechecks.json` remains the independent B001–B004
**56-check** source-only display projection. This layer adds **61** further
publisher-card metadata observations from already accepted main inputs. It does
not rewrite the old count, change the 1,214-row directory, elevate any Work or
fictional claim, mark audiovisual close-reading complete, or approve a synopsis.

| Accepted input | Source-local directory leads | Records | Status |
| --- | --- | ---: | --- |
| B005 DS9 rendered publisher guides | `lead:0051`–`lead:0066` | 16 | Publisher metadata only |
| B006 VOY rendered publisher guides | `lead:0070`–`lead:0082` | 13 | Publisher metadata only |
| B007 VOY rendered publisher guides | `lead:0083`–`lead:0089` | 7 | Publisher metadata only |
| B008 ENT rendered publisher guides | `lead:0090`–`lead:0098` | 9 | Publisher metadata only |
| B009 ENT rendered publisher guides | `lead:0099`–`lead:0107` | 9 | Publisher metadata only |
| DIS S3 Paramount+ seven local work records | `lead:0108`–`lead:0114` | 7 | Publisher metadata only |

The accepted SNW S3 publisher-card batches contain 10 local episode records,
but no explicit source-local `lead_id` / directory-row reconciliation. Those
10 are **not** automatically matched by title or season/episode number and do
not appear in this sidecar. A future reconciler can append accepted crosswalk
decisions with provenance rather than inventing those joins.

## Build, verify, and query

```sh
python tools/build_accepted_source_card_rechecks.py
python tools/build_accepted_source_card_rechecks.py --check
python tools/query_accepted_source_card_rechecks.py --row-id lead:0106
python tools/query_accepted_source_card_rechecks.py --series ENT --title-check COMBINED_CARD_SPLIT_UNRESOLVED
python tools/query_accepted_source_card_rechecks.py --title "terra firma" --limit 10
python -m unittest tests.test_accepted_source_card_rechecks -v
```

The compiler reads accepted proposal JSON, pins their SHA-256 checksums,
requires directory digest `2326f882…`, validates explicit lead IDs/series,
and refuses false exact-title claims, unapproved status vocabulary (including
forged admission-like strings ending in `UNRESOLVED`), or unexpected batches. The committed
sidecar is reproducible byte-for-byte. The CLI queries **only** a projection
whose current bytes equal a fresh source rebuild, so tampered/stale downloads
fail closed. Output includes original source paths and hashes, publisher card
titles, season/episode slots, unresolved spelling/split status, and source-only
scope. Source URL is null when an accepted observation did not retain a
per-record URL.

**46 exact title strings** and **15 unresolved cases** are classifications of
rendered publisher cards *relative to local Wikidata-derived discovery titles*,
not evidence of watched episodes, source equality, identical Work identity,
or independent validation. The two `Broken Bow` leads refer to one combined
publisher card and remain unresolved as separate source-local rows. The
`Terra Firma` Roman/Arabic numeral difference remains unresolved. No brief
publisher descriptions or draft original synopses are included in this output.

All six batches belong to the same Paramount corporate publisher lineage.
The prior Wikidata-derived directory is a discovery source, not an independent
corroborating full episode. The repository's source → work → entity → evidence
→ assertion method remains the only path to stronger research states.

This sidecar is a data compiler and offline callable index, **not** a public
Explorer UI release by itself. Publishing the JSON or displaying badges
requires a distinct Explorer integration and its own verification/review.
