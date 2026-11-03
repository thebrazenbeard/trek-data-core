import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

// Import from its actual module URL. A data: URL is not a valid origin for the
// pinned, relative, same-origin semantic-engine dependency.
const { mountLoreWebChat } = await import(new URL('../explorer/lore-public-chat.js', import.meta.url));
const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');

class Node {
  constructor(tag = 'div') {
    this.tagName = tag;
    this.children = [];
    this.listeners = new Map();
    this.dataset = {};
    this.textContent = '';
    this.value = '';
    this.hidden = false;
    this.disabled = false;
  }
  addEventListener(name, callback) {
    const handlers = this.listeners.get(name) || [];
    handlers.push(callback);
    this.listeners.set(name, handlers);
  }
  async fire(name, data = { preventDefault() {} }) {
    return Promise.all((this.listeners.get(name) || []).map((fn) => fn(data)));
  }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren() { this.children.length = 0; }
  focus() { this.focused = true; }
}

function fixture(endpoint) {
  const ids = [
    'lore-web-connect', 'lore-web-browser', 'lore-web-form', 'lore-web-input',
    'lore-web-send', 'lore-web-stop', 'lore-web-clear', 'lore-web-status',
    'lore-web-log', 'lore-web-mode', 'lore-web-challenge', 'lore-console', 'lore-close'
  ];
  const nodes = new Map(ids.map((id) => [id, new Node()]));
  const root = {
    baseURI: 'https://thebrazenbeard.github.io/trek-data-core/explorer/',
    getElementById: (id) => { assert.ok(nodes.has(id), `missing DOM node ${id}`); return nodes.get(id); },
    querySelector: (selector) => selector === 'meta[name="trek-lore-api"]' ? { content: endpoint }
      : selector === 'meta[name="trek-lore-turnstile-sitekey"]' ? { content: 'public-site-key' } : null,
    querySelectorAll: () => [],
    createElement: (tag) => new Node(tag)
  };
  return { root, nodes, get: (id) => nodes.get(`lore-web-${id}`) };
}

test('public page visibly prioritizes website chat without local token or local service setup', () => {
  const web = html.indexOf('id="lore-web-heading"');
  const legacy = html.indexOf('class="lore-legacy-options"');
  assert.ok(web > 0 && legacy > web, 'website chat must precede collapsed legacy UI');
  assert.match(html, /<details class="lore-legacy-options">/);
  assert.match(html, /Fictional, procedural dialogue/);
  assert.match(html, /<section id="lore-console"[^>]*>/);
  assert.doesNotMatch(html, /<section id="lore-console"[^>]*\shidden/);
  assert.match(html, /id="lore-web-send" type="submit">Transmit/);
  assert.match(html, /<meta name="trek-lore-api" content="">/);
  assert.match(html, /<meta name="trek-lore-turnstile-sitekey" content="">/);
  assert.match(html, /src="\.\/lore-public-chat\.js\?v=[a-f0-9]{64}"/);
  assert.doesNotMatch(html, /src="\.\/lore-web-model\.js\?v=/);
});

test('default Lore is immediately usable with no network request, token, model download or local service', async () => {
  const { root, get } = fixture('');
  const previousFetch = globalThis.fetch;
  const previousWindow = globalThis.window;
  const previousNavigator = globalThis.navigator;
  let fetchCalls = 0;
  globalThis.window = { addEventListener() {} };
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { gpu: null } });
  globalThis.fetch = async () => { fetchCalls += 1; throw new Error('No off-site transport allowed'); };
  try {
    const service = mountLoreWebChat(root);
    assert.equal(service.getMode(), 'semantic');
    assert.equal(get('send').disabled, false);
    assert.equal(get('log').children.length, 1, 'the page greets the visitor');
    get('input').value = 'What do you think of Data?';
    await get('form').fire('submit');
    assert.equal(get('log').children.length, 3);
    assert.equal(get('log').children[1].children[1].textContent, 'What do you think of Data?');
    assert.ok(get('log').children[2].children[1].textContent.length > 20);
    get('input').value = 'And what about that?';
    await get('form').fire('submit');
    assert.equal(get('log').children.length, 5);
    assert.equal(fetchCalls, 0);
    await get('clear').fire('click');
    assert.equal(get('log').children.length, 0);
    assert.equal(get('send').disabled, false);
  } finally {
    globalThis.fetch = previousFetch;
    globalThis.window = previousWindow;
    Object.defineProperty(globalThis, 'navigator', { configurable: true, value: previousNavigator });
  }
});

