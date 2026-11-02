# Offline publisher roster CSV intake

`tools/normalize_episode_roster.py` converts an operator-collected **metadata-only**
CSV into the existing publisher episode-roster *candidate* contract. It cannot
download a roster, establish that the claimed publisher page was actually read,
or create accepted Mission Briefings. Its output passes through
`tools/validate_publisher_episode_roster.py` before it is written.

Use this when an authorized researcher has inspected a publisher's episode
listing and recorded only its season/episode slot and short title. Do not copy
episode transcripts, stills, descriptions, full articles or copyrighted books.

## Input

Create a UTF-8 CSV file with **exactly** these three columns:

```csv
season,episode_number,title
1,1,Example Episode One
1,2,Example Episode Two
```

These example titles are synthetic. The tool sorts valid slots, rejects repeated
season/episode pairs or duplicate titles, and limits input to 500 rows/128 KiB.
It does **not** infer that sequential slots prove season completeness.

Record a separate UTF-8 JSON receipt (example placeholders shown):

```json
{
  "batch_id": "example-publisher-20261102",
  "mission_id": "tng",
  "publisher": "Example publisher",
  "independence_group": "publisher:example",
  "observed_on": "2026-11-02",
  "primary_locator": "https://example.org/series/episodes",
  "crosscheck_locator": "https://example.org/series/catalog",
  "csv_sha256": "REPLACE_WITH_SHA256_OF_EXACT_CSV_BYTES"
}
```

Replace every example value with an honest observation. `mission_id` must match
`registry/mission_catalog.json` (a Mission is a series, a Mission Briefing an
episode). The independence group identifies the underlying publisher; two pages
from the same publisher are not two independent sources. The two locators must
be public HTTPS page URLs without query tokens or fragments. Calculate the CSV
hash from the file's bytes, for example `sha256sum /path/to/slots.csv` on Linux,
or `Get-FileHash -Algorithm SHA256` in PowerShell; enter its lowercase hex value.
The hash binds this receipt to the local CSV, not to a publisher HTTP response.

## Usage

From the repository root, first choose and create a new review partition under
`proposals/`. The destination file itself must not yet exist.

```bash
python3 tools/normalize_episode_roster.py \
  --csv /path/to/slots.csv \
  --receipt /path/to/observation.json \
  --output proposals/librarian/my-batch/bundle.json \
  --check
```

Remove `--check` after inspecting any rejections to write the new file. The
generator does not create missing directories, overwrite an existing file,
perform network requests or modify the accepted registry. The resulting
`bundle.json` can independently be checked with:

```bash
python3 tools/validate_publisher_episode_roster.py \
  --input proposals/librarian/my-batch/bundle.json
python3 -m unittest discover -s tests -p 'test_normalize_episode_roster.py' -v
```

The generated proposal deliberately contains `CANDIDATE_METADATA_ONLY`,
`roster_completeness: UNRESOLVED`, four accepted/coverage/denominator effects
set to `NONE`, and no canonical Work or Source-binding IDs. It never claims
a source-page body hash or that audiovisual content was examined. The CSV
digest is reported by the command; retain the original offline CSV and receipt
in authorized private custody for future independent review.

The next step is not automatic promotion: separately verify page evidence,
publisher identity, episode identity, rights, and completeness before following
the repository's Librarian admission and coverage gates.
