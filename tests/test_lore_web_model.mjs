import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import vm from 'node:vm';

const scriptPath = path.join(import.meta.dirname, '..', 'explorer', 'lore-web-model.js');
const source = fs.readFileSync(scriptPath, 'utf8');

function harness({webgpu = true, shaderF16 = true} = {}) {
  let imported = 0;
  let created = 0;
  let completionRequest = null;
  let unloaded = 0;
  const progress = [];
  const engine = {
    unload: async () => { unloaded++; },
    chat: {completions: {create: async (request) => {
      completionRequest = request;
      return (async function* () {
        yield {choices: [{delta: {content: 'Fascinating'}}]};
        yield {choices: [{delta: {content: ', Patrick.'}}]};
      })();
    }}},
  };
  const window = {
    __testImport: async () => {
      imported++;
      return {
        prebuiltAppConfig: {model_list: [
          {model_id: 'Qwen2.5-0.5B-Instruct-q4f16_1-MLC'},
          {model_id: 'Qwen2.5-0.5B-Instruct-q4f32_1-MLC'},
        ]},
        CreateMLCEngine: async (id, config) => {
          created++;
          config.initProgressCallback({text: 'Download', progress: 0.5});
          return engine;
        },
      };
    },
  };
  const gpu = webgpu ? {requestAdapter: async () => ({features: new Set(shaderF16 ? ['shader-f16'] : [])})} : undefined;
  const context = {window, navigator: {gpu}, DOMException, isSecureContext: true};
  // Only the ES module import is replaced in this deterministic, offline test.
  vm.runInNewContext(source.replace('await import(WEBLLM_ESM_URL)', 'await window.__testImport()'), context);
  return {
    client: window.LoreWebModel,
    stats: () => ({imported, created, unloaded, completionRequest, progress}),
    progress: (value) => progress.push(value),
  };
}

test('browser model import and weight loading are lazy; streaming is a real completion', async () => {
  const h = harness();
  assert.equal(h.stats().imported, 0);
  assert.equal(h.client.isReady(), false);
  const info = await h.client.load({onProgress: h.progress});
  assert.equal(info.model, 'Qwen2.5-0.5B-Instruct-q4f16_1-MLC');
  assert.equal(info.backend, 'webgpu-browser');
  assert.equal(h.stats().imported, 1);
  assert.equal(h.stats().created, 1);
  assert.equal(h.client.isReady(), true);
  await h.client.load();
  assert.equal(h.stats().imported, 1, 'cached engine is reused');
  assert.ok(h.stats().progress.some((line) => line.includes('50%')));
  const chunks = [];
  const reply = await h.client.generate({
    messages: [
      {role: 'system', content: 'You are Lore.'},
      {role: 'user', content: 'Remember TAU-42.'},
      {role: 'assistant', content: 'I shall.'},
      {role: 'user', content: 'What was our phrase?'},
    ],
    onToken: (fragment, full) => chunks.push([fragment, full]),
  });
  assert.equal(reply, 'Fascinating, Patrick.');
  assert.deepEqual(chunks, [
    ['Fascinating', 'Fascinating'],
    [', Patrick.', 'Fascinating, Patrick.'],
  ]);
  assert.equal(h.stats().completionRequest.messages.length, 4);
  assert.equal(h.stats().completionRequest.stream, true);
});

test('WebGPU-disabled clients receive a truthful refusal without package download', async () => {
  const h = harness({webgpu: false});
  await assert.rejects(() => h.client.load(), /WebGPU/);
  assert.equal(h.stats().imported, 0);
});

test('fallback selects non-f16 weights when GPU shader-f16 is unavailable', async () => {
  const h = harness({shaderF16: false});
  const info = await h.client.load();
  assert.equal(info.model, 'Qwen2.5-0.5B-Instruct-q4f32_1-MLC');
});

test('cancellation after a pending model load frees GPU memory', async () => {
  const h = harness();
  const controller = new AbortController();
  await assert.rejects(() => h.client.load({
    signal: controller.signal,
    onProgress: (message) => {
      if (message.includes('50%')) controller.abort();
    },
  }), {name: 'AbortError'});
  assert.equal(h.client.isReady(), false);
  assert.equal(h.stats().unloaded, 1);
});

test('invalid messages fail closed, no invented response', async () => {
  const h = harness();
  await h.client.load();
  await assert.rejects(() => h.client.generate({messages: []}), /required/);
  await assert.rejects(() => h.client.generate({messages: [{role: 'arbitrary', content: 'No.'}]}), /Invalid/);
  assert.equal(h.stats().completionRequest, null);
});

test('large histories retain the system boundary and recent turns only', async () => {
  const h = harness();
  await h.client.load();
  const messages = [
    {role: 'system', content: 'Stable system instruction.'},
    ...Array.from({length: 30}, (_, i) => ({
      role: i % 2 ? 'assistant' : 'user',
      content: `Turn ${i}: ${'x'.repeat(2000)}`,
    })),
  ];
  await h.client.generate({messages});
  const passed = h.stats().completionRequest.messages;
  assert.equal(passed[0].role, 'system');
  assert.equal(passed[0].content, 'Stable system instruction.');
  assert.equal(passed.length, 12);
  assert.equal(passed.at(-1).content.startsWith('Turn 29:'), true);
  assert.ok(passed.every((item) => item.content.length <= 1200));
});
