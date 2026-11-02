# Public Explorer cross-index audit

`tools/audit_research_leads.py` checks the relationships between the three
published JSON data surfaces:

- `registry/mission_catalog.json` — display-only Mission (series) identities;
- `explorer/index.json` — governed projection Briefings and continuity records;
- `explorer/research-leads.json` — unverified episode-discovery candidates.

Run from any directory:

```sh
python3 tools/audit_research_leads.py
python3 -m unittest discover -s tests -p 'test_research_leads_audit.py' -v
```

The audit is **read-only**. It validates that the published Mission list matches
the display catalog, every record's Mission Briefing link resolves to the same
Mission, candidate source identities are unique, publisher slots remain
separately typed, and unverified research leads cannot claim acceptance or
coverage. Its report supplies side-by-side counts per Mission without adding
candidate leads to admitted Briefing totals.

The audit does **not** verify external publishers, source bytes, observation
quality, Wikidata truth, licensed access, review independence, coverage
denominators or projection signatures. In particular, a result of
`PUBLIC_INDEX_RELATIONS_CONSISTENT` is a structural consistency result, not
content admission or a public deployment qualification.

The existing deterministic builders and admission validators remain the source
of their respective contracts. Run this audit *in addition to*, not instead
of, their full checks before a new publication. The published data can lag
`main` until a separately authorized manual Pages release.
