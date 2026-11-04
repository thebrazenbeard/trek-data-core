import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash, webcrypto } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { initHeldPublisherPreview, validateHeldPublisherPreview } from '../proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.mjs';

class FakeNode {
  constructor(tag = 'div') {
    this.tagName = tag;
    this.children = [];
    this.listeners = new Map();
    this.hidden = false;
    this.textContent = '';
    this.disabled = false;
    this.attributes = {};
  }
  addEventListener(type, callback) { this.listeners.set(type, callback); }
  fire(type) { return this.listeners.get(type)?.({ preventDefault() {} }); }
  replaceChildren(...nodes) { this.children = [...nodes]; }
  append(...nodes) { this.children.push(...nodes); }
  setAttribute(name, value) { this.attributes[name] = String(value); }
}

function realFixture() {
  return JSON.parse(readFileSync(new URL('../proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.json', import.meta.url)));
}

async function setup(payload = realFixture(), override = {}) {
  const names = ['held-preview-open', 'held-preview-state', 'held-preview-count', 'held-preview-list', 'held-preview-reset'];
  const nodes = new Map(names.map(name => [name, new FakeNode()]));
  const document = {
    getElementById: id => nodes.get(id),
    createElement: tag => new FakeNode(tag),
  };
  const bytes = new TextEncoder().encode(JSON.stringify(payload));
  const digest = await webcrypto.subtle.digest('SHA-256', bytes);
  const sha256 = Buffer.from(digest).toString('hex');
  const calls = [];
  const fetchImpl = async (path, init) => {
    calls.push({ path, init });
    return { ok: true, arrayBuffer: async () => bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) };
  };
  initHeldPublisherPreview({ document, fetchImpl: override.fetchImpl ?? fetchImpl,
    cryptoSubtle: webcrypto.subtle, expectedSha256: override.expectedSha256 ?? sha256 });
  return { nodes, calls, bytes };
}

test('HELD preview has no automatic fetch, then opt-in reveals 10 explicitly non-admitted editions', async () => {
  const { nodes, calls } = await setup();
  assert.equal(calls.length, 0, 'no requests before explicit opt-in');
  assert.equal(nodes.get('held-preview-list').children.length, 0);
  await nodes.get('held-preview-open').fire('click');
  assert.equal(calls.length, 1);
  assert.equal(calls[0].path, './held-publisher-preview.json');
  assert.equal(nodes.get('held-preview-count').textContent,
    '10 HELD publisher edition metadata leads (2 publisher source families; 0 Work admissions from this preview)');
  assert.equal(nodes.get('held-preview-list').children.length, 10);
  assert.match(nodes.get('held-preview-state').textContent, /not accepted|HELD/i);
  assert.equal(nodes.get('held-preview-list').children[0].tagName, 'article');
  assert.ok(nodes.get('held-preview-list').children[0].children[0].children.some(child =>
    child.textContent.includes('No Work admission from this edition')));
  assert.ok(nodes.get('held-preview-list').children.every(card => card.children.every(child => child.tagName !== 'img')));
  nodes.get('held-preview-reset').fire('click');
  assert.equal(nodes.get('held-preview-list').children.length, 0);
  assert.equal(nodes.get('held-preview-count').textContent, '—');
});

test('missing or SHA-tampered preview fails closed with no cards or counts', async () => {
  const { nodes } = await setup(realFixture(), { expectedSha256: '0'.repeat(64) });
  await nodes.get('held-preview-open').fire('click');
  assert.equal(nodes.get('held-preview-count').textContent, '—');
  assert.equal(nodes.get('held-preview-list').children.length, 0);
  assert.match(nodes.get('held-preview-state').textContent, /withheld|unavailable|failed/i);
});

test('even rehashed false admission claims cannot appear as HELD cards', async () => {
  const promoted = realFixture();
  promoted.rows[0].admission_effect = 'ADMITTED';
  const { nodes } = await setup(promoted);
  await nodes.get('held-preview-open').fire('click');
  assert.equal(nodes.get('held-preview-list').children.length, 0);
  assert.equal(nodes.get('held-preview-count').textContent, '—');
});

test('even with rehashed JSON, a same-publisher wrong edition URL or forged title fails closed', async () => {
  const swapped = realFixture();
  swapped.rows[0].source_url = swapped.rows[1].source_url;
  const first = await setup(swapped);
  await first.nodes.get('held-preview-open').fire('click');
  assert.equal(first.nodes.get('held-preview-list').children.length, 0, 'must reject a URL for another ISBN');

  const forged = realFixture();
  forged.rows[0].title = 'A fabricated title at a real publisher locator';
  const second = await setup(forged);
  await second.nodes.get('held-preview-open').fire('click');
  assert.equal(second.nodes.get('held-preview-list').children.length, 0, 'must reject a title not in reviewed source metadata');
});

