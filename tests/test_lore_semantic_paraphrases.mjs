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

test('alternate pet phrasing, attribution, and memory are not recast as Trek records', () => {
  const engine = createLoreSemanticEngine();
  assert.match(engine.ask('My rescue beagle goes by Nebula-88.').text, /Nebula-88/);
  assert.match(engine.ask('What did I call my pup?').text, /Nebula-88/);
  const origin = engine.ask('Is that from Star Trek, or just something I told you?');
  assert.match(origin.text, /you supplied|you told|did not come from a Trek source/i);
  assert.deepEqual(origin.references, []);
});

test('grief and requested gentleness suppress ordinary character sarcasm', () => {
  const engine = createLoreSemanticEngine();
  const grief = engine.ask('My friend died yesterday. I feel completely lost.');
  assert.match(grief.text, /difficult|listen|sorry|take your time/i);
  for (const prompt of ['Please be gentle.', 'I do not need advice, only someone to hear me.']) {
    const response = engine.ask(prompt);
    assert.match(response.text, /listen|no jokes|take your time/i);
    assert.doesNotMatch(response.text, /laugh|catastroph|entertaining|poop/i);
  }
});

test('two technical concepts keep distinction through pronoun, repair and source-origin followups', () => {
  const engine = createLoreSemanticEngine();
  const first = engine.ask('Can you contrast a transporter and a replicator?');
  assert.match(first.text, /transport.*replicat/i);
  assert.doesNotMatch(first.text, /poop|dinner|excrement/i);
  assert.match(engine.ask('What is the practical difference?').text, /transporter.*replicator/i);
  assert.match(engine.ask('That was evasive. Start over.').text, /transporter.*replicator/i);
  assert.match(engine.ask('Is that from Star Trek, or just something I told you?').text, /unsourced|did not attach/i);
  assert.match(engine.ask('New subject: should I become an engineer?').text, /engineer.*work/i);
});

test('named previous source can be retrieved anew after unrelated turns', () => {
  const engine = createLoreSemanticEngine({ records: [{ row_id: 'tng:darmok', title: 'Darmok', medium: 'EPISODE', verification_status: 'UNVERIFIED_METADATA' }] });
  engine.ask('Tell me about Darmok');
  engine.ask('Should I become an engineer?');
  assert.equal(engine.ask('Which source?').references.length, 0);
  const resumed = engine.ask('Return to Darmok. Which archive record did you find?');
  assert.equal(resumed.references[0]?.row_id, 'tng:darmok');
});

test('less literal comparison requests still distinguish warp core and holodeck', () => {
  const engine = createLoreSemanticEngine();
  assert.match(engine.ask('Is a warp core basically the same thing as a holodeck?').text, /warp core.*holodeck/i);
  assert.match(engine.ask('What distinguishes those two?').text, /warp core.*holodeck/i);
  assert.match(engine.ask('Hypothesize a ship powered by a holodeck.').text, /hypothetical|imaginary|energy/i);
});
