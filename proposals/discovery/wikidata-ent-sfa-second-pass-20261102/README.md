# Enterprise and Starfleet Academy second-pass discovery

One bounded follow-up Wikidata Query Service search for each series, dated 2026-11-02. Earlier `P31/P279*` query for Enterprise timed out and the corresponding Starfleet Academy query returned zero rows; both outcomes remain documented in candidate research draft [#169](https://github.com/thebrazenbeard/trek-data-core/pull/169).

| Mission | Series QID | Raw response rows | Candidate proposals | Explicit identity holds | Accepted episodes |
|---|---|---:|---:|---:|---:|
| *Star Trek: Enterprise* | Q380519 | 20 | 20 | 2 | 0 |
| *Star Trek: Starfleet Academy* | Q134592591 (redirect) | 0 | 0 | Series QID requires re-query review | 0 |

Files:

- `queries/*.rq`: exact public SPARQL query texts. These intentionally avoid a costly property path; the resulting candidate set has weaker episode-type guarantees.
- `receipts/*.json`: researcher-supplied origin/license/query/retrieval metadata.
- `proposals/ent.json`: deterministic offline importer output, **not** canonical episode data.
- `REVIEW_HOLDS.json`: two candidate QIDs needing episode identity or multipart review before inclusion in a public episode search.
- The SFA query used `Q134592591`, which the current Wikidata item page identifies as a redirect to `Q117350388`. Its zero-row result applies only to the historical query literal; it is **not** a negative finding about the canonical SFA series item. This is a separate source-identity hold, with no unrecorded retry.
- `RESEARCH_RECORD.md`: protocol, failure history, response hashes, and limitations.

The raw SPARQL response JSON is deliberately not committed; `TREK_REPO_PROTOCOL.md` keeps source-response bytes outside the public repo. `response_sha256` and query hashes support independent integrity checks only if the corresponding outside-repo response bytes are available. No full episode inventory or primary source material has been ingested.
