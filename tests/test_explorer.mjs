import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const SCRIPT = readFileSync(new URL('../explorer/app.js', import.meta.url), 'utf8');
const IDS = ['search-input', 'scope-filter', 'mission-filter', 'kind-filter', 'status-filter',
  'filters', 'data-state', 'mission-count', 'briefing-count', 'record-count', 'research-top-count', 'research-nav-count', 'film-top-count', 'film-nav-count', 'film-state', 'film-list', 'film-query', 'film-filters', 'film-summary', 'discovery-nav-count', 'discovery-state', 'discovery-metrics', 'discovery-list', 'discovery-query', 'discovery-medium', 'discovery-lineage', 'discovery-filters', 'discovery-summary', 'discovery-empty', 'notice',
  'mission-list', 'briefing-list', 'record-list', 'mission-empty', 'briefing-empty',
  'record-empty', 'missions', 'briefings', 'records', 'result-summary', 'search-heading',
  'research-query', 'research-mission', 'research-reset', 'research-filters', 'research-count',
  'research-state', 'research-list', 'research-empty', 'research-summary', 'tone-toggle'];

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

async function runWithIndex(index, status = 200, research = null, researchStatus = 404, browserAudio = {}, films = null, filmStatus = 404, directory = null, directoryStatus = 404) {
  const nodes = new Map(IDS.map((id) => [id, new FakeNode()]));
  nodes.get('scope-filter').value = 'all';
  nodes.get('mission-filter').value = 'all';
  nodes.get('kind-filter').value = 'all';
  nodes.get('status-filter').value = 'all';
  nodes.get('research-mission').value = 'all';
  nodes.get('discovery-medium').value = 'all';
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
    createElement: (tag) => new FakeNode(tag),
    createDocumentFragment: () => new FakeNode('#fragment')
  };
  const fetch = async (path, opts) => {
    assert.equal(opts.cache, 'no-store');
    if (path === './index.json') return { status, ok: status >= 200 && status < 300, json: async () => index };
    if (path === './research-leads.json') return { status: researchStatus, ok: researchStatus >= 200 && researchStatus < 300, json: async () => research };
    if (path === './film-catalog.json') return { status: filmStatus, ok: filmStatus >= 200 && filmStatus < 300, json: async () => films };
    if (path === './discovery-catalog.json') return { status: directoryStatus, ok: directoryStatus >= 200 && directoryStatus < 300, json: async () => directory };
    assert.fail('Unexpected data request: ' + path);
  };
  vm.runInNewContext(SCRIPT, {
    document, fetch, Option: OptionNode, URL, location: { origin: 'https://example.test' },
    window: { requestAnimationFrame: (fn) => fn(), ...browserAudio }, console
  }, { filename: 'app.js' });
  await new Promise((resolve) => setImmediate(resolve));
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

const filmCatalog = {
  schema_version: '1.0.0', data_status: 'DISCOVERY_ONLY', coverage_effect: 'NONE',
  source_group: 'publisher:startrek.com', film_count: 2,
  films: [
    { id: 'star-trek-2009', title: 'Star Trek (2009)', source_locator: 'https://www.startrek.com/movies/star-trek-2009', source_group: 'publisher:startrek.com', work_type: 'FEATURE_FILM', verification_status: 'UNVERIFIED_METADATA', discovery_source: 'OFFICIAL_DIRECTORY' },
    { id: 'section-31', title: 'Star Trek: Section 31', source_locator: 'https://www.startrek.com/news/star-trek-section-31-premieres-january-24', source_group: 'publisher:startrek.com', work_type: 'STREAMING_ORIGINAL_FILM', verification_status: 'UNVERIFIED_METADATA', discovery_source: 'OFFICIAL_ANNOUNCEMENT' }
  ]
};

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
  assert.equal(nodes.get('discovery-nav-count').textContent, '1,186');
  assert.match(nodes.get('discovery-state').textContent, /not a franchise total/);
  assert.match(nodes.get('discovery-metrics').textContent, /Episode refs: 1,155/);
  assert.match(nodes.get('discovery-metrics').textContent, /Film rows: 14/);
  assert.match(nodes.get('discovery-metrics').textContent, /Literary Works: 1/);
  assert.match(nodes.get('discovery-metrics').textContent, /Short-form releases: 15/);
  assert.match(nodes.get('discovery-metrics').textContent, /Audio containers: 1/);
  assert.match(nodes.get('discovery-list').textContent, /Data receipt: explorer\/research-leads\.json/);
  assert.equal(nodes.get('briefing-count').textContent, '0');
  assert.equal(nodes.get('discovery-list').children.length, 41, '40 rows and Show next, not 1,186 cards on load');
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
  assert.equal(nodes.get('discovery-list').children.length, 15);
  assert.match(nodes.get('discovery-list').textContent, /Announced promotional release order/);
  nodes.get('discovery-medium').value = 'AUDIO';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 1);
  assert.match(nodes.get('discovery-list').textContent, /Khan/);
  nodes.get('discovery-medium').value = 'LITERATURE';
  nodes.get('discovery-filters').fire('change');
  assert.equal(nodes.get('discovery-list').children.length, 1);
  assert.match(nodes.get('discovery-list').textContent, /Ring of Fire/);
  assert.match(nodes.get('discovery-list').textContent, /ISBN 9781668095898/);
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

