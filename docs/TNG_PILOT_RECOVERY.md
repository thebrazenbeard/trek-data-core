# TNG first-five pilot recovery (candidate stage)

This adapter recovers **episode metadata and provenance receipts only** from
historical [PR #3](https://github.com/thebrazenbeard/trek-data-core/pull/3).
The historical commit is pinned immutably to
`0695fb2d36870e9c156ce7acd16f00f70103b19e`. It reads that commit's
Git objects via `git show`/`git cat-file` without checking out or executing
any historical script, task, hook, editor setting or executable asset.

## Pilot boundary

- Five proposed TNG Season 1 episode Work candidates.
- Historically reported 58 Evidence candidates, 69 Local Entity candidates
  and 31 Assertion candidates. These counts are copied as **proposal metadata**
  and do not represent accepted research or measured coverage.
- Exact historical manifest Git blob SHA and SHA-256 and all 11 referenced
  artifact byte hashes are independently verified before export.
- The original Source strategy's retrieval dates, transcript URLs,
  crosscheck URLs, provenance-family caveats, audiovisual-verification gaps,
  and title/production-code numbering divergences are retained.
- The adapter **does not export transcript passages, dialogue, prose research,
  assertions or local entity representations**. There is no source-content
  redistribution and no implied right to reproduce third-party material.
- Every Work/Source canonical ID remains `null`, binding status is
  `NOT_ADMITTED`, and accepted corpus and coverage effects are `NONE`.

## Generate / verify

From this repository root, after preserving an immutable local Git object
store that contains PR #3's objects:

```sh
python3 tools/recover_tng_pilot.py \
  --historical-repo path/to/trek-data-core-full-history \
  --output proposals/tng/tng-s01-b001-historical-candidates.json
python3 -m unittest discover -s tests -p 'test_recover_tng_pilot.py' -v
```

The CLI uses exclusive creation and refuses to overwrite an existing
proposal. It does not fetch the network. The generated proposal remains
historical candidate input pending Librarian Source/Work verification,
primary audiovisual or otherwise rights-valid source review, binding
admission, typed conversion, and independent reconciliation/coverage audit.
