# Bounded Wikidata episode-discovery samples — 2026-11-02

Four original, read-only SPARQL requests were submitted to the official
`https://query.wikidata.org/sparql` endpoint. Each has `LIMIT 20`, a 30-second
deadline, a 1 MiB response cap, explicit JSON Accept header and a named user
agent. The sandbox proxy initially blocked the first request; the same
request succeeded after the required approved network escalation. No
credentials, alternate proxies or additional queries were used.

| Mission (TV series) | Wikidata series ID | HTTP | Raw rows | Candidate output | Response SHA-256 |
|---|---|---|---:|---|---|
| Lower Decks | Q62573569 | 200 | 20 | `proposals/ld.json` | `201104200bf77095509aeed2a730007c8aedc2ba645cce27d25660c7da487e9f` |
| Prodigy | Q65250765 | 200 | 20 | `proposals/pro.json` | `fa4d26a9c98b384eeccafbce4b80049b661f07d50a6682ebfd357539b118f68a` |
| Strange New Worlds | Q94527193 | 200 | 20 | `proposals/snw.json` | `7a98a9b52c0a1fc167ef5d857cfa1d0cfa4616c80b060564d27c29f75a4e2826` |
| Starfleet Academy | Q134592591 | 200 | **0** | **None (importer correctly rejected empty result)** | `e25493ee2061a5d3127af537f85981f4645c8e22d0ebefec42107679ce2ab756` |

The series QIDs correspond to the television programs, not similarly named
books or games. Each `queries/*.rq` file is the exact UTF-8 SPARQL request
whose bytes are reproduced inside its matching `receipts/*.json` file. All
raw `responses/*.json` bytes were preserved. The receipts contain the request
query, source URL, explicit Wikidata structured-data CC0-1.0 licensing
statement, UTC epoch of the local response file, and a snapshot ID. The
response and query digests are also written into each normalized proposal.

The command used per Mission, changing only its short code, was:

```sh
curl --silent --show-error --fail-with-body --get --max-time 30 \
  --connect-timeout 8 --max-filesize 1000000 \
  --header 'Accept: application/sparql-results+json' \
  --user-agent 'TrekDataCore-Research/0.1 (CC0 episode discovery)' \
  --data-urlencode query@queries/ld.rq \
  --output responses/ld.json \
  --write-out 'HTTP:%{http_code} BYTES:%{size_download} TYPE:%{content_type}\n' \
  https://query.wikidata.org/sparql
```

After acquisition, the offline importer was invoked with the corresponding
`--input responses/<code>.json`, `--receipt receipts/<code>.json`, and
`--output proposals/<code>.json`. It produced exactly 20 candidates each for
LD/PRO/SNW; it rejected SFA with `SPARQL results require 1 to 10000 rows`
and created no SFA proposal. Its 13 adversarial tests passed.

## Research boundary and anomalies

- **No episodes are admitted.** Every normalized row is `CANDIDATE` with
  `canonical_work_id: null`, no Source binding, no evidence admission and no
  coverage effect.
- These are 20-row samples sorted by Wikidata item identifier, **not** counts
  of all episodes and not representative of an entire season or series.
- Prodigy includes distinct Wikidata items titled *Lost and Found* and
  *Lost and Found: Part 1/2*. Multipart Work identity must be manually
  reconciled before creating canonical Works.
- The zero-row Starfleet Academy response does **not** establish that the
  show has no episodes. It signals a gap in this query pattern, item modeling
  or Wikidata coverage, requiring different independently verified discovery.
- Wikidata structured data is available under CC0, but it is a secondary
  discovery catalog, not independent evidence of depicted events or dialogue.
  No transcript or narrative passages have been copied.
- The HTTP responses are not issuer-signed; receipts truthfully describe
  locally acquired bytes, not an independently authenticated source snapshot.
