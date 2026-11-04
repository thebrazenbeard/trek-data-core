# Librarian Source→Work route hold — TNG *The Neutral Zone*

**Status:** `PROPOSED / SOURCE_ROUTE_HELD`; no acceptance or research coverage effect.

**Accepted-state basis:** `main` `3028765359001b90bc3e6b5c1835ee283b326e91`.
**Exact input:** `proposals/librarian/tng-official-metadata-20261102/bundle.json`, SHA-256
`622f25232a4bb8dc9c11a21ebff56fbf87240c20523047ac26c569af2449ce12`.

This is an **eligibility and blocker audit**, not a new episode or book research
tranche. Director [issue #23](https://github.com/thebrazenbeard/trek-data-core/issues/23)
is OPEN; its admission hold takes priority over enlarging metadata staging.

## Exact inspected artifacts

- The previously accepted TNG publisher **metadata proposal** above (five Source, Work,
  and binding candidates); specifically the `The Neutral Zone` page association.
- `schema/source-work-binding.schema.json`, `registry/README.md`,
  `tools/coverage_ledger.py`, `tools/validate.py`,
  `docs/FIRST_NONFIXTURE_EPISODE_PILOT.md`, and `docs/SOURCE_CUSTODY_RECEIPTS.md`.
- The accepted-tree episode readiness command found **zero accepted nonfixture
  episode Works**, **zero approved projection hashes**, and status
  `TECHNICAL_PREREQUISITES_BLOCKED`.

No fresh Paramount+/StarTrek.com body, video, transcript, subtitle, or book
contents were retrieved or read for this audit. This batch does not establish
rights to access any actual audiovisual episode or verify page bytes currently
served by a publisher. The previous metadata packet's titles and slot labels
remain *publisher-utterance observations*, not source-body evidence.

## Held route

| Component | Accepted proposal observation | Missing gate |
| --- | --- | --- |
| Candidate Work | `proposal:tng:work:neutral-zone:20261102`, *The Neutral Zone* | Work `PROPOSED`; no accepted parent Mission Work or independent identity adjudication |
| Candidate Source | `proposal:tng:source:neutral-zone:20261102` | `WEB_METADATA_ONLY`, source `PROPOSED`; no edition/version, source bytes or content SHA-256 |
| Candidate binding | `proposal:tng:binding:neutral-zone:20261102` | `PROPOSED / METADATA_ONLY`, with no matched `BYTE_HASH` basis |
| Publisher locator | `https://www.startrek.com/videos/star-trek-the-next-generation-the-neutral-zone` | Page title/label S1E26 does not verify audiovisual content, access rights, or exact full-episode Source identity |
| Lineage | `publisher:startrek.com` | One publisher family; not independent corroboration |

`python3 tools/audit_tng_source_route.py` rechecks the exact reviewed bundle
bytes, candidate identity tuple, lineage and seven structural eligibility
conditions. Exit **2** means `STRUCTURAL_ROUTE_BLOCKED` (expected); **3**
means reviewed input was changed/ambiguous and must be requalified. A future
zero exit, if the checker were revised for a truly upgraded input, would **not**
prove a source was read, rights were granted, identity was independently
adjudicated, or anything was accepted. The command never writes canonical state.

## Specific next admissible step

Under an authorized Librarian custody arrangement, obtain a rights-valid,
version-identified **complete source representation** for the selected episode,
retain bytes privately, compute an exact independent SHA-256 custody receipt,
and separately resolve Work parent/episode identity and the scope of the
prospective Source↔Work binding. Only then prepare separate governed proposal
records and independent review; no coverage stage is automatically unlocked.

## Validation

```sh
python3 tools/audit_tng_source_route.py  # expected exit 2: held
python3 -m unittest discover -s tests -p test_tng_source_route_audit.py -v
python3 -O -m unittest discover -s tests -p test_tng_source_route_audit.py -v
python3 tools/check_episode_pilot_readiness.py
python3 tools/validate.py
```
