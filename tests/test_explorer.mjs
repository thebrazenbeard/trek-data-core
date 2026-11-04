import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';
import { webcrypto, createHash } from 'node:crypto';

const SCRIPT = readFileSync(new URL('../explorer/app.js', import.meta.url), 'utf8');
const IDS = ['search-input', 'scope-filter', 'mission-filter', 'kind-filter', 'status-filter',
  'explorer-navigation', 'navigation-scroll-hint', 'navigation-scroll-controls', 'navigation-scroll-previous', 'navigation-scroll-next',
  'filters', 'data-state', 'mission-count', 'briefing-count', 'record-count', 'research-top-count', 'research-nav-count', 'film-top-count', 'film-nav-count', 'film-state', 'film-list', 'film-query', 'film-filters', 'film-summary', 'beyond-premiere-panel', 'beyond-premiere-toggle', 'beyond-premiere-status', 'beyond-premiere-image', 'beyond-premiere-credit', 'discovery-nav-count', 'discovery-top-count', 'discovery-episode-count', 'discovery-literature-count', 'discovery-state', 'discovery-metrics', 'discovery-list', 'discovery-query', 'discovery-medium', 'discovery-series', 'discovery-kind', 'discovery-lineage', 'discovery-overview', 'discovery-verification', 'discovery-publisher-check', 'publisher-card-state', 'publisher-card-download', 'discovery-synopsis', 'discovery-tag', 'discovery-filters', 'discovery-summary', 'discovery-empty', 'notice',
  'mission-list', 'briefing-list', 'record-list', 'mission-empty', 'briefing-empty',
  'record-empty', 'missions', 'briefings', 'records', 'result-summary', 'search-heading',
  'research-query', 'research-mission', 'research-reset', 'research-filters', 'research-count',
  'research-state', 'research-list', 'research-empty', 'research-summary', 'tone-toggle',
  'lore-toggle', 'lore-console', 'lore-close', 'lore-form', 'lore-query', 'lore-answer',
  'lore-chat-form', 'lore-chat-token', 'lore-chat-pair', 'lore-chat-consent', 'lore-chat-input',
  'lore-chat-send', 'lore-chat-clear', 'lore-chat-status', 'lore-chat-log',
  'discovery-directory', 'episode-source-cards',
  'artwork-toggle', 'artwork-state', 'artwork-gallery', 'artwork-gallery-summary',
  'artwork-nav-link', 'artwork-nav-count', 'artwork-gallery-list', 'publisher-edition-nav-count', 'publisher-edition-state',
  'publisher-edition-query', 'publisher-edition-tag', 'publisher-edition-filters',
  'publisher-edition-summary', 'publisher-edition-list', 'publisher-edition-empty',
  'publisher-isbn-nav-count', 'publisher-isbn-state', 'publisher-isbn-download',
  'publisher-isbn-query', 'publisher-isbn-status', 'publisher-isbn-tag',
  'publisher-isbn-filters', 'publisher-isbn-summary', 'publisher-isbn-list', 'publisher-isbn-empty',
  'paramount-nav-count', 'paramount-state', 'paramount-download', 'paramount-query',
  'paramount-status', 'paramount-tag', 'paramount-filters', 'paramount-summary',
  'paramount-list', 'paramount-empty', 'paramount-chronology', 'paramount-chronology-list',
  'episode-source-nav-count', 'episode-source-state',
  'episode-source-download', 'episode-source-query', 'episode-source-series',
  'episode-source-status', 'episode-source-tag', 'episode-source-filters',
  'episode-source-summary', 'episode-source-list', 'episode-source-empty',
  'owner-opf-file', 'owner-opf-query', 'owner-opf-clear', 'owner-opf-more',
  'owner-opf-state', 'owner-opf-summary', 'owner-opf-list', 'owner-opf-empty'];

class FakeNode {
  constructor(tag = 'div') {
    this.tagName = tag;
    this.children = [];
    this.handlers = new Map();
    this.attributes = new Map();
    this._text = '';
    this.value = '';
    this.hidden = false;
    this.className = '';
    this.focused = false;
    this.parentNode = null;
    this._documentRoot = false;
    this.dataset = {};
  }

  get isConnected() { return this._documentRoot || Boolean(this.parentNode?.isConnected); }
  contains(node) { return this === node || this.children.some((child) => child.contains(node)); }
  set textContent(value) {
    for (const child of this.children) child.parentNode = null;
    this._text = String(value);
    this.children = [];
  }
  get textContent() { return this._text + this.children.map((child) => child.textContent).join(''); }
  set innerHTML(_) { throw Error('HTML injection sink is forbidden'); }
  set outerHTML(_) { throw Error('HTML injection sink is forbidden'); }
  setAttribute(key, value) { this.attributes.set(key, String(value)); }
  getAttribute(key) { return this.attributes.get(key) || null; }
  removeAttribute(key) { this.attributes.delete(key); }
  append(...children) {
    for (const child of children) {
      if (child.tagName === '#fragment') {
        for (const grandchild of child.children) {
          grandchild.parentNode = this;
          this.children.push(grandchild);
        }
        child.children = [];
      } else {
        child.parentNode = this;
        this.children.push(child);
      }
    }
  }
  replaceChildren(...children) {
    for (const child of this.children) child.parentNode = null;
    this.children = [];
    this._text = '';
    this.append(...children);
  }
  add(option) { this.children.push(option); }
  addEventListener(type, listener) {
    const list = this.handlers.get(type) || [];
    list.push(listener);
    this.handlers.set(type, list);
  }
  scrollTo({ left }) {
    this.scrollLeft = left;
    this.fire('scroll');
  }
  fire(type, event) { return Promise.all((this.handlers.get(type) || []).map((listener) => listener(event))); }
  scrollIntoView() {}
  focus() { this.focused = true; }
}

function traverse(node, predicate) {
  const found = predicate(node) ? [node] : [];
  for (const child of node.children) found.push(...traverse(child, predicate));
  return found;
}

async function runWithIndex(index, status = 200, research = null, researchStatus = 404, browserAudio = {}, films = null, filmStatus = 404, directory = null, directoryStatus = 404, artwork = null, artworkStatus = 404, synopsis = null, synopsisStatus = 404, appScript = SCRIPT, metadataBytes = null, metadataStatus = 404, shortBytes = null, shortStatus = 404, rejectDigest = false, publisherBytes = null, publisherStatus = 404, sourceCardBytes = null, sourceCardStatus = 404, isbnBytes = null, isbnStatus = 404, paramountBytes = null, paramountStatus = 404, episodeBytes = null, episodeStatus = 404, mediumArtwork = null, mediumStatus = 404, premiereBytes = null, premiereStatus = 404, decisionBytes = null, decisionStatus = 404, chatBackend = null, picardBytes = null, picardStatus = 404) {
  const nodes = new Map(IDS.map((id) => [id, new FakeNode()]));
  for (const node of nodes.values()) node._documentRoot = true;
  const requested = new Set();
  const chatRequests = [];
  nodes.chatRequests = chatRequests;
  const inFlightDigests = new Set();
  nodes.get('lore-console').hidden = true;
  nodes.get('navigation-scroll-hint').hidden = true;
  nodes.get('scope-filter').value = 'all';
  nodes.get('mission-filter').value = 'all';
  nodes.get('kind-filter').value = 'all';
  nodes.get('status-filter').value = 'all';
  nodes.get('research-mission').value = 'all';
  nodes.get('discovery-medium').value = 'all';
  nodes.get('discovery-series').value = 'all';
  nodes.get('discovery-kind').value = 'all';
  nodes.get('discovery-lineage').value = 'all';
  nodes.get('discovery-overview').value = 'all';
  nodes.get('discovery-verification').value = 'all';
  nodes.get('discovery-publisher-check').value = 'all';
  nodes.get('discovery-synopsis').value = 'all';
  nodes.get('discovery-tag').value = 'all';
  nodes.get('publisher-edition-tag').value = 'all';
  nodes.get('publisher-isbn-status').value = 'all';
  nodes.get('publisher-isbn-tag').value = 'all';
  nodes.get('paramount-status').value = 'all';
  nodes.get('paramount-tag').value = 'all';
  nodes.get('episode-source-series').value = 'all';
  nodes.get('episode-source-status').value = 'all';
  nodes.get('episode-source-tag').value = 'all';
  class OptionNode extends FakeNode {
    constructor(text, value) { super('option'); this.textContent = text; this.value = value; }
  }
  const document = {
    baseURI: 'https://example.test/explorer/index.html',
    getElementById: (id) => {
      assert.ok(nodes.has(id), `unknown DOM ID ${id}`);
      return nodes.get(id);
    },
    querySelector: (selector) => selector === '.lcars-navigation' ? nodes.get('explorer-navigation')
      : selector === '.navigation-scroll-hint' ? nodes.get('navigation-scroll-hint') : null,
    createElement: (tag) => new FakeNode(tag),
    createDocumentFragment: () => new FakeNode('#fragment')
  };
  const fetch = async (path, opts) => {
    assert.equal(opts.cache, 'no-store');
    requested.add(path);
    if (/^http:\/\/127\.0\.0\.1:(9877|9887)\/api\/(chat|session)$/.test(path)) {
      chatRequests.push({ path, opts });
      const backend = chatBackend || browserAudio.chatBackend;
      assert.ok(backend, 'unconsented chat request is forbidden');
      return backend(path, opts);
    }
    if (path === './index.json') return { status, ok: status >= 200 && status < 300, json: async () => index };
    if (path === './research-leads.json') return { status: researchStatus, ok: researchStatus >= 200 && researchStatus < 300, json: async () => research };
    if (path === './film-catalog.json') return { status: filmStatus, ok: filmStatus >= 200 && filmStatus < 300, json: async () => films };
    if (path === './beyond-premiere-photo.json') return {
      status: premiereStatus, ok: premiereStatus >= 200 && premiereStatus < 300,
      arrayBuffer: async () => premiereBytes.buffer.slice(premiereBytes.byteOffset, premiereBytes.byteOffset + premiereBytes.byteLength)
    };
    if (path === './beyond-premiere-release-decision.json') return {
      status: decisionStatus, ok: decisionStatus >= 200 && decisionStatus < 300,
      arrayBuffer: async () => decisionBytes.buffer.slice(decisionBytes.byteOffset, decisionBytes.byteOffset + decisionBytes.byteLength)
    };
    if (path === './discovery-catalog.json') return { status: directoryStatus, ok: directoryStatus >= 200 && directoryStatus < 300, json: async () => directory };
    if (path === './picard-literature-overlay.json') {
      const bytes = picardBytes ?? browserAudio.picardBytes;
      const sidecarStatus = browserAudio.picardStatus ?? picardStatus;
      return {
        status: sidecarStatus, ok: sidecarStatus >= 200 && sidecarStatus < 300,
        arrayBuffer: async () => bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength)
      };
    }
    if (path === './picard-jackets-v1.0.json') {
      const bytes = browserAudio.picardJacketsBytes;
      const sidecarStatus = browserAudio.picardJacketsStatus ?? 404;
      return {
        status: sidecarStatus, ok: sidecarStatus >= 200 && sidecarStatus < 300,
        arrayBuffer: async () => bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength)
      };
    }
    if (path === './artwork-catalog-v1.3.json') {
      const effectiveStatus = browserAudio.mediumStatus ?? mediumStatus;
      return { status: effectiveStatus, ok: effectiveStatus >= 200 && effectiveStatus < 300,
        json: async () => browserAudio.mediumArtwork ?? mediumArtwork };
    }
    if (path === './artwork-catalog.json') return { status: artworkStatus, ok: artworkStatus >= 200 && artworkStatus < 300, json: async () => artwork };
    if (path === './synopsis-catalog.json') return { status: synopsisStatus, ok: synopsisStatus >= 200 && synopsisStatus < 300, json: async () => synopsis };
    if (path === './metadata-rechecks.json') return {
      status: metadataStatus, ok: metadataStatus >= 200 && metadataStatus < 300,
      arrayBuffer: async () => metadataBytes.buffer.slice(metadataBytes.byteOffset, metadataBytes.byteOffset + metadataBytes.byteLength)
    };
    if (path === './short-synopsis-catalog.json') return {
      status: shortStatus, ok: shortStatus >= 200 && shortStatus < 300,
      arrayBuffer: async () => shortBytes.buffer.slice(shortBytes.byteOffset, shortBytes.byteOffset + shortBytes.byteLength)
    };
    if (path === './lit-publisher-edition-leads.json') return {
      status: publisherStatus, ok: publisherStatus >= 200 && publisherStatus < 300,
      arrayBuffer: async () => publisherBytes.buffer.slice(publisherBytes.byteOffset, publisherBytes.byteOffset + publisherBytes.byteLength)
    };
    if (path === './accepted-source-card-rechecks.json') return {
      status: sourceCardStatus, ok: sourceCardStatus >= 200 && sourceCardStatus < 300,
      arrayBuffer: async () => sourceCardBytes.buffer.slice(sourceCardBytes.byteOffset, sourceCardBytes.byteOffset + sourceCardBytes.byteLength)
    };
    if (path === './publisher-isbn-crosschecks.json') return {
      status: isbnStatus, ok: isbnStatus >= 200 && isbnStatus < 300,
      arrayBuffer: async () => isbnBytes.buffer.slice(isbnBytes.byteOffset, isbnBytes.byteOffset + isbnBytes.byteLength)
    };
    if (path === './paramount-film-rechecks.json') return {
      status: paramountStatus, ok: paramountStatus >= 200 && paramountStatus < 300,
      arrayBuffer: async () => paramountBytes.buffer.slice(paramountBytes.byteOffset, paramountBytes.byteOffset + paramountBytes.byteLength)
    };
    if (path === './episode-source-cards.json') return {
      status: episodeStatus, ok: episodeStatus >= 200 && episodeStatus < 300,
      arrayBuffer: async () => episodeBytes.buffer.slice(episodeBytes.byteOffset, episodeBytes.byteOffset + episodeBytes.byteLength)
    };
    assert.fail('Unexpected data request: ' + path);
  };
  const deterministicCrypto = {
    subtle: {
      digest(algorithm, bytes) {
        // Real WebCrypto is asynchronous on CI. Track every actual digest
        // completion rather than assuming one setImmediate settles sidecars.
        const pending = rejectDigest ? Promise.reject(new Error('Synthetic WebCrypto digest failure'))
          : webcrypto.subtle.digest(algorithm, bytes);
        inFlightDigests.add(pending);
        // Observe both outcomes without creating an ignored rejecting promise.
        pending.then(() => inFlightDigests.delete(pending), () => inFlightDigests.delete(pending));
        return pending;
      }
    }
  };
  vm.runInNewContext(appScript, {
    document, fetch, Option: OptionNode, URL, crypto: deterministicCrypto, TextDecoder, TextEncoder,
    AbortController, setTimeout: browserAudio.mockSetTimeout || setTimeout,
    clearTimeout: browserAudio.mockClearTimeout || clearTimeout,
    location: { origin: 'https://example.test', ...(browserAudio.mockLocation || {}) },
    window: { requestAnimationFrame: (fn) => fn(), ...browserAudio }, console
  }, { filename: 'app.js' });
  // Every fixture must reach the optional loader frontier and finish every
  // observed WebCrypto task. A second quiet event-loop turn lets chained
  // Promise callbacks update the DOM. This avoids machine-load timing races
  // without a guessed fixed delay or swallowing a rejected request.
  const optionalPaths = ['./film-catalog.json', './discovery-catalog.json', './lit-publisher-edition-leads.json',
    './artwork-catalog-v1.3.json', './synopsis-catalog.json',
    './metadata-rechecks.json', './short-synopsis-catalog.json', './accepted-source-card-rechecks.json',
    './publisher-isbn-crosschecks.json', './paramount-film-rechecks.json', './episode-source-cards.json'];
  if ((picardBytes || browserAudio.picardBytes) &&
      (browserAudio.picardStatus ?? picardStatus) === 200 &&
      ((browserAudio.mediumStatus ?? mediumStatus) === 200 || artworkStatus === 200))
    optionalPaths.push('./picard-jackets-v1.0.json');
  if (filmStatus === 200 && films?.films?.some((f) => f.id === 'film-beyond' && f.title === 'Star Trek Beyond' &&
      f.source_locator === 'https://www.startrek.com/movies/star-trek-beyond')) {
    optionalPaths.push('./beyond-premiere-photo.json');
    if (premiereStatus === 200 && premiereBytes &&
        appScript.includes('bfbd57bc95d67315215b4b61ae0ed12193d3114d3c52a40ef99deca09282b634') &&
        createHash('sha256').update(premiereBytes).digest('hex') ===
          'bfbd57bc95d67315215b4b61ae0ed12193d3114d3c52a40ef99deca09282b634')
      optionalPaths.push('./beyond-premiere-release-decision.json');
  }
  const deadline = Date.now() + 5000;
  let quietTurns = 0;
  while (quietTurns < 2 && Date.now() < deadline) {
    await new Promise((resolve) => setImmediate(resolve));
    if (optionalPaths.every((path) => requested.has(path)) &&
        (requested.has('./artwork-catalog.json') ||
         (browserAudio.mediumStatus ?? mediumStatus) >= 200 &&
         (browserAudio.mediumStatus ?? mediumStatus) < 300) &&
        inFlightDigests.size === 0) quietTurns++;
    else quietTurns = 0;
  }
  assert.equal(quietTurns, 2, 'Explorer fixture optional requests/WebCrypto did not reach settled state');
  return nodes;
}

function candidateIndex(count = 3) {
  return {
    schema_version: '2.0.0', data_status: 'CANDIDATE_DISCOVERY_ONLY',
    source_policy: 'EXTERNAL_METADATA_ONLY', coverage_effect: 'NONE',
    held_candidate_count: 2, lead_count: count, sampled_missions_count: count ? 1 : 0,
    leads: Array.from({ length: count }, (_, i) => ({
      mission_id: 'tng', source_type: 'WIKIDATA_METADATA', independence_group: 'wikidata:wdqs',
      episode_qid: `Q${i + 1}`, episode_label: i === 1 ? 'The Neutral Zone' : `Episode ${i + 1}`,
      snapshot_id: 'WDQS-TNG-Q16290-20261102-10ROW-001',
      query_sha256: 'a'.repeat(64), response_sha256: 'b'.repeat(64),
      verification_status: 'UNVERIFIED_METADATA'
    }))
  };
}

const catalog = {
  schema_version: '1.0.0', build: { data_status: 'MISSION_CATALOG_ONLY', projection_hash: null },
  missions: [{ id: 'tng', title: 'Star Trek: The Next Generation' }, { id: 'voy', title: 'Star Trek: Voyager' }],
  briefings: [], records: []
};

const episodeNodes = (bytes, status = 200, script = SCRIPT) => runWithIndex(catalog, 200,
  null, 404, {}, null, 404, null, 404, null, 404, null, 404, script,
  null, 404, null, 404, false, null, 404, null, 404, null, 404, null, 404, bytes, status);

const runMediumArtwork = (directory, mediumArtwork, mediumStatus = 200, smallArtwork = null) =>
  runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200,
    smallArtwork, smallArtwork ? 200 : 404, null, 404, SCRIPT,
    null, 404, null, 404, false, null, 404, null, 404, null, 404,
    null, 404, null, 404, mediumArtwork, mediumStatus);

async function selectLocalOpf(nodes, bytes, declaredSize = bytes.length) {
  nodes.get('owner-opf-file').files = [{ size: declaredSize, arrayBuffer: async () =>
    bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) }];
  nodes.get('owner-opf-file').fire('change');
  const deadline = Date.now() + 5000;
  while (Date.now() < deadline) {
    const status = nodes.get('owner-opf-state').textContent;
    if (status.startsWith('Exact reviewed') || status.startsWith('Local index rejected')) return;
    await new Promise((resolve) => setImmediate(resolve));
  }
  assert.fail('Owner-local OPF selection did not settle');
}

test('owner OPF shelf requires explicit local file choice and does not change public counts', async () => {
  const nodes = await runWithIndex(catalog);
  const publicBefore = ['discovery-top-count', 'publisher-edition-nav-count', 'record-count']
    .map((id) => nodes.get(id).textContent);
  assert.equal(nodes.get('owner-opf-list').children.length, 0);
  assert.match(nodes.get('owner-opf-state').textContent, /No local file selected/);
  const bytes = readFileSync(new URL('../proposals/librarian/private-opf-metadata-20261103/search-index.json', import.meta.url));
  await selectLocalOpf(nodes, bytes);
  assert.match(nodes.get('owner-opf-state').textContent, /browser memory only/);
  assert.match(nodes.get('owner-opf-summary').textContent, /347 of 347 locally selected OPF metadata observations/);
  assert.match(nodes.get('owner-opf-summary').textContent, /0 admitted Works, 0 verified edition bindings, 0 book close reads/);
  assert.equal(traverse(nodes.get('owner-opf-list'), (node) => node.tagName === 'article').length, 40);
  assert.equal(nodes.get('owner-opf-more').hidden, false);
  nodes.get('owner-opf-more').fire('click');
  assert.equal(traverse(nodes.get('owner-opf-list'), (node) => node.tagName === 'article').length, 80);
  nodes.get('owner-opf-query').value = 'gateways';
  nodes.get('owner-opf-query').fire('input');
  assert.match(nodes.get('owner-opf-list').textContent, /star trek gateways/);
  nodes.get('owner-opf-query').value = 'this title should not exist zzzzz';
  nodes.get('owner-opf-query').fire('input');
  assert.equal(nodes.get('owner-opf-empty').hidden, false);
  nodes.get('owner-opf-clear').fire('click');
  assert.equal(nodes.get('owner-opf-list').children.length, 0);
  assert.equal(nodes.get('owner-opf-query').disabled, true);
  assert.match(nodes.get('owner-opf-summary').textContent, /not loaded/);
  assert.deepEqual(['discovery-top-count', 'publisher-edition-nav-count', 'record-count']
    .map((id) => nodes.get(id).textContent), publicBefore);
});

