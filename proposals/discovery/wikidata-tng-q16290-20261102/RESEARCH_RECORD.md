Archived location in this repository: `proposals/discovery/wikidata-tng-q16290-20261102/` (raw response and query bytes unchanged). The commands below record the original acquisition workdir and are not copy/paste paths in a fresh clone.

# Wikidata bounded episode candidate acquisition — 2026-11-02

## Frozen pre-registration (unchanged after first experiment)

Question: Can one bounded, read-only Wikidata Query Service SPARQL request retrieve verifiable Star Trek: The Next Generation episode metadata without credentials so the existing offline importer can stage candidate-only records?

H1: A public HTTPS GET for the frozen ten-row TNG query returns HTTP 200, a SPARQL results JSON object and at least one matching episode. Falsifier: network/proxy restriction, endpoint timeout/error, malformed response, or no episode bindings.

H2: The existing offline importer can emit a new `proposals/`-only candidate artifact from exact response bytes plus an explicit CC0/query/timestamp receipt. Falsifier: importer rejection or accepted Work/Source effects.

Methods:

- E1 (confirmatory): verify WDQS response format / request interface and Wikidata's structured-data license in official docs, noting retrieval date.
- E2 (confirmatory): perform exactly one bounded GET for `queries/tng-small.rq` with `Accept: application/sparql-results+json`, identifiable user agent, `--max-time 30`, and a maximum response size. Preserve actual bytes/status/command.
- E3 (confirmatory, conditional on E2): create user-supplied receipt with exact query and retrieval epoch, run the offline `import_wikidata_episodes.py` to produce only a candidate `proposals/...` path; run tests and SHA-256 receipts.

Stopping rules: Stop upon E2 network restriction/time-out or HTTP failure; do not retry via unapproved alternate proxies/credentials. Stop after E3 one successful candidate file; no bulk data crawling, remote repository writes, canonical admission or acceptance claims.

## Evidence log

E1 / confirmatory / PASS — Retrieved official MediaWiki WDQS manual at https://www.mediawiki.org/wiki/Wikidata_query_service/User_Manual (web ref `turn23search0`, retrieved 2026-11-02). It documents HTTPS GET with query parameter and `Accept: application/sparql-results+json`. Retrieved official Wikidata licensing policy at https://www.wikidata.org/wiki/Wikidata:Licensing (web ref `turn24view0`, retrieved 2026-11-02): structured data CC0, unlike ordinary prose outside structured namespaces. No versioned client library is used (Python stdlib importer; curl executable).

E2a / confirmatory / FAIL (sandbox) — Exact curl GET below, exit code `7`: `curl: (7) Failed to connect to browser-proxy port 8889 after 0 ms: Couldn't connect to server`, status `HTTP:000 BYTES:0 TYPE:`. Following sandbox policy, retried the exact bounded command with `require_escalated`, no alternate proxy or credentials.

E2b / confirmatory / PASS (approved unsandboxed network) — Exact request:

```sh
curl --silent --show-error --fail-with-body --get --max-time 30 --connect-timeout 8 --max-filesize 1000000 --header 'Accept: application/sparql-results+json' --user-agent 'TrekDataCore-Research/0.1 (CC0 episode discovery)' --data-urlencode query@queries/tng-small.rq --output tng-small-response.json --write-out 'HTTP:%{http_code} BYTES:%{size_download} TYPE:%{content_type}\n' https://query.wikidata.org/sparql
```

Exit `0`, decisive output `HTTP:200 BYTES:3652 TYPE:application/sparql-results+json;charset=utf-8`; fetched 10 SPARQL JSON rows with head vars `episode`, `episodeLabel`, `series`, all TNG series item Q16290. Evidence source `tng-small-response.json` SHA-256 `ea959ea993f21bb1de28ac955319a03f7024c37449a09c35129a795076d77499`; query source `queries/tng-small.rq` SHA-256 `10ff1070c9196ed80f90b8d2e95d29a6328d9501ce49a7a72d81f98ab7164b71`. The returned result is a bounded discovery sample, not completeness or independent narrative evidence.

E3a / confirmatory / FAIL, importer exact-query contract — `python3 ../trek-wikidata-discovery-slice/tools/import_wikidata_episodes.py --input tng-small-response.json --receipt tng-small-receipt.json --output proposals/tng-small-q16290.json` exit `1`, decisive error `query_text must be a trimmed, nonempty printable string (max 20000)`. Actual transmitted `.rq` had a trailing newline; stripping it would falsify the exact-query receipt.

E3b / confirmatory / PASS after narrowly documented importer amendment — `clean_text(..., multiline=True)` now preserves legal leading/trailing SPARQL whitespace while still rejecting whitespace-only query text. Added test `test_exact_multiline_query_with_trailing_newline_preserved`; fresh suite **13/13 PASS**. Reran same CLI: exit `0`, decisive output `EPISODE_DISCOVERY_CANDIDATES: 10 -> .../proposals/tng-small-q16290.json`. Output contains `proposal_only=true`, ten `status=CANDIDATE`, null `canonical_work_id`, `accepted_work_effect=NONE`, `accepted_source_binding_effect=NONE`, `coverage_effect=NONE`; response hash recorded exactly. Receipt SHA-256 `72750bd639180ebb64d78dbb41aa946ad1d012e2a394dfc7b9ebee90661ece25`; candidate proposal SHA-256 `7a4bfa898273ab105e20dcf3c9ff845024bf98a3e6c6194e42b99c0441a27a3c`. No canonical ingestion or GitHub remote write.

## Deviations and dead ends

Deviations: E2 needed explicitly approved sandbox escalation after proxy failure. E3 initially failed on exact-query trailing newline; implementation was amended locally and regression tested (not yet published to GitHub PR #161). The candidate sample is ten rows of TNG, not a complete season/show; external Wikidata is metadata only and does not corroborate narrative assertions. No credentials used.

## Verdict

PASS for bounded, ten-row metadata discovery; independent research admission review remains pending. No episodes are accepted by this record.