test('hosted Lore remains a separately opted-in optional bridge, never the default route', async () => {
  const { root, get } = fixture('https://lore.example.test/api/chat');
  const previousFetch = globalThis.fetch;
  const previousWindow = globalThis.window;
  const previousNavigator = globalThis.navigator;
  const seen = [];
  let verify;
  globalThis.window = { addEventListener() {}, turnstile: {
    render(_target, args) { verify = args.callback; verify('turnstile-verification-receipt'); return 1; },
    reset() { verify('turnstile-verification-receipt'); }
  } };
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { gpu: null } });
  globalThis.fetch = async (url, options) => {
    assert.equal(url, 'https://lore.example.test/api/chat');
    assert.equal(options.credentials, 'omit');
    assert.equal(options.mode, 'cors');
    assert.equal(options.redirect, 'error');
    assert.deepEqual(Object.keys(options.headers), ['Content-Type']);
    const request = JSON.parse(options.body);
    assert.equal(request.turnstile_token, 'turnstile-verification-receipt');
    seen.push(request.messages);
    return { ok: true, json: async () => ({
      mode: 'fictional_lore_web_chat', model_text_unverified: true,
      model_text: '<img src=x onerror=alert(1)> Fictional reply', publication_effect: 'NONE'
    }) };
  };
  try {
    mountLoreWebChat(root);
    assert.equal(seen.length, 0);
    assert.equal(get('send').disabled, false);
    assert.equal(get('log').children.length, 1);
    await get('connect').fire('click');
    assert.equal(get('send').disabled, false);
    assert.equal(seen.length, 0);
    get('input').value = 'Hello, Lore';
    await get('form').fire('submit');
    assert.deepEqual(seen[0], [{ role: 'user', content: 'Hello, Lore' }]);
    assert.equal(get('log').children.length, 3);
    assert.equal(get('log').children[2].children[1].textContent,
      '<img src=x onerror=alert(1)> Fictional reply');
    assert.equal(get('log').children[2].children[1].children.length, 0);
    get('input').value = 'What did I just say?';
    await get('form').fire('submit');
    assert.equal(seen[1].length, 3);
    assert.equal(seen[1][0].content, 'Hello, Lore');
    assert.equal(seen[1][1].role, 'assistant');
    assert.equal(seen[1][2].content, 'What did I just say?');
    assert.equal(get('log').children.length, 5);
  } finally {
    globalThis.fetch = previousFetch;
    globalThis.window = previousWindow;
    Object.defineProperty(globalThis, 'navigator', { configurable: true, value: previousNavigator });
  }
});

test('invalid or missing hosted endpoint never blocks default zero-setup Lore', () => {
  const previousWindow = globalThis.window;
  const previousNavigator = globalThis.navigator;
  globalThis.window = { addEventListener() {} };
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { gpu: null } });
  try {
    for (const endpoint of ['', 'http://lore.example.test/api/chat', 'https://user:password@lore.example.test/api/chat',
      'https://lore.example.test/api/chat?token=secret', 'https://lore.example.test/bad/path']) {
      const { root, get } = fixture(endpoint);
      const result = mountLoreWebChat(root);
      assert.equal(result.getMode(), 'semantic');
      assert.equal(get('connect').hidden, true, endpoint);
      assert.equal(get('send').disabled, false, endpoint);
      assert.match(get('status').textContent, /Channel open/);
    }
  } finally {
    globalThis.window = previousWindow;
    Object.defineProperty(globalThis, 'navigator', { configurable: true, value: previousNavigator });
  }
});

test('hosted failure never fabricates conversation, and permits retry without losing prompt', async () => {
  const previousWindow = globalThis.window;
  const previousNavigator = globalThis.navigator;
  const previousFetch = globalThis.fetch;
  let verify;
  globalThis.window = { addEventListener() {}, turnstile: {
    render(_target, args) { verify = args.callback; verify('turnstile-verification-receipt'); return 1; },
    reset() { verify('turnstile-verification-receipt'); }
  } };
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { gpu: null } });
  globalThis.fetch = async () => ({ ok: false, status: 429 });
  try {
    const { root, get } = fixture('https://lore.example.test/api/chat');
    mountLoreWebChat(root);
    await get('connect').fire('click');
    get('input').value = 'Test daily cap';
    await get('form').fire('submit');
    assert.equal(get('log').children.length, 1);
    assert.match(get('status').textContent, /free usage limit/);
    assert.equal(get('send').disabled, false);
    assert.equal(get('input').value, 'Test daily cap');
  } finally {
    globalThis.window = previousWindow;
    globalThis.fetch = previousFetch;
    Object.defineProperty(globalThis, 'navigator', { configurable: true, value: previousNavigator });
  }
});

test('hosted 403 exposes the verification failure without fabricating a Lore reply', async () => {
  const previousWindow = globalThis.window;
  const previousNavigator = globalThis.navigator;
  const previousFetch = globalThis.fetch;
  let verify;
  globalThis.window = { addEventListener() {}, turnstile: {
    render(_target, args) { verify = args.callback; verify('fresh-challenge'); return 1; },
    reset() { verify('fresh-challenge'); }
  } };
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { gpu: null } });
  globalThis.fetch = async () => ({ ok: false, status: 403 });
  try {
    const { root, get } = fixture('https://lore.example.test/api/chat');
    mountLoreWebChat(root);
    await get('connect').fire('click');
    get('input').value = 'Hello Lore';
    await get('form').fire('submit');
    assert.match(get('status').textContent, /visitor check/);
    assert.equal(get('log').children.length, 1);
    assert.equal(get('input').value, 'Hello Lore');
  } finally {
    globalThis.window = previousWindow;
    globalThis.fetch = previousFetch;
    Object.defineProperty(globalThis, 'navigator', { configurable: true, value: previousNavigator });
  }
});
