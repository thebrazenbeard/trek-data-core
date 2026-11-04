import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const css = readFileSync(new URL('../explorer/app.css', import.meta.url), 'utf8');
const mobile = css.match(/@media \(max-width: 460px\) \{([\s\S]*?)\n\}\n@media \(max-width: 359px\)/)?.[1];

test('320/390-width LCARS cards put full-width provenance next to an original 82px visual', () => {
  assert.ok(mobile, 'the common 320/390 mobile breakpoint must exist');
  for (const selector of [
    '.directory-card.media-card, .film-grid .media-card',
    '.artwork-gallery-card',
    '.publisher-edition-card'
  ]) {
    assert.ok(mobile.includes(`${selector} { grid-template-columns: minmax(0,`),
      `${selector} cannot retain an 82px provenance-only column at 390px`);
  }
  assert.match(mobile, /\.artwork-panel\s*\{[^}]*width:\s*100%;[^}]*grid-template-columns:\s*82px minmax\(0, 1fr\)/);
  assert.match(mobile, /\.publisher-edition-card \.artwork-panel\s*\{\s*grid-row:\s*auto;/);
  assert.match(mobile, /\.publisher-edition-card details\s*\{\s*grid-column:\s*1;/,
    'a source disclosure cannot create a phantom second grid column on narrow cards');
  assert.match(mobile, /\.artwork-caption\s*\{[^}]*font-size:\s*\.82rem;/,
    'mobile provenance must be readable at about 13px rather than 8px');
  assert.match(mobile, /\.artwork-provenance-note\s*\{\s*font-size:\s*\.8rem;/);
  assert.match(mobile, /\.artwork-caption \.artwork-record-source\s*\{[^}]*min-height:\s*44px;/,
    'mobile record metadata links need a full-height tap target');
  assert.match(css, /@media \(max-width: 359px\)[\s\S]*?\.artwork-caption\s*\{[^}]*font-size:\s*\.82rem;/,
    'the narrower override must not restore unreadable caption text');
});

function luminance(hex) {
  const channels = hex.match(/[\da-f]{2}/gi)?.map((pair) => parseInt(pair, 16) / 255);
  assert.equal(channels?.length, 3);
  const linear = channels.map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2];
}

function contrast(first, second) {
  const a = luminance(first);
  const b = luminance(second);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

test('source-only LCARS caption palette satisfies WCAG AA contrast on the solid card surface', () => {
  const vars = new Map([...css.matchAll(/--([a-z0-9-]+):\s*(#[a-f0-9]{6});/gi)]
    .map((match) => [match[1], match[2]]));
  const background = vars.get('surface2');
  assert.equal(background, '#171a2d');
  for (const [name, minimum] of [['muted', 4.5], ['aqua', 4.5], ['amber', 4.5]]) {
    const value = vars.get(name);
    assert.ok(value && contrast(value, background) >= minimum,
      `${name} caption text must have at least ${minimum}:1 against the solid card background`);
  }
});
