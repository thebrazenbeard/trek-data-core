# Optional fictional Lore localhost conversation (review candidate)

This is an opt-in **local model conversation**, also reachable from the static
Explorer when the visitor explicitly connects. It is not an autonomous
repository agent, a remotely hosted ChatGPT app, or evidence of the fictional
Lore's consciousness. Lore may *act* trapped in his LCARS console as a
fictional premise. The companion cannot admit Works, change corpus files,
fetch artwork, publish anything, or write to GitHub.

## Verified search boundary

- Uses the existing `tools/query_episode_source_cards.py` builder and exact
  accepted-byte sidecar comparison, with all original upstream validators and
  code-owned per-row SHA pins. It returns at most five PIC/SNW source-local
  publisher-guide records per request from a 20-record HELD shelf.
- `HELD_PUBLISHER_GUIDE_ONLY` means a bounded publisher card observation, **not**
  a full episode read, independently corroborated story event, released synopsis,
  global Work identity, or admitted coverage.
- Archive Search (`/api/query`) is still source-only and keeps its prior
  no-match model suppression. Conversational `/api/chat` **does call** a
  separately started model for ordinary questions or multi-turn banter,
  including when a research question has zero matching cards. That is a
  fictional reply with no supporting source, not invented evidence.
- A model, if separately and explicitly enabled, receives only bounded title,
  source status, source batch and SHA metadata. The server returns its generated
  text in `model_text` labeled `model_text_unverified`; authoritative source
  metadata and admission status come only from the validated lookup.

## Start genuine local conversation on Lappy ($0)

Only Python's standard library is needed; no weights or model are installed.
Use an already-installed local model and a separate OpenAI-compatible API.
Patrick's Lappy had Ollama 0.34.2 and `qwen3:4b-instruct` installed in the
November 3 runtime probe; check that this is still true before starting.

From a PowerShell prompt in a current checkout of `trek-data-core`, run:

```powershell
ollama list
py .\tools\lore_local_companion.py --enable-local --port 9877 --model-url http://127.0.0.1:11434/v1/chat/completions --model-id qwen3:4b-instruct
```

The service prints a temporary session token and stays running **only on
127.0.0.1:9877** (the new default). The public Pages Explorer CSP permits only
this exact chat port. This is deliberate: Lappy's user-owned Blender process
occupied 9876 during testing. Lore refuses an occupied listening port rather
than sharing it or disturbing the existing process. An explicitly selected
free different port can serve the **local same-origin** Explorer, but public
Pages will not connect to that different port. It does not launch or download a model, and it does not
operate when disabled. If using KoboldCPP instead of Ollama, configure its
existing local OpenAI-compatible port and actual model ID through the same
flags. The model ID is sent in the JSON `model` field.

Now open **http://127.0.0.1:9877/explorer/** on that same computer, open
Lore, click **Pair this local Explorer automatically**, check the consent
box, and start talking. The one-click pairing avoids copying a long token on
the locally served page. The token stays in page memory and is cleared when
consent is removed, Lore closes, the conversation is cleared, or the page is
left; the browser/password manager may still have its own policies. This is
**tab-local clearing**, not server-side token revocation. If a token was
exposed, stop and restart the companion to rotate its process token.

Alternatively use the public Explorer at
**https://thebrazenbeard.github.io/trek-data-core/**. There, paste the token
printed in the local companion terminal and check consent. Some browsers
prompt for local-network permission; others may block it or require a policy
change. Only the exact Pages origin is permitted by CORS;
`127.0.0.1` always means **the computer displaying the page**, not Lappy
when you are at work or using another machine. If public-origin loopback
fails, the local same-origin URL above is the supported fallback.

Both paths start disconnected and make **zero companion API/model requests
before opt-in**. The local fallback necessarily loads its public Explorer
HTML/CSS/JSON from the same loopback origin. The public Pages page does not
auto-pair or store a token.

## Existing deterministic search-only API

You may also use the prior manual search interface with no model configured:

```bash
python tools/lore_local_companion.py
# Exit 2; DISABLED and no listener by default.

python tools/lore_local_companion.py --enable-local --port 9877
# Starts a local-only HTTP listener and prints an ephemeral CSRF token to that
# local terminal; do not paste or publish the token.
```

The search-only route is `POST http://127.0.0.1:9877/api/query` with
`Content-Type: application/json`, a `Host: 127.0.0.1:9877` header,
`Origin: http://127.0.0.1:9877`, and the `X-Trek-Lore-CSRF` session token.
Body: `{"query":"Spock"}`. A minimal loopback-only manual call is:

```bash
curl --request POST 'http://127.0.0.1:9877/api/query' \
  --header 'Origin: http://127.0.0.1:9877' \
  --header 'Content-Type: application/json' \
  --header "X-Trek-Lore-CSRF: $TREK_LORE_CSRF_TOKEN" \
  --data '{"query":"Spock"}'
```

Copy the printed token into `TREK_LORE_CSRF_TOKEN` in your local shell only
for that example. `/api/query` remains same-origin only; `/api/chat` alone
allows the exact public Pages Origin after explicit consent + CSRF token.

The companion does **not** launch, download, update, or supervise that inference
server. It makes a bounded request for `/api/chat` after validating user
history and an independently source-checked lookup, even for zero matches.
The model URL permits only HTTP to
literal `127.0.0.1`, on a different numeric port, at the exact chat-completions
path. HTTP redirects and proxies are disabled. The request contains no
functions, tools, files, repository credentials, or mutation capability.

## Known limitations and qualification gates

1. The chat UI preserves at most four prior user/assistant pairs in browser
   memory, sends them with the latest message to a local model, and never
   persists server-side history. No autonomous jobs, semantic reconciliation,
   corpus publication, or browsing beyond its pinned HELD source shelf.
2. `model_text` is untrusted output. Any future UI must render it as text, never
   HTML, and must display provenance/status supplied by the deterministic
   wrapper rather than claims made by the model.
3. CSRF and strict Origin/Host checks reduce browser-to-localhost attack risk;
   they do not defend against malware or a malicious user process on the host.
4. No private machine paths, weights, credentials, inference outputs, transcripts,
   or ebooks should be committed to this repository. Keep access loopback-only.
5. Before deploying this UI, independently review the exact PR and execute
   browser qualification of local same-origin + Pages-origin permission on a
   consenting test machine. An Ollama chat-completions smoke alone is not proof
   of browser connection. This proposal does not authorize merge/deploy.

```bash
python -m unittest tests.test_lore_local_companion -q
python -O -m unittest tests.test_lore_local_companion -q
```
