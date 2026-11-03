# Explorer: first-party Paramount film-page source rechecks

This independent LCARS Explorer shelf exposes **13 source-local observations**
from three accepted, first-party Paramount film-page research packets: six
original pages, six subsequent pages, and the separate *Star Trek Beyond*
page. These are observed publisher listing **year, rating, runtime, genre and
selected credits**, not film viewings, independently authenticated works, or
primary audiovisual text analysis. Paramount and StarTrek.com belong to related
corporate lines, not independent factual corroboration.

The URL path provides a practical source-page label; the projected slug is
**not asserted to be a separately verified official title**. Each record
retains a source-local candidate ID and an input file SHA-256 receipt. Three
original research anomalies remain visibly **HELD**: *First Contact* studio
director attribution, *Search for Spock* publisher-directory year conflict,
and *Insurrection* credit name rendering. None is reconciled by this index.

## Strict source/custody boundaries

- Compiler inputs are exactly three accepted research packets, totaling 13
  distinct source-local IDs. The original validators have immutable review
  pins for packet bytes, row metadata, source URLs and release boundaries.
- The compiler **re-runs each original validator** before accepting source
  bytes and checks the code-owned whole-packet SHA against the source. The
  Pages artifact workflow separately reruns all three validators and refuses
  modified/uncommitted output bytes or unexpected Explorer files.
- No film files, full episode content, publisher-description paraphrases,
  poster/cover URLs or image bytes are copied into this public projection.
  All Work, synopsis, artwork and coverage effects remain **NONE**.
- Search tags and facets are structural: publisher family, source batch, year,
  rating, and whether an already-recorded anomaly is held. No invented
  thematic or canon tags and no global Work identity resolution.
- This 13-row shelf is **separate** from the existing 14-film directory,
  1,214-entry multimedia source directory, 56+61 metadata recheck layers,
  37 reviewed promotional synopsis overviews, 39 ISBN crosschecks, and three
  edition candidates. Its row count must not inflate a shared Work denominator.

## Reproduce and query

```sh
python3 proposals/films/paramount-six-source-pages-20261103/validate.py
python3 proposals/films/paramount-second-six-pages-20261103/validate.py
python3 proposals/films/beyond-paramount-metadata-20261103/validate.py
python3 tools/build_paramount_film_rechecks.py --check
python3 tools/query_paramount_film_rechecks.py --q "Patrick Stewart"
python3 tools/query_paramount_film_rechecks.py --tag "anomaly:held"
python3 -m unittest tests.test_paramount_film_rechecks
node --test tests/test_explorer.mjs tests/test_explorer_accessibility.mjs
```

The downloadable public artifact is `explorer/paramount-film-rechecks.json`.
The browser checks a full code-owned SHA-256 before rendering, then checks exact
row and receipt shapes. Missing or invalid data shows **unavailable**, not a
misleading zero or a promoted source status.