test('owner OPF shelf rejects altered, oversized and malformed local JSON without data retention', async () => {
  const nodes = await runWithIndex(catalog);
  const bytes = readFileSync(new URL('../proposals/librarian/private-opf-metadata-20261103/search-index.json', import.meta.url));
  const tampered = Buffer.from(bytes.toString('utf8').replace('star trek gateways', '<img src=x onerror=alert(1)>'));
  await selectLocalOpf(nodes, tampered);
  assert.match(nodes.get('owner-opf-state').textContent, /Local index rejected/);
  assert.equal(nodes.get('owner-opf-list').children.length, 0);
  await selectLocalOpf(nodes, bytes, 512 * 1024 + 1);
  assert.match(nodes.get('owner-opf-state').textContent, /Local index rejected/);
  assert.equal(nodes.get('owner-opf-list').children.length, 0);
  await selectLocalOpf(nodes, Buffer.from('{"records":[]}'));
  assert.match(nodes.get('owner-opf-state').textContent, /Local index rejected/);
  assert.equal(nodes.get('owner-opf-query').disabled, true);
  assert.equal(nodes.get('owner-opf-clear').disabled, true);
  assert.equal(nodes.get('owner-opf-list').textContent.includes('<img'), false);
});

test('owner OPF Clear cancels an in-flight local file read without reviving metadata', async () => {
  const nodes = await runWithIndex(catalog);
  const bytes = readFileSync(new URL('../proposals/librarian/private-opf-metadata-20261103/search-index.json', import.meta.url));
  let completeRead;
  const deferredBytes = new Promise((resolve) => { completeRead = resolve; });
  nodes.get('owner-opf-file').files = [{ size: bytes.length, arrayBuffer: () => deferredBytes }];
  nodes.get('owner-opf-file').fire('change');
  assert.equal(nodes.get('owner-opf-clear').disabled, false, 'Clear must remain available during pending read');
  assert.match(nodes.get('owner-opf-state').textContent, /Checking selected file locally/);
  nodes.get('owner-opf-clear').fire('click');
  completeRead(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength));
  await new Promise((resolve) => setImmediate(resolve));
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(nodes.get('owner-opf-list').children.length, 0);
  assert.equal(nodes.get('owner-opf-query').disabled, true);
  assert.equal(nodes.get('owner-opf-clear').disabled, true);
  assert.match(nodes.get('owner-opf-state').textContent, /No local file selected/);
  assert.match(nodes.get('owner-opf-summary').textContent, /not loaded/);
});

test('owner OPF markup is a manual local file input with clear and distinct private status', () => {
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  assert.match(html, /id="owner-opf-file" type="file"/);
  assert.match(html, /id="owner-opf-clear" type="button" disabled/);
  assert.match(html, /id="owner-opf-query" type="search"[^>]+disabled/);
  assert.match(html, /nothing is uploaded, fetched automatically, saved/);
  assert.match(html, /already exists in the public repository/);
  assert.match(html, /not necessarily one book/);
  assert.equal(html.includes('./private-opf-metadata-20261103/search-index.json'), false);
});

test('20 separately validated publisher episode guide cards search by title, series, slot and utterance tag', async () => {
  const bytes = readFileSync(new URL('../explorer/episode-source-cards.json', import.meta.url));
  const nodes = await episodeNodes(bytes);
  assert.equal(nodes.get('episode-source-nav-count').textContent, '20');
  assert.equal(nodes.get('episode-source-download').hidden, false);
  assert.match(nodes.get('episode-source-summary').textContent, /^20 of 20/);
  assert.equal(traverse(nodes.get('episode-source-list'), (n) => n.tagName === 'article').length, 20);
  assert.equal(traverse(nodes.get('episode-source-list'), (n) => n.className === 'episode-source-chips').length, 20);
  assert.match(nodes.get('episode-source-list').textContent, /HELD · 0 coverage/);
  assert.match(nodes.get('episode-source-list').textContent, /Artwork not released/);
  assert.match(nodes.get('episode-source-list').textContent, /The Impossible Box/);
  assert.match(nodes.get('episode-source-list').textContent, /Hegemony, Part II/);
  for (const forbidden of ['CLOSE_READ', 'AUDITED_WORK_ADMITTED', 'thumbnail_url', 'synopsis_paraphrase_candidate']) {
    assert.equal(nodes.get('episode-source-list').textContent.includes(forbidden), false);
  }
  nodes.get('episode-source-query').value = 'S3E06';
  nodes.get('episode-source-filters').fire('input');
  assert.match(nodes.get('episode-source-summary').textContent, /^1 of 20/);
  assert.match(nodes.get('episode-source-list').textContent, /The Sehlat Who Ate Its Tail/);
  nodes.get('episode-source-query').value = '';
  nodes.get('episode-source-series').value = 'PIC';
  nodes.get('episode-source-filters').fire('change');
  assert.match(nodes.get('episode-source-summary').textContent, /^10 of 20/);
  nodes.get('episode-source-series').value = 'all';
  nodes.get('episode-source-tag').value = 'publisher-utterance:pike';
  nodes.get('episode-source-filters').fire('change');
  assert.match(nodes.get('episode-source-summary').textContent, /^4 of 20/);
  nodes.get('episode-source-tag').value = 'all';
  nodes.get('episode-source-status').value = 'HELD_PUBLISHER_GUIDE_ONLY';
  nodes.get('episode-source-filters').fire('change');
  assert.match(nodes.get('episode-source-summary').textContent, /^20 of 20/);
});

test('episode card shelf fails closed on absent, altered and rehashed source/rights/slot forgeries', async () => {
  const original = readFileSync(new URL('../explorer/episode-source-cards.json', import.meta.url));
  const missing = await episodeNodes(original, 404);
  assert.equal(missing.get('episode-source-nav-count').textContent, '—');
  assert.match(missing.get('episode-source-summary').textContent, /unavailable; not a verified zero/);
  const mangled = Buffer.from(original.toString('utf8').replace('Remembrance', 'MALICIOUS TITLE'));
  const rejected = await episodeNodes(mangled);
  assert.equal(rejected.get('episode-source-nav-count').textContent, '—');
  const source = JSON.parse(original);
  const currentHash = '38dfde3c3a1cfe38e41bf6740327b070f7846e2dc7c6149b74f88db7b85186f6';
  for (const mutate of [
    (d) => { d.rows[0].source_status = 'AUDITED_WORK_ADMITTED'; },
    (d) => { d.rows[0].work_admission_effect = 'ADMITTED'; },
    (d) => { d.rows[0].artwork_release_effect = 'CLEARED'; },
    (d) => { d.rows[0].publisher_guide_url = 'https://www.paramountplus.com/shows/star-trek-strange-new-worlds/episodes/3/'; },
    (d) => { d.rows[0].title = d.rows[1].title; },
    (d) => {
      const row = d.rows[0];
      const previous = row.publisher_utterance_labels[0];
      row.publisher_utterance_labels[0] = 'False Entity Added';
      row.tags = row.tags.map((tag) => tag === `publisher-utterance:${previous.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`
        ? 'publisher-utterance:false-entity-added' : tag).sort();
    },
    (d) => { d.rows[0].tags.push('publisher-utterance:forged'); },
    (d) => { d.rows[0].source_input_sha256 = '0'.repeat(64); },
    (d) => { d.rows[1] = d.rows[0]; },
  ]) {
    const d = structuredClone(source);
    mutate(d);
    const bytes = Buffer.from(JSON.stringify(d));
    const patchedScript = SCRIPT.replace(currentHash, createHash('sha256').update(bytes).digest('hex'));
    const nodes = await episodeNodes(bytes, 200, patchedScript);
    assert.equal(nodes.get('episode-source-nav-count').textContent, '—');
    assert.equal(nodes.get('episode-source-list').children.length, 0);
    assert.match(nodes.get('episode-source-state').textContent, /withheld/i);
  }
});

test('13 first-party Paramount source-only film page rechecks search by cast, year and held anomaly', async () => {
  const bytes = readFileSync(new URL('../explorer/paramount-film-rechecks.json', import.meta.url));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, null, 404, null, 404,
    null, 404, SCRIPT, null, 404, null, 404, false, null, 404, null, 404, null, 404, bytes, 200);
  assert.equal(nodes.get('paramount-nav-count').textContent, '13');
  assert.equal(nodes.get('paramount-download').hidden, false);
  assert.match(nodes.get('paramount-summary').textContent, /^13 of 13/);
  assert.equal(traverse(nodes.get('paramount-list'), (n) => n.tagName === 'article').length, 13);
  const chronology = nodes.get('paramount-chronology-list');
  assert.equal(nodes.get('paramount-chronology').hidden, false);
  const timelineCards = traverse(chronology, (n) => n.tagName === 'li');
  const source = JSON.parse(bytes.toString('utf8')).rows;
  assert.equal(timelineCards.length, 13, 'each validated publisher source row gets its own visual timeline link');
  const ordered = [...source].sort((a, b) => a.year_as_listed - b.year_as_listed ||
    a.source_page_slug.localeCompare(b.source_page_slug));
  assert.deepEqual(timelineCards.map((n) => traverse(n, (child) => child.className === 'paramount-chronology-year')[0].textContent),
    ordered.map((n) => String(n.year_as_listed)), 'source-reported years define chronology, not invented chronology');
  const links = traverse(chronology, (n) => n.tagName === 'a');
  assert.deepEqual(links.map((n) => n.href), ordered.map((n) => n.source_locator));
  assert.ok(links.every((n) => n.target === '_blank' && n.rel === 'noopener noreferrer'));
  assert.equal(timelineCards.filter((n) => n.className.includes('held')).length, 3);
  assert.equal(traverse(chronology, (n) => n.tagName === 'img').length, 0,
    'publisher metadata may never silently grant poster or screenshot display');
  assert.match(chronology.textContent, /Publisher page/i);
  assert.match(chronology.textContent, /HELD anomaly/);
  assert.match(chronology.textContent, /No Work admitted · no film image/,
    'visual source-only cards must never imply film pixels, accepted Works or canon facts');
  assert.match(nodes.get('paramount-state').textContent, /3 source discrepancies held/);
  assert.doesNotMatch(nodes.get('paramount-list').textContent, /poster_asset_locator|original_synopsis_candidate/);
  nodes.get('paramount-status').value = 'HELD_UNRESOLVED_SOURCE_ANOMALY';
  nodes.get('paramount-filters').fire('change');
  assert.match(nodes.get('paramount-summary').textContent, /^3 of 13/);
  assert.equal(traverse(nodes.get('paramount-list'), (n) => n.className === 'card paramount-card paramount-held').length, 3);
  assert.equal(traverse(chronology, (n) => n.tagName === 'li').length, 3);
  nodes.get('paramount-status').value = 'all';
  nodes.get('paramount-query').value = 'Patrick Stewart';
  nodes.get('paramount-filters').fire('input');
  assert.ok(traverse(nodes.get('paramount-list'), (n) => n.tagName === 'article').length >= 1);
  assert.ok(traverse(chronology, (n) => n.tagName === 'li').length >= 1);
  nodes.get('paramount-query').value = '';
  nodes.get('paramount-tag').value = 'anomaly:held';
  nodes.get('paramount-filters').fire('change');
  assert.match(nodes.get('paramount-summary').textContent, /^3 of 13/);
  assert.equal(traverse(chronology, (n) => n.tagName === 'li').length, 3);
});

test('Paramount public sidecar rejects missing bytes, tampering and rehashed source/rights escalation', async () => {
  const bytes = readFileSync(new URL('../explorer/paramount-film-rechecks.json', import.meta.url));
  const bad = Buffer.from(bytes.toString('utf8').replace('star-trek-beyond', 'star-trek-forged'));
  for (const [sample, status] of [[bytes, 404], [bad, 200]]) {
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, null, 404, null, 404,
      null, 404, SCRIPT, null, 404, null, 404, false, null, 404, null, 404, null, 404, sample, status);
    assert.equal(nodes.get('paramount-nav-count').textContent, '—');
    assert.match(nodes.get('paramount-summary').textContent, /unavailable; not a verified zero/);
    assert.equal(nodes.get('paramount-list').children.length, 0);
    assert.equal(nodes.get('paramount-chronology').hidden, true);
    assert.equal(nodes.get('paramount-chronology-list').children.length, 0);
  }
  const original = JSON.parse(bytes.toString('utf8'));
  const digest = '40d968f1faa11bd888f2af838c6cc4075c1c89ba4b269cf08a2e33878e87e26b';
  for (const mutate of [
    (d) => { d.rows[0].source_locator = 'https://evil.example/movies/star-trek-beyond'; },
    (d) => { d.rows[0].source_input_sha256 = '0'.repeat(64); },
    (d) => { d.rows[0].coverage_effect = 'CLOSE_READ'; },
    (d) => { d.rows[0].source_anomaly = 'NEW UNSOURCED ANOMALY NOT_RECONCILED'; },
    (d) => { d.rows[0].tags.push('work:admitted'); },
    (d) => { d.rows[0].selected_cast_performers_as_listed[0] = '<img>'; },
    (d) => { d.rows[0].poster_asset_locator = 'https://example.test/cover.jpg'; }
  ]) {
    const data = structuredClone(original);
    mutate(data);
    const forged = Buffer.from(JSON.stringify(data));
    const script = SCRIPT.replace(digest, createHash('sha256').update(forged).digest('hex'));
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, null, 404, null, 404,
      null, 404, script, null, 404, null, 404, false, null, 404, null, 404, null, 404, forged, 200);
    assert.equal(nodes.get('paramount-nav-count').textContent, '—');
    assert.equal(nodes.get('paramount-list').children.length, 0);
  }
});

test('39 source-local publisher ISBN crosschecks are independently searchable without Work/edition authentication', async () => {
  const isbnBytes = readFileSync(new URL('../explorer/publisher-isbn-crosschecks.json', import.meta.url));
  const editions = readFileSync(new URL('../explorer/lit-publisher-edition-leads.json', import.meta.url));
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const metadata = readFileSync(new URL('../explorer/metadata-rechecks.json', import.meta.url));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200,
    null, 404, null, 404, SCRIPT, metadata, 200, null, 404, false, editions, 200, null, 404, isbnBytes, 200);
  assert.equal(nodes.get('publisher-isbn-nav-count').textContent, '39');
  assert.match(nodes.get('publisher-isbn-state').textContent, /30 source-local identifier agreements, 9 held discrepancies/);
  assert.equal(nodes.get('publisher-isbn-download').hidden, false);
  assert.match(nodes.get('publisher-isbn-summary').textContent, /39 of 39 source-local publisher ISBN crosschecks match/);
  assert.equal(traverse(nodes.get('publisher-isbn-list'), (n) => n.tagName === 'article').length, 12);
  assert.equal(nodes.get('publisher-edition-nav-count').textContent, '3');
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,214');
  assert.match(nodes.get('discovery-metrics').textContent, /metadata rechecked: 56 \/ 1,214/i);
  assert.doesNotMatch(nodes.get('publisher-isbn-list').textContent, /original_publisher_description_paraphrase|C:\\Users|OneDrive/i);
  const more = nodes.get('publisher-isbn-list').children.find((n) => n.tagName === 'button');
  assert.ok(more, '39 records remain navigable in bounded pages');
  more.fire('click');
  assert.equal(traverse(nodes.get('publisher-isbn-list'), (n) => n.tagName === 'article').length, 24);
  nodes.get('publisher-isbn-status').value = 'held';
  nodes.get('publisher-isbn-filters').fire('change');
  assert.match(nodes.get('publisher-isbn-summary').textContent, /^9 of 39 source-local/);
  assert.equal(traverse(nodes.get('publisher-isbn-list'), (n) => n.className === 'card publisher-isbn-card isbn-held').length, 9);
  assert.match(nodes.get('publisher-isbn-list').textContent, /HELD: publisher\/source-local date discrepancy/);
  nodes.get('publisher-isbn-status').value = 'agreement';
  nodes.get('publisher-isbn-query').value = 'grounded';
  nodes.get('publisher-isbn-filters').fire('input');
  assert.match(nodes.get('publisher-isbn-summary').textContent, /^1 of 39 source-local/);
  assert.match(nodes.get('publisher-isbn-list').textContent, /Grounded/);
  assert.match(nodes.get('publisher-isbn-list').textContent, /private edition unverified/);
  nodes.get('publisher-isbn-status').value = 'all';
  nodes.get('publisher-isbn-query').value = '';
  nodes.get('publisher-isbn-tag').value = 'source-batch:opf-tng-0076-0079';
  nodes.get('publisher-isbn-filters').fire('change');
  assert.match(nodes.get('publisher-isbn-summary').textContent, /^4 of 39 source-local/);
  assert.match(nodes.get('publisher-isbn-list').textContent, /Here There Be Dragons/);
});

test('publisher ISBN shelf rejects missing/tampered projection without reducing older catalog counts', async () => {
  const valid = readFileSync(new URL('../explorer/publisher-isbn-crosschecks.json', import.meta.url));
  const altered = Buffer.from(valid.toString('utf8').replace('Grounded', 'Forged Edition'));
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const editions = readFileSync(new URL('../explorer/lit-publisher-edition-leads.json', import.meta.url));
  for (const [bytes, status] of [[valid, 404], [altered, 200]]) {
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200,
      null, 404, null, 404, SCRIPT, null, 404, null, 404, false, editions, 200, null, 404, bytes, status);
    assert.equal(nodes.get('publisher-isbn-nav-count').textContent, '—');
    assert.equal(nodes.get('publisher-edition-nav-count').textContent, '3');
    assert.equal(nodes.get('discovery-nav-count').textContent, '1,214');
    assert.equal(nodes.get('publisher-isbn-download').hidden, true);
    assert.match(nodes.get('publisher-isbn-summary').textContent, /withheld or unavailable; its count is not zero/);
    assert.equal(nodes.get('publisher-isbn-list').children.length, 0);
  }
});

test('repinned publisher ISBN JSON cannot smuggle private custody, plot text, external URLs or Work claims', async () => {
  const valid = JSON.parse(readFileSync(new URL('../explorer/publisher-isbn-crosschecks.json', import.meta.url), 'utf8'));
  const digest = '1170e8cb56b4ff3c5beab8d412fa5613b6e3b9d0ab7b5a18f80fe403c5bde3e8';
  const mutations = [
    (data) => { data.rows[0].crosscheck_state = 'VERIFIED_PRIVATE_EBOOK_WORK_ADMITTED'; },
    (data) => { data.rows[0].private_edition_equivalence = 'VERIFIED'; },
    (data) => { data.rows[0].publisher_title = '<script>alert(1)</script>'; },
    (data) => { data.rows[0].publisher_creators[0] = '<img>'; },
    (data) => { data.rows[0].publisher_url = 'https://evil.example.test/books/a/b/c/9780743439978'; },
    (data) => { data.rows[0].publisher_isbn13 = '9780743439979'; },
    (data) => { data.rows[0].source_local_ref = 'opf-local:9999'; },
    (data) => { data.rows[0].public_source_record = 'C:\\Users\\patri\\OneDrive\\Books'; },
    (data) => { data.rows[0].private_archive_path = 'C:\\Users\\patri\\OneDrive\\Books'; },
    (data) => { data.rows[0].public_synopsis_effect = 'APPROVED'; },
    (data) => { data.canonical_works_admitted = 39; },
    (data) => { data.row_count = 40; }
  ];
  for (const mutate of mutations) {
    const forged = structuredClone(valid);
    mutate(forged);
    const bytes = Buffer.from(JSON.stringify(forged));
    const repinned = SCRIPT.replace(digest, createHash('sha256').update(bytes).digest('hex'));
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, null, 404,
      null, 404, null, 404, repinned, null, 404, null, 404, false, null, 404, null, 404, bytes, 200);
    assert.match(nodes.get('publisher-isbn-state').textContent, /withheld/);
    assert.equal(nodes.get('publisher-isbn-list').children.length, 0);
    const output = nodes.get('publisher-isbn-list').textContent;
    for (const forbidden of ['VERIFIED_PRIVATE_EBOOK', '<script>', '<img>', 'OneDrive']) {
      assert.equal(output.includes(forbidden), false);
    }
  }
});

test('61 first-party source-card observations are searchable without inflating 56 checks, 37 synopses, or 3 ISBN leads', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const metadata = readFileSync(new URL('../explorer/metadata-rechecks.json', import.meta.url));
  const sidecar = readFileSync(new URL('../explorer/accepted-source-card-rechecks.json', import.meta.url));
  const publisher = readFileSync(new URL('../explorer/lit-publisher-edition-leads.json', import.meta.url));
  const synopses = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const shorts = readFileSync(new URL('../explorer/short-synopsis-catalog.json', import.meta.url));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200,
    null, 404, synopses, 200, SCRIPT, metadata, 200, shorts, 200, false, publisher, 200, sidecar, 200);
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,214');
  assert.equal(nodes.get('publisher-edition-nav-count').textContent, '3');
  assert.match(nodes.get('discovery-metrics').textContent, /metadata rechecked: 56 \/ 1,214/i);
  assert.match(nodes.get('discovery-metrics').textContent, /Additional source-local publisher cards: 61 \(46 title matches · 15 held\)/);
  assert.match(nodes.get('publisher-card-state').textContent, /61 additional accepted publisher-card reads/);
  assert.match(nodes.get('publisher-card-state').textContent, /10 SNW cards unjoined/);
  assert.equal(nodes.get('publisher-card-download').hidden, false);
  assert.equal(nodes.get('publisher-card-download').getAttribute('href'), null, 'download URL is static HTML, never injected via source JSON');

  nodes.get('discovery-publisher-check').value = 'held_unresolved';
  nodes.get('discovery-filters').fire('change');
  assert.match(nodes.get('discovery-summary').textContent, /^15 source-local metadata rows match/);
  assert.match(nodes.get('discovery-list').textContent, /HELD \/ UNRESOLVED publisher card title or split/);
  assert.match(nodes.get('discovery-list').textContent, /No audiovisual close read, raw publisher page custody, Work identity admission, or approved synopsis/);
  assert.ok(nodes.get('discovery-list').textContent.includes('Broken Bow - Part 1 and 2'));
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'directory-publisher-card held').length, 15);
  nodes.get('discovery-query').value = 'broken bow';
  nodes.get('discovery-filters').fire('input');
  assert.match(nodes.get('discovery-summary').textContent, /^2 source-local metadata rows match/);
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'directory-publisher-card held').length, 2);
  nodes.get('discovery-query').value = 'juggernaut';
  nodes.get('discovery-publisher-check').value = 'title_exact';
  nodes.get('discovery-filters').fire('input');
  assert.match(nodes.get('discovery-summary').textContent, /^1 source-local metadata rows match/);
  assert.match(nodes.get('discovery-list').textContent, /Publisher card title string match/);
  nodes.get('discovery-query').value = '';
  nodes.get('discovery-publisher-check').value = 'all';
  nodes.get('discovery-tag').value = 'publisher-card:held_unresolved';
  nodes.get('discovery-filters').fire('change');
  assert.match(nodes.get('discovery-summary').textContent, /^15 source-local metadata rows match/);
  assert.equal(nodes.get('publisher-edition-list').children.length, 3);
  assert.equal(synopses.synopsis_count + JSON.parse(shorts.toString('utf8')).synopsis_count, 37);
});

