# Paramount+ legacy Season 3 publisher metadata — proposal only

**Observed:** 2026-11-02. **Status:** `DISCOVERY_ONLY`. **Acceptance/coverage/episode-denominator effects:** `NONE`.

This tranche captures **126 source-local episode-listing observations**, not 126
newly verified episodes or admitted Briefings. Official Paramount+ season-guide
HTML was retrieved over HTTPS and processed locally, with exact source-body
SHA-256/byte receipts in `index.json`. Raw publisher HTML is deliberately **not
committed**. The stored CSVs record only season, episode slot, and title; the
bundles explicitly leave canonical Work IDs and Source bindings unresolved.

| Mission | Publisher season-3 guide | Listing rows |
| --- | --- | ---: |
| TOS | https://www.paramountplus.com/shows/star_trek/episodes/3/ | 24 |
| TNG | https://www.paramountplus.com/shows/star_trek_the_next_generation/episodes/3/ | 26 |
| DS9 | https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/3/ | 26 |
| VOY | https://www.paramountplus.com/shows/star_trek_voyager/episodes/3/ | 26 |
| ENT | https://www.paramountplus.com/shows/enterprise/episodes/3/ | 24 |

Lineage is a *single publisher family*, `publisher:paramount`. Five guide
pages are not five independent corroborating publishers. An HTTP source-body
digest is a local capture receipt, **not** a publisher signature; no full
audiovisual program was watched in this batch. Listings can change after the
capture date and could share Work identities with other observation rows.

The deterministic builder checks receipt hashes, official URL scopes, exact
CSV-to-bundle agreement, ordered Season 3 slots, candidate-only effects, and
symlink-safe local output handling:

```sh
python tools/build_legacy_s3_discovery.py --check
python -m unittest tests.test_legacy_paramount_s3 -v
python tools/validate.py
```

Initial processing required temporary source files named `tos-s3.html`,
`tng-s3.html`, `ds9-s3.html`, `voy-s3.html`, `ent-s3.html` at a local path
**outside Git**. The original page bodies are not needed for reproducibly
checking the committed candidate metadata, but fresh source revalidation must
fetch the publisher pages again and compare snapshots, never assume a hash
alone authenticates a new HTTP response.

**Next frontier:** Librarian source-binding review and Consolidator-only
integration into the separately labeled public discovery directory. No
source-local reference should be promoted automatically to a canonical Work,
accepted Briefing, or franchise episode denominator.
