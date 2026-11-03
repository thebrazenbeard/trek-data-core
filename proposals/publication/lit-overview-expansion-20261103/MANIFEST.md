# Literary overview expansion — model editorial request, not Explorer publication

**2026-11-03; role: Index Consolidator; state: PROPOSAL ONLY.**

Purpose: prepare an exact, deterministic review packet for 18 distinct Simon &
Schuster publisher-page literary candidates already present in accepted research
(`lit-six-era-publisher`, `lit-six-next-publisher-works`, and
`lit-six-series-expansion`). The current public Explorer directory has only nine
literature rows; all nine already have publisher-description paraphrases in the
23-entry `synopsis-catalog.json`. This packet does **not** claim the remaining 18
are accepted Explorer directory rows or governed Works.

`tools/build_lit_overview_expansion_request.py` compiles
`editorial-request.json` deterministically with exact candidate IDs, ISBN edition
URLs, original paraphrases + SHA-256 fingerprints, source artifact SHA-256 hashes,
and proposed-but-unaccepted row IDs. `--check` fails on output/source drift.

The three source records share one publisher lineage. No copyrighted books
were read or made source-bound by this projection. No source-page bytes are
custodied. All cover images remain candidate URLs held from public display;
copyright and trademark clearance are not implied by a public publisher image.

**Required before public UI:** independently review every paraphrase against
the exact first-party source page, accept explicit directory candidate row
creation without silently reconciling global Work identities, write a separate
reviewer-owned exact-text/model-review receipt, update the deterministic display
compiler and its tests, pass current-head CI, and obtain the Director's
publication/merge gate. This packet has **zero publication, coverage, or Work
admission effect** by construction.

Validate:

```bash
python3 tools/build_lit_overview_expansion_request.py --check
python3 -m unittest tests/test_lit_overview_expansion_request.py
```