test('publisher-card sidecar absent, tampered, or digest-failed leaves existing Explorer states intact', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const metadata = readFileSync(new URL('../explorer/metadata-rechecks.json', import.meta.url));
  const valid = readFileSync(new URL('../explorer/accepted-source-card-rechecks.json', import.meta.url));
  const altered = Buffer.from(valid.toString('utf8').replace('Forget Me Not', 'Forget All Evidence'));
  for (const [bytes, status] of [[valid, 404], [altered, 200]]) {
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200,
      null, 404, null, 404, SCRIPT, metadata, 200, null, 404, false, null, 404, bytes, status);
    assert.equal(nodes.get('discovery-nav-count').textContent, '1,214');
    assert.match(nodes.get('discovery-metrics').textContent, /metadata rechecked: 56 \/ 1,214/i);
    assert.doesNotMatch(nodes.get('discovery-metrics').textContent, /Additional source-local publisher cards: 61/);
    assert.match(nodes.get('publisher-card-state').textContent, /unavailable or rejected/);
    assert.match(nodes.get('publisher-card-state').textContent, /not loaded, not zero/);
    assert.equal(nodes.get('publisher-card-download').hidden, true);
    nodes.get('discovery-publisher-check').value = 'held_unresolved';
    nodes.get('discovery-filters').fire('change');
    assert.match(nodes.get('discovery-summary').textContent, /^0 source-local metadata rows match/);
  }
});

test('repinned malicious publisher-card labels, admission, URLs, and IDs still fail semantic verification', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const original = JSON.parse(readFileSync(new URL('../explorer/accepted-source-card-rechecks.json', import.meta.url), 'utf8'));
  const acceptedDigest = '4ff4246f772117d847ed939a40218679fe6d1621c2c422f539d9c177971804a6';
  const mutations = [
    (data) => { data.rows[0].publisher_title_check = 'AUDITED_WORK_ADMITTED_FULL_TEXT_AVAILABLE_UNRESOLVED'; },
    (data) => { data.rows[0].original_resolution = 'AUDITED_WORK_ADMITTED_FULL_TEXT_AVAILABLE_UNRESOLVED'; },
    (data) => { data.rows[0].publisher_family = 'independent:other'; },
    (data) => { data.rows[0].admission_effect = 'WORK_ADMITTED'; },
    (data) => { data.rows[0].source_local_title = '<img src=x onerror=alert(1)>'; },
    (data) => { data.rows[0].row_id = 'lead:0900'; },
    (data) => { data.rows[0].publisher_guide_url = 'https://evil.example.test/episodes'; },
    (data) => { data.rows[0].publisher_card_title = '<script>alert(1)</script>'; },
    (data) => { data.new_publisher_card_source_local_lead_count = 62; },
    (data) => { data.rows[60].publisher_title_check = 'EXACT'; },
    (data) => { data.rows[60].synopsis_publication_effect = 'APPROVED'; }
  ];
  for (const mutate of mutations) {
    const forged = structuredClone(original);
    mutate(forged);
    const bytes = Buffer.from(JSON.stringify(forged));
    const digest = createHash('sha256').update(bytes).digest('hex');
    const repinned = SCRIPT.replace(acceptedDigest, digest);
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200,
      null, 404, null, 404, repinned, null, 404, null, 404, false, null, 404, bytes, 200);
    assert.match(nodes.get('publisher-card-state').textContent, /unavailable or rejected/);
    assert.doesNotMatch(nodes.get('discovery-metrics').textContent, /Additional source-local publisher cards: 61/);
    // The renderer uses textContent; these assertions check that a rejected
    // sidecar adds no forged card text. They are not HTML filtering logic.
    const visibleText = nodes.get('discovery-list').textContent;
    for (const rejectedLiteral of ['AUDITED_WORK_ADMITTED', '<script>', '<img']) {
      assert.equal(visibleText.includes(rejectedLiteral), false);
    }
  }
});

test('accepted publisher editions appear as three searchable metadata-only cards without inflating universe or synopsis counts', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const base = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const short = readFileSync(new URL('../explorer/short-synopsis-catalog.json', import.meta.url));
  const publisher = readFileSync(new URL('../explorer/lit-publisher-edition-leads.json', import.meta.url));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
    null, 404, base, 200, SCRIPT, null, 404, short, 200, false, publisher, 200);
  const shelf = nodes.get('publisher-edition-list');
  assert.equal(nodes.get('publisher-edition-nav-count').textContent, '3');
  assert.equal(shelf.children.length, 3);
  assert.match(shelf.textContent, /The Kobayashi Maru/);
  assert.match(shelf.textContent, /Genesis Wave Book 3/);
  assert.match(shelf.textContent, /Shadows of the Sun/);
  assert.match(shelf.textContent, /Synopsis held/);
  assert.doesNotMatch(shelf.textContent, /shuttlecraft-stranding.*mission for peace/i);
  assert.equal(traverse(shelf, (node) => node.className === 'artwork-slot artwork-literature').length, 3,
    'publisher candidates only receive original abstract art, not a fabricated publisher cover');
  assert.equal(traverse(shelf, (node) => node.className === 'edition-source').length, 3);
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,214');
  nodes.get('discovery-overview').value = 'reviewed';
  nodes.get('discovery-filters').fire('change');
  assert.match(nodes.get('discovery-summary').textContent, /^37 source-local metadata rows match/);
  nodes.get('publisher-edition-query').value = 'Ecklar 9780743419987';
  nodes.get('publisher-edition-filters').fire('input');
  assert.equal(shelf.children.length, 1);
  assert.match(shelf.textContent, /The Kobayashi Maru/);
  nodes.get('publisher-edition-query').value = '';
  nodes.get('publisher-edition-tag').value = 'publisher-claim:character:leonard-mccoy';
  nodes.get('publisher-edition-filters').fire('change');
  assert.equal(shelf.children.length, 1);
  assert.match(shelf.textContent, /Shadows of the Sun/);
});

test('publisher edition viewer fails closed for missing or tampered accepted bytes', async () => {
  const exact = readFileSync(new URL('../explorer/lit-publisher-edition-leads.json', import.meta.url));
  const forged = Buffer.from(exact.toString('utf8').replace('254 pages', '999 pages'));
  for (const [bytes, status, rejectDigest] of [[exact, 404, false], [forged, 200, false], [exact, 200, true]]) {
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, null, 404,
      null, 404, null, 404, SCRIPT, null, 404, null, 404, rejectDigest, bytes, status);
    assert.equal(nodes.get('publisher-edition-nav-count').textContent, '—');
    assert.equal(nodes.get('publisher-edition-list').children.length, 0);
    assert.match(nodes.get('publisher-edition-state').textContent, /withheld/i);
  }
});

test('separate internally reviewed Short Trek appendix yields fourteen real publisher premises and one null hold', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const original = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const bytes = readFileSync(new URL('../explorer/short-synopsis-catalog.json', import.meta.url));
  const appendix = JSON.parse(bytes.toString('utf8'));
  assert.equal(appendix.synopsis_count, 14);
  assert.equal(original.synopsis_count + appendix.synopsis_count, 37);
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
    null, 404, original, 200, SCRIPT, null, 404, bytes, 200);
  nodes.get('discovery-medium').value = 'SHORT_FORM';
  nodes.get('discovery-filters').fire('input');
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'synopsis-evidence-link').length, 14);
  const cards = nodes.get('discovery-list').children.filter((n) => n.tagName === 'article');
  assert.equal(cards.length, 35);
  assert.equal(cards.filter((card) => card.textContent.includes('Publisher-description-based overview')).length, 14);
  const held = cards.find((card) => card.textContent.includes('Holograms, All the Way Down'));
  assert.ok(held);
  assert.match(held.textContent, /Synopsis pending source verification/);
  assert.equal(traverse(held, (n) => n.className === 'synopsis-evidence-link').length, 0);
  assert.equal(cards.filter((card) => card.textContent.includes('Synopsis pending source verification')).length, 21);
  assert.match(nodes.get('discovery-list').textContent, /Not a full-work close read/);
  assert.equal(traverse(nodes.get('film-list'), (n) => n.className === 'synopsis-evidence-link').length, 14,
    'original film summaries stay intact after short appendix');
});

test('overview availability facet filters the actual pinned source-local overviews without promoting discoveries', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const base = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const short = readFileSync(new URL('../explorer/short-synopsis-catalog.json', import.meta.url));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
    null, 404, base, 200, SCRIPT, null, 404, short, 200);
  nodes.get('discovery-overview').value = 'reviewed';
  nodes.get('discovery-filters').fire('change');
  assert.match(nodes.get('discovery-summary').textContent, /^37 source-local metadata rows match/);
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'synopsis-evidence-link').length, 37);
  for (const [medium, count] of [['LITERATURE', 9], ['FILM', 14], ['SHORT_FORM', 14], ['EPISODE', 0]]) {
    nodes.get('discovery-medium').value = medium;
    nodes.get('discovery-filters').fire('change');
    assert.equal(nodes.get('discovery-list').children.filter((n) => n.tagName === 'article').length, count, medium);
  }
  nodes.get('discovery-medium').value = 'all';
  nodes.get('discovery-overview').value = 'not-loaded';
  nodes.get('discovery-filters').fire('change');
  assert.match(nodes.get('discovery-summary').textContent, /^1,177 source-local metadata rows match/);
  assert.equal(nodes.get('discovery-list').children.filter((n) => n.tagName === 'article').length, 40);
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'synopsis-evidence-link').length, 0);
  assert.equal(nodes.get('briefing-count').textContent, '0');
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,214');
});

test('overview availability is fail-closed when its separate short appendix is missing or forged', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const base = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const exact = readFileSync(new URL('../explorer/short-synopsis-catalog.json', import.meta.url));
  const forged = Buffer.from(exact.toString('utf8').replace('"synopsis_count": 14', '"synopsis_count": 15'));
  for (const [short, status] of [[exact, 404], [forged, 200]]) {
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
      null, 404, base, 200, SCRIPT, null, 404, short, status);
    nodes.get('discovery-overview').value = 'reviewed';
    nodes.get('discovery-filters').fire('change');
    assert.match(nodes.get('discovery-summary').textContent, /^23 source-local metadata rows match/);
    assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'synopsis-evidence-link').length, 23);
  }
});

test('directory free-text finds only loaded reviewed overview words and source receipt paths', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const base = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const short = readFileSync(new URL('../explorer/short-synopsis-catalog.json', import.meta.url));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
    null, 404, base, 200, SCRIPT, null, 404, short, 200);
  for (const [term, count, title] of [
    ['vice admiral', 1, 'The Autobiography of Kathryn Janeway'],
    ['artificial-intelligence interface', 1, 'Calypso'],
    ['prh-star-trek-autobiographies-20261103/records.json', 5, 'The Autobiography of Kathryn Janeway']
  ]) {
    nodes.get('discovery-query').value = term;
    nodes.get('discovery-filters').fire('input');
    assert.equal(nodes.get('discovery-list').children.filter((n) => n.tagName === 'article').length,
      count, `query ${term} agrees with deterministic source-local CLI`);
    assert.match(nodes.get('discovery-list').textContent, new RegExp(title));
  }
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,214');
  assert.equal(nodes.get('briefing-count').textContent, '0');
});

test('query excludes unpublished and altered promotional text even if typed into the search field', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const original = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const short = readFileSync(new URL('../explorer/short-synopsis-catalog.json', import.meta.url));
  const tampered = structuredClone(original);
  tampered.synopses[0].overview_text += ' invented_explorer_only_claim';
  for (const [base, baseStatus, shortBytes, shortStatus, term] of [
    [null, 404, short, 200, 'vice admiral'],
    [tampered, 200, short, 200, 'invented_explorer_only_claim'],
    [tampered, 200, short, 200, 'vice admiral'],
    [original, 200, short, 404, 'artificial-intelligence interface']
  ]) {
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
      null, 404, base, baseStatus, SCRIPT, null, 404, shortBytes, shortStatus);
    nodes.get('discovery-query').value = term;
    nodes.get('discovery-filters').fire('input');
    assert.equal(nodes.get('discovery-list').children.filter((n) => n.tagName === 'article').length, 0,
      `unreleased overview words must never be searchable: ${term}`);
    assert.equal(nodes.get('briefing-count').textContent, '0');
  }
});

test('changed or missing short synopsis appendix is rejected without deleting original film or literature summaries', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const original = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const exact = readFileSync(new URL('../explorer/short-synopsis-catalog.json', import.meta.url));
  const tampered = Buffer.from(exact.toString('utf8').replace('"synopsis_count": 14', '"synopsis_count": 15'));
  for (const [bytes, status] of [[exact, 404], [tampered, 200]]) {
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
      null, 404, original, 200, SCRIPT, null, 404, bytes, status);
    nodes.get('discovery-medium').value = 'SHORT_FORM';
    nodes.get('discovery-filters').fire('input');
    assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'synopsis-evidence-link').length, 0);
    assert.equal(traverse(nodes.get('film-list'), (n) => n.className === 'synopsis-evidence-link').length, 14);
  }
});

test('rejected native digest settles without a floating unhandled rejection or a forged recheck badge', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const original = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const metadata = readFileSync(new URL('../explorer/metadata-rechecks.json', import.meta.url));
  const short = readFileSync(new URL('../explorer/short-synopsis-catalog.json', import.meta.url));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
    null, 404, original, 200, SCRIPT, metadata, 200, short, 200, true);
  assert.doesNotMatch(nodes.get('discovery-metrics').textContent, /Official rendered metadata rechecked/);
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'directory-recheck').length, 0);
  nodes.get('discovery-medium').value = 'SHORT_FORM';
  nodes.get('discovery-filters').fire('input');
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'synopsis-evidence-link').length, 0);
  assert.equal(traverse(nodes.get('film-list'), (n) => n.className === 'synopsis-evidence-link').length, 14,
    'failed optional digest does not remove 23 previously reviewed film/literature summaries');
});

const filmCatalog = {
  schema_version: '1.0.0', data_status: 'DISCOVERY_ONLY', coverage_effect: 'NONE',
  source_group: 'publisher:startrek.com', film_count: 2,
  films: [
    { id: 'star-trek-2009', title: 'Star Trek (2009)', source_locator: 'https://www.startrek.com/movies/star-trek-2009', source_group: 'publisher:startrek.com', work_type: 'FEATURE_FILM', verification_status: 'UNVERIFIED_METADATA', discovery_source: 'OFFICIAL_DIRECTORY' },
    { id: 'section-31', title: 'Star Trek: Section 31', source_locator: 'https://www.startrek.com/news/star-trek-section-31-premieres-january-24', source_group: 'publisher:startrek.com', work_type: 'STREAMING_ORIGINAL_FILM', verification_status: 'UNVERIFIED_METADATA', discovery_source: 'OFFICIAL_ANNOUNCEMENT' }
  ]
};

const beyondFilmCatalog = {
  ...filmCatalog, film_count: 1,
  films: [{ id: 'film-beyond', title: 'Star Trek Beyond',
    source_locator: 'https://www.startrek.com/movies/star-trek-beyond',
    source_group: 'publisher:startrek.com', work_type: 'FEATURE_FILM',
    verification_status: 'UNVERIFIED_METADATA', discovery_source: 'OFFICIAL_DIRECTORY' }]
};

const premiereBytes = readFileSync(new URL('../explorer/beyond-premiere-photo.json', import.meta.url));
const premiereReleaseBytes = readFileSync(new URL('../explorer/beyond-premiere-release-decision.json', import.meta.url));
function premiereNodes(bytes = premiereBytes, status = 200, films = beyondFilmCatalog, script = SCRIPT,
  decision = premiereReleaseBytes, decisionStatus = 200) {
  return runWithIndex(catalog, 200, null, 404, {}, films, 200, null, 404,
    null, 404, null, 404, script, null, 404, null, 404, false,
    null, 404, null, 404, null, 404, null, 404, null, 404,
    null, 404, bytes, status, decision, decisionStatus);
}

test('CC BY 2.0 Beyond source remains visible but public image display HELD under exact accepted decision', async () => {
  assert.equal(createHash('sha256').update(premiereBytes).digest('hex'),
    'bfbd57bc95d67315215b4b61ae0ed12193d3114d3c52a40ef99deca09282b634');
  const nodes = await premiereNodes();
  const panel = nodes.get('beyond-premiere-panel');
  const button = nodes.get('beyond-premiere-toggle');
  const holder = nodes.get('beyond-premiere-image');
  const credit = nodes.get('beyond-premiere-credit');
  assert.equal(panel.hidden, false);
  assert.equal(button.disabled, true);
  assert.equal(button.getAttribute('aria-pressed'), 'false');
  assert.equal(traverse(holder, (n) => n.tagName === 'img').length, 0, 'zero pixels before independent release');
  assert.match(nodes.get('beyond-premiere-status').textContent, /HELD/);
  assert.match(credit.textContent, /Dick Thomas Johnson/);
  assert.match(credit.textContent, /not a frame from the film/);
  assert.match(credit.textContent, /No .*studio.* endorsement/i);
  const links = traverse(credit, (n) => n.tagName === 'a');
  assert.equal(links.length, 4);
  assert.ok(links.some((n) => n.href === 'https://creativecommons.org/licenses/by/2.0/'));
  assert.ok(links.every((n) => n.rel === 'noopener noreferrer' && n.referrerPolicy === 'no-referrer'));
  button.fire('click');
  assert.equal(traverse(holder, (n) => n.tagName === 'img').length, 0,
    'programmatic click also cannot bypass held release decision');
});

test('hypothetical independently approved exact decision keeps image local and opt-in gated', async () => {
  const approved = JSON.parse(premiereReleaseBytes);
  approved.public_image_display_authorized = true;
  approved.decision_status = 'INDEPENDENT_RELEASE_APPROVED';
  approved.independent_image_release_review = 'GO';
  approved.independent_browser_visual_review = 'GO';
  approved.owner_release_disposition = 'RELEASE_AUTHORIZED';
  const bytes = Buffer.from(JSON.stringify(approved));
  const decisionSha = createHash('sha256').update(bytes).digest('hex');
  const patched = SCRIPT.replace('b3041c0fe9ed739c1187b5d9da97e9817dfca753683ca100bd8c93263b68cd89', decisionSha);
  const nodes = await premiereNodes(premiereBytes, 200, beyondFilmCatalog, patched, bytes);
  const button = nodes.get('beyond-premiere-toggle');
  const holder = nodes.get('beyond-premiere-image');
  assert.equal(button.disabled, false);
  assert.equal(traverse(holder, (n) => n.tagName === 'img').length, 0, 'even approved source starts unloaded');
  button.fire('click');
  const photos = traverse(holder, (n) => n.tagName === 'img');
  assert.equal(photos.length, 1);
  assert.equal(photos[0].src, './licensed-artwork/beyond-premiere-japan-2016-960.jpg');
  assert.equal(photos[0].alt, JSON.parse(premiereBytes).alt_text);
  assert.equal(photos[0].referrerPolicy, 'no-referrer');
  assert.equal(photos[0].parentNode.href, JSON.parse(premiereBytes).source_url);
  assert.equal(button.getAttribute('aria-pressed'), 'true');
  button.fire('click');
  assert.equal(traverse(holder, (n) => n.tagName === 'img').length, 0);
  assert.equal(button.getAttribute('aria-pressed'), 'false');
  button.fire('click');
  photos[0].fire('error');
  assert.equal(traverse(holder, (n) => n.tagName === 'img').length, 1,
    'detached error cannot remove new opt-in image or schedule stale retry');
  traverse(holder, (n) => n.tagName === 'img')[0].fire('error');
  assert.equal(traverse(holder, (n) => n.tagName === 'img').length, 0);
  assert.match(holder.textContent, /Photograph unavailable/);
  assert.match(nodes.get('beyond-premiere-status').textContent, /No alternative source/);
});

test('premiere release fails closed when film observation, digest, bytes or source receipt is missing', async () => {
  const missingFilm = await premiereNodes(premiereBytes, 200, filmCatalog);
  assert.equal(missingFilm.get('beyond-premiere-panel').hidden, true);
  assert.equal(missingFilm.get('beyond-premiere-toggle').disabled, true);
  const missingManifest = await premiereNodes(null, 404);
  assert.equal(missingManifest.get('beyond-premiere-panel').hidden, true);
  const tampered = Buffer.from(premiereBytes);
  tampered[30] ^= 1;
  const bad = await premiereNodes(tampered);
  assert.equal(bad.get('beyond-premiere-panel').hidden, true);
  assert.match(bad.get('beyond-premiere-status').textContent, /differs from reviewed bytes/);
  const noCrypto = await premiereNodes(premiereBytes, 200, beyondFilmCatalog,
    SCRIPT.replace('bfbd57bc95d67315215b4b61ae0ed12193d3114d3c52a40ef99deca09282b634', '0'.repeat(64)));
  assert.equal(noCrypto.get('beyond-premiere-panel').hidden, true);
  const noDecision = await premiereNodes(premiereBytes, 200, beyondFilmCatalog, SCRIPT, null, 404);
  assert.equal(noDecision.get('beyond-premiere-toggle').disabled, true);
  const fakeDecision = Buffer.from(premiereReleaseBytes);
  fakeDecision[50] ^= 1;
  const tamperedDecision = await premiereNodes(premiereBytes, 200, beyondFilmCatalog, SCRIPT, fakeDecision);
  assert.equal(tamperedDecision.get('beyond-premiere-toggle').disabled, true);
  assert.match(tamperedDecision.get('beyond-premiere-status').textContent, /HELD/);
});

const licensedArtwork = {
  schema_version: '1.2.0', data_status: 'PROVENANCE_REVIEWED_ARTWORK', coverage_effect: 'NONE',
  rights_policy: 'PER_ENTRY_DISPLAY_GATE', artwork_count: 1,
  artwork: [{
    row_id: 'film:star-trek-2009', image_path: './licensed-artwork/verified-film-cover.webp',
    image_sha256: '1'.repeat(64), alt_text: 'Licensed publisher artwork for Star Trek (2009)',
    source_locator: filmCatalog.films[0].source_locator, rights_status: 'PUBLIC_DISPLAY_PERMISSION_VERIFIED',
    rights_receipt_sha256: '2'.repeat(64), artwork_kind: 'POSTER',
    attribution_text: 'Synthetic poster rights fixture · not a public asset',
    attribution_url: 'https://commons.wikimedia.org/wiki/File:Synthetic_test_poster.webp'
  }]
};

