# Optional fictional Lore localhost companion (proposal)

This is an isolated, opt-in **local prototype**, not a public GitHub Pages or
Explorer integration, not an autonomous repository agent, and not evidence of
the fictional Lore's consciousness. All research identity remains **source
local**; the companion cannot admit Works, change corpus files, fetch artwork,
publish anything, or write to GitHub.

## Verified search boundary

- Uses the existing `tools/query_episode_source_cards.py` builder and exact
  accepted-byte sidecar comparison, with all original upstream validators and
  code-owned per-row SHA pins. It returns at most five PIC/SNW source-local
  publisher-guide records per request from a 20-record HELD shelf.
- `HELD_PUBLISHER_GUIDE_ONLY` means a bounded publisher card observation, **not**
  a full episode read, independently corroborated story event, released synopsis,
  global Work identity, or admitted coverage.
- Unmatched questions return zero rows, without consulting a model.
- A model, if separately and explicitly enabled, receives only bounded title,
  source status, source batch and SHA metadata. The server returns its generated
  text in `model_text` labeled `model_text_unverified`; authoritative source
  metadata and admission status come only from the validated lookup.

## Manual local operation

Only Python's standard library is needed; no weights or model are installed.

```bash
python tools/lore_local_companion.py
# Exit 2; DISABLED and no listener by default.

python tools/lore_local_companion.py --enable-local --port 9876
# Starts a local-only HTTP listener and prints an ephemeral CSRF token to that
# local terminal; do not paste or publish the token.
```

The only available route is `POST http://127.0.0.1:9876/api/query` with
`Content-Type: application/json`, a `Host: 127.0.0.1:9876` header,
`Origin: http://127.0.0.1:9876`, and the `X-Trek-Lore-CSRF` session token.
Body: `{"query":"Spock"}`. A minimal loopback-only manual call is:

```bash
curl --request POST 'http://127.0.0.1:9876/api/query' \
  --header 'Origin: http://127.0.0.1:9876' \
  --header 'Content-Type: application/json' \
  --header "X-Trek-Lore-CSRF: $TREK_LORE_CSRF_TOKEN" \
  --data '{"query":"Spock"}'
```

Copy the printed token to the `TREK_LORE_CSRF_TOKEN` environment variable in
your local shell only. This is a manual example, **not** a browser endpoint;
GitHub Pages cannot fetch it. The server deliberately refuses cross-origin
preflight requests and omits CORS headers. Other routes and HTTP methods are
not supported.

To *opt in* to a separately started OpenAI-chat-compatible local inference
server, add an explicit numeric-loopback `--model-url`, for example:

```bash
python tools/lore_local_companion.py --enable-local --port 9876 \
  --model-url http://127.0.0.1:9931/v1/chat/completions
```

The companion does **not** launch, download, update, or supervise that inference
server. It makes a bounded request only after a validated source result with
at least one matching source-local record. The model URL permits only HTTP to
literal `127.0.0.1`, on a different numeric port, at the exact chat-completions
path. HTTP redirects and proxies are disabled. The request contains no
functions, tools, files, repository credentials, or mutation capability.

## Known limitations and qualification gates

1. This is a search companion only. It does not support multi-turn memory,
   autonomous jobs, semantic reconciliation, corpus publication, or browsing
   beyond its pinned HELD shelf.
2. `model_text` is untrusted output. Any future UI must render it as text, never
   HTML, and must display provenance/status supplied by the deterministic
   wrapper rather than claims made by the model.
3. CSRF and strict Origin/Host checks reduce browser-to-localhost attack risk;
   they do not defend against malware or a malicious user process on the host.
4. No private machine paths, weights, credentials, inference outputs, transcripts,
   or ebooks should be committed to this repository. Keep access loopback-only.
5. Before a live opt-in UI, independently review the exact commit, run local
   security tests including request smuggling/redirect/fake status probes, test
   a real pre-existing model only with explicit host ownership, and verify model
   failure and contradictory-evidence handling. No public auto-connection from
   the static Explorer is authorized by this proposal.

```bash
python -m unittest tests.test_lore_local_companion -q
python -O -m unittest tests.test_lore_local_companion -q
```
