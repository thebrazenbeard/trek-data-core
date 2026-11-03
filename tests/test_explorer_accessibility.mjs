import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import vm from 'node:vm';

const script = readFileSync(new URL('../explorer/app.js', import.meta.url), 'utf8');
const ids = [
  'search-input', 'scope-filter', 'mission-filter', 'kind-filter', 'status-filter',
  'filters', 'data-state', 'mission-count', 'briefing-count', 'record-count', 'research-top-count', 'research-nav-count', 'film-top-count', 'film-nav-count', 'film-state', 'film-list', 'film-query', 'film-filters', 'film-summary', 'discovery-nav-count', 'discovery-top-count', 'discovery-episode-count', 'discovery-literature-count', 'discovery-state', 'discovery-metrics', 'discovery-list', 'discovery-query', 'discovery-medium', 'discovery-lineage', 'discovery-publisher-check', 'publisher-card-state', 'publisher-card-download', 'discovery-filters', 'discovery-summary', 'discovery-empty', 'notice',
  'mission-list', 'briefing-list', 'record-list', 'mission-empty', 'briefing-empty',
  'record-empty', 'missions', 'briefings', 'records', 'result-summary', 'search-heading',
  'research-query', 'research-mission', 'research-reset', 'research-filters',
  'research-count', 'research-state', 'research-list', 'research-empty',
  'research-summary', 'research-heading', 'tone-toggle', 'artwork-toggle', 'artwork-state',
  'lore-toggle', 'lore-console', 'lore-close', 'lore-form', 'lore-query', 'lore-answer',
  'publisher-edition-nav-count', 'publisher-edition-state', 'publisher-edition-query',
  'publisher-edition-tag', 'publisher-edition-filters', 'publisher-edition-summary',
  'publisher-edition-list', 'publisher-edition-empty',
  'publisher-isbn-nav-count', 'publisher-isbn-state', 'publisher-isbn-download',
  'publisher-isbn-query', 'publisher-isbn-status', 'publisher-isbn-tag',
  'publisher-isbn-filters', 'publisher-isbn-summary', 'publisher-isbn-list', 'publisher-isbn-empty',
  'paramount-nav-count', 'paramount-state', 'paramount-download', 'paramount-query',
  'paramount-status', 'paramount-tag', 'paramount-filters', 'paramount-summary',
  'paramount-list', 'paramount-empty',
  'episode-source-nav-count', 'episode-source-state', 'episode-source-download',
  'episode-source-query', 'episode-source-series', 'episode-source-status',
  'episode-source-tag', 'episode-source-filters', 'episode-source-summary',
  'episode-source-list', 'episode-source-empty'
];

class Node {
  constructor(tagName = 'div') {
    this.tagName = tagName;
    this.children = [];
    this.events = new Map();
    this.attributes = new Map();
    this._text = '';
    this.value = '';
    this.hidden = false;
    this.focused = false;
  }
  get textContent() { return this._text + this.children.map((node) => node.textContent).join(''); }
  set textContent(value) { this._text = String(value); this.children = []; }
  setAttribute(name, value) { this.attributes.set(name, String(value)); }
  append(...children) { for (const child of children) this.children.push(...(child.tagName === '#fragment' ? child.children : [child])); }
  replaceChildren(...children) { this.children = []; this._text = ''; this.append(...children); }
  add(option) { this.children.push(option); }
  addEventListener(name, callback) { this.events.set(name, [...(this.events.get(name) || []), callback]); }
  fire(name) { for (const callback of this.events.get(name) || []) callback({ preventDefault() {} }); }
  focus() { this.focused = true; }
  scrollIntoView() { this.scrolled = true; }
}

const index = {
  schema_version: '1.0.0', build: { data_status: 'MISSION_CATALOG_ONLY', projection_hash: null },
  missions: [{ id: 'tng', title: 'The Next Generation' }, { id: 'voy', title: 'Voyager' }],
  briefings: [], records: []
};

const research = {
  schema_version: '2.0.0', data_status: 'CANDIDATE_DISCOVERY_ONLY',
  source_policy: 'EXTERNAL_METADATA_ONLY', coverage_effect: 'NONE',
  held_candidate_count: 2, lead_count: 2, sampled_missions_count: 2,
  leads: ['tng', 'voy'].map((mission_id, i) => ({
    mission_id, source_type: 'WIKIDATA_METADATA', independence_group: 'wikidata:wdqs',
    episode_qid: `Q${i + 1}`, episode_label: `Unverified ${mission_id}`,
    snapshot_id: 'WDQS-TEST-001', query_sha256: 'a'.repeat(64), response_sha256: 'b'.repeat(64),
    verification_status: 'UNVERIFIED_METADATA'
  }))
};

async function load(researchPayload, researchStatus = 200) {
  const nodes = new Map(ids.map((id) => [id, new Node()]));
  nodes.get('lore-console').hidden = true;
  for (const id of ['scope-filter', 'mission-filter', 'kind-filter', 'status-filter', 'research-mission', 'publisher-edition-tag']) nodes.get(id).value = 'all';
  const document = {
    baseURI: 'https://example.test/explorer/index.html',
    getElementById: (id) => { assert.ok(nodes.has(id), `missing fake ${id}`); return nodes.get(id); },
    createElement: (tag) => new Node(tag),
    createDocumentFragment: () => new Node('#fragment')
  };
  const fetch = async (name) => name === './index.json'
    ? { status: 200, ok: true, json: async () => index }
    : name === './research-leads.json'
      ? { status: researchStatus, ok: researchStatus === 200, json: async () => researchPayload }
      : { status: 404, ok: false };
  vm.runInNewContext(script, {
    document, fetch, URL, location: { origin: 'https://example.test' },
    Option: class extends Node { constructor(text, value) { super('option'); this.textContent = text; this.value = value; } },
    window: { requestAnimationFrame: (fn) => fn() }
  });
  await new Promise((resolve) => setImmediate(resolve));
  return nodes;
}