test('rehashed malformed dates, negative extents and misplaced author anomaly fail closed', async () => {
  const mutations = [
    row => { row.publisher_date_us = '2099-99-99'; },
    row => { row.publisher_date_us = '<img src=x onerror=alert(1)>'; },
    row => { row.publisher_extent_pages = -4; },
    row => { row.source_anomaly = 'AUTHOR_HEADER_JERI_VS_DESCRIPTION_TERI_UNRESOLVED'; },
  ];
  for (const mutate of mutations) {
    const forged = realFixture();
    mutate(forged.rows[0]); // The Lives Of Dax is not the anomalous Unification edition.
    const { nodes } = await setup(forged); // Rehashed to simulate an unsafe repin.
    await nodes.get('held-preview-open').fire('click');
    assert.equal(nodes.get('held-preview-list').children.length, 0,
      'a changed source-local edition metadata field must withhold every card');
    assert.equal(nodes.get('held-preview-count').textContent, '—');
  }
});

test('source-family copy does not become extra corroboration through rehashed labels', async () => {
  const falseFamilies = realFixture();
  falseFamilies.source_family_count = 10;
  const one = await setup(falseFamilies);
  await one.nodes.get('held-preview-open').fire('click');
  assert.equal(one.nodes.get('held-preview-list').children.length, 0);

  const reassigned = realFixture();
  reassigned.rows[0].source_family = 'publisher:titanbooks.com';
  const two = await setup(reassigned);
  await two.nodes.get('held-preview-open').fire('click');
  assert.equal(two.nodes.get('held-preview-list').children.length, 0);

  const exact = realFixture();
  assert.deepEqual([...new Set(exact.rows.map(row => row.source_family))].sort(),
    ['publisher:simonandschuster.com', 'publisher:titanbooks.com']);
});

test('preview page is isolated from main Explorer and contains no remote image autoload', () => {
  const html = readFileSync(new URL('../proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.html', import.meta.url), 'utf8');
  assert.match(html, /id="held-preview-open"/);
  assert.match(html, /id="held-preview-list"/);
  assert.doesNotMatch(html, /<img\b|http-equiv="refresh"|src="https?:/i);
  const mainApp = readFileSync(new URL('../explorer/app.js', import.meta.url), 'utf8');
  assert.doesNotMatch(mainApp, /held-publisher-preview\.json/);
  const script = readFileSync(new URL('../proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.mjs', import.meta.url), 'utf8');
  assert.doesNotMatch(script, /innerHTML|outerHTML|insertAdjacentHTML|document\.write|createElement\(['"]img['"]\)/);
  assert.match(script, /credentials: 'omit'/);
  assert.doesNotMatch(script, /fetchImpl\(['"]https?:/);
  assert.match(html, /img-src 'none'/);
  assert.match(html, /connect-src 'self'/);
});

test('HELD draft HTML and data are outside the strict Pages artifact upload root', () => {
  const workflow = readFileSync(new URL('../.github/workflows/static.yml', import.meta.url), 'utf8');
  assert.match(workflow, /Upload Explorer only/);
  assert.match(workflow, /path: explorer\b/);
  assert.match(workflow, /find explorer -mindepth 1/);
  assert.doesNotMatch(workflow, /held-publisher-preview|proposals\/consolidator/);
  assert.doesNotMatch(readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8'), /held-publisher-preview/);
});

test('preview JSON/source script/CSS fingerprints match reviewed bytes, and real edition data validates', () => {
  const html = readFileSync(new URL('../proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.html', import.meta.url), 'utf8');
  const js = readFileSync(new URL('../proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.mjs', import.meta.url), 'utf8');
  const json = readFileSync(new URL('../proposals/consolidator/held-publisher-ui-preview-20261104/held-publisher-preview.json', import.meta.url));
  const css = readFileSync(new URL('../explorer/app.css', import.meta.url));
  const jsSha = createHash('sha256').update(js).digest('hex');
  const jsonSha = createHash('sha256').update(json).digest('hex');
  const cssSha = createHash('sha256').update(css).digest('hex');
  assert.ok(html.includes(`held-publisher-preview.mjs?v=${jsSha}`));
  assert.ok(html.includes(`../../../explorer/app.css?v=${cssSha}`));
  assert.ok(js.includes(`const PREVIEW_SHA256 = '${jsonSha}';`));
  assert.equal(validateHeldPublisherPreview(JSON.parse(json)).length, 10);
});
