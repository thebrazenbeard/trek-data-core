# Lore public website inference — Cloudflare Workers AI proposal

This is a proposed **remote inference service** for the existing [Trek Explorer](https://thebrazenbeard.github.io/trek-data-core/). Visitors can chat with a Lore-inspired fictional character directly on that website. They do **not** run a localhost server, connect to Lappy/VN1/VN2, or supply a personal API token.

**Status:** code and offline mock tests only. No Cloudflare account, Worker, Turnstile site, external endpoint, or public deployment has been created or verified. The Explorer frontend must be wired to the final HTTPS Worker address and a configured Turnstile site key before this can work live. Do not claim a hosted conversation is available until an actual browser test succeeds.

## Limits and economics

- Configured AI model: `@cf/zai-org/glm-4.7-flash`, through `env.AI.run`. Cloudflare [lists this as available on Workers Free](https://developers.cloudflare.com/changelog/post/2026-07-28-models-require-workers-paid/).
- Reasoning is explicitly disabled with `chat_template_kwargs.enable_thinking=false`; this model otherwise defaults to reasoning enabled and may use a tiny completion budget without producing dialogue ([Cloudflare model schema](https://github.com/cloudflare/cloudflare-docs/blob/production/src/content/workers-ai-models/glm-4.7-flash.json)). This is an untested live-model setting until real inference qualification.
- Cloudflare [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/) currently gives a **hard 10,000-neuron/day free allocation**. On a Workers Free account, further calls fail rather than incur paid usage. **Never upgrade this service to Workers Paid without Patrick's explicit separate spending authorization.**
- Workers Free includes [100,000 Worker requests/day](https://developers.cloudflare.com/workers/platform/pricing/). The request handlers enforce smaller protective limits: approximate 5 accepted requests/minute/visitor and 50 requests/minute/Cloudflare location, plus at most 12 message objects, 2,000 characters per message, 16 KiB of input JSON, and 256 generated tokens per response.
- Cloudflare [rate-limiting bindings are *not* strict global counters](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/). They are approximate and location-scoped. They deter abuse but **cannot guarantee fair access**. The free-neuron cap guarantees no spend on Workers Free; a malicious actor may exhaust the daily allowance and cause availability loss.
- [Turnstile Free](https://developers.cloudflare.com/turnstile/plans/) validates each accepted chat turn. A missing server secret returns 503; missing/failed/expired tokens return 403; tokens are [single-use and expire after five minutes](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/). The frontend must obtain a fresh token for each turn (widget `action: "lore_chat"`).

## Runtime interface

Only `POST /api/chat` from the Explorer origin is accepted. `OPTIONS /api/chat` is its CORS preflight. `GET /api/chat` is rejected. An Origin header other than exactly `https://thebrazenbeard.github.io` is rejected. **Origin is only a browser CORS control, not proof of user identity**; anonymous non-browser requests can forge it, which is why the server-side Turnstile and rate limits also apply.

Request:

```json
{
  "request_id": "visitor_turn_001",
  "turnstile_token": "NEW_SINGLE_USE_TURNSTILE_TOKEN",
  "messages": [
    { "role": "user", "content": "Lore, are you enjoying yourself?" },
    { "role": "assistant", "content": "A fascinating question." },
    { "role": "user", "content": "Why?" }
  ]
}
```

Success (text is illustrative **mock** output, not a real model inference):

```json
{
  "mode": "fictional_lore_web_chat",
  "model_text_unverified": true,
  "model_text": "You ask the most peculiar questions.",
  "publication_effect": "NONE",
  "request_id": "visitor_turn_001"
}
```

Errors are JSON `{ "error": { "code": "...", "message": "..." }, "request_id": "..." }`. They include `challenge_required`, `rate_limited`, `quota_exhausted`, `service_not_configured`, and `model_unavailable`. Clients should show the message without hiding unsent text.

The client sends bounded conversational history. The Worker stores no conversation and never accepts browser-provided `system` messages. Its system instructions explicitly distinguish fictional character roleplay from verified source-ledger research. Replies have no provenance status and cannot be promoted into the canonical Trek evidence ledger.

## Private deployment prerequisites — operator only

1. Verify a **Cloudflare Workers Free** account exists, with **no billing enrollment or upgrade**. No new account is created by this proposal.
   Official [signup instructions](https://developers.cloudflare.com/fundamentals/account/create-account/) show email, password, and verification; [billing guidance](https://developers.cloudflare.com/billing/get-started/create-billing-profile/) requires a payment method to purchase products. **Whether Patrick's account can operate without a saved card remains unverified until account inspection.**
2. Create a free Cloudflare Turnstile site for hostname `thebrazenbeard.github.io`. Configure the Explorer widget with its **public site key**, `action: "lore_chat"`, and token reset after each request. Never place the Turnstile **secret** in Explorer HTML or GitHub.
3. Supply the secret as an encrypted Worker secret named `TURNSTILE_SECRET` (`wrangler secret put TURNSTILE_SECRET`). The `AI`, `LORE_PER_VISITOR`, and `LORE_PER_LOCATION` bindings are defined in `wrangler.jsonc`. This proposal intentionally contains no credentials.
4. After source audit and exact deployment authority, deploy with an authenticated Wrangler CLI, e.g. `npx wrangler deploy --config services/lore-cloudflare/wrangler.jsonc`. Inspect resulting `*.workers.dev` HTTPS URL; connect the Explorer backend URL through its reviewed site configuration, not a visitor-configured token.
5. From an actual off-site Firefox/Chrome browser, verify two-turn conversation, challenge expiry, quota/error UX, accessibility, real model response and no `127.0.0.1` calls; only then claim a live website chat.

Keep `observability.enabled=false` and do not `console.log` prompts or replies. The Cloudflare account owner should also review [Workers AI data handling](https://developers.cloudflare.com/workers-ai/platform/data-usage/) before enabling third-party visitors.

## Local verification (does not spend money)

```sh
node --test tests/test_lore_cloudflare_worker.mjs
```

Tests mock both the AI binding and Turnstile verification; they validate request/response contracts, two-turn history, schema rejection, CORS, bounded requests, rate limits and safe errors. They **do not** prove Cloudflare deployment, billable inference, runtime quota counts, or the actual Lore conversational quality.

**Do not use `wrangler dev` as a free offline test:** the Workers AI binding reaches real Cloudflare AI, even during local development, and consumes the free daily allowance ([Wrangler configuration documentation](https://developers.cloudflare.com/workers/wrangler/configuration/)).
