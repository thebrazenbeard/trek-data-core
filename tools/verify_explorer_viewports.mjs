/**
 * Optional real-browser regression for the 320px Explorer artwork receipt select.
 *
 * Requires an existing Playwright installation and Chromium/Edge executable.
 * Never downloads browser binaries, starts a server, or contacts third parties.
 *
 * PLAYWRIGHT_CHROMIUM_EXECUTABLE=/path/to/existing/chrome \
 *   node tools/verify_explorer_viewports.mjs
 *
 * TREK_VISUAL_ARTIFACT_DIR overrides the temporary screenshot directory.
 */
import assert from 'node:assert/strict';
import { readFile, mkdir } from 'node:fs/promises';
import { resolve, dirname, extname, join, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const { chromium } = await import('playwright');
const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const explorerRoot = join(repoRoot, 'explorer');
const screenshotRoot = process.env.TREK_VISUAL_ARTIFACT_DIR || join(tmpdir(), 'trek-visuals-wave-20261104');
const browserExecutable = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE;
const browser = await chromium.launch({ headless: true, ...(browserExecutable ? { executablePath: browserExecutable } : {}) });
const contentTypes = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.svg': 'image/svg+xml'
};

async function serveFile(route) {
  const requestURL = new URL(route.request().url());
  if (requestURL.origin !== 'http://trek.test') return route.abort('blockedbyclient');
  const requested = decodeURIComponent(requestURL.pathname).replace(/^\/+/, '');
  const localPath = resolve(explorerRoot, requested.replace(/^explorer\//, ''));
  if (localPath !== explorerRoot && !localPath.startsWith(explorerRoot + sep)) return route.fulfill({ status: 403 });
  try {
    const body = await readFile(localPath);
    return route.fulfill({ status: 200, contentType: contentTypes[extname(localPath)] || 'application/octet-stream', body });
  } catch (error) {
    if (error.code === 'ENOENT') return route.fulfill({ status: 404 });
    throw error;
  }
}

try {
  await mkdir(screenshotRoot, { recursive: true });
  for (const width of [320, 390, 1280]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    const externalRequests = [];
    await page.route('**/*', async (route) => {
      if (new URL(route.request().url()).origin !== 'http://trek.test') {
        externalRequests.push(route.request().url());
      }
      await serveFile(route);
    });
    await page.goto('http://trek.test/explorer/index.html', { waitUntil: 'networkidle' });
    const artworkSelect = page.locator('#discovery-artwork');
    assert.equal(await artworkSelect.count(), 1, `Missing artwork receipt selector at ${width}px`);
    const labels = [];
    for (const value of ['all', 'receipt_pinned', 'not_loaded']) {
      await artworkSelect.selectOption(value);
      const measured = await artworkSelect.evaluate((element) => {
        const style = getComputedStyle(element);
        const option = element.selectedOptions[0];
        const context = document.createElement('canvas').getContext('2d');
        context.font = style.font;
        const textWidth = context.measureText(option.textContent.trim()).width;
        const contentWidth = element.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
        return { label: option.textContent.trim(), textWidth, contentWidth, width: element.getBoundingClientRect().width };
      });
      // Keep allowance for the native select arrow and separation from its glyphs.
      assert.ok(measured.textWidth + 30 <= measured.contentWidth,
        `${width}px ${value}: "${measured.label}" needs ${Math.ceil(measured.textWidth + 30)}px, has ${Math.floor(measured.contentWidth)}px`);
      labels.push({ value, ...measured });
    }
    const overflow = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
    assert.ok(overflow.document <= overflow.viewport, `${width}px page horizontal overflow: ${JSON.stringify(overflow)}`);
    assert.deepEqual(externalRequests, [], `Unexpected pre-consent third-party request at ${width}px`);
    const badgey = page.locator('#lore-toggle');
    await badgey.focus();
    await page.keyboard.press('Enter');
    assert.equal(await badgey.getAttribute('aria-expanded'), 'true', `Badgey Enter failed at ${width}px`);
    await page.keyboard.press('Escape');
    assert.equal(await badgey.getAttribute('aria-expanded'), 'false', `Badgey Escape failed at ${width}px`);
    assert.equal(await badgey.evaluate((element) => element === document.activeElement), true,
      `Badgey keyboard focus not restored at ${width}px`);
    await artworkSelect.selectOption('receipt_pinned');
    await artworkSelect.scrollIntoViewIfNeeded();
    const screenshot = join(screenshotRoot, `explorer-artwork-filter-${width}.png`);
    await page.screenshot({ path: screenshot });
    console.log(JSON.stringify({ width, overflow, labels, screenshot, externalRequests: externalRequests.length, badgeyKeyboard: 'PASS' }));
    await page.close();
  }
} finally {
  await browser.close();
}