test('untrusted directory cannot forge admission or publisher navigation', async () => {
  const catalogData = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  const accepted = structuredClone(catalogData);
  accepted.rows[0].admission_effect = 'ACCEPTED';
  const blocked = await runWithIndex(catalog, 200, null, 404, {}, null, 404, accepted, 200);
  assert.equal(blocked.get('discovery-nav-count').textContent, '—');
  assert.match(blocked.get('discovery-state').textContent, /rejected/);
  const forged = structuredClone(catalogData);
  forged.rows[0].source_locator = 'https://www.startrek.com@evil.invalid/bogus';
  const noLink = await runWithIndex(catalog, 200, null, 404, {}, null, 404, forged, 200);
  assert.equal(noLink.get('discovery-nav-count').textContent, '—');
  const duplicate = structuredClone(catalogData);
  duplicate.rows[1].row_id = duplicate.rows[0].row_id;
  const noDuplicate = await runWithIndex(catalog, 200, null, 404, {}, null, 404, duplicate, 200);
  assert.equal(noDuplicate.get('discovery-nav-count').textContent, '—');
  const absent = await runWithIndex(null, 404, null, 404, {}, null, 404, catalogData, 200);
  assert.equal(absent.get('discovery-nav-count').textContent, '1,186', 'discovery does not depend on governed Mission index');
  assert.equal(absent.get('mission-count').textContent, '—');
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

test('HTML exposes the separate research search and status elements', () => {
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  assert.match(html, /<nav class="lcars-navigation" aria-label="Explorer sections">/);
  assert.match(html, /href="#research-leads">Episode research leads/);
  assert.match(html, /href="#films">Films/);
  assert.match(html, /id="film-list"/);
  assert.match(html, /id="film-filters"[^>]*aria-label="Search film discovery titles"/);
  assert.match(html, /id="film-state"[^>]*role="status"/);
  assert.match(html, /id="discovery-directory"/);
  assert.match(html, /id="discovery-filters"[^>]*aria-label="Search multimedia discovery metadata"/);
  assert.match(html, /for="discovery-lineage">Source group<\/label>/, 'source-group labels do not imply independent publishers');
  assert.match(html, /id="research-leads"/);
  assert.match(html, /id="research-filters"/);
  assert.match(html, /id="research-state"/);
  assert.match(html, /not admitted Briefings or continuity facts/);
  assert.match(html, /<dt>Briefings<\/dt>/);
  assert.match(html, /<h2 id="briefings-heading">Briefings<\/h2>/);
  assert.match(html, /src="\.\/trek-data-core-hero\.jpg\?v=[0-9a-f]{64}"/);
  assert.match(html, /id="tone-toggle"[^>]*aria-pressed="false"/);
  assert.match(html, /id="filters" role="search" aria-label="Search governed Mission index"/);
  assert.match(html, /id="research-filters"[^>]*role="search" aria-label="Search unverified research leads"/);
});
