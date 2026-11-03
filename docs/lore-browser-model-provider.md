# Lore browser-model fallback (proposal)

**Status:** source implementation and offline mock tests only; **not verified as a
successful actual WebGPU model load on the deployed GitHub Pages Explorer**.
No site deployment or private host exposure is implied.

`explorer/lore-web-model.js` offers an opt-in, visitor-side text-generation model.
It does not rely on localhost, a secret token, Cloudflare account, or a site-hosted
inference server. It also does **not** run in every browser: WebGPU hardware/browser
support is an explicit gate. It is appropriate as a fallback to a genuinely
site-hosted endpoint, not as the only way to talk to Lore from arbitrary devices.

The provider sets `window.LoreWebModel` when the local script is loaded. Its API:

```js
await LoreWebModel.load({onProgress: (message) => {}, signal});
const completedText = await LoreWebModel.generate({
  messages: [
    {role: 'system', content: 'You are a fictional Lore portrayal.'},
    {role: 'user', content: 'Are you there?'},
  ],
  onToken: (delta, completeTextSoFar) => {},
  signal,
});
```

- The engine and model import only after `load()` is invoked. First download
  can approach 1 GB for the documented Qwen2.5-0.5B prebuilt variants.
- Model: `Qwen2.5-0.5B-Instruct-q4f16_1-MLC` with shader-f16 support, otherwise
  `Qwen2.5-0.5B-Instruct-q4f32_1-MLC`. Browser GPU and available RAM can still
  prevent model loading. Supports multi-turn chat history and streaming.
- Browser performs downloads from third-party WebLLM/npm and Hugging Face
  infrastructure. Those are network requests, not messages sent to an LLM API.
- The website's CSP must expressly admit the pinned `cdn.jsdelivr.net` module and WebLLM
  model distribution endpoints and allow WebAssembly initialization. The website
  must not suggest a server-hosted exchange or universal compatibility.
- Model replies are fictional simulation and unverified. No answer promotes
  private/held evidence or source-local discovery into accepted canonical truth.
- Tests: `node --test tests/test_lore_web_model.mjs`. These mock model creation,
  GPU detection, and streaming; they **do not** prove the upstream model can
  actually initialize or answer in a real browser.

## Source and license context

- [WebLLM](https://github.com/mlc-ai/web-llm), Apache-2.0, documents in-browser
  WebGPU inference, CDN loading, and streamed OpenAI-style completions.
- [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct),
  Apache-2.0 according to the model publisher's model card.
- [MLC q4f32 prebuilt weights](https://huggingface.co/mlc-ai/Qwen2.5-0.5B-Instruct-q4f32_1-MLC).

These are dependency/source locators, not independent Trek research evidence.
