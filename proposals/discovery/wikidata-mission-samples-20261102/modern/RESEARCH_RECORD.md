# Bounded modern-series episode metadata discovery — 2026-11-02

## Frozen pre-registration

Question: Can a maximum of four bounded public Wikidata Query Service GET requests retrieve candidate television episode QIDs and English labels for Voyager (`Q156329`), Enterprise (`Q380519`), Discovery (`Q21296543`) and Picard (`Q62573305`), preserving exact source bytes and query receipts, without creating accepted canon records?

Hypothesis H1: A GET to `https://query.wikidata.org/sparql` with the frozen per-Mission query and `Accept: application/sparql-results+json` will return HTTP 200, valid SPARQL JSON and at least one row with the requested series QID. Falsifier: network/permission error, non-200 HTTP, malformed JSON or empty rows.

Hypothesis H2: The offline candidate importer will accept each exact raw response and accompanying query/CC0 receipt and produce only CANDIDATE rows with null canonical Work IDs and no accepted source-binding/coverage effects. Falsifier: importer rejects, mutates accepted records, or produces acceptance claims.

Confirmatory experiments:

- **E1**: Read official WDQS API format and Wikidata structured-data license documentation; confirm installed curl/Python versions.
- **E2-VOY, E2-ENT, E2-DIS, E2-PIC**: One GET each, 20-row `LIMIT`, fixed query text in `queries/<series>.rq`, HTTP header `Accept: application/sparql-results+json`, bounded total timeout (30s), connection timeout (8s), maximum response (1 MiB), descriptive user agent, and raw output in `responses/<series>.json`.
- **E3-<series>**: Generate a user-supplied UTC epoch/CC0/exact-query receipt under `receipts/`; run `tools/import_wikidata_episodes.py` offline with output only under `proposals/`. Check raw response and query SHA-256, candidate status, absence of canonical admission and correct series identity.

Stopping rules: At most four GET requests total. If sandbox network fails, request the documented escalation once; if denied, stop. For any non-200 result, rate limit, timeout, malformed response, duplicate episode QID, or importer failure, record the failure and stop that series; never change the endpoint, use another proxy, credentials or bulk scraping. Keep the full history of failed experiments and deviations below.

## Evidence log

E1 / confirmatory / PASS — Official MediaWiki WDQS manual: https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual (retrieved 2026-11-02 via web search); documented GET `query` parameter and JSON `Accept` header. Official Wikidata licensing: https://www.wikidata.org/wiki/Wikidata:Licensing (same retrieval), structured data CC0. Installed tools: curl 8.5.0, Python 3.12.14. No client-library dependency.

E2-NETWORK / confirmatory / FAIL sandbox then approved escalation — Initial VOY command exited `7`, decisive output `curl: (7) Failed to connect to browser-proxy port 8889 after 0 ms: Couldn't connect to server` and `HTTP:000 BYTES:0 TYPE:`. The same bounded command was rerun once outside the restricted sandbox with explicit escalation; no alternate endpoint, proxy or credentials.

E2-VOY / confirmatory / PASS — HTTP 200, exact output `HTTP:200 BYTES:7219 TYPE:application/sparql-results+json;charset=utf-8`, exit `0`, 20 unique episode QIDs all linked to Voyager television series `Q156329`. Raw `responses/voy.json` SHA-256 `d4dbb3f7f0ff6397385231d8187da3796b17552d0967826487dcdc45bafe7010`. Query `queries/voy.rq` SHA-256 `4c73930312107008e5d90429737f22703fb466fadcf4dcb79470cffea9abadc3`.

E2-ENT / confirmatory / FAIL — Single approved bounded GET exit `28`, decisive output `curl: (28) Operation timed out after 30002 milliseconds with 0 bytes received` and `HTTP:000 BYTES:0 TYPE:`. There is no retrieved Enterprise response and no Enterprise candidate file; no retry or alternative request was made. Query `queries/ent.rq` SHA-256 `376c8c8e81285982023e7fb982fb1f7fe118452e3363e92dc10131f3b9b8e531`.

E2-DIS / confirmatory / PASS — HTTP 200, exact output `HTTP:200 BYTES:7299 TYPE:application/sparql-results+json;charset=utf-8`, exit `0`, 20 unique episode QIDs all linked to Discovery television series `Q21296543`. Raw `responses/dis.json` SHA-256 `d691dd242e50c60afcc263efe9be12c41a994307f1e9d66a647ccaa0a6a19c8b`; query SHA-256 `c442dffbff010586f683c99caac1feb9897f8f9a06b5938d99cc29c9016d1c48`.

E2-PIC / confirmatory / PASS — HTTP 200, exact output `HTTP:200 BYTES:7255 TYPE:application/sparql-results+json;charset=utf-8`, exit `0`, 20 unique episode QIDs all linked to Picard television series `Q62573305`. Raw `responses/pic.json` SHA-256 `20b050932c01f280af6863727b70f5d5dd48145d07e7bccbaa814f7fd4e4cf90`; query SHA-256 `e1cdd414be7dc20869cd2719f6a34c52f147eb612d7dba89d2059da0085e8a9a`.

