import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';
import { webcrypto, createHash } from 'node:crypto';

const SCRIPT = readFileSync(new URL('../explorer/app.js', import.meta.url), 'utf8');
const IDS = ['search-input', 'scope-filter', 'mission-filter', 'kind-filter', 'status-filter',
  'explorer-navigation', 'navigation-scroll-hint',
  'filters', 'data-state', 'mission-count', 'briefing-count', 'record-count', 'research-top-count', 'research-nav-count', 'film-top-count', 'film-nav-count', 'film-state', 'film-list', 'film-query', 'film-filters', 'film-summary', 'discovery-nav-count', 'discovery-top-count', 'discovery-state', 'discovery-metrics', 'discovery-list', 'discovery-query', 'discovery-medium', 'discovery-series', 'discovery-kind', 'discovery-lineage', 'discovery-overview', 'discovery-verification', 'discovery-publisher-check', 'publisher-card-state', 'publisher-card-download', 'discovery-synopsis', 'discovery-tag', 'discovery-filters', 'discovery-summary', 'discovery-empty', 'notice',
  'mission-list', 'briefing-list', 'record-list', 'mission-empty', 'briefing-empty',
  'record-empty', 'missions', 'briefings', 'records', 'result-summary', 'search-heading',
  'research-query', 'research-mission', 'research-reset', 'research-filters', 'research-count',
  'research-state', 'research-list', 'research-empty', 'research-summary', 'tone-toggle',
  'lore-toggle', 'lore-console', 'lore-close', 'lore-form', 'lore-query', 'lore-answer',
  'discovery-directory', 'episode-source-cards',
  'artwork-toggle', 'artwork-state', 'publisher-edition-nav-count', 'publisher-edition-state',
  'publisher-edition-query', 'publisher-edition-tag', 'publisher-edition-filters',
  'publisher-edition-summary', 'publisher-edition-list', 'publisher-edition-empty',
  'publisher-isbn-nav-count', 'publisher-isbn-state', 'publisher-isbn-download',
  'publisher-isbn-query', 'publisher-isbn-status', 'publisher-isbn-tag',
  'publisher-isbn-filters', 'publisher-isbn-summary', 'publisher-isbn-list', 'publisher-isbn-empty',
  'paramount-nav-count', 'paramount-state', 'paramount-download', 'paramount-query',
  'paramount-status', 'paramount-tag', 'paramount-filters', 'paramount-summary',
  'paramount-list', 'paramount-empty', 'episode-source-nav-count', 'episode-source-state',
  'episode-source-download', 'episode-source-query', 'episode-source-series',
  'episode-source-status', 'episode-source-tag', 'episode-source-filters',
  'episode-source-summary', 'episode-source-list', 'episode-source-empty'];

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
  }

  set textContent(value) { this._text = String(value); this.children = []; }
  get textContent() { return this._text + this.children.map((child) => child.textContent).join(''); }
  set innerHTML(_) { throw Error('HTML injection sink is forbidden'); }
  set outerHTML(_) { throw Error('HTML injection sink is forbidden'); }
  setAttribute(key, value) { this.attributes.set(key, String(value)); }
  getAttribute(key) { return this.attributes.get(key) || null; }
  removeAttribute(key) { this.attributes.delete(key); }
  append(...children) {
    for (const child of children) {
      if (child.tagName === '#fragment') this.children.push(...child.children);
      else this.children.push(child);
    }
  }
  replaceChildren(...children) { this.children = []; this._text = ''; this.append(...children); }
  add(option) { this.children.push(option); }
  addEventListener(type, listener) {
    const list = this.handlers.get(type) || [];
    list.push(listener);
    this.handlers.set(type, list);
  }
  fire(type, event) { for (const listener of this.handlers.get(type) || []) listener(event); }
  scrollIntoView() {}
  focus() { this.focused = true; }
}

function traverse(node, predicate) {
  const found = predicate(node) ? [node] : [];
  for (const child of node.children) found.push(...traverse(child, predicate));
  return found;
}