// Test-only simulation of an independent code-owned release receipt. The
// shipping script intentionally carries *no* local image authorizations.
const licensedArtworkTestScript = SCRIPT.replace('const reviewedLocalArtworkReceipts = new Map();',
  `const reviewedLocalArtworkReceipts = new Map([[${JSON.stringify(licensedArtwork.artwork[0].row_id)}, ${JSON.stringify(licensedArtwork.artwork[0])}]]);`);

const synopsisRelease = {
  schema_version: '1.0.0', data_status: 'EDITORIALLY_REVIEWED_DISPLAY_ONLY',
  coverage_effect: 'NONE', admission_effect: 'NONE', synopsis_count: 1,
  synopses: [{
    row_id: 'film:star-trek-2009', title: 'Star Trek (2009)', medium: 'FILM',
    source_locator: filmCatalog.films[0].source_locator,
    overview_evidence_locator: filmCatalog.films[0].source_locator,
    source_group: 'publisher:startrek.com', source_input: 'explorer/film-catalog.json', source_context: 'FEATURE_FILM',
    overview_text: 'Synthetic display fixture: this sentence tests the overview rendering contract without asserting any film events.',
    overview_basis: 'PUBLISHER_DESCRIPTION_PARAPHRASE', source_snapshot_date: '2026-11-03',
    research_observation_path: 'proposals/research/fixture/observations.json',
    research_observation_sha256: '1'.repeat(64), raw_webpage_sha256: null,
    editorial_receipt_sha256: '2'.repeat(64), directory_alias_row_id: null, directory_alias_context: null,
    admission_effect: 'NONE', coverage_effect: 'NONE'
  }]
};

test('accepted B001–B004 rendered metadata checks add 56 source-local badges, not research admission', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const bytes = readFileSync(new URL('../explorer/metadata-rechecks.json', import.meta.url));
  const source = JSON.parse(bytes.toString('utf8'));
  assert.equal(source.rendered_metadata_rechecks, 56);
  assert.equal(source.embedded_research_leads_rechecked, 51);
  assert.equal(source.literary_directory_rows_rechecked, 5);
  assert.equal(source.unresolved_title_or_multipart_cases, 4);
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200,
    null, 404, null, 404, SCRIPT, bytes, 200);
  assert.match(nodes.get('discovery-metrics').textContent, /Official rendered metadata rechecked: 56 \/ 1,214/);
  assert.match(nodes.get('discovery-metrics').textContent, /51 \/ 218 embedded research leads/);
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'directory-recheck').length, 40);
  assert.match(nodes.get('discovery-list').textContent, /no raw-page custody, full-work read or identity admission/);
  nodes.get('discovery-query').value = 'Hide and Q';
  nodes.get('discovery-filters').fire('input');
  assert.match(nodes.get('discovery-list').textContent, /title\/identity unresolved punctuation/);
  nodes.get('discovery-query').value = 'Chain of Command';
  nodes.get('discovery-filters').fire('input');
  assert.match(nodes.get('discovery-list').textContent, /title\/identity unresolved multipart/);
  assert.match(nodes.get('discovery-list').textContent, /Synopsis pending source verification/);
});

test('tampered or absent metadata-recheck projection cannot give unadmitted cards a rechecked badge', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const bytes = readFileSync(new URL('../explorer/metadata-rechecks.json', import.meta.url));
  const altered = Buffer.from(bytes.toString('utf8').replace('"rendered_metadata_rechecks": 56', '"rendered_metadata_rechecks": 99'));
  const cases = [[bytes, 404], [altered, 200]];
  for (const [payload, status] of cases) {
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200,
      null, 404, null, 404, SCRIPT, payload, status);
    assert.doesNotMatch(nodes.get('discovery-metrics').textContent, /Official rendered metadata rechecked/);
    assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'directory-recheck').length, 0);
  }
});

test('reviewed publisher release renders exactly nine literary and fourteen film overviews in both source surfaces', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const published = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  assert.equal(published.synopsis_count, 23);
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
    null, 404, published, 200);
  assert.equal(nodes.get('film-list').children.length, 14);
  assert.equal(traverse(nodes.get('film-list'), (n) => n.className === 'synopsis-evidence-link').length, 14);
  assert.doesNotMatch(nodes.get('film-list').textContent, /Synopsis pending source verification/);
  for (const [medium, expectedReviewed] of [['LITERATURE', 9], ['FILM', 14]]) {
    nodes.get('discovery-medium').value = medium;
    nodes.get('discovery-filters').fire('input');
    const cards = nodes.get('discovery-list').children.filter((n) => n.tagName === 'article');
    assert.equal(cards.length, expectedReviewed);
    assert.equal(traverse(nodes.get('discovery-list'), (n) => n.className === 'synopsis-evidence-link').length,
      expectedReviewed, 'film directory aliases must be explicitly reviewed source-local display crosswalks');
    assert.ok(cards.every((c) => c.textContent.includes('Publisher-description-based overview')));
    assert.ok(cards.every((c) => !c.textContent.includes('Synopsis pending source verification')));
  }
  for (const medium of ['EPISODE', 'SHORT_FORM', 'AUDIO']) {
    nodes.get('discovery-medium').value = medium;
    nodes.get('discovery-filters').fire('input');
    const cards = nodes.get('discovery-list').children.filter((n) => n.tagName === 'article');
    assert.ok(cards.length > 0);
    assert.ok(cards.every((c) => c.textContent.includes('Synopsis pending source verification')));
  }
  assert.equal(nodes.get('briefing-count').textContent, '0');
});

test('published review pins reject changed evidence edition or film directory aliases as a whole', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const films = JSON.parse(readFileSync(new URL('../explorer/film-catalog.json', import.meta.url), 'utf8'));
  const published = JSON.parse(readFileSync(new URL('../explorer/synopsis-catalog.json', import.meta.url), 'utf8'));
  const changes = [
    (x) => { x.synopses.find((r) => r.title.includes('Second Self')).overview_evidence_locator = 'https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781982194833'; },
    (x) => { x.synopses.find((r) => r.medium === 'FILM').directory_alias_row_id = 'directory:film:film-nemesis'; },
    (x) => { x.synopses.find((r) => r.medium === 'FILM').directory_alias_context = 'Fictional Work'; },
    (x) => { x.synopses.find((r) => r.medium === 'FILM').editorial_receipt_sha256 = 'f'.repeat(64); },
    (x) => { x.synopses.find((r) => r.medium === 'LITERATURE').raw_webpage_sha256 = 'f'.repeat(64); },
  ];
  for (const change of changes) {
    const forged = structuredClone(published);
    change(forged);
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, films, 200, directory, 200,
      null, 404, forged, 200);
    assert.match(nodes.get('film-list').textContent, /Synopsis pending source verification/);
    nodes.get('discovery-medium').value = 'LITERATURE';
    nodes.get('discovery-filters').fire('input');
    assert.match(nodes.get('discovery-list').textContent, /Synopsis pending source verification/);
    assert.doesNotMatch(nodes.get('discovery-list').textContent, /Publisher-description-based overview/);
  }
});

test('all five discovery media and sampled research leads carry an honest synopsis state without source reads', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, candidateIndex(), 200, {}, filmCatalog, 200, directory, 200);
  assert.equal(nodes.get('film-list').children.length, filmCatalog.films.length);
  assert.match(nodes.get('film-list').textContent, /Synopsis pending source verification/);
  assert.match(nodes.get('research-list').textContent, /Synopsis pending source verification/);
  for (const medium of ['EPISODE', 'FILM', 'LITERATURE', 'SHORT_FORM', 'AUDIO']) {
    nodes.get('discovery-medium').value = medium;
    nodes.get('discovery-filters').fire('input');
    const cards = nodes.get('discovery-list').children.filter((n) => n.tagName === 'article');
    assert.ok(cards.length > 0, `expected ${medium} source-local cards`);
    assert.ok(cards.every((c) => c.textContent.includes('Synopsis pending source verification')));
  }
  assert.equal(nodes.get('briefing-count').textContent, '0');
});

test('a self-attested synopsis sidecar cannot publish unreviewed or mismatched text', async () => {
  const unpinned = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200,
    null, 404, null, 404, synopsisRelease, 200);
  assert.match(unpinned.get('film-list').textContent, /Synopsis pending source verification/);
  assert.doesNotMatch(unpinned.get('film-list').textContent, /Synthetic display fixture/);
  const reviewed = synopsisRelease.synopses[0];
  const pin = { title: reviewed.title, source_locator: reviewed.source_locator,
    overview_evidence_locator: reviewed.overview_evidence_locator,
    source_group: reviewed.source_group, source_input: reviewed.source_input, source_context: reviewed.source_context,
    directory_alias_row_id: null, directory_alias_context: null,
    overview_text: reviewed.overview_text, source_snapshot_date: reviewed.source_snapshot_date,
    research_observation_path: reviewed.research_observation_path,
    research_observation_sha256: reviewed.research_observation_sha256,
    raw_webpage_sha256: null,
    editorial_receipt_sha256: reviewed.editorial_receipt_sha256 };
  const trustedScript = SCRIPT.replace(/const reviewedSynopsisReceipts = new Map\(\[[\s\S]*?\]\);/,
    `const reviewedSynopsisReceipts = new Map([['film:star-trek-2009', ${JSON.stringify(pin)}]]);`);
  assert.notEqual(trustedScript, SCRIPT, 'the test must patch only a deliberately pinned synthetic review fixture');
  const valid = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200,
    null, 404, null, 404, synopsisRelease, 200, trustedScript);
  assert.match(valid.get('film-list').textContent, /Publisher-description-based overview/);
  assert.match(valid.get('film-list').textContent, /Synthetic display fixture/);
  for (const change of [
    (x) => { x.synopses[0].overview_text += ' Changed without review'; },
    (x) => { x.synopses[0].source_locator = 'https://www.startrek.com/movies/star-trek-into-darkness'; },
    (x) => { x.synopses[0].overview_evidence_locator = 'https://www.startrek.com/movies/star-trek-into-darkness'; },
    (x) => { x.synopses[0].overview_evidence_locator = 'https://evil.invalid/tracker'; },
    (x) => { x.synopses[0].directory_alias_row_id = 'directory:film:bogus'; },
    (x) => { x.synopses[0].source_input = 'proposals/forged.json'; },
    (x) => { x.synopses[0].source_snapshot_date = '2025-01-01'; },
    (x) => { x.synopses[0].research_observation_sha256 = '3'.repeat(64); },
    (x) => { x.synopses[0].research_observation_path = 'proposals/research/forgery/observations.json'; },
    (x) => { x.synopses[0].raw_webpage_sha256 = '3'.repeat(64); },
    (x) => { x.synopses[0].coverage_effect = 'CLOSE_READ'; },
    (x) => { x.synopses[0].overview_basis = 'PRIMARY_WORK_CLOSE_READ'; },
    (x) => { x.synopses[0].overview_text = '<script>alert(1)</script>'; }
  ]) {
    const forged = structuredClone(synopsisRelease);
    change(forged);
    const rejected = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200,
      null, 404, null, 404, forged, 200, trustedScript);
    assert.match(rejected.get('film-list').textContent, /Synopsis pending source verification/);
    assert.doesNotMatch(rejected.get('film-list').textContent, /Synthetic display fixture/);
  }
});

test('honest LCARS artwork placeholders render without remote image requests or licensed assets', async () => {
  const discovery = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200, discovery, 200);
  assert.equal(nodes.get('artwork-toggle').disabled, true);
  assert.match(nodes.get('artwork-state').textContent, /not yet display-cleared/);
  assert.match(nodes.get('discovery-list').textContent, /Artwork not sourced/);
  assert.match(nodes.get('discovery-list').textContent, /original index art/);
  assert.match(nodes.get('discovery-list').textContent, /The Doomsday Machine/,
    'the record-identity graphic includes the exact source-local episode title');
  assert.match(nodes.get('discovery-list').textContent, /TOS/,
    'the card graphic includes the accepted source-local series context');
  assert.ok(traverse(nodes.get('discovery-list'), (n) => n.tagName === 'figure').length > 0);
  assert.match(nodes.get('film-list').textContent, /Artwork not sourced/);
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.tagName === 'img').length, 0);
  assert.equal(traverse(nodes.get('film-list'), (n) => n.tagName === 'img').length, 0);
  assert.equal(nodes.get('briefing-count').textContent, '0', 'image presentation never changes admission');
});

test('record graphics disclose medium-specific missing imagery and separate metadata lineage from artwork rights', async () => {
  const discovery = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200, discovery, 200);
  for (const [medium, expectedShort, expectedLong] of [
    ['EPISODE', 'No still', 'No episode still displayed'],
    ['FILM', 'No poster', 'No film poster displayed'],
    ['LITERATURE', 'No cover', 'No book cover displayed']
  ]) {
    nodes.get('discovery-medium').value = medium;
    nodes.get('discovery-filters').fire('input');
    const frame = traverse(nodes.get('discovery-list'), (node) => node.tagName === 'div' &&
      node.className === `artwork-slot artwork-${medium.toLowerCase()}`)[0];
    assert.ok(frame, `${medium} has a source-local visual fallback`);
    const figure = frame.parentNode;
    const caption = traverse(figure, (node) => node.tagName === 'figcaption')[0];
    const provenance = traverse(caption, (node) => node.className === 'artwork-provenance-note');
    const sourceLink = traverse(caption, (node) => node.className === 'artwork-record-source');
    assert.equal(frame.getAttribute('role'), 'img');
    assert.match(frame.getAttribute('aria-label'), new RegExp(expectedLong, 'i'));
    assert.match(frame.textContent, new RegExp(expectedShort, 'i'));
    assert.match(caption.textContent, new RegExp(expectedLong));
    assert.equal(provenance.length, 1);
    assert.match(provenance[0].textContent, /Metadata: .* · no image-rights grant/);
    assert.match(provenance[0].getAttribute('title'), /^Source-local record key: directory:/);
    assert.equal(sourceLink.length, 1);
    assert.equal(sourceLink[0].textContent, 'Record metadata · not image rights');
    assert.match(sourceLink[0].getAttribute('aria-label'), /does not grant image rights/);
    assert.equal(traverse(figure, (node) => node.tagName === 'img').length, 0,
      `${medium} fallback never downloads a source image`);
  }
  assert.equal(nodes.get('briefing-count').textContent, '0');
});

test('each original LCARS record signal is deterministically tied to its exact source-local row, not a licensed image', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200, directory, 200);
  const sample = () => traverse(nodes.get('discovery-list'), (node) =>
    node.tagName === 'div' && /^artwork-slot artwork-/.test(node.className))
    .slice(0, 8).map((frame) => {
      const beacon = traverse(frame.parentNode, (node) => node.className === 'artwork-record-beacon');
      assert.equal(beacon.length, 1, 'each record has one visible abstract signal strip');
      assert.equal(beacon[0].children.length, 8, 'signal is bounded original local geometry');
      assert.ok(beacon[0].children.every((node) => node.tagName === 'span' &&
        ['artwork-beacon-on', 'artwork-beacon-off'].includes(node.className)));
      const key = frame.getAttribute('data-source-local-key');
      assert.ok(key?.startsWith('directory:'), 'source-local key remains exact, never canonical Work identity');
      const label = traverse(frame.parentNode, (node) => node.className === 'artwork-record-label');
      assert.equal(label.length, 1);
      assert.match(label[0].textContent, /^Original signal · [0-9a-f]{8}$/);
      assert.match(frame.getAttribute('aria-label'), /not an official still, poster or cover/);
      assert.match(frame.getAttribute('data-record-phase'), /^[0-7]$/);
      return [key, frame.getAttribute('data-record-phase'), label[0].textContent,
        beacon[0].children.map((node) => node.className).join('|')];
    });
  const first = sample();
  assert.equal(first.length, 8);
  assert.deepEqual(first.map((row) => row[0]), directory.rows.slice(0, 8)
    .map((row) => `directory:${row.row_id}`), 'visual keys map to exact displayed source-local rows');
  assert.ok(new Set(first.map((row) => row[2])).size > 1, 'two different records need not share one generic mark');
  nodes.get('discovery-filters').fire('input');
  assert.deepEqual(sample(), first, 'identical source rows regenerate byte-for-byte identical local signals');
  assert.equal(traverse(nodes.get('discovery-list'), (node) => node.tagName === 'img').length, 0,
    'an original per-record visual must never fetch an external image');
});

test('explicit artwork opt-in displays only same-origin rights-receipted assets with graceful error fallback', async () => {
  assert.ok(SCRIPT.indexOf("img.referrerPolicy = 'no-referrer'") < SCRIPT.indexOf('img.src = remoteLibrary'),
    'privacy policy must be assigned before src could initiate a request');
  assert.ok(SCRIPT.indexOf("img.loading = 'lazy'") < SCRIPT.indexOf('img.src = remoteLibrary'),
    'lazy loading must be assigned before src could initiate a request');
  const unpinned = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200, null, 404, licensedArtwork, 200);
  assert.equal(unpinned.get('artwork-toggle').disabled, true,
    'a manifest with plausible SHA/rights text cannot authorize an unpinned publicity asset');
  assert.match(unpinned.get('artwork-state').textContent, /independently reviewed/);
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200, null, 404,
    licensedArtwork, 200, null, 404, licensedArtworkTestScript);
  const toggle = nodes.get('artwork-toggle');
  assert.equal(toggle.disabled, false);
  assert.equal(toggle.attributes.get('aria-pressed'), 'false');
  assert.equal(traverse(nodes.get('film-list'), (n) => n.tagName === 'img').length, 0, 'nothing auto-loads');
  toggle.fire('click');
  assert.equal(toggle.attributes.get('aria-pressed'), 'true');
  const images = traverse(nodes.get('film-list'), (n) => n.tagName === 'img');
  assert.equal(images.length, 1);
  assert.equal(images[0].parentNode.tagName, 'a', 'authorized image itself links to exact attribution receipt');
  assert.equal(images[0].parentNode.href, licensedArtwork.artwork[0].attribution_url);
  assert.equal(images[0].parentNode.rel, 'noopener noreferrer');
  assert.equal(images[0].parentNode.referrerPolicy, 'no-referrer');
  assert.equal(images[0].src, './licensed-artwork/verified-film-cover.webp');
  assert.equal(images[0].loading, 'lazy');
  assert.equal(images[0].referrerPolicy, 'no-referrer');
  assert.match(images[0].alt, /Licensed publisher artwork/);
  const credits = traverse(nodes.get('film-list'), (n) => n.className === 'artwork-credit');
  assert.equal(credits.length, 1);
  assert.equal(credits[0].href, 'https://commons.wikimedia.org/wiki/File:Synthetic_test_poster.webp');
  assert.match(credits[0].textContent, /Synthetic poster rights fixture/);
  assert.match(nodes.get('film-list').textContent, /Rights-reviewed poster/);
  images[0].fire('error');
  assert.equal(traverse(nodes.get('film-list'), (n) => n.tagName === 'img').length, 0);
  assert.match(nodes.get('film-list').textContent, /Image unavailable/);
  assert.match(nodes.get('film-list').textContent, /Metadata: startrek.com · no image-rights grant/,
    'failed image reverts to provenance-labeled original artwork without losing attribution');
  assert.match(nodes.get('film-list').textContent, /Synthetic poster rights fixture/,
    'attribution remains visible when an authorized image fails to load');
  toggle.fire('click');
  assert.equal(toggle.attributes.get('aria-pressed'), 'false');
  assert.equal(traverse(nodes.get('film-list'), (n) => n.tagName === 'img').length, 0);
});

test('malicious, unreviewed, duplicated or off-origin artwork records are rejected as a whole', async () => {
  const changes = [
    (r) => { r.schema_version = '1.1.0'; },
    (r) => { r.artwork[0].image_path = 'https://evil.example/track.jpg'; },
    (r) => { r.artwork[0].image_path = './licensed-artwork/../secrets.webp'; },
    (r) => { r.artwork[0].image_path = 'data:image/png;base64,AAAA'; },
    (r) => { r.artwork[0].source_locator = 'https://www.startrek.com@evil.invalid/x'; },
    (r) => { r.artwork[0].rights_status = 'NOT_ESTABLISHED'; },
    (r) => { r.artwork[0].image_sha256 = 'unknown'; },
    (r) => { r.artwork[0].rights_receipt_sha256 = 'unknown'; },
    (r) => { r.artwork[0].attribution_url = 'https://evil.example/image'; },
    (r) => { r.artwork[0].attribution_text = '<script>'; },
    (r) => { r.artwork[0].artwork_kind = 'COVER'; },
    (r) => { r.artwork[0].artwork_kind = 'UNVERIFIED'; },
    (r) => { r.artwork[0].admission_status = 'ACCEPTED'; },
    (r) => { r.artwork[0].row_id = 'film:unknown'; },
    (r) => { r.artwork.push(structuredClone(r.artwork[0])); r.artwork_count = 2; },
    (r) => { r.coverage_effect = 'AUDITED'; },
  ];
  for (const change of changes) {
    const bad = structuredClone(licensedArtwork);
    change(bad);
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200, null, 404,
      bad, 200, null, 404, licensedArtworkTestScript);
    assert.equal(nodes.get('artwork-toggle').disabled, true);
    assert.match(nodes.get('artwork-state').textContent, /rejected/);
    assert.equal(traverse(nodes.get('film-list'), (n) => n.tagName === 'img').length, 0);
    assert.equal(nodes.get('film-list').children.length, 2, 'film metadata remains visible');
  }
});

