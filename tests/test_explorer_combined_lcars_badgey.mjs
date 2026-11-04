// Independent integration invariants: neither draft may erase the other's
// public interface controls or corrupt the Pages asset fingerprints.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const root = new URL('../explorer/', import.meta.url);
const html = readFileSync(new URL('index.html', root), 'utf8');
const css = readFileSync(new URL('app.css', root));
const script = readFileSync(new URL('app.js', root));
const js = script.toString('utf8');
const style = css.toString('utf8');
const sha = (bytes) => createHash('sha256').update(bytes).digest('hex');

test('both drafts coexist under exact public CSS and JS digest pins', () => {
  assert.match(html, new RegExp(`\\./app\\.css\\?v=${sha(css)}`));
  assert.match(html, new RegExp(`\\./app\\.js\\?v=${sha(script)}`));
  assert.equal((html.match(/id="lore-console"/g) || []).length, 1);
  assert.equal((html.match(/id="explorer-navigation"/g) || []).length, 1);
  assert.equal((html.match(/id="navigation-scroll-controls"/g) || []).length, 1);
});

test('LCARS original record marks, source-local disclaimer, and overflow nav survive Badgey', () => {
  assert.match(html, /id="navigation-scroll-previous"[^>]+aria-controls="explorer-navigation"/);
  assert.match(html, /id="navigation-scroll-next"[^>]+aria-controls="explorer-navigation"/);
  assert.match(html, /class="hero-search-link" href="#discovery-query"/);
  assert.match(js, /function recordVisualSeed\(key\)/);
  assert.match(js, /Artwork not sourced · original index art/);
  assert.match(js, /Record metadata · not image rights/);
  assert.match(js, /no image-rights grant/);
  assert.match(js, /Original signal · source-local key unresolved/);
  assert.match(style, /\.artwork-record-beacon/);
  assert.match(style, /\.navigation-scroll-controls button:focus-visible/);
  assert.match(js, /navigationPrevious\?\.addEventListener\('click'/);
  assert.match(js, /navigationNext\?\.addEventListener\('click'/);
});

test('Badgey safety, bounded runtime, and independently reachable support survive LCARS', () => {
  assert.match(html, /id="lore-toggle"[^>]+aria-controls="lore-console"/);
  assert.match(html, /id="lore-realworld-help"[^>]+aria-label="Real-world support information"/);
  assert.match(html, /Fictional simulation/);
  assert.match(js, /function isScopedBadgeyPrompt\(input, memory\)/);
  assert.match(js, /function createBadgey\(/);
  assert.match(js, /kind: 'urgent-safety', sources: \[\]/);
  assert.match(js, /kind: 'scope-limit', sources: \[\]/);
  assert.match(js, /memory\.topic = null/);
  assert.match(style, /\.lore-realworld-help a:focus-visible/);
});

test('visitor-requested help and artwork provenance coexist without opening a research or network pathway', () => {
  assert.match(html, /id="lore-chat-help"[^>]*type="button"[^>]*aria-describedby="lore-realworld-help"/);
  assert.match(html, /id="lore-realworld-help"[^>]*tabindex="-1"/);
  assert.match(js, /function requestHelp\(\)/);
  assert.match(js, /kind: 'realworld-help', sources: \[\]/);
  assert.match(js, /support\.scrollIntoView\(\{ block: 'nearest' \}\)/);
  assert.match(js, /support\.focus\(\)/);
  assert.match(js, /artworkFallbackLabels = Object\.freeze/);
  assert.match(js, /Record metadata · not image rights/);
  assert.match(js, /no image-rights grant/);
  assert.match(js, /artworkState\.enabled \? artworkState\.entries\.get\(key\) : null/);
  assert.doesNotMatch(html, /connect-src[^";]*127\.0\.0\.1/);
});

test('integrated CSP remains origin-bound and contains no implicit remote-model exception', () => {
  const csp = html.match(/<meta http-equiv="Content-Security-Policy" content="([^"]+)"/);
  assert.ok(csp, 'CSP exists');
  assert.match(csp[1], /default-src 'none'/);
  assert.match(csp[1], /script-src 'self'/);
  assert.match(csp[1], /connect-src 'self'/);
  assert.doesNotMatch(csp[1], /'unsafe-inline'|'unsafe-eval'|127\.0\.0\.1/);
  assert.doesNotMatch(html, /https?:\/\/[^" ]+\.(?:js|css)(?:\?|["'])/i);
});