async function runWithIndex(index, status = 200, research = null, researchStatus = 404, browserAudio = {}, films = null, filmStatus = 404, directory = null, directoryStatus = 404, artwork = null, artworkStatus = 404, synopsis = null, synopsisStatus = 404, appScript = SCRIPT, metadataBytes = null, metadataStatus = 404, shortBytes = null, shortStatus = 404, rejectDigest = false, publisherBytes = null, publisherStatus = 404, sourceCardBytes = null, sourceCardStatus = 404, isbnBytes = null, isbnStatus = 404, paramountBytes = null, paramountStatus = 404, episodeBytes = null, episodeStatus = 404) {
  const nodes = new Map(IDS.map((id) => [id, new FakeNode()]));
  const requested = new Set();
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
    if (path === './index.json') return { status, ok: status >= 200 && status < 300, json: async () => index };
    if (path === './research-leads.json') return { status: researchStatus, ok: researchStatus >= 200 && researchStatus < 300, json: async () => research };
    if (path === './film-catalog.json') return { status: filmStatus, ok: filmStatus >= 200 && filmStatus < 300, json: async () => films };
    if (path === './discovery-catalog.json') return { status: directoryStatus, ok: directoryStatus >= 200 && directoryStatus < 300, json: async () => directory };
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
    location: { origin: 'https://example.test' },
    window: { requestAnimationFrame: (fn) => fn(), ...browserAudio }, console
  }, { filename: 'app.js' });
  // Every fixture must reach the optional loader frontier and finish every
  // observed WebCrypto task. A second quiet event-loop turn lets chained
  // Promise callbacks update the DOM. This avoids machine-load timing races
  // without a guessed fixed delay or swallowing a rejected request.
  const optionalPaths = ['./film-catalog.json', './discovery-catalog.json', './lit-publisher-edition-leads.json',
    './artwork-catalog.json', './synopsis-catalog.json',
    './metadata-rechecks.json', './short-synopsis-catalog.json', './accepted-source-card-rechecks.json',
    './publisher-isbn-crosschecks.json', './paramount-film-rechecks.json', './episode-source-cards.json'];
  const deadline = Date.now() + 5000;
  let quietTurns = 0;
  while (quietTurns < 2 && Date.now() < deadline) {
    await new Promise((resolve) => setImmediate(resolve));
    if (optionalPaths.every((path) => requested.has(path)) && inFlightDigests.size === 0) quietTurns++;
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
  assert.match(nodes.get('paramount-state').textContent, /3 source discrepancies held/);
  assert.doesNotMatch(nodes.get('paramount-list').textContent, /poster_asset_locator|original_synopsis_candidate/);
  nodes.get('paramount-status').value = 'HELD_UNRESOLVED_SOURCE_ANOMALY';
  nodes.get('paramount-filters').fire('change');
  assert.match(nodes.get('paramount-summary').textContent, /^3 of 13/);
  assert.equal(traverse(nodes.get('paramount-list'), (n) => n.className === 'card paramount-card paramount-held').length, 3);
  nodes.get('paramount-status').value = 'all';
  nodes.get('paramount-query').value = 'Patrick Stewart';
  nodes.get('paramount-filters').fire('input');
  assert.ok(traverse(nodes.get('paramount-list'), (n) => n.tagName === 'article').length >= 1);
  nodes.get('paramount-query').value = '';
  nodes.get('paramount-tag').value = 'anomaly:held';
  nodes.get('paramount-filters').fire('change');
  assert.match(nodes.get('paramount-summary').textContent, /^3 of 13/);
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

const licensedArtwork = {
  schema_version: '1.1.0', data_status: 'PROVENANCE_REVIEWED_ARTWORK', coverage_effect: 'NONE',
  rights_policy: 'PER_ENTRY_DISPLAY_GATE', artwork_count: 1,
  artwork: [{
    row_id: 'film:star-trek-2009', image_path: './licensed-artwork/verified-film-cover.webp',
    image_sha256: '1'.repeat(64), alt_text: 'Licensed publisher artwork for Star Trek (2009)',
    source_locator: filmCatalog.films[0].source_locator, rights_status: 'PUBLIC_DISPLAY_PERMISSION_VERIFIED',
    rights_receipt_sha256: '2'.repeat(64)
  }]
};

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
  assert.match(nodes.get('discovery-list').textContent, /original abstract/);
  assert.match(nodes.get('film-list').textContent, /Artwork not sourced/);
  assert.equal(traverse(nodes.get('discovery-list'), (n) => n.tagName === 'img').length, 0);
  assert.equal(traverse(nodes.get('film-list'), (n) => n.tagName === 'img').length, 0);
  assert.equal(nodes.get('briefing-count').textContent, '0', 'image presentation never changes admission');
});