test('Mission card navigates to its unverified leads without promoting them or losing keyboard focus', async () => {
  const nodes = await load(research);
  const missionCard = nodes.get('mission-list').children[0];
  assert.match(missionCard.textContent, /Indexed Briefings0/);
  assert.match(missionCard.textContent, /Unverified research leads1/);
  const shortcut = missionCard.children.find((node) => node.className === 'research-shortcut');
  assert.ok(shortcut, 'candidate-only shortcut exists for a Mission with leads');
  assert.match(shortcut.attributes.get('aria-label'), /unverified Research Leads for The Next Generation/);

  nodes.get('research-query').value = 'no match';
  nodes.get('research-filters').fire('input');
  assert.equal(nodes.get('research-list').children.length, 0);
  shortcut.fire('click');
  assert.equal(nodes.get('research-query').value, '');
  assert.equal(nodes.get('research-mission').value, 'tng');
  assert.equal(nodes.get('research-list').children.length, 1);
  assert.match(nodes.get('research-list').textContent, /Unverified tng/);
  assert.equal(nodes.get('research-query').focused, true);
  assert.equal(nodes.get('research-heading').scrolled, true);
  assert.equal(nodes.get('mission-filter').value, 'all', 'governed index filters remain independent');
  assert.equal(nodes.get('briefing-count').textContent, '0');
});

test('Missing or rejected research data never creates misleading candidate shortcuts', async () => {
  const missing = await load(null, 404);
  const bad = structuredClone(research);
  bad.leads[0].verification_status = 'ACCEPTED';
  const rejected = await load(bad);
  for (const nodes of [missing, rejected]) {
    assert.equal(nodes.get('mission-list').children.length, 2);
    assert.equal(nodes.get('mission-list').children[0].children.some((node) => node.className === 'research-shortcut'), false);
    assert.equal(nodes.get('mission-list').children[0].textContent.includes('Unverified research leads'), false);
    assert.equal(nodes.get('briefing-count').textContent, '0');
  }
});

test('publisher-card filter and availability use explicit accessible source-only labels', () => {
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  assert.match(html, /<label for="discovery-publisher-check">Additional publisher-card read \(source-local\)<\/label>/);
  assert.match(html, /<select id="discovery-publisher-check" name="publisher-check">/);
  assert.match(html, /<p class="directory-state publisher-card-state" id="publisher-card-state" role="status" aria-live="polite">/);
  assert.match(html, /id="publisher-card-download"[^>]*hidden>/);
  assert.match(html, /Publisher card title string match/);
  assert.match(html, /Held title \/ split unresolved/);
});

test('public publisher ISBN shelf distinguishes unverified private edition state from first-party metadata', () => {
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  assert.match(html, /<section id="publisher-isbn-crosschecks"[^>]*aria-labelledby="publisher-isbn-heading"/);
  assert.match(html, /<label for="publisher-isbn-query">Title, creator, ISBN or source-local reference<\/label>/);
  assert.match(html, /<label for="publisher-isbn-status">ISBN crosscheck status<\/label>/);
  assert.match(html, /<label for="publisher-isbn-tag">Source \/ discrepancy tag<\/label>/);
  assert.match(html, /id="publisher-isbn-state"[^>]*role="status" aria-live="polite"/);
  assert.match(html, /id="publisher-isbn-download"[^>]*hidden>/);
  assert.match(html, /Not an owner-private ebook authentication/);
});

test('Paramount film-page shelf exposes accessible filters and explicit non-admission provenance', () => {
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  assert.match(html, /<section id="paramount-rechecks"[^>]*aria-labelledby="paramount-heading"/);
  assert.match(html, /<form id="paramount-filters"[^>]*role="search" aria-label="Search Paramount source-local film-page metadata"/);
  assert.match(html, /<label for="paramount-query">Publisher URL label, cast, director, year or rating<\/label>/);
  assert.match(html, /<label for="paramount-status">Source review state<\/label>/);
  assert.match(html, /<label for="paramount-tag">Source-local facet<\/label>/);
  assert.match(html, /id="paramount-state"[^>]*role="status" aria-live="polite"/);
  assert.match(html, /id="paramount-download"[^>]*hidden>/);
  assert.match(html, /not film viewing, canonical Work identity, independent witnesses or released poster\/synopsis text/);
});

test('HELD publisher episode-guide shelf has accessible tags, filters, and no Work or synopsis promotion', () => {
  const html = readFileSync(new URL('../explorer/index.html', import.meta.url), 'utf8');
  assert.match(html, /<section id="episode-source-cards"[^>]*aria-labelledby="episode-source-heading"/);
  assert.match(html, /<form id="episode-source-filters"[^>]*role="search" aria-label="Search accepted held publisher episode-guide cards"/);
  for (const id of ['episode-source-query', 'episode-source-series', 'episode-source-status', 'episode-source-tag']) {
    assert.ok(html.includes(`<label for="${id}">`));
  }
  assert.match(html, /id="episode-source-state"[^>]*role="status" aria-live="polite"/);
  assert.match(html, /id="episode-source-download"[^>]*hidden>/);
  assert.match(html, /not an admitted Work, watched episode, canon fact, approved synopsis or licensed image/);
});
