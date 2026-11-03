import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createLoreSemanticEngine } from '../explorer/lore-semantic-chat.js';

test('flexible visitor naming and pronoun recall never become Trek evidence', () => {
  const engine = createLoreSemanticEngine();
  assert.match(engine.ask('I named my border collie Quark-9.').text, /Quark-9/);
  assert.match(engine.ask('Can you remember his name?').text, /Quark-9/);
  assert.match(engine.ask('Which animal?').text, /border collie/i);
  assert.deepEqual(engine.ask('What source proves the name?').references, []);
  engine.reset();
  assert.doesNotMatch(engine.ask('Can you remember his name?').text, /Quark-9/);
});

test('conversational topic reflection and technical comparison do not trigger archive search', () => {
  const engine = createLoreSemanticEngine();
  assert.match(engine.ask('Let us talk about the ethics of Section 31.').text, /Section 31|ethic|security/i);
  assert.match(engine.ask('What are we even discussing?').text, /Section 31/i);
  assert.match(engine.ask('Compare a warp core with a holodeck.').text, /propulsion|power.*simulation/i);
  assert.match(engine.ask('Who was Guinan?').text, /Guinan|Ten Forward/i);
});

test('distress tone and repair remain respectful through paraphrases', () => {
  const engine = createLoreSemanticEngine();
  assert.match(engine.ask('I got terrible news today and I feel shaken.').text, /listen|difficult|take your time/i);
  const quiet = engine.ask('Please do not make a joke.');
  assert.match(quiet.text, /no jokes|listen/i);
  assert.doesNotMatch(quiet.text, /laugh|entertaining|amusing/i);
  assert.match(engine.ask('Just listen.').text, /listen/i);
  assert.match(engine.ask('That explanation missed the point.').text, /fair criticism|listen|difficult/i);
  assert.match(engine.ask('Answer directly now.').text, /listening|hear|difficult/i);
});

test('generic franchise searches are not arbitrarily attached to 1214 discovery rows', () => {
  const catalog = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url), 'utf8'));
  assert.equal(catalog.row_count, catalog.rows.length);
  const engine = createLoreSemanticEngine({ records: catalog.rows });
  for (const query of [
    'Tell me about Star Trek Voyager',
    'Search Star Trek Enterprise',
    'Find a book about Star Trek',
    'Tell me about Star Trek Deep Space Nine',
  ]) {
    assert.deepEqual(engine.ask(query).references, [], query);
  }
  assert.ok(engine.ask('Tell me about Darmok').references.some(row => row.title === 'Darmok'));
});

test('archive lead cannot survive a personal topic change and indirect citation question', () => {
  const engine = createLoreSemanticEngine({ records: [{ row_id: 'darmok', medium: 'EPISODE', title: 'Darmok', verification_status: 'UNVERIFIED_METADATA' }] });
  assert.equal(engine.ask('Tell me about Darmok').references.length, 1);
  engine.ask('My cat is named Radar-18.');
  const source = engine.ask('Show me the citation for that.');
  assert.deepEqual(source.references, []);
  assert.doesNotMatch(source.text, /darmok/i);
});
