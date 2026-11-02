# Enterprise and Starfleet Academy: bounded follow-up discovery

## Preregistered method (2026-11-02)

Question: Does a simple, forward `wdt:P179` membership query produce bounded Wikidata metadata candidates for *Star Trek: Enterprise* (`Q380519`) and *Star Trek: Starfleet Academy* (`Q134592591`) where the earlier path/type-constrained queries timed out or yielded zero rows?

These are follow-up exploratory queries with distinct snapshots. The earlier timeout and empty result remain intact, and results are not treated as episode totals, canonical Work identity, content evidence, or accepted coverage.

Predeclared execution: at most **one GET per series**, on official WDQS SPARQL endpoint, `Accept: application/sparql-results+json`, custom descriptive user agent, 30-second total timeout, 8-second connection timeout, 1 MiB maximum response, `LIMIT 20`. Record HTTP code, reported bytes, content type, UTC retrieval epoch, exact query/response SHA-256, and no raw source response in the public repository. A failed query yields no candidate; do not retry, evade rate limits, change endpoints, or infer rows.

Analysis: run existing offline candidate importer with a separate exact-query CC0 receipt. Verify each episode URI and requested series QID, no duplicates, `status=CANDIDATE`, null canonical Work ID, no accepted source/coverage effects. Existing `P179` information is a third-party discovery hint, not an independent primary source claim about story identity.

## Evidence log

E0 / confirmatory / PASS with later correction — Checked the repository protocol from `main`, candidate importer [#161](https://github.com/thebrazenbeard/trek-data-core/pull/161), and nine-Mission metadata [#169](https://github.com/thebrazenbeard/trek-data-core/pull/169) (both subsequently merged). Wikidata identifies `Q380519` as *Star Trek: Enterprise*. The originally selected `Q134592591` Starfleet Academy URL resolves through a redirect to `Q117350388`, discovered on subsequent item verification in E4 below. Official WDQS documentation permits GET SPARQL requests and Wikidata licensing describes CC0 structured data. Sources: https://www.wikidata.org/wiki/Q380519 ; https://www.wikidata.org/wiki/Q134592591 ; https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual/en ; https://www.wikidata.org/wiki/Wikidata:Licensing .

E1-NETWORK / confirmatory / FAIL sandbox, then approved escalation — The ordinary bounded `curl` request for ENT failed exit `7`: `Failed to connect to browser-proxy port 8889 after 0 ms`. The equivalent SFA request failed for the same sandbox network boundary. Each was rerun once under the environment's explicit network permission mechanism, without altering endpoints, proxies, query text or rate limits.

E2-ENT / confirmatory / PASS — HTTP `200`, `7237` bytes, content type `application/sparql-results+json;charset=utf-8`, exit `0`. Twenty unique result bindings, each with series URI `http://www.wikidata.org/entity/Q380519` and an English label. Source response SHA-256 `5925ba3576baf65f0406e99cd8f78ce085192fbacb53b1a6b46d277bb9580c71`; exact query SHA-256 `9abb9deda113ad7c97cb13b52acd56601a6448db3b9fd30d3184fc09fd0a048f`; output file mtime epoch `1793624650` (recorded after completion) used as receipt epoch. Input response retained outside public repository under temporary local research storage.

E2-SFA / confirmatory / FAIL to yield candidates — HTTP `200`, `115` bytes, content type `application/sparql-results+json;charset=utf-8`, exit `0`. Valid SPARQL JSON with an empty `bindings` list. Source response SHA-256 `e25493ee2061a5d3127af537f85981f4645c8e22d0ebefec42107679ce2ab756`; exact query SHA-256 `315a0153d1841f82ac9f445b6ce76c6e375e27f75d6be882fb1da94a059ab4cb`; output file mtime epoch `1793624663` (recorded after completion). No SFA importer input or proposal was fabricated. This result establishes only that the exact query with the obsolete/redirected QID returned no bindings; it does **not** characterize candidate availability under the current target series QID.

E3-ENT / confirmatory / PASS — Existing #161 offline importer accepted the exact ENT response and `receipts/ent.json` and created exactly 20 `status=CANDIDATE` records in `proposals/ent.json` with all canonical Work IDs `null`, all accepted effects `NONE`. **Review hold**: `Q56247746` is labeled *Temporal Cold War arc*, apparently a story arc rather than an installment; `Q866375` is an unsuffixed *In a Mirror, Darkly* item alongside a separate Part II lead and requires identity review. Both remain proposal-only and are excluded from suggested public episode search by `REVIEW_HOLDS.json` until individually verified. This demonstrates the risk of a relaxed P179-only query. A strict typed query was already attempted in earlier #169 work and timed out; the present broader result must not bypass type/evidence review.

E3-SFA / confirmatory / NOT RUN — The importer requires at least one row; empty results are recorded as negative search evidence, never as a synthetic episode proposal.

E4-SFA / source-identity review / HOLD — Direct read-only inspection of https://www.wikidata.org/wiki/Q134592591 displays `Star Trek: Starfleet Academy (Q117350388)` and explicitly `Redirected from Q134592591`. The raw SFA query and receipt must remain unchanged for reproducibility. A new query targeting `Q117350388` would constitute a separate retrieval, not a correction of the recorded snapshot; none was run for this batch. The zero-row observation is therefore held from any assertion about SFA episode discovery completeness.

E4-ENT / candidate-identity review / HOLD — All 20 recorded IDs are distinct Q-prefixed decimal entity identifiers with nonempty English labels in the importer proposal and the same `Q380519` parent identifier; their individual current Wikidata claims and episode ontology have **not** been independently authenticated against the offline response bytes. The independent source-response digest cannot be recomputed from the public proposal alone. `Q56247746` (arc) and `Q866375` (multipart ambiguity) are explicitly quarantined; the remaining 18 are still research candidates, not certified episode Works.

Exact command template (executed separately for `ent` and `sfa`, with separate network escalation after sandbox port failure):

```sh
curl --silent --show-error --fail-with-body --get --max-time 30 --connect-timeout 8 --max-filesize 1000000 --header 'Accept: application/sparql-results+json' --user-agent 'TrekDataCore-Research/0.1 (CC0 episode discovery)' --data-urlencode query@proposals/discovery/wikidata-ent-sfa-second-pass-20261102/queries/ent.rq --output /tmp/<research-directory>/ent.json --write-out 'HTTP:%{http_code} BYTES:%{size_download} TYPE:%{content_type}\n' https://query.wikidata.org/sparql
```

`sfa` substituted for `ent` in the second query path and output file; no other parameter changed. **Important**: the response digests and local mtime are researcher-supplied receipts, not signed remote attestations. Empty SFA response bytes remain out of the public tree.

## Verdict

One additional Mission now has 20 **external metadata discovery leads**, not 20 accepted episode identities; two of those leads carry explicit episode-identity review holds. The SFA literal query returned zero rows but used a redirected series QID; this is an **unresolved source-identity hold**, not negative evidence about the current SFA item. No canonical Work, Source↔Work binding, episode narrative fact, accepted coverage count, or deployment has changed.
