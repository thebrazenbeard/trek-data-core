/*
 * Independent source-relevance falsifiers using the real, admitted Explorer
 * discovery catalog. Discovery metadata is not close-read narrative evidence.
 * This suite intentionally refuses plausible title-token collisions.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createLoreSemanticEngine } from '../explorer/lore-semantic-chat.js';

const catalog = JSON.parse(readFileSync(new URL('../explorer/discovery-catalog.json', import.meta.url)));
assert.equal(catalog.data_status, 'DISCOVERY_ONLY');
assert.equal(catalog.coverage_effect, 'NONE');
assert.equal(catalog.rows.length, catalog.row_count);
assert.ok(catalog.rows.length >= 1200);

function refsFor(prompt) {
  const engine = createLoreSemanticEngine({ records: catalog.rows });
  return engine.ask(prompt).references;
}

function proveNoGenericCollision(prompt, expectedMedium = null) {
  const references = refsFor(prompt);
  for (const ref of references) {
    assert.equal(ref.identity_scope, 'SOURCE_LOCAL', `identity scope for ${ref.title}`);
    assert.equal(ref.verification_status, 'UNVERIFIED_METADATA', `metadata status for ${ref.title}`);
    assert.ok(ref.source_group, `source group for ${ref.title}`);
    if (expectedMedium) {
      assert.equal(ref.medium, expectedMedium, `wrong medium for ${JSON.stringify(prompt)}: ${ref.title}`);
    } else {
      assert.fail(`Generic series/subject query ${JSON.stringify(prompt)} attached an unrelated specific title: ${ref.title}`);
    }
  }
}

for (const prompt of [
  'Tell me about Star Trek Voyager',
  'Search Star Trek Enterprise',
  'Tell me about Star Trek Deep Space Nine',
  'Which Star Trek series came first?',
  'Tell me about the Enterprise starship',
  'What do you have on Star Trek: Picard?',
]) {
  test(`generic subject has no unrelated specific archive hit: ${prompt}`, () => {
    proveNoGenericCollision(prompt);
  });
}

for (const [prompt, medium] of [
  ['Find a book about Star Trek', 'LITERATURE'],
  ['Which Voyager episodes feature the Borg?', 'EPISODE'],
  ['Show me novels set aboard Voyager', 'LITERATURE'],
  ['List Enterprise episodes', 'EPISODE'],
  ['Do you have Deep Space Nine episode records?', 'EPISODE'],
  ['Find books with Picard in them', 'LITERATURE'],
  ['Where can I find Star Trek movie records?', 'FILM'],
  ['Search for the Star Trek Discovery episodes', 'EPISODE'],
]) {
  test(`archive medium constraint: ${prompt}`, () => {
    proveNoGenericCollision(prompt, medium);
  });
}

for (const [prompt, exactTitle, expectedMedium] of [
  ['Tell me about Darmok', 'Darmok', 'EPISODE'],
  ['Find Nepenthe', 'Nepenthe', 'EPISODE'],
  ['Find The Voyager Conspiracy', 'The Voyager Conspiracy', 'EPISODE'],
  ['Tell me about Star Trek Beyond', 'Star Trek Beyond', 'FILM'],
]) {
  test(`precise title preserves source metadata match: ${prompt}`, () => {
    const matches = refsFor(prompt);
    assert.ok(matches.some(ref => ref.title === exactTitle && ref.medium === expectedMedium),
      `no exact ${expectedMedium} title match for ${JSON.stringify(prompt)}: ${matches.map(r => r.title).join(', ')}`);
    for (const match of matches) {
      assert.equal(match.identity_scope, 'SOURCE_LOCAL');
      assert.equal(match.verification_status, 'UNVERIFIED_METADATA');
    }
  });
}

test('source follow-up cannot cite old title after unrelated topical turn', () => {
  const engine = createLoreSemanticEngine({ records: catalog.rows });
  assert.ok(engine.ask('Tell me about Darmok').references.some(ref => ref.title === 'Darmok'));
  assert.equal(engine.ask('Do replicators use poop?').references.length, 0);
  assert.deepEqual(engine.ask('Which source?').references, []);
});

test('immediate source follow-up preserves an exact source-local metadata lead', () => {
  const engine = createLoreSemanticEngine({ records: catalog.rows });
  assert.ok(engine.ask('Tell me about Darmok').references.some(ref => ref.title === 'Darmok'));
  assert.ok(engine.ask('Which source?').references.some(ref => ref.title === 'Darmok'));
});