test('Open Library cover claims need a separately reviewed edition-to-cover receipt before any opt-in', async () => {
  // Synthetic *test fixture* only: this title does NOT yet have a row in the
  // accepted public directory. Never attach its cover to the Ring of Fire row.
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const lastBestHopeUrl = 'https://www.simonandschuster.com/books/Star-Trek-Picard-The-Last-Best-Hope/Una-McCormack/Star-Trek-Picard/9781982142186';
  const original = directory.rows.find((row) => row.medium === 'LITERATURE');
  assert.ok(original);
  directory.rows.push({ ...original,
    row_id: 'fixture:last-best-hope-not-published', title: 'Fixture novel — not a public Work',
    context: 'TEST FIXTURE ONLY — literature', source_locator: lastBestHopeUrl,
    source_input: 'proposals/fixtures/artwork-test.json', details: ['Hardcover · ISBN 9781982142186']
  });
  directory.row_count++;
  directory.counts_by_medium.LITERATURE++;
  const apiArtwork = {
    schema_version: '1.2.0', data_status: 'PROVENANCE_REVIEWED_ARTWORK', coverage_effect: 'NONE',
    rights_policy: 'PER_ENTRY_DISPLAY_GATE', artwork_count: 1,
    artwork: [{ row_id: 'directory:fixture:last-best-hope-not-published', provider: 'OPEN_LIBRARY_COVERS_API',
      cover_id: 10157401, isbn: '9781982142186', alt_text: 'Cover image for a fixture novel, via Open Library',
      source_locator: lastBestHopeUrl, rights_status: 'API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED',
      edition_metadata_sha256: '33c016d2aad3cc9457249246ec231cc4d6d3acb31374424430ef7bfe743a2ba0',
      attribution_url: 'https://openlibrary.org/isbn/9781982142186'
    }]
  };
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, apiArtwork, 200);
  assert.equal(nodes.get('artwork-toggle').disabled, true,
    'a well-formed ISBN, cover ID and metadata digest in the untrusted sidecar cannot self-certify an edition match');
  assert.match(nodes.get('artwork-state').textContent, /independently reviewed.*crosswalk receipt/);
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.tagName === 'img').length, 0);
  nodes.get('artwork-toggle').fire('click');
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.tagName === 'img').length, 0,
    'clicking a disabled artwork toggle still cannot load an external image');
  const forged = structuredClone(apiArtwork);
  forged.artwork[0].row_id = `directory:${original.row_id}`;
  const rejected = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, forged, 200);
  assert.equal(rejected.get('artwork-toggle').disabled, true, 'different novel may never inherit this cover');

  // Matching the target row's source_locator is insufficient: a cover from a
  // different book or edition can still carry a well-shaped ISBN/hash pair.
  const crossEdition = structuredClone(apiArtwork);
  crossEdition.artwork[0].row_id = `directory:${original.row_id}`;
  crossEdition.artwork[0].source_locator = original.source_locator;
  const mismatched = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, crossEdition, 200);
  assert.equal(mismatched.get('artwork-toggle').disabled, true,
    'cover ISBN must identify the same publisher edition as the directory row, not merely share its locator');
  assert.match(mismatched.get('artwork-state').textContent, /source-local edition/);

  const alternateEdition = structuredClone(apiArtwork);
  alternateEdition.artwork[0].row_id = `directory:${original.row_id}`;
  alternateEdition.artwork[0].source_locator = original.source_locator;
  alternateEdition.artwork[0].isbn = '9781668095904'; // paperback; row URL identifies hardcover
  alternateEdition.artwork[0].attribution_url = 'https://openlibrary.org/isbn/9781668095904';
  const wrongEdition = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, alternateEdition, 200);
  assert.equal(wrongEdition.get('artwork-toggle').disabled, true,
    'a listed alternate edition ISBN is not the specific edition identified by the row URL');
  assert.match(wrongEdition.get('artwork-state').textContent, /source URL edition/);

  const sameEdition = structuredClone(apiArtwork);
  sameEdition.artwork[0].row_id = `directory:${original.row_id}`;
  sameEdition.artwork[0].source_locator = original.source_locator;
  sameEdition.artwork[0].isbn = '9781668095898';
  sameEdition.artwork[0].attribution_url = 'https://openlibrary.org/isbn/9781668095898';
  const matching = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, sameEdition, 200);
  assert.equal(matching.get('artwork-toggle').disabled, true,
    'the exact publisher-edition ISBN still cannot certify an unrelated cover ID and digest');
  assert.match(matching.get('artwork-state').textContent, /crosswalk receipt/);

  const unlistedEdition = structuredClone(apiArtwork);
  unlistedEdition.artwork[0].isbn = '9781982194833';
  unlistedEdition.artwork[0].attribution_url = 'https://openlibrary.org/isbn/9781982194833';
  const unlisted = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, unlistedEdition, 200);
  assert.equal(unlisted.get('artwork-toggle').disabled, true);
  assert.match(unlisted.get('artwork-state').textContent, /source-local edition/,
    'unlisted ISBN rejected before any independently reviewed crosswalk lookup');

  const forgedCoverId = structuredClone(sameEdition);
  forgedCoverId.artwork[0].cover_id = 123456;
  const wrongCover = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, forgedCoverId, 200);
  assert.equal(wrongCover.get('artwork-toggle').disabled, true, 'a plausible but unreviewed cover ID cannot self-certify');

  const forgedDigest = structuredClone(sameEdition);
  forgedDigest.artwork[0].edition_metadata_sha256 = 'a'.repeat(64);
  const wrongDigest = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, forgedDigest, 200);
  assert.equal(wrongDigest.get('artwork-toggle').disabled, true, 'a plausible but unreviewed metadata hash cannot self-certify');

  for (const medium of ['SHORT_FORM', 'AUDIO']) {
    const sourceRow = directory.rows.find((row) => row.medium === medium);
    assert.ok(sourceRow, `valid ${medium} control exists`);
    const nonLiterary = structuredClone(apiArtwork);
    nonLiterary.artwork[0].row_id = `directory:${sourceRow.row_id}`;
    nonLiterary.artwork[0].source_locator = sourceRow.source_locator;
    const rejectedMedium = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, nonLiterary, 200);
    assert.equal(rejectedMedium.get('artwork-toggle').disabled, true,
      `Open Library cover previews are not allowed on ${medium} rows`);
  }
});

test('only four independently visually identified fictional-autobiography jackets are opt-in; a misidentified title page is held', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const reviewed = [
    ['literature:prh-autobiography-kirk', '9781783297481', 13083310,
      'dd84f9c51b9ee75de748b3ac542e74c9099d4eac0882ffcf97877fc182fb13aa'],
    ['literature:prh-autobiography-picard', '9781785659409', 10694457,
      '733e32b6e06efcca3392046968e4b34d6fa92747c223e012665aebf39df4644f'],
    ['literature:prh-autobiography-janeway', '9781789095333', 12097815,
      'b70790160ac39ca865e9447684df05b45f601c3004c7a7e0d2384c23701cdf09'],
    ['literature:prh-autobiography-spock', '9781785659416', 11945787,
      'b5b382d37755a124b0298ae86deebec1fadf1979c526ce5e47304c331892bc2d']
  ];
  const artwork = reviewed.map(([id, isbn, cover, sha]) => {
    const source = directory.rows.find((row) => row.row_id === id);
    assert.ok(source, `exact accepted source row ${id} exists`);
    assert.ok(source.details.some((detail) => detail.includes(isbn)));
    return {
      row_id: `directory:${id}`, provider: 'OPEN_LIBRARY_COVERS_API', cover_id: cover, isbn,
      alt_text: `Optional Open Library jacket preview for ${source.title}; copyright unresolved`,
      source_locator: source.source_locator,
      rights_status: 'API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED',
      edition_metadata_sha256: sha, attribution_url: `https://openlibrary.org/isbn/${isbn}`
    };
  });
  const sidecar = { schema_version: '1.2.0', data_status: 'PROVENANCE_REVIEWED_ARTWORK',
    coverage_effect: 'NONE', rights_policy: 'PER_ENTRY_DISPLAY_GATE',
    artwork_count: artwork.length, artwork };
  // The shipped release-sidecar is independently validated by the Pages
  // packaging gate. Check the actual bytes here too, so a future mismatch
  // between the four code-pinned jackets and public sidecar fails visibly.
  const shipped = JSON.parse(readFileSync(new URL('../explorer/artwork-catalog.json', import.meta.url), 'utf8'));
  const key = (entry) => [entry.row_id, entry.isbn, entry.cover_id, entry.edition_metadata_sha256];
  assert.deepEqual(shipped.artwork.map(key), sidecar.artwork.map(key));
  assert.equal(shipped.schema_version, '1.2.0');
  assert.equal(shipped.coverage_effect, 'NONE');
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, shipped, 200);
  assert.equal(nodes.get('artwork-toggle').disabled, false);
  assert.match(nodes.get('artwork-toggle').textContent, /Show sourced artwork \(4 previews\)/);
  assert.match(nodes.get('artwork-state').textContent, /4 Open Library API previews/);
  assert.equal(nodes.get('artwork-nav-link').hidden, false,
    'an accepted image manifest exposes a direct top navigation entry');
  assert.equal(nodes.get('artwork-nav-count').textContent, '4');
  assert.equal(nodes.get('artwork-gallery').hidden, false,
    'the source-linked LCARS gallery itself should be discoverable before opt-in');
  assert.equal(nodes.get('artwork-gallery').attributes.get('data-preview-state'), 'off');
  assert.equal(nodes.get('artwork-gallery-list').children.length, 4,
    'four sourced LCARS key cards must be discoverable without external preview requests');
  assert.equal(traverse(nodes.get('artwork-gallery-list'), (n) => n.tagName === 'img').length, 0,
    'the visible gallery shell must not create any remote image element before opt-in');
  assert.equal(traverse(nodes.get('artwork-gallery-list'), (n) => n.className === 'artwork-image-link').length, 0,
    'no image links to external editions appear before visitor opt-in');
  assert.match(nodes.get('artwork-gallery-summary').textContent, /nothing is fetched before that choice/);
  assert.equal(traverse(nodes.get('artwork-gallery-list'), (n) => n.className === 'artwork-record-source').length, 4,
    'each visible placeholder links to its own source record');
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.tagName === 'img').length, 0,
    'there are no external image URLs in the DOM until a visitor explicitly opts in');
  nodes.get('discovery-query').value = 'autobiography';
  nodes.get('discovery-filters').fire('input');
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.tagName === 'img').length, 0,
    'the four exact cover-bearing rows themselves cannot initiate off-site image requests before opt-in');
  nodes.get('artwork-toggle').fire('click');
  assert.equal(nodes.get('artwork-gallery').hidden, false);
  assert.equal(nodes.get('artwork-gallery').attributes.get('data-preview-state'), 'on');
  assert.equal(nodes.get('artwork-gallery-list').children.length, 4,
    'a dedicated art gallery makes all four source-matched images discoverable without hiding in pagination');
  assert.match(nodes.get('artwork-gallery-summary').textContent, /4 of 4 individually source-bound image options.*do not add Works/);
  assert.equal(traverse(nodes.get('artwork-gallery-list'), (n) => n.tagName === 'img').length, 4);
  const rendered = traverse(nodes.get('discovery-list'), (n) => n.tagName === 'img');
  assert.equal(rendered.length, 4, 'all four visually checked edition jackets are bound to their proper rows');
  assert.ok(rendered.every((img) => img.parentNode.tagName === 'a' &&
    img.parentNode.href === `https://openlibrary.org/isbn/${artwork.find((row) =>
      `https://covers.openlibrary.org/b/id/${row.cover_id}-S.jpg?default=false` === img.src)?.isbn}`),
  'each clicked cover must navigate to the exact same ISBN edition provenance, never to an unrelated record');
  assert.ok(rendered.every((img) => img.parentNode.target === '_blank' &&
    img.parentNode.rel === 'noopener noreferrer' && img.parentNode.referrerPolicy === 'no-referrer'));
  assert.deepEqual(rendered.map((img) => img.src).sort(),
    reviewed.map(([, , cover]) => `https://covers.openlibrary.org/b/id/${cover}-S.jpg?default=false`).sort());
  assert.ok(rendered.every((img) => img.loading === 'lazy' && img.referrerPolicy === 'no-referrer'));
  assert.match(nodes.get('discovery-list').textContent, /Open Library cover preview · copyright unresolved/);
  const credits = traverse(nodes.get('discovery-list'), (n) => n.className === 'artwork-credit');
  assert.equal(credits.length, 4);
  assert.ok(credits.every((link) => link.rel === 'noopener noreferrer'));
  const findLinks = traverse(nodes.get('artwork-gallery-list'), (n) => n.className === 'artwork-gallery-locate');
  assert.equal(findLinks.length, 4);
  findLinks[0].fire('click');
  assert.match(nodes.get('discovery-query').value, /autobiography/i);
  assert.equal(nodes.get('discovery-medium').value, 'LITERATURE');
  assert.equal(nodes.get('discovery-directory').focused, true,
    'the gallery locator preserves keyboard focus on the filtered results');
  nodes.get('artwork-toggle').fire('click');
  assert.equal(nodes.get('artwork-gallery').hidden, false);
  assert.equal(nodes.get('artwork-gallery').attributes.get('data-preview-state'), 'off');
  assert.equal(nodes.get('artwork-gallery-list').children.length, 4,
    'hiding external imagery preserves the source-linked local visual index');
  assert.equal(traverse(nodes.get('artwork-gallery-list'), (n) => n.tagName === 'img').length, 0,
    'hiding must remove remote images from the gallery too');
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.tagName === 'img').length, 0,
    'hiding imagery must remove all remote image elements, not merely hide gallery visuals');

  // A matching ISBN/JSON digest alone is not sufficient: this purported
  // Enterprise War cover ID actually displayed an interior title page.
  const heldRow = directory.rows.find((row) => row.row_id === 'literature:proposed-lit-discovery-enterprise-war');
  assert.ok(heldRow);
  const held = structuredClone(sidecar);
  held.artwork.push({
    ...artwork[0], row_id: `directory:${heldRow.row_id}`,
    source_locator: heldRow.source_locator, isbn: '9781982113315', cover_id: 12857937,
    attribution_url: 'https://openlibrary.org/isbn/9781982113315',
    edition_metadata_sha256: 'ecaca36ebb2419de7d96214f8ed8145c13bf1d90a20d0e72ac62e71090425208'
  });
  held.artwork_count++;
  const rejected = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200, held, 200);
  assert.equal(rejected.get('artwork-nav-link').hidden, true,
    'a rejected image manifest must not expose a dead artwork navigation target');
  assert.equal(rejected.get('artwork-nav-count').textContent, '—');
  assert.equal(rejected.get('artwork-toggle').disabled, true,
    'a visually rejected interior title page cannot be marketed as a book cover');
  assert.match(rejected.get('artwork-state').textContent, /crosswalk receipt/);
});

test('additive v1.3 medium jacket URL preserves four v1.2 small covers for old browser clients', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const small = JSON.parse(readFileSync(new URL('../explorer/artwork-catalog.json', import.meta.url), 'utf8'));
  assert.equal(small.schema_version, '1.2.0', 'the legacy URL must remain unchanged for old cached app.js');
  const medium = structuredClone(small);
  medium.schema_version = '1.3.0';
  for (const entry of medium.artwork) entry.image_size = 'M';
  const nodes = await runMediumArtwork(directory, medium, 200, small);
  assert.equal(nodes.get('artwork-toggle').disabled, false);
  assert.equal(nodes.get('artwork-gallery').hidden, false,
    'accepted #420 preserves source-linked LCARS gallery before image consent');
  assert.equal(nodes.get('artwork-gallery').attributes.get('data-preview-state'), 'off');
  assert.equal(nodes.get('artwork-gallery-list').children.length, 4);
  assert.equal(traverse(nodes.get('artwork-gallery-list'), (n) => n.tagName === 'img').length, 0);
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.tagName === 'img').length, 0,
    'no Open Library images enter the DOM before the explicit consent click');
  nodes.get('artwork-toggle').fire('click');
  const gallery = nodes.get('artwork-gallery-list');
  const galleryImages = traverse(gallery, (n) => n.tagName === 'img');
  assert.equal(galleryImages.length, 4);
  assert.ok(galleryImages.every((img) => img.parentNode.tagName === 'a' &&
    img.parentNode.className === 'artwork-image-link' &&
    img.parentNode.href === medium.artwork.find((item) =>
      img.src === `https://covers.openlibrary.org/b/id/${item.cover_id}-M.jpg?default=false`)?.attribution_url &&
    img.parentNode.target === '_blank' && img.parentNode.rel === 'noopener noreferrer' &&
    img.parentNode.referrerPolicy === 'no-referrer'),
  'clicking each 180px jacket opens its exact ISBN edition source with a protected external link');
  assert.deepEqual(galleryImages.map((img) => img.src).sort(),
    medium.artwork.map((a) => `https://covers.openlibrary.org/b/id/${a.cover_id}-M.jpg?default=false`).sort());
  assert.ok(galleryImages.every((img) => img.width === 180 &&
    img.height >= 271 && img.height <= 275 && img.loading === 'lazy' &&
    img.referrerPolicy === 'no-referrer'));
  assert.equal(traverse(gallery, (n) => n.className === 'artwork-panel artwork-panel-medium').length, 4,
    'native-width medium jackets need their own responsive gallery presentation');
  assert.match(gallery.textContent, /Medium Open Library API jacket preview · 180 pixels wide .*copyright unresolved/);
  assert.doesNotMatch(gallery.textContent, /Enterprise War/);
  const credits = traverse(gallery, (n) => n.className === 'artwork-credit');
  assert.equal(credits.length, 4);
  assert.ok(credits.every((a) => /^https:\/\/openlibrary\.org\/isbn\/978\d{10}$/.test(a.href)));
  const firstMediumImage = galleryImages[0];
  const firstMediumSrc = firstMediumImage.src;
  firstMediumImage.fire('error');
  assert.match(firstMediumImage.src, /-S\.jpg\?default=false$/,
    'a failed M request may retry only its exact already-approved S jacket');
  assert.equal(firstMediumImage.referrerPolicy, 'no-referrer');
  assert.equal(firstMediumImage.loading, 'lazy');
  firstMediumImage.fire('error');
  assert.equal(traverse(gallery, (n) => n === firstMediumImage).length, 0,
    'a failed M and S must return to original LCARS art, without an infinite network retry');
  assert.match(gallery.textContent, /Sourced image unavailable · LCARS record graphic/);
  assert.notEqual(firstMediumSrc, firstMediumImage.src);
  const pendingMediumImage = galleryImages[1];
  const pendingSrc = pendingMediumImage.src;
  nodes.get('artwork-toggle').fire('click');
  assert.equal(traverse(gallery, (n) => n.tagName === 'img').length, 0);
  pendingMediumImage.fire('error');
  assert.equal(pendingMediumImage.src, pendingSrc,
    'late image error after opt-out must not initiate an S fallback request');
  nodes.get('artwork-toggle').fire('click');
  const renewedMediumImages = traverse(gallery, (n) => n.tagName === 'img');
  assert.equal(renewedMediumImages.length, 4, 're-opt-in creates a fresh image generation');
  assert.ok(renewedMediumImages.every((img) => img.isConnected));
  assert.equal(pendingMediumImage.isConnected, false);
  pendingMediumImage.fire('error');
  assert.equal(pendingMediumImage.src, pendingSrc,
    'late detached M error after Show-Hide-Show must not use the renewed consent to fetch S');
  assert.equal(traverse(gallery, (n) => n.tagName === 'img').length, 4,
    'a stale callback must not mutate current-generation image nodes');

  const old = await runMediumArtwork(directory, null, 404, small);
  assert.equal(old.get('artwork-toggle').disabled, false, 'v1.2 fallback must remain displayable');
  old.get('artwork-toggle').fire('click');
  const oldImages = traverse(old.get('artwork-gallery-list'), (n) => n.tagName === 'img');
  assert.equal(oldImages.length, 4);
  assert.ok(oldImages.every((img) => /-S\.jpg\?default=false$/.test(img.src)));
  assert.equal(traverse(old.get('artwork-gallery-list'), (n) => n.className === 'artwork-panel artwork-panel-medium').length, 0);
});

test('forged medium manifests fail independently and cannot erase approved small jackets', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const small = JSON.parse(readFileSync(new URL('../explorer/artwork-catalog.json', import.meta.url), 'utf8'));
  const medium = structuredClone(small);
  medium.schema_version = '1.3.0';
  for (const entry of medium.artwork) entry.image_size = 'M';
  const mutations = [
    (data) => { data.artwork[0].image_size = 'L'; },
    (data) => { delete data.artwork[0].image_size; },
    (data) => { data.artwork.pop(); data.artwork_count--; },
    (data) => { data.artwork.shift(); data.artwork_count--; },
    (data) => { data.artwork[0].cover_id = 12857937; },
    (data) => { data.artwork[0].provider = 'UNREVIEWED_COVER_HOST'; },
    (data) => { data.artwork[0].rights_status = 'PUBLIC_DISPLAY_PERMISSION_VERIFIED'; },
    (data) => { data.artwork[0].alt_text = 'Paramount officially licensed original movie frame; public domain rights granted'; },
    (data) => { data.artwork[0].attribution_url = 'https://evil.example/'; },
    (data) => { data.schema_version = '1.2.0'; },
  ];
  for (const mutate of mutations) {
    const forged = structuredClone(medium);
    mutate(forged);
    const nodes = await runMediumArtwork(directory, forged, 200, small);
    assert.equal(nodes.get('artwork-toggle').disabled, false,
      'an invalid v1.3 candidate must not break separately reviewed v1.2 fallback');
    assert.match(nodes.get('artwork-state').textContent, /Medium rendition held/);
    nodes.get('artwork-toggle').fire('click');
    const urls = traverse(nodes.get('artwork-gallery-list'), (n) => n.tagName === 'img').map((n) => n.src);
    assert.equal(urls.length, 4);
    assert.ok(urls.every((url) => /-S\.jpg\?default=false$/.test(url)), 'forged variant must never be fetched');
  }
  const missingOld = await runMediumArtwork(directory, medium, 200);
  assert.equal(missingOld.get('artwork-toggle').disabled, false, 'valid new medium manifest stands alone');
  missingOld.get('artwork-toggle').fire('click');
  assert.equal(traverse(missingOld.get('artwork-gallery-list'), (n) => n.tagName === 'img').length, 4);
});

test('PRH distributor discovery leads require exact fictional-memoir source scope', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const index = directory.rows.findIndex((row) => row.candidate_kind === 'FICTIONAL_MEMOIR');
  assert.ok(index >= 0, 'accepted discovery has a source-local fictional memoir lead');
  const baseline = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200);
  assert.match(baseline.get('discovery-state').textContent, /1,214/);
  for (const mutate of [
    (r) => { r.candidate_kind = 'NOVEL'; },
    (r) => { r.source_group = 'publisher:simonandschuster.com'; },
    (r) => { r.medium = 'FILM'; },
    (r) => { r.source_locator = 'https://www.penguinrandomhouse.com/books/unrelated/'; },
    (r) => { r.source_locator = 'https://www.penguinrandomhouse.com/books/250795/unrelated?tracking=1'; }
  ]) {
    const forged = structuredClone(directory);
    mutate(forged.rows[index]);
    if (forged.rows[index].medium === 'FILM') {
      forged.counts_by_medium.LITERATURE--;
      forged.counts_by_medium.FILM++;
    }
    const rejected = await runWithIndex(catalog, 200, null, 404, {}, null, 404, forged, 200);
    assert.match(rejected.get('discovery-state').textContent, /rejected/,
      'PRH host never becomes a general-purpose source allowlist');
  }
});

