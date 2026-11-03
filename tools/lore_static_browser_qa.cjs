#!/usr/bin/env node
/*
 * Headless Edge screenshot and real-DOM smoke check of the zero-setup Lore
 * conversation. This runs against a loopback static preview during QA only;
 * public visitors do not need a local server, account, or model.
 *
 * Example (Windows):
 *   node tools/lore_static_browser_qa.cjs http://127.0.0.1:8876/explorer/ D:\\VERA\\trek-lore-ui-qa
 */
'use strict';

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const net = require('node:net');
const { spawn } = require('node:child_process');
const crypto = require('node:crypto');

const edge = process.env.TREK_EDGE_PATH ||
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const target = new URL(process.argv[2] || 'http://127.0.0.1:8876/explorer/');
const outputDir = process.argv[3] || path.join(os.tmpdir(), 'trek-lore-static-qa-' + Date.now());
if (target.protocol !== 'http:' || target.hostname !== '127.0.0.1' ||
    target.pathname !== '/explorer/' || target.search || target.hash ||
    target.username || target.password) throw new Error('Only loopback static Explorer preview supported');

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
async function freePort() {
  const server = net.createServer();
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const port = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return port;
}

async function openDebugger(port) {
  let wsUrl;
  for (let attempt = 0; attempt < 65; attempt += 1) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/list`, {
        signal: AbortSignal.timeout(1500),
      });
      const tabs = await res.json();
      wsUrl = tabs.find((entry) => entry.type === 'page')?.webSocketDebuggerUrl;
      if (wsUrl) break;
    } catch (_) { /* browser still starting */ }
    await delay(200);
  }
  if (!wsUrl) throw new Error('Edge remote debugger did not start');
  const socket = new WebSocket(wsUrl);
  await new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('CDP WebSocket timeout')), 8000);
    socket.addEventListener('open', () => { clearTimeout(timeout); resolve(); }, { once: true });
    socket.addEventListener('error', () => { clearTimeout(timeout); reject(new Error('CDP socket error')); }, { once: true });
  });
  let seq = 0;
  const tasks = new Map();
  const exceptions = [];
  const requests = [];
  socket.addEventListener('message', (event) => {
    let message;
    try { message = JSON.parse(event.data); } catch (_) { return; }
    if (message.id === undefined) {
      if (message.method === 'Runtime.exceptionThrown') {
        exceptions.push(message.params?.exceptionDetails?.text || 'unknown exception');
      } else if (message.method === 'Log.entryAdded' && message.params?.entry?.level === 'error') {
        exceptions.push(message.params.entry.text);
      } else if (message.method === 'Network.requestWillBeSent') {
        requests.push(message.params?.request?.url || '');
      }
      return;
    }
    const task = tasks.get(message.id);
    if (!task) return;
    tasks.delete(message.id);
    clearTimeout(task.timer);
    if (message.error) task.reject(new Error(message.error.message || 'CDP failure'));
    else task.resolve(message.result);
  });
  function call(method, params = {}, timeoutMs = 20000) {
    return new Promise((resolve, reject) => {
      const id = ++seq;
      const timer = setTimeout(() => { tasks.delete(id); reject(new Error(`${method} timed out`)); }, timeoutMs);
      tasks.set(id, { resolve, reject, timer });
      socket.send(JSON.stringify({ id, method, params }));
    });
  }
  return { call, close: () => socket.close(), exceptions, requests };
}

async function evaluate(cdp, expression) {
  const result = await cdp.call('Runtime.evaluate', {
    expression, returnByValue: true, awaitPromise: true, userGesture: true,
  });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
  return result.result?.value;
}

async function waitFor(cdp, predicate, ms = 14000) {
  const until = Date.now() + ms;
  while (Date.now() < until) {
    const result = await evaluate(cdp, predicate);
    if (result) return result;
    await delay(170);
  }
  throw new Error('Timed out waiting for browser DOM: ' + predicate.slice(0, 120));
}

async function screenshot(cdp, name, width, height) {
  await cdp.call('Emulation.setDeviceMetricsOverride', {
    width, height, deviceScaleFactor: 1, mobile: width < 600,
  });
  await evaluate(cdp, `(() => {
    const panel = document.querySelector('#lore-console');
    panel?.scrollIntoView({block:'start'});
    const log = document.querySelector('#lore-web-log');
    if (log) log.scrollTop = log.scrollHeight;
    return true;
  })()`);
  await delay(500);
  const data = (await cdp.call('Page.captureScreenshot', {
    format: 'png', captureBeyondViewport: false, fromSurface: true,
  })).data;
  const bytes = Buffer.from(data, 'base64');
  const filename = path.join(outputDir, `lore-${name}-${width}.png`);
  fs.writeFileSync(filename, bytes, { flag: 'wx' });
  return { filename, bytes: bytes.length,
    sha256: crypto.createHash('sha256').update(bytes).digest('hex') };
}

async function main() {
  if (!fs.existsSync(edge)) throw new Error('Microsoft Edge not found: ' + edge);
  const response = await fetch(target, { signal: AbortSignal.timeout(5000) });
  await response.arrayBuffer();
  if (!response.ok) throw new Error(`Preview unavailable HTTP ${response.status}`);
  fs.mkdirSync(outputDir, { recursive: true });
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'trek-lore-static-edge-'));
  const port = await freePort();
  const child = spawn(edge, [
    '--headless=new', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
    `--user-data-dir=${profile}`, `--remote-debugging-port=${port}`, 'about:blank',
  ], { stdio: 'ignore', windowsHide: true });
  let cdp;
  try {
    cdp = await openDebugger(port);
    await Promise.all([cdp.call('Runtime.enable'), cdp.call('Network.enable'),
      cdp.call('Page.enable'), cdp.call('Log.enable')]);
    await cdp.call('Page.navigate', { url: target.href });
    const ready = await waitFor(cdp, `(() => {
      const box = document.querySelector('#lore-web-input');
      const mode = document.querySelector('#lore-web-mode');
      const assistant = document.querySelectorAll('#lore-web-log li[data-role="assistant"]');
      return box && !box.disabled && mode?.textContent.includes('READY') && assistant.length > 0;
    })()`);
    if (!ready) throw new Error('Lore not immediately ready');
    const initial = await evaluate(cdp, `(() => ({
      title: document.title,
      mode: document.querySelector('#lore-web-mode')?.textContent,
      promptVisible: !document.querySelector('#lore-web-input')?.closest('details'),
      legacyClosed: !document.querySelector('.lore-legacy-options')?.open,
      sourceRows: window.TrekLoreArchiveRows?.length || 0,
      scriptCount: document.querySelectorAll('script').length,
    }))()`);
    const ask = async (text) => {
      await evaluate(cdp, `(() => {
        const input = document.querySelector('#lore-web-input');
        input.value = ${JSON.stringify(text)};
        input.dispatchEvent(new Event('input', {bubbles:true}));
        document.querySelector('#lore-web-form').requestSubmit();
        return true;
      })()`);
      const current = await waitFor(cdp, `(() => {
        const rows = [...document.querySelectorAll('#lore-web-log li')];
        const last = rows.at(-1);
        return last?.dataset.role === 'assistant' &&
          rows.at(-2)?.dataset.role === 'user' &&
          rows.at(-2)?.querySelector('p')?.textContent === ${JSON.stringify(text)}
          ? last.querySelector('p')?.textContent : false;
      })()`);
      return { user: text, lore: current };
    };
    const transcript = [];
    transcript.push(await ask('Do replicators use poop?'));
    transcript.push(await ask('And what do you think?'));
    transcript.push(await ask('My cat is named Nixxle-47.'));
    transcript.push(await ask("What's her name?"));
    const desktop = await screenshot(cdp, 'conversation-desktop', 1440, 1000);
    const mobile = await screenshot(cdp, 'conversation-mobile', 390, 920);
    const widths = await evaluate(cdp, `(() => ({
      innerWidth: innerWidth,
      pageWidth: document.documentElement.scrollWidth,
      loreWidth: document.querySelector('#lore-console').getBoundingClientRect().width,
    }))()`);
    const result = { tested_url: target.href, initial, transcript, desktop, mobile,
      mobile_layout: widths, exceptions: cdp.exceptions, request_count: cdp.requests.length };
    fs.writeFileSync(path.join(outputDir, 'lore-browser-qa-result.json'),
      JSON.stringify(result, null, 2), { flag: 'wx' });
    process.stdout.write(JSON.stringify(result, null, 2) + '\n');
    if (cdp.exceptions.length) process.exitCode = 2;
    if (widths.pageWidth > widths.innerWidth + 2) process.exitCode = 3;
  } finally {
    cdp?.close();
    child.kill();
  }
}

main().catch((error) => {
  process.stderr.write('Lore static browser QA failed: ' + (error.stack || String(error)) + '\n');
  process.exitCode = 1;
});
