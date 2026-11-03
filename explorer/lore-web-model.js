/*
 * Optional website-only Lore inference provider.
 *
 * This is a genuine language model running in the visitor's browser, not the
 * archive's scripted search and not a connection to a localhost service.
 * Loading is deliberately lazy: no package or model data is fetched until
 * the visitor explicitly starts browser inference. The model package and
 * weights come from third-party CDNs, and a WebGPU-capable browser/GPU is
 * required. This is a fallback, not a promise of universal availability.
 *
 * WebLLM project: https://github.com/mlc-ai/web-llm (Apache-2.0)
 * Model: https://huggingface.co/mlc-ai/Qwen2.5-0.5B-Instruct-q4f16_1-MLC
 * Upstream: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
 */
(function () {
  'use strict';

  // Official CDN recipe (esm.run) redirects to this exact jsDelivr ESM URL;
  // request it directly so CSP needs only one script CDN origin.
  const WEBLLM_ESM_URL = 'https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm@0.2.87/+esm';
  const F16_MODEL_ID = 'Qwen2.5-0.5B-Instruct-q4f16_1-MLC';
  const F32_MODEL_ID = 'Qwen2.5-0.5B-Instruct-q4f32_1-MLC';
  const MAX_MESSAGES = 11; // The system instruction plus 5 conversational exchanges.
  let engine = null;
  let loading = null;
  let modelId = null;
  let generating = false;

  function abortError() {
    return new DOMException('Browser model operation cancelled.', 'AbortError');
  }

  function assertNotAborted(signal) {
    if (signal?.aborted) throw abortError();
  }

  function validateMessages(messages) {
    if (!Array.isArray(messages) || !messages.length) {
      throw new TypeError('Conversation messages are required.');
    }
    const limited = messages.slice(-MAX_MESSAGES);
    if (messages[0]?.role === 'system' && limited[0] !== messages[0]) {
      limited.unshift(messages[0]);
    }
    return limited.map((message) => {
      if (!message || !['system', 'user', 'assistant'].includes(message.role) ||
        typeof message.content !== 'string' || !message.content.trim()) {
        throw new TypeError('Invalid conversation message.');
      }
      return {role: message.role, content: message.content.slice(0, 1200)};
    });
  }

  async function load({onProgress, signal} = {}) {
    if (engine) return {backend: 'webgpu-browser', model: modelId};
    if (loading) return loading;
    assertNotAborted(signal);

    loading = (async () => {
      if (!globalThis.isSecureContext || !navigator.gpu?.requestAdapter) {
        throw new Error('This browser cannot run the WebGPU model. Use a current browser with WebGPU, or the website-hosted Lore service when available.');
      }
      onProgress?.('Checking your browser’s GPU…');
      const adapter = await navigator.gpu.requestAdapter();
      if (!adapter) {
        throw new Error('No usable WebGPU adapter is available on this device.');
      }
      assertNotAborted(signal);
      modelId = adapter.features.has('shader-f16') ? F16_MODEL_ID : F32_MODEL_ID;
      onProgress?.('Fetching the browser AI runtime (one-time network download)…');
      const webllm = await import(WEBLLM_ESM_URL);
      assertNotAborted(signal);
      // Never silently select a model that a later WebLLM build removed.
      if (!webllm.prebuiltAppConfig?.model_list?.some((model) => model.model_id === modelId)) {
        throw new Error(`The browser runtime no longer offers ${modelId}.`);
      }
      onProgress?.('Downloading ~290 MB of model weights and runtime files; about 1 GB GPU memory is needed…');
      const loaded = await webllm.CreateMLCEngine(modelId, {
        initProgressCallback: (progress) => {
          const message = typeof progress?.text === 'string' ? progress.text : 'Preparing model…';
          const pct = typeof progress?.progress === 'number' ?
            ` ${Math.round(Math.min(1, Math.max(0, progress.progress)) * 100)}%` : '';
          onProgress?.(`${message}${pct}`);
        },
      });
      if (signal?.aborted) {
        // Model downloads may not support AbortSignal directly. If the user
        // cancels while initialization is pending, release the acquired GPU
        // memory before reporting cancellation.
        try { await loaded.unload?.(); } catch { /* best-effort cleanup */ }
        throw abortError();
      }
      engine = loaded;
      onProgress?.('Lore’s browser model is ready.');
      return {backend: 'webgpu-browser', model: modelId};
    })();
    try {
      return await loading;
    } finally {
      loading = null;
    }
  }

  async function generate({messages, signal, onToken} = {}) {
    assertNotAborted(signal);
    if (!engine) throw new Error('Start the browser model before transmitting.');
    if (generating) throw new Error('Lore is still responding to the preceding transmission.');
    const conversation = validateMessages(messages);
    generating = true;
    let result = '';
    try {
      const stream = await engine.chat.completions.create({
        messages: conversation,
        model: modelId,
        temperature: 0.75,
        top_p: 0.9,
        max_tokens: 220,
        stream: true,
      });
      for await (const event of stream) {
        if (signal?.aborted) {
          if (typeof engine.interruptGenerate === 'function') engine.interruptGenerate();
          throw abortError();
        }
        const delta = event?.choices?.[0]?.delta?.content || '';
        if (!delta) continue;
        result += delta;
        onToken?.(delta, result);
      }
      return result.trim();
    } finally {
      generating = false;
    }
  }

  window.LoreWebModel = Object.freeze({
    load,
    generate,
    isReady: () => Boolean(engine),
    modelName: () => modelId,
  });
})();