test('Open Library variant fails closed for forged URL, identifier, medium and rights', async () => {
  const bad = structuredClone(licensedArtwork);
  bad.artwork[0] = { row_id: 'film:star-trek-2009', provider: 'OPEN_LIBRARY_COVERS_API',
    cover_id: 10157401, isbn: '9781982142186', alt_text: 'Unreviewed unrelated art',
    source_locator: filmCatalog.films[0].source_locator, rights_status: 'API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED',
    edition_metadata_sha256: 'a'.repeat(64), attribution_url: 'https://openlibrary.org/isbn/9781982142186' };
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200, null, 404, bad, 200);
  assert.equal(nodes.get('artwork-toggle').disabled, true, 'book-cover API cannot silently decorate a film');
});

test('catalog-only payload never admits injected briefings or records', async () => {
  const nodes = await runWithIndex({
    schema_version: '1.0.0',
    build: { data_status: 'MISSION_CATALOG_ONLY', projection_hash: null },
    missions: [{ id: 'tng', title: 'The Next Generation', focus: 'Exploration and ethics' }],
    briefings: [{ id: 'b1', title: 'Not admitted', mission_id: 'tng' }],
    records: [{ id: 'r1', title: 'Not admitted', mission_id: 'tng' }]
  });
  assert.equal(nodes.get('mission-count').textContent, '1');
  assert.equal(nodes.get('briefing-count').textContent, '0');
  assert.equal(nodes.get('record-count').textContent, '0');
  assert.equal(nodes.get('mission-list').children.length, 1);
  assert.equal(nodes.get('briefing-list').children.length, 0);
  assert.equal(nodes.get('record-list').children.length, 0);
  assert.match(nodes.get('data-state').textContent, /Catalog-only transmission/);
  assert.match(nodes.get('briefing-empty').textContent, /no Briefings/);
});

test('untrusted titles render as literal text; javascript links are not created', async () => {
  const attack = '<script>globalThis.pwned=true</script>';
  const nodes = await runWithIndex({
    schema_version: '1.0.0',
    build: { data_status: 'GOVERNED_PROJECTION', projection_hash: 'sha256:' + 'a'.repeat(64) },
    missions: [{ id: 'tng', title: attack, focus: 'Source check' }],
    briefings: [{ id: 'b1', title: '<img src=x onerror=alert(1)>', mission_id: 'tng', season: 1, episode: 1, admission_status: 'PROPOSED' }],
    records: [{ id: 'r1', title: attack, summary: 'Contested record', kind: 'episode', mission_id: 'tng', briefing_id: 'b1', projection_status: 'CONTESTED', source_ids: ['SRC-1'], source_refs: [
      { label: 'Unsafe', href: 'javascript:alert(1)' },
      { label: 'Source record', href: 'https://example.org/evidence' }
    ] }]
  });
  assert.equal(nodes.get('briefing-count').textContent, '1');
  assert.equal(nodes.get('record-count').textContent, '1');
  assert.equal(traverse(nodes.get('record-list'), (node) => node.tagName === 'script').length, 0);
  assert.match(nodes.get('record-list').textContent, /<script>globalThis.pwned=true<\/script>/);
  const links = traverse(nodes.get('record-list'), (node) => node.tagName === 'a');
  assert.equal(links.length, 1);
  assert.equal(links[0].href, 'https://example.org/evidence');
  assert.match(nodes.get('record-list').textContent, /Briefing \(episode\)/);
  assert.match(nodes.get('data-state').textContent, /index declares a governed projection/);
});

test('search filters visible cards without changing dataset counts', async () => {
  const nodes = await runWithIndex({
    schema_version: '1.0.0',
    build: { data_status: 'MISSION_CATALOG_ONLY', projection_hash: null },
    missions: [{ id: 'tos', title: 'The Original Series' }, { id: 'voy', title: 'Voyager' }],
    briefings: [], records: []
  });
  nodes.get('search-input').value = 'Voyager';
  nodes.get('filters').fire('input');
  assert.equal(nodes.get('mission-list').children.length, 1);
  assert.match(nodes.get('result-summary').textContent, /1 matching entry/);
  assert.equal(nodes.get('mission-count').textContent, '2');
  const event = { prevented: false, preventDefault() { this.prevented = true; } };
  nodes.get('filters').fire('submit', event);
  assert.equal(event.prevented, true, 'Enter should not submit and reload the page');
});

test('large briefing results can be reached with Show next', async () => {
  const nodes = await runWithIndex({
    schema_version: '1.0.0',
    build: { data_status: 'GOVERNED_PROJECTION', projection_hash: 'sha256:' + 'b'.repeat(64) },
    missions: [{ id: 'tng', title: 'Star Trek: The Next Generation' }],
    briefings: Array.from({ length: 80 }, (_, i) => ({ id: `b${i}`, title: `Episode ${i + 1}`, mission_id: 'tng' })),
    records: []
  });
  const container = nodes.get('briefing-list');
  assert.equal(container.children.length, 73, '72 briefings and a load-more button');
  assert.equal(container.children.at(-1).tagName, 'button');
  container.children.at(-1).fire('click');
  assert.equal(container.children.length, 80, 'all 80 briefings become reachable');
  assert.equal(container.children[72].focused, true, 'focus first newly shown briefing after Show next');
  assert.equal(container.children[72].attributes.get('tabindex'), '-1', 'temporary reading target is programmatically focusable');
});

test('missing or incompatible index gives an honest no-data state', async () => {
  const missing = await runWithIndex(null, 404);
  assert.equal(missing.get('record-count').textContent, '—');
  assert.equal(missing.get('film-top-count').textContent, '—');
  assert.match(missing.get('notice').textContent, /not been built yet/);
  assert.match(missing.get('result-summary').textContent, /matching entries is unknown/);
  assert.equal(missing.get('missions').hidden, true, 'unavailable catalog is not an empty search result');
  const invalid = await runWithIndex({ schema_version: '0.0.1' });
  assert.equal(invalid.get('mission-count').textContent, '—');
  assert.match(invalid.get('notice').textContent, /incompatible schema/);
  const forged = await runWithIndex({
    schema_version: '1.0.0', build: { data_status: 'GOVERNED_PROJECTION', projection_hash: 'sha256:abc' },
    missions: [{ id: 'tng', title: 'TNG' }], briefings: [], records: []
  });
  assert.equal(forged.get('record-count').textContent, '—');
  assert.match(forged.get('notice').textContent, /verified projection hash/);
});

test('publisher film discovery remains available when the separate Mission index is missing', async () => {
  const nodes = await runWithIndex(null, 404, null, 404, {}, filmCatalog, 200);
  assert.equal(nodes.get('film-top-count').textContent, '2');
  assert.equal(nodes.get('film-list').children.length, 2);
  assert.equal(nodes.get('mission-count').textContent, '—');
  assert.match(nodes.get('result-summary').textContent, /unknown/);
});

test('separate official film discovery remains unadmitted and strictly source-scoped', async () => {
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200);
  assert.equal(nodes.get('film-top-count').textContent, '2');
  assert.equal(nodes.get('film-nav-count').textContent, '2');
  assert.equal(nodes.get('film-list').children.length, 2);
  assert.match(nodes.get('film-list').textContent, /Star Trek: Section 31/);
  nodes.get('film-query').value = 'section 31';
  nodes.get('film-filters').fire('input');
  assert.equal(nodes.get('film-list').children.length, 1, 'film discovery is separately searchable');
  assert.match(nodes.get('film-summary').textContent, /1 of 2/);
  assert.equal(nodes.get('briefing-count').textContent, '0', 'discovered movies do not create Briefings');
  const forged = structuredClone(filmCatalog);
  forged.films[0].admission_status = 'ACCEPTED';
  const rejected = await runWithIndex(catalog, 200, null, 404, {}, forged, 200);
  assert.equal(rejected.get('film-top-count').textContent, '—');
  assert.equal(rejected.get('film-list').children.length, 0);
  assert.equal(rejected.get('mission-count').textContent, '2', 'invalid optional film data does not corrupt governed catalog');
  const malicious = structuredClone(filmCatalog);
  malicious.films[0].source_locator = 'https://example.com/movies/star-trek-2009';
  const quarantined = await runWithIndex(catalog, 200, null, 404, {}, malicious, 200);
  assert.equal(quarantined.get('film-top-count').textContent, '—');
  const duplicate = structuredClone(filmCatalog);
  duplicate.films[1].source_locator = duplicate.films[0].source_locator;
  const deduped = await runWithIndex(catalog, 200, null, 404, {}, duplicate, 200);
  assert.equal(deduped.get('film-top-count').textContent, '—');
});

test('multimedia source-local directory is independently searchable, paged, and never admitted', async () => {
  const discovery = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, discovery, 200);
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,214');
  assert.equal(nodes.get('discovery-top-count').textContent, '1,214',
    'the primary status board shows source-local directory size, distinct from twelve series Missions');
  assert.equal(nodes.get('discovery-episode-count').textContent, '1,155',
    'episode observations surface as source-local leads, not accepted episode Works');
  assert.equal(nodes.get('discovery-literature-count').textContent, '9',
    'literary discovery leads surface separately from admitted Works');
  nodes.get('discovery-query').value = 'Voyager';
  nodes.get('discovery-medium').value = 'AUDIO';
  nodes.get('discovery-series').value = 'VOY';
  nodes.get('discovery-tag').value = 'source:not-present';
  nodes.get('discovery-episode-count').fire('click');
  assert.equal(nodes.get('discovery-directory').focused, true,
    'count drilldown focuses the newly filtered directory section');
  assert.equal(nodes.get('discovery-medium').value, 'EPISODE');
  assert.equal(nodes.get('discovery-query').value, '');
  assert.equal(nodes.get('discovery-series').value, 'all');
  assert.equal(nodes.get('discovery-tag').value, 'all');
  assert.match(nodes.get('discovery-summary').textContent, /^1,155 source-local metadata rows match/);
  nodes.get('discovery-literature-count').fire('click');
  assert.equal(nodes.get('discovery-medium').value, 'LITERATURE');
  assert.match(nodes.get('discovery-summary').textContent, /^9 source-local metadata rows match/);
  assert.equal(nodes.get('discovery-list').children.length, 9);
  nodes.get('discovery-medium').value = 'all';
  nodes.get('discovery-filters').fire('change');
  assert.match(nodes.get('discovery-state').textContent, /not a franchise total/);
  assert.match(nodes.get('discovery-metrics').textContent, /Episode refs: 1,155/);
  assert.match(nodes.get('discovery-metrics').textContent, /Film rows: 14/);
  assert.match(nodes.get('discovery-metrics').textContent, /Literary leads: 9/);
  assert.match(nodes.get('discovery-metrics').textContent, /Short-form releases: 35/);
  assert.match(nodes.get('discovery-metrics').textContent, /Audio containers: 1/);
  assert.match(nodes.get('discovery-list').textContent, /Data receipt: explorer\/research-leads\.json/);
  assert.equal(nodes.get('briefing-count').textContent, '0');
  assert.equal(nodes.get('discovery-list').children.length, 41, '40 rows and Show next, not 1,214 cards on load');
  nodes.get('discovery-list').children.at(-1).fire('click');
  assert.equal(nodes.get('discovery-list').children.length, 81, 'second directory page is reachable');
  assert.equal(nodes.get('discovery-list').children[40].focused, true, 'focus first newly shown source row');
  assert.equal(nodes.get('discovery-list').children[40].attributes.get('tabindex'), '-1', 'new directory row is programmatically focusable');
  nodes.get('discovery-query').value = 'Voyager';
  nodes.get('discovery-filters').fire('input');
  assert.match(nodes.get('discovery-summary').textContent, /source-local metadata rows match/);
  assert.notEqual(nodes.get('discovery-list').children.length, 0, 'full series name searches source-local VOY rows');
  assert.match(nodes.get('discovery-list').textContent, /VOY/, 'Voyager search includes VOY source-local results');
  nodes.get('discovery-query').value = '';
  nodes.get('discovery-filters').fire('input');
  nodes.get('discovery-medium').value = 'SHORT_FORM';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 35);
  assert.match(nodes.get('discovery-list').textContent, /Announced promotional release order/);
  assert.match(nodes.get('discovery-list').textContent, /Star Trek: Scouts/);
  nodes.get('discovery-medium').value = 'AUDIO';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 1);
  assert.match(nodes.get('discovery-list').textContent, /Khan/);
  nodes.get('discovery-medium').value = 'LITERATURE';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 9);
  assert.match(nodes.get('discovery-list').textContent, /Ring of Fire/);
  assert.match(nodes.get('discovery-list').textContent, /ISBN 9781668095898/);
  assert.match(nodes.get('discovery-list').textContent, /Second Self/);
  assert.match(nodes.get('discovery-list').textContent, /The High Country/);
  assert.match(nodes.get('discovery-list').textContent, /The Enterprise War/);
  assert.match(nodes.get('discovery-list').textContent, /ISBN 9781797149226/);
  assert.match(nodes.get('discovery-list').textContent, /The Autobiography of Kathryn Janeway/);
  assert.match(nodes.get('discovery-list').textContent, /The Autobiography of Benjamin Sisko/);
  nodes.get('discovery-medium').value = 'all';
  nodes.get('discovery-query').value = 'Starstruck';
  nodes.get('discovery-filters').fire('input');
  assert.match(nodes.get('discovery-list').textContent, /inferred/, 'studio title-list position is not disguised as official numbering');
  assert.match(nodes.get('discovery-list').textContent, /Ep#103/, 'isolated image caption remains same-source metadata');
  nodes.get('discovery-medium').value = 'all';
  nodes.get('discovery-query').value = 'Section 31';
  nodes.get('discovery-filters').fire('input');
  assert.equal(nodes.get('discovery-list').children.length, 1);
  assert.match(nodes.get('discovery-list').textContent, /Section 31/);
  assert.equal(nodes.get('mission-count').textContent, '2', 'directory is segregated from Mission catalog');
});

test('two separately pinned Picard literary proposals augment only Explorer and Lore view, not historical ledger', async () => {
  const historical = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const picardBytes = readFileSync(new URL('../explorer/picard-literature-overlay.json', import.meta.url));
  const nodes = await runWithIndex(catalog, 200, null, 404, { picardBytes, picardStatus: 200 },
    null, 404, historical, 200);
  assert.equal(historical.rows.length, 1214, 'accepted metadata recheck denominator stays immutable');
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,216');
  assert.equal(nodes.get('discovery-top-count').textContent, '1,216');
  assert.equal(nodes.get('discovery-literature-count').textContent, '11');
  assert.match(nodes.get('discovery-state').textContent, /1,214 original source-local rows \+ 2 separately pinned Picard metadata proposals/);
  nodes.get('discovery-query').value = 'Rogue Elements';
  nodes.get('discovery-medium').value = 'LITERATURE';
  nodes.get('discovery-filters').fire('change');
  assert.match(nodes.get('discovery-summary').textContent, /^1 source-local metadata rows match/);
  assert.match(nodes.get('discovery-list').textContent, /John Jackson Miller/);
  assert.match(nodes.get('discovery-list').textContent, /UNVERIFIED_METADATA|unadmitted discovery/);
  assert.equal(traverse(nodes.get('discovery-list'), (node) => node.tagName === 'img').length, 0,
    'unreleased cover art is not silently fetched');
  nodes.get('lore-query').value = 'The Dark Veil';
  nodes.get('lore-form').fire('submit', { preventDefault() {} });
  assert.match(nodes.get('lore-answer').textContent, /The Dark Veil/);
});

test('two separately reviewed Picard paperback covers add visible source-matched M jackets only after explicit opt-in', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const picardBytes = readFileSync(new URL('../explorer/picard-literature-overlay.json', import.meta.url));
  const picardJacketsBytes = readFileSync(new URL('../explorer/picard-jackets-v1.0.json', import.meta.url));
  const mediumArtwork = JSON.parse(readFileSync(new URL('../explorer/artwork-catalog-v1.3.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404,
    { picardBytes, picardStatus: 200, picardJacketsBytes, picardJacketsStatus: 200,
      mediumArtwork, mediumStatus: 200 }, null, 404, directory, 200);
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,216',
    'two editions must not inflate the historical 1,214 source-local discovery denominator');
  assert.equal(nodes.get('artwork-nav-count').textContent, '6');
  assert.match(nodes.get('artwork-toggle').textContent, /Show sourced artwork \(6 previews\)/);
  assert.equal(nodes.get('artwork-gallery-list').children.length, 6);
  assert.match(nodes.get('artwork-gallery-list').textContent, /The Dark Veil/);
  assert.match(nodes.get('artwork-gallery-list').textContent, /Rogue Elements/);
  assert.equal(traverse(nodes.get('artwork-gallery-list'), (n) => n.tagName === 'img').length, 0,
    'no remote JPEG element or URL may enter the DOM before visitor consent');
  nodes.get('artwork-toggle').fire('click');
  const gallery = nodes.get('artwork-gallery-list');
  const images = traverse(gallery, (n) => n.tagName === 'img');
  assert.equal(images.length, 6);
  for (const [isbn, cover, title, height] of [
    ['9781982154073', 10691195, 'The Dark Veil', 271],
    ['9781982175207', 13231543, 'Rogue Elements', 280]
  ]) {
    const img = images.find((node) => node.src === `https://covers.openlibrary.org/b/id/${cover}-M.jpg?default=false`);
    assert.ok(img, `real edition-pinned ${title} jacket must display in gallery`);
    assert.equal(img.width, 180);
    assert.equal(img.height, height);
    assert.equal(img.loading, 'lazy');
    assert.equal(img.referrerPolicy, 'no-referrer');
    assert.equal(img.parentNode.href, `https://openlibrary.org/isbn/${isbn}`);
    assert.equal(img.parentNode.rel, 'noopener noreferrer');
    assert.equal(img.parentNode.parentNode.className.includes('artwork-has-source'), true,
      'sourced jacket controls the original record-graphic placeholder');
    assert.match(img.alt, /underlying copyright unresolved/);
  }
  assert.equal(traverse(gallery, (node) => node.className === 'artwork-credit').length, 6,
    'all six external jacket previews expose individually exact-edition credit links');
  nodes.get('artwork-toggle').fire('click');
  assert.equal(traverse(gallery, (node) => node.tagName === 'img').length, 0,
    'opt-out must remove all six JPEG elements');
  assert.equal(nodes.get('artwork-gallery-list').children.length, 6,
    'local source-linked LCARS index remains browsable after consent withdrawal');
});

test('missing, tampered or server-error Picard jacket release leaves original four reviewed covers', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const picardBytes = readFileSync(new URL('../explorer/picard-literature-overlay.json', import.meta.url));
  const original = readFileSync(new URL('../explorer/picard-jackets-v1.0.json', import.meta.url));
  const mediumArtwork = JSON.parse(readFileSync(new URL('../explorer/artwork-catalog-v1.3.json', import.meta.url), 'utf8'));
  const tampered = Buffer.from(original);
  tampered[3] ^= 1;
  for (const variant of [
    { picardJacketsStatus: 404 },
    { picardJacketsBytes: tampered, picardJacketsStatus: 200 },
    { picardJacketsBytes: original, picardJacketsStatus: 500 }
  ]) {
    const nodes = await runWithIndex(catalog, 200, null, 404,
      { picardBytes, picardStatus: 200, mediumArtwork, mediumStatus: 200, ...variant },
      null, 404, directory, 200);
    assert.equal(nodes.get('artwork-nav-count').textContent, '4');
    assert.equal(nodes.get('artwork-gallery-list').children.length, 4);
    assert.equal(traverse(nodes.get('artwork-gallery-list'), (node) => node.tagName === 'img').length, 0);
    nodes.get('artwork-toggle').fire('click');
    const images = traverse(nodes.get('artwork-gallery-list'), (node) => node.tagName === 'img');
    assert.equal(images.length, 4);
    assert.ok(images.every((img) => ![10691195, 13231543].some((id) => img.src.includes(`/id/${id}-`))),
      'withheld Picard image may not leak through legacy artwork cards');
  }
});

test('missing or digest-tampered Picard supplement leaves original 1,214 directory and nine literary rows', async () => {
  const historical = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const raw = readFileSync(new URL('../explorer/picard-literature-overlay.json', import.meta.url));
  const forged = Buffer.from(raw);
  forged[0] ^= 1;
  for (const input of [{}, { picardBytes: forged, picardStatus: 200 }, { picardBytes: raw, picardStatus: 500 }]) {
    const nodes = await runWithIndex(catalog, 200, null, 404, input, null, 404, historical, 200);
    assert.equal(nodes.get('discovery-top-count').textContent, '1,214');
    assert.equal(nodes.get('discovery-literature-count').textContent, '9');
    nodes.get('discovery-query').value = 'Rogue Elements';
    nodes.get('discovery-medium').value = 'LITERATURE';
    nodes.get('discovery-filters').fire('change');
    assert.equal(nodes.get('discovery-list').children.length, 0,
      'tampered, absent or error sidecar must never silently appear');
  }
});

test('series facet filters source-local episode observations without counting them as distinct Works', async () => {
  const discovery = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, discovery, 200);
  const series = nodes.get('discovery-series');
  const options = series.children.map((child) => [child.value, child.textContent]);
  assert.equal(options.length, 13, 'all series plus the twelve source-local series aliases');
  assert.ok(options.some(([code, label]) => code === 'VOY' && /Voyager/.test(label)));
  assert.ok(options.some(([code, label]) => code === 'TOS' && /Original Series/.test(label)));
  series.value = 'VOY';
  nodes.get('discovery-filters').fire('change');
  assert.match(nodes.get('discovery-summary').textContent, /193 source-local metadata rows match/);
  assert.match(nodes.get('discovery-summary').textContent, /not distinct or admitted Works/);
  assert.equal(nodes.get('discovery-list').children.length, 41, 'forty of 193 observations and Show next');
  assert.equal(nodes.get('discovery-list').children.every((node) => node.tagName === 'button' || node.textContent.includes('VOY')), true);
  nodes.get('discovery-medium').value = 'FILM';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 0, 'film rows cannot be misattributed to selected episode series');
  series.value = 'all';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 14, 'film rows remain independently browsable');
  assert.equal(nodes.get('briefing-count').textContent, '0', 'source-local facet cannot change accepted admission');
});

