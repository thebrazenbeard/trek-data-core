import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';
import { webcrypto } from 'node:crypto';

const SCRIPT = readFileSync(new URL('../explorer/app.js', import.meta.url), 'utf8');
const IDS = ['search-input', 'scope-filter', 'mission-filter', 'kind-filter', 'status-filter',
  'explorer-navigation', 'navigation-scroll-hint',
  'filters', 'data-state', 'mission-count', 'briefing-count', 'record-count', 'research-top-count', 'research-nav-count', 'film-top-count', 'film-nav-count', 'film-state', 'film-list', 'film-query', 'film-filters', 'film-summary', 'discovery-nav-count', 'discovery-top-count', 'discovery-state', 'discovery-metrics', 'discovery-list', 'discovery-query', 'discovery-medium', 'discovery-series', 'discovery-kind', 'discovery-lineage', 'discovery-filters', 'discovery-summary', 'discovery-empty', 'notice',
  'mission-list', 'briefing-list', 'record-list', 'mission-empty', 'briefing-empty',
  'record-empty', 'missions', 'briefings', 'records', 'result-summary', 'search-heading',
  'research-query', 'research-mission', 'research-reset', 'research-filters', 'research-count',
  'research-state', 'research-list', 'research-empty', 'research-summary', 'tone-toggle',
  'artwork-toggle', 'artwork-state'];

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

async function runWithIndex(index, status = 200, research = null, researchStatus = 404, browserAudio = {}, films = null, filmStatus = 404, directory = null, directoryStatus = 404, artwork = null, artworkStatus = 404, synopsis = null, synopsisStatus = 404, appScript = SCRIPT, metadataBytes = null, metadataStatus = 404, shortBytes = null, shortStatus = 404) {
  const nodes = new Map(IDS.map((id) => [id, new FakeNode()]));
  const requested = new Set();
  const inFlightDigests = new Set();
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
    assert.fail('Unexpected data request: ' + path);
  };
  const deterministicCrypto = {
    subtle: {
      digest(algorithm, bytes) {
        // Real WebCrypto is asynchronous on CI. Track every actual digest
        // completion rather than assuming one setImmediate settles sidecars.
        const pending = webcrypto.subtle.digest(algorithm, bytes);
        inFlightDigests.add(pending);
        pending.finally(() => inFlightDigests.delete(pending));
        return pending;
      }
    }
  };
  vm.runInNewContext(appScript, {
    document, fetch, Option: OptionNode, URL, crypto: deterministicCrypto, TextDecoder,
    location: { origin: 'https://example.test' },
    window: { requestAnimationFrame: (fn) => fn(), ...browserAudio }, console
  }, { filename: 'app.js' });
  // Every fixture must reach the optional loader frontier and finish every
  // observed WebCrypto task. A second quiet event-loop turn lets chained
  // Promise callbacks update the DOM. This avoids machine-load timing races
  // without a guessed fixed delay or swallowing a rejected request.
  const optionalPaths = ['./film-catalog.json', './discovery-catalog.json',
    './artwork-catalog.json', './synopsis-catalog.json',
    './metadata-rechecks.json', './short-synopsis-catalog.json'];
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
