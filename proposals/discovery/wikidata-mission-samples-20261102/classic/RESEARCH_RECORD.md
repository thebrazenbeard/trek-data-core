# Bounded Wikidata television episode candidate acquisition — 2026-11-02

## Frozen plan (before experiment results)

Question: Can three bounded read-only WDQS queries retrieve CC0 episode discovery metadata for The Original Series (Q1077), The Animated Series (Q20922), and Deep Space Nine (Q108774), then pass the existing offline candidate-only importer without canonical admission?

Hypothesis H1: Each of three separately scoped `LIMIT 20` GETs will return HTTP 200 with WDQS SPARQL JSON, 1–20 bindings for its exact television-series QID. Falsifiers: rate limit, timeout, network/proxy failure, JSON shape mismatch, wrong series QID, or empty bindings.

Hypothesis H2: Each raw response plus exact query and an explicit CC0/UTC receipt can normalize through `tools/import_wikidata_episodes.py` without accepted Work, Source-binding, or coverage effect. Falsifiers: importer rejection or any accepted side effect.

Methods:

- D1 (confirmatory): verify current WDQS JSON request format and structured-data CC0 terms from vendor documentation; inspect local curl executable version and importer contract.
- E1 (confirmatory): one scoped GET per Mission (three total), `LIMIT 20`, 30-second maximum each, `Accept: application/sparql-results+json`, descriptive User-Agent, 1 MiB response cap, preserve bytes, query and status.
- E2 (confirmatory, E1-dependent): produce per-series provenance receipts using exact query bytes and Unix UTC retrieval time, normalize with offline importer into `proposals/` only, hash all artifacts and verify unadmitted state.
- E3 (confirmatory): run importer tests and recompute content hashes independently; reject mismatches.

Stopping rules: Stop per series on any HTTP non-200, parser rejection, duplicate episode identity, rate limit or source/permission error. Never change proxies or use credentials to bypass restrictions; never exceed three successful data GETs. No GitHub writes, canonical Work creation or promotion.

## Evidence log

**D1 / confirmatory / PASS.** Local curl version is 8.5.0 (OpenSSL 3.0.13); no SDK or application dependency is used. Official WDQS manual, https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual (retrieved 2026-11-02, web `turn26search0`), documents GET `query=` and `Accept: application/sparql-results+json`; Wikidata official https://www.wikidata.org/wiki/Wikidata:Licensing (retrieved 2026-11-02, web `turn27view0`) covers CC0 structured data. For project behavior, local importer `trek-episodes-pr-slice/tools/import_wikidata_episodes.py` remains authoritative.

**E1a / confirmatory / FAIL in sandbox.** The first TOS curl GET returned exit `7`, `HTTP:000 BYTES:0 TYPE:`, with `Failed to connect to browser-proxy port 8889 after 0 ms`. The command was retried with `require_escalated` as prescribed for sandbox network failures. This is an environment failure, not negative evidence of WDQS data.

**E1b / confirmatory / PASS.** The exact bounded command template, with `{mission}` substituted once per scoped request, was:

```sh
curl --silent --show-error --fail-with-body --get --max-time 30 --connect-timeout 8 --max-filesize 1000000 \
  --header 'Accept: application/sparql-results+json' \
  --user-agent 'TrekDataCore-Research/0.1 (CC0 candidate discovery)' \
  --data-urlencode query@queries/{mission}.rq --output responses/{mission}.json \
  --write-out 'HTTP:%{http_code} BYTES:%{size_download} TYPE:%{content_type}\n' \
  https://query.wikidata.org/sparql
```

All three elevated GETs returned exit `0`, HTTP `200`, `application/sparql-results+json;charset=utf-8`:

| Mission / Wikidata QID | HTTP bytes | Query SHA-256 | Raw response SHA-256 | Candidate count |
| --- | ---: | --- | --- | ---: |
| TOS / Q1077 | 7,266 | `fb4c25a625c37eacf3a08e32587ecb5cff7fc4776954853865290b0033e391f4` | `9b65a52eb918f82e5700dcea7f281bf003eca74952fb41e933353641bde1ea6b` | 20 |
| TAS / Q20922 | 7,307 | `67b238da2ea8055877fab9665732116d8020fc0e6ac844a1dc65f850487c80b2` | `87b5fe5c4b3b4a82d80b8c04b0d574d782e9db4c5766e9a8c0f090cb3acb9bc4` | 20 |
| DS9 / Q108774 | 7,219 | `c997b08dd8c9d03ebb9b373df5c6468ad903e475635f06dc8189bc0c09f78e7f` | `c7f0f554ca4d99b744a7b67be8ca0a4464ae2ed1fdd4c63b0b7396951015d53b` | 20 |

The local JSON parser confirmed 20 bindings per response, all series URI values matching the corresponding QID, and variables exactly `episode`, `episodeLabel`, `series`. No other public data GETs were attempted.

**E2 / confirmatory / PASS.** Receipts use each raw response's file mtime epoch after its GET (`1793620639`, `1793620673`, `1793620694` respectively); each receipt's query string exactly equals its `.rq` bytes including final newline. The offline importer ran with `--input responses/{mission}.json --receipt receipts/{mission}.json --output proposals/{mission}-qids.json`, exit `0` each. It produced 20 `CANDIDATE` records per Mission, all `canonical_work_id: null`, with accepted Work, Source-binding, and coverage effects `NONE`.

**E3 / confirmatory / PASS (local self-check only).** Independently recomputed raw query/response hashes against each proposal's provenance, confirmed all 60 QIDs unique across three batches, that no row had an admitted identity/effect, and the unmodified importer suite **13/13 PASS**. Proposal SHA-256 receipts: TOS `c9759293c0b1675738bff21ead03bb9763d752562f6f072399f176985aaae5fa`; TAS `01390b253ee5b1ef445a1fd9862a8774ca66ce76be85815d942edbb591901df9`; DS9 `81296bad4eadea054bca9a359c1ffe16c1491b8bb03e107fc8c0887dbafae809`.

## Deviations and dead ends

The sandbox network proxy refused the first GET, so the identical bounded request was retried with explicit escalated approval. No alternate proxy, account or credentials were used. These requests are deliberately incomplete, `LIMIT 20` discovery samples; no claim about total episode count or continuity truth is supported.

## Verdict

**Partially confirmed pending a fresh independent review:** bounded episode discovery and offline normalization succeeded for all three Missions. This establishes 60 metadata candidates only, with no narrative verification, accepted Source↔Work binding, admitted assertions, or episode coverage. Completeness and provenance authority remain open.