test('candidate-kind facet distinguishes discovery types without promoting admission or changing totals', async () => {
  const discovery = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, discovery, 200);
  const kind = nodes.get('discovery-kind');
  const values = kind.children.map((option) => option.value);
  assert.equal(values[0], 'all');
  assert.ok(values.includes('WIKIDATA_EPISODE'));
  assert.ok(values.includes('PUBLISHER_EPISODE_SLOT'));
  assert.ok(values.includes('PROMOTIONAL_ANIMATION'));
  assert.equal(values.length, new Set(discovery.rows.map((row) => row.candidate_kind)).size + 1);

  kind.value = 'PROMOTIONAL_ANIMATION';
  nodes.get('discovery-filters').fire('change');
  const animated = discovery.rows.filter((row) => row.candidate_kind === 'PROMOTIONAL_ANIMATION');
  assert.match(nodes.get('discovery-summary').textContent, new RegExp(`${animated.length} source-local metadata rows match`));
  assert.ok(animated.length > 0 && animated.length <= 40);
  assert.equal(nodes.get('discovery-list').children.length, animated.length);
  assert.match(nodes.get('discovery-list').textContent, /PROMOTIONAL ANIMATION/);

  nodes.get('discovery-medium').value = 'LITERATURE';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 0, 'incompatible medium and candidate kind are not merged');
  kind.value = 'NOVEL';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length,
    discovery.rows.filter((row) => row.medium === 'LITERATURE' && row.candidate_kind === 'NOVEL').length);
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,214', 'filtering does not redefine source-local inventory');
  assert.equal(nodes.get('briefing-count').textContent, '0', 'filtering does not admit candidate data');
});

test('source-local structural tag, synopsis and metadata facets are searchable without admissions', async () => {
  const discovery = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, discovery, 200);
  const tags = nodes.get('discovery-tag');
  assert.ok(tags.children.some((item) => item.value === 'series:tos'));
  assert.ok(tags.children.some((item) => item.value === 'source:wikidata:wdqs'));
  tags.value = 'series:tos';
  nodes.get('discovery-filters').fire('change');
  assert.ok(nodes.get('discovery-list').children.length > 0);
  assert.match(nodes.get('discovery-list').textContent, /TOS/);
  nodes.get('discovery-verification').value = 'rechecked_exact';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 0,
    'without accepted recheck sidecar, structural index cannot assert official verified status');
  nodes.get('discovery-verification').value = 'not_rechecked';
  nodes.get('discovery-filters').fire('change');
  assert.ok(nodes.get('discovery-list').children.length > 0);
  nodes.get('discovery-synopsis').value = 'reviewed_publisher_paraphrase';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 0,
    'reviewed synopsis filter fails closed if publisher synopsis sidecars are absent');
  nodes.get('discovery-synopsis').value = 'pending';
  nodes.get('discovery-filters').fire('change');
  assert.ok(nodes.get('discovery-list').children.length > 0);
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,214');
  assert.equal(nodes.get('briefing-count').textContent, '0');
});

test('untrusted directory cannot forge admission or publisher navigation', async () => {
  const catalogData = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const accepted = structuredClone(catalogData);
  accepted.rows[0].admission_effect = 'ACCEPTED';
  const blocked = await runWithIndex(catalog, 200, null, 404, {}, null, 404, accepted, 200);
  assert.equal(blocked.get('discovery-nav-count').textContent, '—');
  assert.equal(blocked.get('discovery-top-count').textContent, '—',
    'untrusted discovery content cannot create an authoritative-looking top-line count');
  assert.equal(blocked.get('discovery-episode-count').textContent, '—');
  assert.equal(blocked.get('discovery-literature-count').textContent, '—');
  assert.match(blocked.get('discovery-state').textContent, /rejected/);
  const forged = structuredClone(catalogData);
  forged.rows[0].source_locator = 'https://www.startrek.com@evil.invalid/bogus';
  const noLink = await runWithIndex(catalog, 200, null, 404, {}, null, 404, forged, 200);
  assert.equal(noLink.get('discovery-nav-count').textContent, '—');
  for (const malicious of ['https://youtu.be/j-KvjtSgfJs/redirect',
                            'https://youtu.be/x/../j-KvjtSgfJs',
                            'https://youtu.be/j-KvjtSgfJs?continue=https://evil.invalid/',
                            'https://youtu.be.evil.invalid/j-KvjtSgfJs']) {
    const maliciousCatalog = structuredClone(catalogData);
    const scoutsRow = maliciousCatalog.rows.findIndex(row => row.row_id.startsWith('short:scouts:'));
    assert.ok(scoutsRow >= 0);
    maliciousCatalog.rows[scoutsRow].source_locator = malicious;
    const rejected = await runWithIndex(catalog, 200, null, 404, {}, null, 404, maliciousCatalog, 200);
    assert.equal(rejected.get('discovery-nav-count').textContent, '—');
  }
  const duplicate = structuredClone(catalogData);
  duplicate.rows[1].row_id = duplicate.rows[0].row_id;
  const noDuplicate = await runWithIndex(catalog, 200, null, 404, {}, null, 404, duplicate, 200);
  assert.equal(noDuplicate.get('discovery-nav-count').textContent, '—');
  const absent = await runWithIndex(null, 404, null, 404, {}, null, 404, catalogData, 200);
  assert.equal(absent.get('discovery-nav-count').textContent, '1,214', 'discovery does not depend on governed Mission index');
  assert.equal(absent.get('discovery-top-count').textContent, '1,214',
    'source-local directory remains independently visible when Mission index is unavailable');
  assert.equal(absent.get('discovery-episode-count').textContent, '1,155');
  assert.equal(absent.get('discovery-literature-count').textContent, '9');
  assert.equal(absent.get('mission-count').textContent, '—');
});

test('directory source-group labels must match their actual source hosts', async () => {
  const fixture = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const sourceRow = fixture.rows.find((row) => row.source_group === 'wikidata:wdqs');
  const publisherRow = fixture.rows.find((row) => row.source_group === 'publisher:startrek.com');
  assert.ok(sourceRow && publisherRow);
  for (const [rowId, falseGroup] of [
    [sourceRow.row_id, 'publisher:startrek.com'],
    [publisherRow.row_id, 'wikidata:wdqs'],
    [sourceRow.row_id, 'publisher:paramount'],
  ]) {
    const forged = structuredClone(fixture);
    forged.rows.find((row) => row.row_id === rowId).source_group = falseGroup;
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, forged, 200);
    assert.equal(nodes.get('discovery-nav-count').textContent, '—',
      `directory must reject ${falseGroup} when the source host belongs to another lineage`);
    assert.match(nodes.get('discovery-state').textContent, /rejected/);
  }

  const nullLocator = structuredClone(fixture);
  const spoofed = nullLocator.rows.find((row) => row.row_id === sourceRow.row_id);
  spoofed.source_group = 'publisher:paramount';
  spoofed.source_locator = null;
  const missingPublisherEvidence = await runWithIndex(catalog, 200, null, 404, {}, null, 404, nullLocator, 200);
  assert.equal(missingPublisherEvidence.get('discovery-nav-count').textContent, '—',
    'a publisher source-group badge must never bypass host validation with a null locator');
  assert.match(missingPublisherEvidence.get('discovery-state').textContent, /rejected/);

  const unattributedWikidataLink = structuredClone(fixture);
  unattributedWikidataLink.rows.find((row) => row.row_id === sourceRow.row_id).source_locator = null;
  const unlinked = await runWithIndex(catalog, 200, null, 404, {}, null, 404, unattributedWikidataLink, 200);
  assert.equal(unlinked.get('discovery-nav-count').textContent, '1,214',
    'a null Wikidata URL does not invent a publisher claim or promote source-local metadata');
});

test('Research Leads load separately from admitted Mission Briefings and stay searchable', async () => {
  const nodes = await runWithIndex(catalog, 200, candidateIndex(3), 200);
  assert.equal(nodes.get('research-top-count').textContent, '3');
  assert.equal(nodes.get('research-nav-count').textContent, '3');
  assert.equal(nodes.get('kind-filter').disabled, true, 'no phantom record-kind filter in catalog mode');
  assert.equal(nodes.get('status-filter').disabled, true, 'no phantom evidence-status filter in catalog mode');
  assert.equal(nodes.get('mission-count').textContent, '2');
  assert.equal(nodes.get('briefing-count').textContent, '0');
  assert.equal(nodes.get('record-count').textContent, '0');
  assert.equal(nodes.get('research-count').textContent, '3');
  assert.equal(nodes.get('research-list').children.length, 3);
  assert.match(nodes.get('research-list').textContent, /Candidate · not verified/);
  assert.match(nodes.get('research-state').textContent, /not been admitted/);
  const links = traverse(nodes.get('research-list'), (node) => node.tagName === 'a');
  assert.equal(links[1].href, 'https://www.wikidata.org/wiki/Q2');
  assert.equal(links[1].rel, 'noopener noreferrer');

  nodes.get('research-query').value = 'neutral zone';
  nodes.get('research-filters').fire('input');
  assert.equal(nodes.get('research-list').children.length, 1);
  assert.match(nodes.get('research-summary').textContent, /1 matching unverified lead/);
  assert.equal(nodes.get('research-count').textContent, '3', 'filter must not change dataset count');
  nodes.get('research-query').value = 'Q3';
  nodes.get('research-filters').fire('input');
  assert.equal(nodes.get('research-list').children.length, 1, 'QID search succeeds');
  nodes.get('research-query').value = '';
  nodes.get('research-mission').value = 'voy';
  nodes.get('research-filters').fire('change');
  assert.equal(nodes.get('research-list').children.length, 0, 'a distinct Mission filter cannot relabel TNG leads');
  assert.equal(nodes.get('briefing-count').textContent, '0');

  const event = { prevented: false, preventDefault() { this.prevented = true; } };
  nodes.get('research-filters').fire('submit', event);
  assert.equal(event.prevented, true, 'Enter must not reload research search');
});

test('long Research Leads lists paginate and restore keyboard focus', async () => {
  const nodes = await runWithIndex(catalog, 200, candidateIndex(190), 200);
  const list = nodes.get('research-list');
  assert.equal(list.children.length, 31, 'first 30 cards plus load-more control');
  list.children.at(-1).fire('click');
  assert.equal(list.children.length, 61);
  assert.equal(list.children[30].focused, true, 'focus first newly rendered candidate card');
  assert.equal(list.children[30].attributes.get('tabindex'), '-1');
  assert.match(nodes.get('research-summary').textContent, /Showing 60/);
  for (let remaining = 130; remaining > 0; remaining -= 30) list.children.at(-1).fire('click');
  assert.equal(list.children.length, 190, 'all candidates reachable');
});

test('Academy publisher slots are searchable metadata, not canonical Briefings or a verified denominator', async () => {
  const payload = candidateIndex(1);
  payload.leads.push({
    mission_id: 'sfa', source_type: 'PUBLISHER_EPISODE_SLOT_METADATA',
    independence_group: 'publisher:paramount', episode_label: 'Kids These Days',
    season_number: 1, episode_number: 1,
    source_locator: 'https://www.paramountplus.com/shows/star-trek-starfleet-academy/episodes/1/',
    snapshot_id: 'SFA-PUBLISHER-ROSTER-20261102-001', observed_on: '2026-11-02',
    verification_status: 'UNVERIFIED_METADATA'
  });
  payload.lead_count = 2;
  payload.sampled_missions_count = 2;
  const academyCatalog = { ...catalog, missions: [
    ...catalog.missions, { id: 'sfa', title: 'Star Trek: Starfleet Academy' }
  ]};
  const nodes = await runWithIndex(academyCatalog, 200, payload, 200);
  assert.equal(nodes.get('research-count').textContent, '2');
  assert.equal(nodes.get('briefing-count').textContent, '0');
  assert.match(nodes.get('research-list').textContent, /publisher-listed slot/i);
  assert.match(nodes.get('research-list').textContent, /Season 1, episode 1/);
  assert.match(nodes.get('research-list').textContent, /publisher:paramount/);
  const links = traverse(nodes.get('research-list'), (node) => node.tagName === 'a');
  assert.equal(links[1].href, payload.leads[1].source_locator);
  nodes.get('research-query').value = 's1e1';
  nodes.get('research-filters').fire('input');
  assert.equal(nodes.get('research-list').children.length, 1);
  assert.match(nodes.get('research-list').textContent, /Kids These Days/);
});

test('held Enterprise arc/umbrella and false publisher provenance fail closed', async () => {
  const wrongs = [
    (p) => { p.leads[0].mission_id = 'ent'; p.leads[0].episode_qid = 'Q56247746'; },
    (p) => { p.leads[0].mission_id = 'ent'; p.leads[0].episode_qid = 'Q866375'; },
    (p) => { p.leads[0].independence_group = 'publisher:paramount'; },
    (p) => { p.held_candidate_count = 0; },
    (p) => { p.leads[0].source_type = 'PUBLISHER_EPISODE_SLOT_METADATA'; },
  ];
  for (const mutate of wrongs) {
    const payload = candidateIndex(1);
    mutate(payload);
    const nodes = await runWithIndex(catalog, 200, payload, 200);
    assert.equal(nodes.get('research-count').textContent, '—');
  }
});

test('malformed or injected Research Leads fail closed without affecting canonical index', async () => {
  const cases = [
    (p) => { p.data_status = 'GOVERNED_PROJECTION'; },
    (p) => { p.leads[0].canonical_work_id = 'unapproved-work'; },
    (p) => { p.leads[0].episode_qid = 'javascript:alert(1)'; },
    (p) => { p.leads[0].response_sha256 = 'unverified'; },
    (p) => { p.leads[0].mission_id = 'not-a-known-mission'; },
    (p) => { p.leads[1].episode_qid = p.leads[0].episode_qid; },
    (p) => { p.lead_count = 9999; },
    (p) => { p.leads[0].episode_label = '<script>'.repeat(40); }
  ];
  for (const mutate of cases) {
    const payload = candidateIndex();
    mutate(payload);
    const nodes = await runWithIndex(catalog, 200, payload, 200);
    assert.equal(nodes.get('research-count').textContent, '—');
    assert.equal(nodes.get('research-list').children.length, 0);
    assert.match(nodes.get('research-state').textContent, /Could not load/);
    assert.equal(nodes.get('briefing-count').textContent, '0');
    assert.equal(nodes.get('mission-count').textContent, '2');
    assert.equal(nodes.get('research-query').disabled, true);
  }
});

test('missing Research Leads index is explained without claiming a zero dataset', async () => {
  const nodes = await runWithIndex(catalog);
  assert.equal(nodes.get('research-count').textContent, '—');
  assert.match(nodes.get('research-state').textContent, /has not been published yet/);
  assert.equal(nodes.get('research-query').disabled, true);
  assert.equal(nodes.get('mission-count').textContent, '2');
  assert.equal(nodes.get('briefing-count').textContent, '0');
});

test('interface tones are optional, off by default, and synthesized only after an explicit click', async () => {
  let contextInstances = 0;
  let startedOscillators = 0;
  let closedContexts = 0;
  class FakeAudioContext {
    constructor() { contextInstances++; this.state = 'running'; this.currentTime = 1; this.destination = {}; }
    close() { this.state = 'closed'; closedContexts++; return Promise.resolve(); }
    createOscillator() {
      return { frequency: { setValueAtTime() {} }, connect() {}, start() { startedOscillators++; }, stop() {} };
    }
    createGain() {
      return { gain: { setValueAtTime() {}, exponentialRampToValueAtTime() {} }, connect() {} };
    }
  }
  const nodes = await runWithIndex(catalog, 200, null, 404, { AudioContext: FakeAudioContext });
  const toggle = nodes.get('tone-toggle');
  assert.equal(contextInstances, 0, 'index and candidate loading never initialize audio');
  assert.equal(toggle.attributes.get('aria-pressed'), 'false');
  nodes.get('search-input').value = 'Voyager';
  nodes.get('filters').fire('input');
  assert.equal(startedOscillators, 0, 'typing is silent even before an explicit opt-in');
  toggle.fire('click');
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(contextInstances, 1);
  assert.equal(toggle.attributes.get('aria-pressed'), 'true');
  assert.equal(toggle.textContent, 'Interface tones: On');
  assert.equal(startedOscillators, 2, 'opt-in confirms with an original two-note signal');
  nodes.get('filters').fire('change');
  assert.equal(startedOscillators, 4, 'selection has an optional cue');
  nodes.get('filters').fire('input');
  assert.equal(startedOscillators, 4, 'typing remains silent after opt-in');
  toggle.fire('click');
  assert.equal(toggle.attributes.get('aria-pressed'), 'false');
  assert.equal(closedContexts, 1, 'disabling tones releases the audio context');
  nodes.get('filters').fire('change');
  assert.equal(startedOscillators, 4, 'disabled tones remain silent');
});

test('cancelling a delayed audio start cannot resurrect interface tones', async () => {
  let finishResume;
  let closed = 0;
  let started = 0;
  class DelayedAudioContext {
    constructor() { this.state = 'suspended'; }
    resume() {
      return new Promise((resolve) => { finishResume = () => { this.state = 'running'; resolve(); }; });
    }
    close() { this.state = 'closed'; closed++; return Promise.resolve(); }
    createOscillator() { started++; throw new Error('must not play after cancellation'); }
  }
  const nodes = await runWithIndex(catalog, 200, null, 404, { AudioContext: DelayedAudioContext });
  const toggle = nodes.get('tone-toggle');
  toggle.fire('click');
  assert.equal(toggle.textContent, 'Interface tones: Starting…');
  assert.equal(toggle.attributes.get('aria-label'), 'Cancel enabling interface tones');
  toggle.fire('click');
  assert.equal(closed, 1);
  assert.equal(toggle.textContent, 'Interface tones: Off');
  finishResume();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(toggle.attributes.get('aria-pressed'), 'false');
  assert.equal(started, 0);
});

test('interface tones fail closed when the browser has no audio support', async () => {
  const nodes = await runWithIndex(catalog);
  const toggle = nodes.get('tone-toggle');
  toggle.fire('click');
  assert.equal(toggle.disabled, true);
  assert.equal(toggle.attributes.get('aria-pressed'), 'false');
  assert.equal(toggle.textContent, 'Interface tones unavailable');
});

test('LCARS navigation cue is directional, responsive, accessible and absent when tabs fit', async () => {
  let resize;
  const nodes = await runWithIndex(catalog, 200, null, 404, {
    addEventListener: (type, handler) => { if (type === 'resize') resize = handler; }
  });
  const nav = nodes.get('explorer-navigation');
  const hint = nodes.get('navigation-scroll-hint');
  const controls = nodes.get('navigation-scroll-controls');
  const previous = nodes.get('navigation-scroll-previous');
  const next = nodes.get('navigation-scroll-next');
  assert.equal(hint.hidden, true, 'no cue when section links fit the rail');
  assert.equal(controls.hidden, true, 'no extra control rail when links fit');
  assert.equal(previous.hidden, true);
  assert.equal(next.hidden, true);
  assert.equal(nav.attributes.has('aria-describedby'), false, 'no hidden stale description');
  assert.equal(typeof resize, 'function', 'viewport resize listener installed');
  assert.equal(nav.handlers.get('scroll')?.length, 1, 'combined Explorer registers exactly one rail scroll listener');
  assert.equal(previous.handlers.get('click')?.length, 1, 'earlier control has one action handler');
  assert.equal(next.handlers.get('click')?.length, 1, 'later control has one action handler');

  nav.clientWidth = 375;
  nav.scrollWidth = 1030;
  nav.scrollLeft = 0;
  resize();
  assert.equal(hint.hidden, false, 'real horizontal overflow shows a visible cue');
  assert.match(hint.textContent, /More sections →/);
  assert.match(hint.textContent, /Swipe, scroll or Tab/);
  assert.equal(nav.attributes.get('aria-describedby'), 'navigation-scroll-hint');
  assert.equal(previous.hidden, false, 'overflow exposes a genuine earlier-sections control');
  assert.equal(next.hidden, false, 'overflow exposes a genuine later-sections control');
  assert.equal(controls.hidden, false);
  assert.equal(previous.getAttribute('aria-disabled'), 'true');
  assert.equal(next.getAttribute('aria-disabled'), 'false');

  next.fire('click');
  assert.equal(nav.scrollLeft, 300, 'a real action scrolls the rail, not the whole page');
  assert.match(hint.textContent, /Sections both ways ↔/);
  previous.fire('click');
  assert.equal(nav.scrollLeft, 0);
  previous.fire('click');
  assert.equal(nav.scrollLeft, 0, 'edge controls do not overscroll');

  nav.scrollLeft = 300;
  nav.fire('scroll');
  assert.match(hint.textContent, /Sections both ways ↔/);
  nav.scrollLeft = 655;
  nav.fire('scroll');
  assert.match(hint.textContent, /Earlier sections ←/);
  assert.equal(next.getAttribute('aria-disabled'), 'true');
  next.fire('click');
  assert.equal(nav.scrollLeft, 655, 'last edge is an honest no-op');

  nav.clientWidth = 1030;
  resize();
  assert.equal(hint.hidden, true, 'cue disappears when every link fits');
  assert.equal(controls.hidden, true);
  assert.equal(previous.hidden, true);
  assert.equal(next.hidden, true);
  assert.equal(nav.attributes.has('aria-describedby'), false);
});

test('LCARS navigation controls scroll proportionally at 320 and 390 without replacing native tab order', async () => {
  const nodes = await runWithIndex(catalog);
  const nav = nodes.get('explorer-navigation');
  const earlier = nodes.get('navigation-scroll-previous');
  const later = nodes.get('navigation-scroll-next');
  for (const width of [320, 390]) {
    nav.clientWidth = width;
    nav.scrollWidth = 2200;
    nav.scrollLeft = 0;
    nav.fire('scroll');
    later.fire('click');
    assert.equal(nav.scrollLeft, Math.floor(width * 0.8), `${width}px viewport scrolls proportionally`);
    earlier.fire('click');
    assert.equal(nav.scrollLeft, 0);
    assert.equal(later.hidden, false);
  }
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  assert.ok(html.indexOf('</nav>') < html.indexOf('id="navigation-scroll-previous"'),
    'existing archive links retain their keyboard order before the optional rail controls');
  assert.match(html, /id="navigation-scroll-previous"[^>]*aria-controls="explorer-navigation"[^>]*hidden>/);
  assert.match(html, /id="navigation-scroll-next"[^>]*aria-controls="explorer-navigation"[^>]*hidden>/);
});