Exact commands for the four externally connected requests (all used `require_escalated` after the observed sandbox network block):

```sh
curl --silent --show-error --fail-with-body --get --max-time 30 --connect-timeout 8 --max-filesize 1000000 --header 'Accept: application/sparql-results+json' --user-agent 'TrekDataCore-Research/0.1 (CC0 episode discovery)' --data-urlencode query@queries/voy.rq --output responses/voy.json --write-out 'HTTP:%{http_code} BYTES:%{size_download} TYPE:%{content_type}\n' https://query.wikidata.org/sparql
curl --silent --show-error --fail-with-body --get --max-time 30 --connect-timeout 8 --max-filesize 1000000 --header 'Accept: application/sparql-results+json' --user-agent 'TrekDataCore-Research/0.1 (CC0 episode discovery)' --data-urlencode query@queries/ent.rq --output responses/ent.json --write-out 'HTTP:%{http_code} BYTES:%{size_download} TYPE:%{content_type}\n' https://query.wikidata.org/sparql
curl --silent --show-error --fail-with-body --get --max-time 30 --connect-timeout 8 --max-filesize 1000000 --header 'Accept: application/sparql-results+json' --user-agent 'TrekDataCore-Research/0.1 (CC0 episode discovery)' --data-urlencode query@queries/dis.rq --output responses/dis.json --write-out 'HTTP:%{http_code} BYTES:%{size_download} TYPE:%{content_type}\n' https://query.wikidata.org/sparql
curl --silent --show-error --fail-with-body --get --max-time 30 --connect-timeout 8 --max-filesize 1000000 --header 'Accept: application/sparql-results+json' --user-agent 'TrekDataCore-Research/0.1 (CC0 episode discovery)' --data-urlencode query@queries/pic.rq --output responses/pic.json --write-out 'HTTP:%{http_code} BYTES:%{size_download} TYPE:%{content_type}\n' https://query.wikidata.org/sparql
```

E3-VOY / confirmatory / PASS — Offline importer exit `0`, exact output `EPISODE_DISCOVERY_CANDIDATES: 20 -> /workspace/scratch/c7a701d1b4cc/trek-wdqs-modern/proposals/voy.json`. Output SHA-256 `3990d59bbb40877cef5acf0d78a99f54d80f337b90a4489495b3a197d23fbc42`. The receipt query matches query bytes exactly; output provenance hashes match raw query/response; all rows have `status=CANDIDATE`, `canonical_work_id=null`, and all accepted effects `NONE`.

E3-ENT / confirmatory / NOT RUN — No response; excluded after E2 timeout, as required by stopping rule.

E3-DIS / confirmatory / PASS — Offline importer exit `0`, exact output `EPISODE_DISCOVERY_CANDIDATES: 20 -> /workspace/scratch/c7a701d1b4cc/trek-wdqs-modern/proposals/dis.json`. Output SHA-256 `9d91e66c96b18f7685bc9f6e658f7d1748134e2bb6a89c1f8e46e1127a653388`; all acceptance and hash checks passed.

E3-PIC / confirmatory / PASS — Offline importer exit `0`, exact output `EPISODE_DISCOVERY_CANDIDATES: 20 -> /workspace/scratch/c7a701d1b4cc/trek-wdqs-modern/proposals/pic.json`. Output SHA-256 `0550f2182e5ab0b4ded47ab8d1c9ef7a980fbb07a88ce8e2e404bef95ab68ccf`; all acceptance and hash checks passed.

The importer command for each success was `python3 ../trek-episodes-pr-slice/tools/import_wikidata_episodes.py --input responses/<series>.json --receipt receipts/<series>.json --output proposals/<series>.json` (with `<series>` individually substituted as `voy`, `dis` and `pic`). Importer regression suite: `python3 -m unittest discover -s ../trek-episodes-pr-slice/tests -p 'test_wikidata_episode_discovery.py' -q` exit `0`, 13/13 PASS.

## Deviations and dead ends

The Enterprise request timed out; no Enterprise response or candidate file
exists. This failure was retained without retry or substitution.

The Enterprise query produced no response within its allotted 30 seconds. The frozen plan was honored: no retry, no alternative provider, no assumed Enterprise coverage. The only network escalation was the documented sandbox boundary, not a workaround of rate limits or source restrictions.

## Verdict

Pending independent evidence review; results are candidate-only even if retrieval succeeds.

Self-check verdict: **partially confirmed**, pending independent review. E2/E3 passed for Voyager, Discovery and Picard (60 metadata candidates), failed/timed out for Enterprise; all candidate output was generated offline and all admission effects remain `NONE`. These samples are not representative episode denominators, complete inventories or primary audiovisual witnesses.
