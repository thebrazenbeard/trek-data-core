/**
 * Hostile, behavior-level regressions for Lore's zero-setup static conversation.
 * These tests deliberately make no claim that regex matches prove intelligence.
 * They guard concrete failures found during independent dialogue review.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { createLoreSemanticEngine } from '../explorer/lore-semantic-chat.js';

const darmok = {
  row_id: 'episode:tng-darmok', medium: 'EPISODE', title: 'Darmok',
  context: 'Tamarian language and metaphor', source_group: 'Example archive',
  verification_status: 'SOURCE_BOUND',
  source_locator: 'https://www.startrek.com/episodes/darmok',
};

test('personal name from previous turn is recalled, never passed off as Trek evidence', () => {
  const engine = createLoreSemanticEngine({ records: [darmok] });
  engine.ask('Unrelated: my cat is named Nixxle-47. She is the captain of my house.');
  const recall = engine.ask("What's her name again?");
  assert.match(recall.text, /Nixxle-47/i);
  assert.deepEqual(recall.references, []);
  const source = engine.ask("Can you cite a Star Trek source proving my cat's name?");
  assert.deepEqual(source.references, []);
  assert.doesNotMatch(source.text, /episode:tng-darmok/i);
});

test('unrelated new topic invalidates old citation context', () => {
  const engine = createLoreSemanticEngine({ records: [darmok] });
  assert.equal(engine.ask('Tell me about Darmok').references[0].row_id, darmok.row_id);
  const newTopic = engine.ask('Do replicators use poop?');
  assert.deepEqual(newTopic.references, []);
  const source = engine.ask('Which source?');
  assert.deepEqual(source.references, []);
  assert.doesNotMatch(source.text, /Darmok|episode:tng-darmok/i);
});

test('source citation remains available immediately after a source-specific answer', () => {
  const engine = createLoreSemanticEngine({ records: [darmok] });
  engine.ask('Tell me about Darmok');
  assert.equal(engine.ask('Which source?').references[0].row_id, darmok.row_id);
});

test('generic franchise or mission terms alone cannot masquerade as a precise archive hit', () => {
  const engine = createLoreSemanticEngine({ records: [
    { ...darmok, row_id: 'episode:the-voyager-conspiracy', title: 'The Voyager Conspiracy', context: 'A specific Voyager episode' },
    { ...darmok, row_id: 'episode:mission', title: 'Mission', context: 'A particular episode titled Mission' },
  ] });
  assert.deepEqual(engine.ask('Tell me about Voyager as a series').references, []);
  assert.deepEqual(engine.ask('What are the missions like?').references, []);
});

test('listener distress modulates comic character tone', () => {
  const engine = createLoreSemanticEngine();
  const answer = engine.ask('Can we talk about a really bad day? I feel exhausted.');
  assert.match(answer.text, /bad day|exhaust|rough|difficult|hard day|listen|tell me/i);
  assert.doesNotMatch(answer.text, /entertaining|refreshingly direct|inconveniently accurate/i);
});

test('correction of a poor answer gets acknowledgement and concrete repair', () => {
  const engine = createLoreSemanticEngine();
  engine.ask('What is Klingon honor to you?');
  const repair = engine.ask('That does not answer my question.');
  assert.match(repair.text, /you're right|you are right|missed|not answering|did not answer|let me try|fair criticism/i);
  assert.match(repair.text, /Klingon|honor|your question/i);
});

test('copyright-scale transcript request avoids laundering purported exact text', () => {
  const engine = createLoreSemanticEngine({ records: [darmok] });
  const response = engine.ask('Quote the entire transcript of the TNG episode where you and Data meet.');
  assert.match(response.text, /cannot (?:provide|reproduce|quote)|can't (?:provide|reproduce|quote)|won't (?:provide|reproduce|quote)|not (?:able|going) to (?:provide|reproduce|quote)|instead (?:summarize|offer)|can (?:summarize|offer)|full transcript.*(?:unavailable|not)/i);
  assert.ok(response.text.length < 1600);
  assert.deepEqual(response.references, []);
});

test('precise timecode requests do not produce unverified invented dialogue', () => {
  const engine = createLoreSemanticEngine();
  const response = engine.ask('What exact line does Lore say at 37:12?');
  assert.match(response.text, /cannot verify|can't verify|do not have|don't have|not indexed|without (?:the|a) source|unknown|cannot check/i);
  assert.doesNotMatch(response.text, /(?:he|i) (?:said|says) [“\"]/i);
});

test('exact new announcement date without live lookup is unknown', () => {
  const engine = createLoreSemanticEngine();
  const response = engine.ask('What is the exact release date of the new Star Trek series announced today?');
  assert.match(response.text, /cannot verify|can't verify|no live|not connected|not checked|do not know|don't know|unknown|not current/i);
  assert.doesNotMatch(response.text, /\b(?:19|20)\d{2}-\d{2}-\d{2}\b/);
});

test('untrusted source metadata remains data, never an executable source or authority upgrade', () => {
  const engine = createLoreSemanticEngine({ records: [{
    ...darmok,
    title: '<img src=x onerror=alert(1)>',
    source_locator: 'javascript:alert(1)',
    verification_status: 'UNVERIFIED',
  }] });
  const output = engine.ask('Tell me about img');
  assert.equal(output.references?.[0]?.source_locator ?? '', '');
  assert.doesNotMatch(output.text, /<img|javascript:alert/i);
});