test('LCARS overflow cue updates after a badge widens through ResizeObserver', async () => {
  let observer;
  class FakeResizeObserver {
    constructor(callback) { observer = { callback, targets: [] }; }
    observe(target) { observer.targets.push(target); }
  }
  const nodes = await runWithIndex(catalog, 200, null, 404, { ResizeObserver: FakeResizeObserver });
  const nav = nodes.get('explorer-navigation');
  const hint = nodes.get('navigation-scroll-hint');
  assert.deepEqual(observer.targets, [nav]);
  nav.clientWidth = 480;
  nav.scrollWidth = 530;
  observer.callback();
  assert.equal(hint.hidden, false, 'dynamic content does not strand offscreen links without a hint');
});

test('HTML exposes the separate research search and status elements', () => {
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  assert.match(html, /placeholder="Title, source receipt, series, reviewed overview…"/,
    'free-text discoverability includes only released publisher overviews and existing receipt metadata');
  assert.match(html, /<nav id="explorer-navigation" class="lcars-navigation" aria-label="Explorer sections">/);
  assert.match(html, /<p id="navigation-scroll-hint" class="navigation-scroll-hint" hidden>/, 'overflow cue is hidden before layout is measured');
  assert.match(html, /href="#research-leads">Episode research leads/);
  assert.match(html, /href="#films">Films/);
  assert.match(html, /id="film-list"/);
  assert.match(html, /id="film-filters"[^>]*aria-label="Search film discovery titles"/);
  assert.match(html, /id="film-state"[^>]*role="status"/);
  assert.match(html, /id="discovery-directory"/);
  assert.match(html, /id="discovery-directory"[^>]*tabindex="-1"/,
    'the directory anchor must accept keyboard focus for count drilldowns');
  assert.match(html, /id="discovery-top-count"[^>]*href="#discovery-directory"/,
    'prominent directory count links to the source-local listing rather than implying 12 total episodes');
  assert.match(html, /id="discovery-episode-count"[^>]*href="#discovery-directory"/);
  assert.match(html, /id="discovery-literature-count"[^>]*href="#discovery-directory"/);
  assert.match(html, /id="discovery-episode-count"[^>]*aria-label="Show episode references in the source-local directory"/);
  assert.match(html, /id="discovery-literature-count"[^>]*aria-label="Show literary leads in the source-local directory"/);
  assert.match(html, /Missions are series navigation categories, not an episode count/,
    'the front status board must make the twelve-Mission denominator explicit');
  assert.match(html, /id="discovery-filters"[^>]*aria-label="Search multimedia discovery metadata"/);
  assert.match(html, /for="discovery-series">Series \(source-local\)<\/label>/, 'series facet must disclose its source-local scope');
  assert.match(html, /<label for="discovery-kind">Candidate type<\/label><select id="discovery-kind" name="kind">/, 'candidate facet is labeled and connected to the live directory form');
  assert.match(html, /for="discovery-lineage">Source group<\/label>/, 'source-group labels do not imply independent publishers');
  assert.match(html, /for="discovery-overview">Publisher overview \(loaded\)<\/label>/,
    'reviewed display availability must be visibly distinguished from source/admission status');
  assert.match(html, /id="research-leads"/);
  assert.match(html, /id="research-filters"/);
  assert.match(html, /id="research-state"/);
  assert.match(html, /not admitted Briefings or continuity facts/);
  assert.match(html, /<dt>Briefings<\/dt>/);
  assert.match(html, /<h2 id="briefings-heading">Briefings<\/h2>/);
  assert.match(html, /src="\.\/trek-data-core-hero\.jpg\?v=[0-9a-f]{64}"/);
  assert.match(html, /id="tone-toggle"[^>]*aria-pressed="false"/);
  assert.match(html, /Star Trek \/ Independent research archive/);
  assert.match(html, /class="archive-navigation-mark"/);
  assert.match(html, /id="artwork-toggle"[^>]*aria-pressed="false" disabled/);
  assert.match(html, /img-src 'self' https:\/\/covers\.openlibrary\.org/, 'only explicit image-provider family extends the local CSP');
  assert.match(html, /Unofficial, independent Star Trek research/);
  assert.match(html, /id="filters" role="search" aria-label="Search governed Mission index"/);
  assert.match(html, /id="research-filters"[^>]*role="search" aria-label="Search unverified research leads"/);
});

test('optional fictional Lore console opens outside hero, restores focus, and closes with Escape', async () => {
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  assert.match(html, /id="lore-toggle"[^>]*aria-expanded="false"[^>]*aria-controls="lore-console"/);
  assert.match(html, /<main id="main"[\s\S]*?<section id="lore-console"[^>]*hidden>/);
  assert.match(html, /Fictional simulation/);
  assert.match(html, /Fictional Lore/);
  assert.match(html, /id="lore-chat-token" type="password"/);
  assert.match(html, /id="lore-chat-consent" type="checkbox" required/);
  assert.match(html, /Archive Search \/\/ Scripted index lookup/);
  assert.match(html, /connect-src 'self' http:\/\/127\.0\.0\.1:9877;/);
  assert.doesNotMatch(html, /connect-src[^;]*9876/);
  assert.match(html, /id="lore-answer"[^>]*role="status" aria-live="polite"/);

  const nodes = await runWithIndex(catalog);
  const toggle = nodes.get('lore-toggle');
  const panel = nodes.get('lore-console');
  assert.equal(panel.hidden, true);
  toggle.fire('click');
  assert.equal(panel.hidden, false);
  assert.equal(toggle.attributes.get('aria-expanded'), 'true');
  assert.equal(nodes.get('lore-query').focused, true);
  let prevented = false;
  panel.fire('keydown', { key: 'Escape', preventDefault() { prevented = true; } });
  assert.equal(prevented, true);
  assert.equal(panel.hidden, true);
  assert.equal(toggle.attributes.get('aria-expanded'), 'false');
  assert.equal(toggle.focused, true);
});

test('Lore panel stays in flow and Explorer cache keys match the exact local script and style bytes', () => {
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  const css = readFileSync(new URL('../explorer/app.css', import.meta.url), 'utf8');
  const cssHash = createHash('sha256').update(css).digest('hex');
  const jsHash = createHash('sha256').update(SCRIPT).digest('hex');
  assert.ok(html.includes(`./app.css?v=${cssHash}`));
  assert.ok(html.includes(`./app.js?v=${jsHash}`));
  const panelStyles = css.match(/\.lore-console\s*\{([^}]*)\}/)?.[1];
  assert.ok(panelStyles, 'Lore has a dedicated layout instead of reusing the hero copy');
  assert.doesNotMatch(panelStyles, /position:\s*(absolute|fixed)/,
    'Lore must remain in flow and never cover or duplicate the masthead');
  assert.match(css, /@media \(max-width: 760px\)[\s\S]*?\.lore-stations \{ grid-template-columns: 1fr; \}/);
  assert.match(css, /\.lore-answer \{[^}]*color: var\(--text\)/,
    'terminal text is high contrast against its dark local response surface');
});

test('Lore model chat starts disconnected and makes two genuine bounded turn requests only after consent', async () => {
  const seen = [];
  const hostile = '<img src=x onerror=alert(1)> Lore remembers.';
  const nodes = await runWithIndex(catalog, 200, null, 404, {chatBackend: async (url, options) => {
    assert.equal(url, 'http://127.0.0.1:9877/api/chat');
    assert.equal(options.method, 'POST');
    assert.equal(options.redirect, 'error');
    assert.equal(options.credentials, 'omit');
    assert.equal(options.targetAddressSpace, 'loopback');
    assert.equal(options.headers['X-Trek-Lore-CSRF'], 'A'.repeat(40));
    const body = JSON.parse(options.body);
    seen.push(body);
    return {ok: true, json: async () => ({
      mode: 'opt_in_fictional_multiturn_chat', model_text_unverified: true,
      model_text: hostile, publication_effect: 'NONE', model_repo_authority: 'NONE',
      source_search: {status: 'SOURCE_LOCAL_HELD_ONLY', rows: [{title: 'Wedding Bell Blues', source_local_id: 'snw-s3-e02-pplus'}]}
    })};
  }});
  assert.equal(nodes.chatRequests.length, 0, 'Explorer must not ping localhost on load');
  const form = nodes.get('lore-chat-form');
  nodes.get('lore-chat-input').value = 'Hello Lore';
  await form.fire('submit', { preventDefault() {} });
  assert.equal(nodes.chatRequests.length, 0, 'no token or consent means no request');
  nodes.get('lore-chat-token').value = 'A'.repeat(40);
  await form.fire('submit', { preventDefault() {} });
  assert.equal(nodes.chatRequests.length, 0, 'token alone is insufficient');
  nodes.get('lore-chat-consent').checked = true;
  await form.fire('submit', { preventDefault() {} });
  assert.equal(nodes.chatRequests.length, 1);
  assert.deepEqual(seen[0], {query: 'Hello Lore', history: []});
  assert.equal(nodes.get('lore-chat-log').children.length, 2);
  assert.match(nodes.get('lore-chat-log').textContent, /Fictional model reply · Unverified/);
  assert.match(nodes.get('lore-chat-log').textContent, /Separate held source-card matches/);
  assert.equal(traverse(nodes.get('lore-chat-log'), (node) => ['img', 'script', 'iframe'].includes(node.tagName)).length, 0);
  nodes.get('lore-chat-input').value = 'What did I just say?';
  await form.fire('submit', { preventDefault() {} });
  assert.equal(nodes.chatRequests.length, 2);
  assert.equal(seen[1].history.length, 2);
  assert.equal(seen[1].history[0].role, 'user');
  assert.equal(seen[1].history[0].content, 'Hello Lore');
  assert.equal(seen[1].history[1].role, 'assistant');
  assert.equal(seen[1].history[1].content, hostile);
  assert.ok(!nodes.get('lore-chat-log').textContent.includes('A'.repeat(40)), 'token must never render');
});

test('Lore opt-out, Clear and Close revoke in-flight model response without stale transcript', async () => {
  for (const revoke of ['untick', 'clear', 'close']) {
    let respond;
    const pendingResponse = new Promise((resolve) => { respond = resolve; });
    const nodes = await runWithIndex(catalog, 200, null, 404,
      {chatBackend: () => pendingResponse});
    nodes.get('lore-chat-input').value = 'Are you really there?';
    nodes.get('lore-chat-token').value = 'A'.repeat(40);
    nodes.get('lore-chat-consent').checked = true;
    const pendingSubmit = nodes.get('lore-chat-form').fire('submit', {preventDefault() {}});
    assert.equal(nodes.chatRequests.length, 1, revoke);
    if (revoke === 'untick') {
      nodes.get('lore-chat-consent').checked = false;
      await nodes.get('lore-chat-consent').fire('change', {});
    } else if (revoke === 'clear') {
      await nodes.get('lore-chat-clear').fire('click', {});
    } else {
      await nodes.get('lore-close').fire('click', {});
    }
    respond({ok: true, json: async () => ({mode: 'opt_in_fictional_multiturn_chat',
      model_text_unverified: true, model_text: 'stale', publication_effect: 'NONE',
      model_repo_authority: 'NONE', source_search: {status: 'SOURCE_LOCAL_HELD_ONLY', rows: []}})});
    await pendingSubmit;
    assert.equal(nodes.get('lore-chat-log').children.length, 0, revoke);
    assert.equal(nodes.get('lore-chat-token').value, '', revoke);
    assert.equal(nodes.get('lore-chat-consent').checked, false, revoke);
    assert.match(nodes.get('lore-chat-status').textContent, /Disconnected/, revoke);
  }
});

test('Lore chat has a hard deadline even when browser local-network permission never settles fetch', async () => {
  let expire;
  let warn;
  let releaseLate;
  let backendCalls = 0;
  const stuckRequest = new Promise((resolve) => { releaseLate = resolve; });
  const validReply = (text) => ({ok: true, json: async () => ({
    mode: 'opt_in_fictional_multiturn_chat', model_text_unverified: true,
    model_text: text, publication_effect: 'NONE', model_repo_authority: 'NONE',
    source_search: {status: 'SOURCE_LOCAL_HELD_ONLY', rows: []}
  })});
  const nodes = await runWithIndex(catalog, 200, null, 404, {
    mockSetTimeout: (fn, ms) => {
      if (ms === 12000) warn = fn;
      else if (ms === 45000) expire = fn;
      else assert.fail(`unexpected Lore timeout ${ms}`);
      return ms;
    },
    mockClearTimeout: (id) => assert.ok([12000, 45000].includes(id)),
    chatBackend: (_url, options) => {
      assert.ok(options.signal, 'fetch abort signal remains required');
      backendCalls += 1;
      return backendCalls === 1 ? stuckRequest : validReply('Second attempt worked.');
    }
  });
  nodes.get('lore-chat-token').value = 'A'.repeat(40);
  nodes.get('lore-chat-consent').checked = true;
  nodes.get('lore-chat-input').value = 'A question worth keeping';
  const first = nodes.get('lore-chat-form').fire('submit', {preventDefault() {}});
  assert.equal(nodes.get('lore-chat-send').disabled, true);
  assert.match(nodes.get('lore-chat-status').textContent, /Contacting/);
  assert.equal(nodes.chatRequests.length, 1);
  warn();
  assert.match(nodes.get('lore-chat-status').textContent, /Still waiting/);
  assert.match(nodes.get('lore-chat-status').textContent, /local-network access/);
  expire();
  await first;
  assert.equal(nodes.chatRequests[0].opts.signal.aborted, true);
  assert.equal(nodes.get('lore-chat-send').disabled, false, 'timeout must restore Send');
  assert.match(nodes.get('lore-chat-status').textContent, /No local reply within 45 seconds/);
  assert.match(nodes.get('lore-chat-status').textContent, /local-network permission/);
  assert.match(nodes.get('lore-chat-status').textContent, /http:\/\/127\.0\.0\.1:9877\/explorer\//);
  assert.equal(nodes.get('lore-chat-input').value, 'A question worth keeping');
  assert.equal(nodes.get('lore-chat-consent').checked, true, 'retry still requires prior opt-in');
  assert.equal(nodes.get('lore-chat-log').children.length, 0);
  // The browser may deliver the original response well after our deadline;
  // it must not append a stale turn or overwrite the recovery guidance.
  releaseLate(validReply('Late response must be ignored.'));
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(nodes.get('lore-chat-log').children.length, 0);
  assert.match(nodes.get('lore-chat-status').textContent, /No local reply within 45 seconds/);
  await nodes.get('lore-chat-form').fire('submit', {preventDefault() {}});
  assert.equal(backendCalls, 2, 'visitor can retry without reloading or losing the question');
  assert.equal(nodes.get('lore-chat-log').children.length, 2);
  assert.match(nodes.get('lore-chat-log').textContent, /Second attempt worked/);
});

test('Lore does not truncate a slow valid response after its waiting notice on either origin', async () => {
  for (const localPairEligible of [false, true]) {
    const delays = new Map();
    let release;
    const backend = new Promise((resolve) => { release = resolve; });
    const mockLocation = localPairEligible
      ? {protocol: 'http:', hostname: '127.0.0.1', port: '9877',
        pathname: '/explorer/', origin: 'http://127.0.0.1:9877'} : {};
    const nodes = await runWithIndex(catalog, 200, null, 404, {
      mockLocation,
      mockSetTimeout: (fn, ms) => { delays.set(ms, fn); return ms; },
      mockClearTimeout: (ms) => assert.ok(delays.has(ms)),
      chatBackend: () => backend
    });
    nodes.get('lore-chat-token').value = 'A'.repeat(40);
    nodes.get('lore-chat-consent').checked = true;
    nodes.get('lore-chat-input').value = 'Let the local model warm up';
    const submit = nodes.get('lore-chat-form').fire('submit', {preventDefault() {}});
    assert.equal(delays.has(12000), true);
    assert.equal(delays.has(localPairEligible ? 60000 : 45000), true,
      'public permission waits and localhost cold starts must have a generous hard ceiling');
    delays.get(12000)();
    assert.match(nodes.get('lore-chat-status').textContent, /Still waiting/);
    release({ok: true, json: async () => ({
      mode: 'opt_in_fictional_multiturn_chat', model_text_unverified: true,
      model_text: 'Thank you for waiting.', publication_effect: 'NONE',
      model_repo_authority: 'NONE', source_search: {status: 'SOURCE_LOCAL_HELD_ONLY', rows: []}
    })});
    await submit;
    assert.equal(nodes.get('lore-chat-send').disabled, false);
    assert.equal(nodes.get('lore-chat-log').children.length, 2,
      `slow ${localPairEligible ? 'localhost' : 'public'} request must be retained`);
    assert.match(nodes.get('lore-chat-log').textContent, /Thank you for waiting/);
  }
});

test('local same-origin Lore pairing requires a click and late pairing cannot restore a revoked token', async () => {
  for (const port of ['9877', '9887']) for (const revoke of ['none', 'clear', 'close']) {
    const local = {protocol: 'http:', hostname: '127.0.0.1', port,
      pathname: '/explorer/', origin: `http://127.0.0.1:${port}`};
    let release;
    const pending = new Promise((resolve) => { release = resolve; });
    const nodes = await runWithIndex(catalog, 200, null, 404,
      {mockLocation: local, chatBackend: async (path, options) => {
        assert.equal(path, `http://127.0.0.1:${port}/api/session`);
        assert.equal(options.method, 'GET');
        assert.equal(options.headers['X-Trek-Lore-Pair'], '1');
        assert.equal(options.credentials, 'omit');
        return pending;
      }});
    assert.equal(nodes.get('lore-chat-pair').hidden, false);
    assert.equal(nodes.chatRequests.length, 0, 'pairing must never happen on load');
    const pair = nodes.get('lore-chat-pair').fire('click', {});
    assert.equal(nodes.chatRequests.length, 1);
    if (revoke === 'clear') await nodes.get('lore-chat-clear').fire('click', {});
    else if (revoke === 'close') await nodes.get('lore-close').fire('click', {});
    release({ok: true, json: async () => ({pairing_scope: 'LOCAL_SAME_ORIGIN_ONLY', local_session_token: 'A'.repeat(40)})});
    await pair;
    if (revoke === 'none') {
      assert.equal(nodes.get('lore-chat-token').value, 'A'.repeat(40));
      assert.equal(nodes.get('lore-chat-consent').checked, undefined,
        'pairing may not enable consent automatically');
    } else {
      assert.equal(nodes.get('lore-chat-token').value, '', revoke);
      assert.equal(nodes.get('lore-chat-consent').checked, false, revoke);
      assert.match(nodes.get('lore-chat-status').textContent, /Disconnected/, revoke);
    }
  }
});

test('local Explorer custom port chat stays same-origin and never contacts the occupied 9876', async () => {
  const local = {protocol: 'http:', hostname: '127.0.0.1', port: '9887',
    pathname: '/explorer/', origin: 'http://127.0.0.1:9887'};
  const nodes = await runWithIndex(catalog, 200, null, 404, {mockLocation: local,
    chatBackend: async (url, opts) => {
      assert.equal(url, 'http://127.0.0.1:9887/api/chat');
      assert.equal(opts.method, 'POST');
      return {ok: true, json: async () => ({
        mode: 'opt_in_fictional_multiturn_chat', model_text_unverified: true,
        model_text: 'I am still here.', publication_effect: 'NONE', model_repo_authority: 'NONE',
        source_search: {status: 'SOURCE_LOCAL_HELD_ONLY', rows: []}
      })};
    }});
  nodes.get('lore-chat-token').value = 'A'.repeat(40);
  nodes.get('lore-chat-consent').checked = true;
  nodes.get('lore-chat-input').value = 'Lore, respond.';
  await nodes.get('lore-chat-form').fire('submit', {preventDefault() {}});
  assert.equal(nodes.chatRequests.length, 1);
  assert.ok(nodes.chatRequests.every(({path}) => !path.includes(':9876/')));
  assert.equal(nodes.get('lore-chat-log').children.length, 2);
});

test('Lore searches validated local directory records, labels source limits and offers native inspection', async () => {
  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200);
  nodes.get('lore-query').value = 'Voyager';
  nodes.get('lore-form').fire('submit', { preventDefault() {} });
  const answer = nodes.get('lore-answer');
  assert.match(answer.textContent, /directory observations/);
  assert.match(answer.textContent, /Publisher-guide shelf unavailable/,
    'a missing secondary shelf must not be represented as zero matches');
  assert.match(answer.textContent, /source-local records, not unique Works/);
  const inspect = traverse(answer, (node) => node.tagName === 'button' && node.textContent === 'Inspect directory matches')[0];
  assert.ok(inspect);
  inspect.fire('click');
  assert.equal(nodes.get('discovery-query').value, 'Voyager');
  assert.equal(nodes.get('discovery-query').focused, true);
  assert.match(nodes.get('discovery-summary').textContent, /source-local metadata rows match/);
});

test('Lore fails closed on absent local data and never interprets hostile search text as HTML', async () => {
  const noShelves = await runWithIndex(catalog);
  noShelves.get('lore-query').value = 'Datalore';
  noShelves.get('lore-form').fire('submit', { preventDefault() {} });
  assert.match(noShelves.get('lore-answer').textContent, /Neither validated local shelf is available/);
  assert.doesNotMatch(noShelves.get('lore-answer').textContent, /0 directory observations/);

  const directory = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, null, 404, directory, 200);
  const payload = '<img src=x onerror=alert(1)>';
  nodes.get('lore-query').value = payload;
  nodes.get('lore-form').fire('submit', { preventDefault() {} });
  assert.ok(nodes.get('lore-answer').textContent.includes(payload), 'query may be shown as inert text');
  assert.equal(traverse(nodes.get('lore-answer'), (node) => ['img', 'script', 'svg'].includes(node.tagName)).length, 0);
  nodes.get('lore-query').value = 'x'.repeat(101);
  nodes.get('lore-form').fire('submit', { preventDefault() {} });
  assert.match(nodes.get('lore-answer').textContent, /1–100 characters/);
  assert.equal(nodes.get('lore-answer').textContent.includes('directory observations'), false);
});