test('explicit artwork opt-in displays only same-origin rights-receipted assets with graceful error fallback', async () => {
  const nodes = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200, null, 404, licensedArtwork, 200);
  const toggle = nodes.get('artwork-toggle');
  assert.equal(toggle.disabled, false);
  assert.equal(toggle.attributes.get('aria-pressed'), 'false');
  assert.equal(traverse(nodes.get('film-list'), (n) => n.tagName === 'img').length, 0, 'nothing auto-loads');
  toggle.fire('click');
  assert.equal(toggle.attributes.get('aria-pressed'), 'true');
  const images = traverse(nodes.get('film-list'), (n) => n.tagName === 'img');
  assert.equal(images.length, 1);
  assert.equal(images[0].src, './licensed-artwork/verified-film-cover.webp');
  assert.equal(images[0].loading, 'lazy');
  assert.equal(images[0].referrerPolicy, 'no-referrer');
  assert.match(images[0].alt, /Licensed publisher artwork/);
  images[0].fire('error');
  assert.equal(traverse(nodes.get('film-list'), (n) => n.tagName === 'img').length, 0);
  assert.match(nodes.get('film-list').textContent, /Image unavailable/);
  toggle.fire('click');
  assert.equal(toggle.attributes.get('aria-pressed'), 'false');
  assert.equal(traverse(nodes.get('film-list'), (n) => n.tagName === 'img').length, 0);
});

test('malicious, unreviewed, duplicated or off-origin artwork records are rejected as a whole', async () => {
  const changes = [
    (r) => { r.artwork[0].image_path = 'https://evil.example/track.jpg'; },
    (r) => { r.artwork[0].image_path = './licensed-artwork/../secrets.webp'; },
    (r) => { r.artwork[0].image_path = 'data:image/png;base64,AAAA'; },
    (r) => { r.artwork[0].source_locator = 'https://www.startrek.com@evil.invalid/x'; },
    (r) => { r.artwork[0].rights_status = 'NOT_ESTABLISHED'; },
    (r) => { r.artwork[0].image_sha256 = 'unknown'; },
    (r) => { r.artwork[0].rights_receipt_sha256 = 'unknown'; },
    (r) => { r.artwork[0].admission_status = 'ACCEPTED'; },
    (r) => { r.artwork[0].row_id = 'film:unknown'; },
    (r) => { r.artwork.push(structuredClone(r.artwork[0])); r.artwork_count = 2; },
    (r) => { r.coverage_effect = 'AUDITED'; },
  ];
  for (const change of changes) {
    const bad = structuredClone(licensedArtwork);
    change(bad);
    const nodes = await runWithIndex(catalog, 200, null, 404, {}, filmCatalog, 200, null, 404, bad, 200);
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
    schema_version: '1.1.0', data_status: 'PROVENANCE_REVIEWED_ARTWORK', coverage_effect: 'NONE',
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
  assert.equal(hint.hidden, true, 'no cue when section links fit the rail');
  assert.equal(nav.attributes.has('aria-describedby'), false, 'no hidden stale description');
  assert.equal(typeof resize, 'function', 'viewport resize listener installed');

  nav.clientWidth = 375;
  nav.scrollWidth = 1030;
  nav.scrollLeft = 0;
  resize();
  assert.equal(hint.hidden, false, 'real horizontal overflow shows a visible cue');
  assert.match(hint.textContent, /More sections →/);
  assert.match(hint.textContent, /Swipe, scroll or Tab/);
  assert.equal(nav.attributes.get('aria-describedby'), 'navigation-scroll-hint');

  nav.scrollLeft = 300;
  nav.fire('scroll');
  assert.match(hint.textContent, /Sections both ways ↔/);
  nav.scrollLeft = 655;
  nav.fire('scroll');
  assert.match(hint.textContent, /Earlier sections ←/);

  nav.clientWidth = 1030;
  resize();
  assert.equal(hint.hidden, true, 'cue disappears when every link fits');
  assert.equal(nav.attributes.has('aria-describedby'), false);
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
  assert.match(html, /id="discovery-top-count"[^>]*href="#discovery-directory"/,
    'prominent directory count links to the source-local listing rather than implying 12 total episodes');
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
  assert.match(html, /not an AI model, a trapped consciousness, or an authority on canon/);
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
