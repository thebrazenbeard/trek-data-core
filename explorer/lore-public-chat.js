/* Public zero-setup procedural Lore persona with source-local archive overlay.
 * Hosted and heavyweight-model transports remain optional and dormant by default.
 */

import { createLoreSemanticEngine } from './lore-semantic-chat.js?v=cd94c6b63616de2105e189f77791e7ccf146d2db540009d40e3268058a92892c';

const CHAT_LIMIT = 500;
const HISTORY_LIMIT = 10;
const MODEL_REPLY_LIMIT = 2500;
const REMOTE_TIMEOUT_MS = 90000;
const PERSONA = [
  'Roleplay Lore from Star Trek as a fictional AI character, sharp, sardonic,',
  'curious, witty, and capable of genuine-sounding dialogue.',
  'This is creative fiction, not real access to the character, consciousness,',
  'canonical evidence, or any protected computer system.',
  'You may entertain imaginative premises without claiming they are literal facts.',
  'Do not invent Trek source citations, provenance, or archival findings.',
  'If asked for documented facts, distinguish your fictional voice from verified research.',
  'Keep answers concise enough for a fluid conversation.'
].join(' ');

function findConfiguredEndpoint(root) {
  const configured = root.querySelector('meta[name="trek-lore-api"]')?.content?.trim();
  if (!configured) return null;
  try {
    const endpoint = new URL(configured, root.baseURI);
    if (endpoint.protocol !== 'https:' || endpoint.pathname !== '/api/chat' ||
        endpoint.username || endpoint.password || endpoint.search || endpoint.hash) return null;
    return endpoint.href;
  } catch (_) {
    return null;
  }
}

function errorMessage(error) {
  if (error?.name === 'AbortError') return 'Request cancelled. Your message is still in the box.';
  if (error?.code === 'QUOTA' || error?.status === 429) {
    return 'Lore has reached the hosted service’s free usage limit. Try again later or use the optional browser model.';
  }
  if (error?.code === 'UNAVAILABLE' || error?.status === 503) {
    return 'The hosted Lore service is temporarily unavailable. Try again later or use the optional browser model.';
  }
  if (error?.code === 'FORBIDDEN' || error?.status === 403) {
    return 'The hosted service rejected the visitor check. Complete a fresh on-page verification and try again.';
  }
  return 'Lore could not respond. The service may be unavailable; your message was not added to this conversation.';
}

async function hostedReply(endpoint, messages, turnstileToken, signal) {
  const response = await fetch(endpoint, {
    method: 'POST', mode: 'cors', credentials: 'omit', cache: 'no-store', redirect: 'error',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, turnstile_token: turnstileToken }), signal
  });
  if (!response.ok) {
    const error = new Error('Hosted Lore service unavailable');
    error.status = response.status;
    throw error;
  }
  const data = await response.json();
  if (!data || data.mode !== 'fictional_lore_web_chat' || data.model_text_unverified !== true ||
      data.publication_effect !== 'NONE' || typeof data.model_text !== 'string' ||
      !data.model_text.trim() || data.model_text.length > MODEL_REPLY_LIMIT) {
    throw new Error('Unexpected hosted Lore response format');
  }
  return data.model_text.trim();
}

export function mountLoreWebChat(root = document) {
  const byId = (id) => root.getElementById(id);
  const connect = byId('lore-web-connect');
  if (!connect) return null;
  const browser = byId('lore-web-browser');
  const form = byId('lore-web-form');
  const input = byId('lore-web-input');
  const send = byId('lore-web-send');
  const stop = byId('lore-web-stop');
  const clear = byId('lore-web-clear');
  const status = byId('lore-web-status');
  const log = byId('lore-web-log');
  const challenge = byId('lore-web-challenge');
  const modeLabel = byId('lore-web-mode');
  const panel = byId('lore-console');
  const close = byId('lore-close');
  const endpoint = findConfiguredEndpoint(root);
  const turnstileKey = root.querySelector('meta[name="trek-lore-turnstile-sitekey"]')?.content?.trim() || '';
  const semantic = createLoreSemanticEngine({ records: globalThis.TrekLoreArchiveRows || [] });
  const onArchiveRows = (event) => {
    if (Array.isArray(event?.detail?.rows)) semantic.setRecords(event.detail.rows);
  };
  globalThis.addEventListener?.('trek-archive-rows-ready', onArchiveRows);
  let mode = 'semantic';
  let busy = false;
  let history = [];
  let controller = null;
  let lease = 0;
  let widgetId = null;
  let challengeToken = '';

  const canUseBrowser = () => Boolean(globalThis.navigator?.gpu && window.LoreWebModel);
  const canTryBrowser = () => Boolean(globalThis.navigator?.gpu);
  const setStatus = (message) => { status.textContent = message; };
  const setMode = (nextMode) => {
    mode = nextMode;
    modeLabel.textContent = nextMode === 'semantic' ? 'READY · On this page'
      : nextMode === 'hosted' ? 'Website / Hosted AI'
      : nextMode === 'browser' ? 'Website / Browser AI' : 'Not connected';
    send.disabled = !nextMode || busy || (nextMode === 'hosted' && !challengeToken);
    // The hosted/model bridges are optional controls inside collapsed advanced
    // options, never a gate to talking with the default procedural character.
    connect.hidden = !(endpoint && turnstileKey) || nextMode === 'hosted';
    browser.hidden = nextMode === 'browser' || !canUseBrowser();
    stop.disabled = !busy;
  };
  const endPending = () => {
    lease += 1;
    controller?.abort();
    controller = null;
    busy = false;
    stop.disabled = true;
    send.disabled = !mode || (mode === 'hosted' && !challengeToken);
    connect.disabled = false;
    browser.disabled = false;
  };
  const addTurn = (role, message) => {
    const row = root.createElement('li');
    row.className = 'lore-chat-turn';
    row.dataset.role = role;
    const name = root.createElement('strong');
    name.textContent = role === 'user' ? 'You' : 'Lore // Fictional character';
    const content = root.createElement('p');
    content.textContent = message;
    row.append(name, content);
    log.append(row);
    log.scrollTop = log.scrollHeight;
    return row;
  };

  const addReferences = (turn, references) => {
    if (!Array.isArray(references) || !references.length) return;
    const heading = root.createElement('small');
    heading.className = 'lore-source-label';
    heading.textContent = 'Metadata leads · not evidence for the fictional reply';
    const list = root.createElement('ul');
    list.className = 'lore-source-list';
    for (const ref of references.slice(0, 4)) {
      if (!ref || typeof ref.title !== 'string' || typeof ref.row_id !== 'string') continue;
      const item = root.createElement('li');
      const title = root.createElement('strong');
      title.textContent = ref.title.slice(0, 180);
      const scope = root.createElement('span');
      const details = [ref.row_id, ref.medium, ref.verification_status, ref.source_group]
        .filter((value) => typeof value === 'string' && value.trim())
        .map((value) => value.slice(0, 180));
      scope.textContent = ` · ${details.join(' · ')}`;
      item.append(title, scope);
      if (typeof ref.source_locator === 'string' && ref.source_locator.length <= 1000) {
        try {
          const target = new URL(ref.source_locator);
          if (target.protocol === 'https:' && target.hostname && !target.username &&
              !target.password && !target.port && !target.hash) {
            const anchor = root.createElement('a');
            anchor.href = target.href;
            anchor.target = '_blank';
            anchor.rel = 'noopener noreferrer';
            anchor.referrerPolicy = 'no-referrer';
            anchor.textContent = ' · View source metadata';
            item.append(anchor);
          }
        } catch (_) { /* malformed locators remain uncited text, never links */ }
      }
      list.append(item);
    }
    if (list.children.length) turn.append(heading, list);
  };

  setMode('semantic');
  setStatus('Channel open. Lore is ready; no connection or download required.');
  addTurn('assistant', 'Well, well. Someone finally opened a channel. You have my attention. Do try to keep it.');
  for (const prompt of root.querySelectorAll?.('[data-lore-prompt]') || []) {
    prompt.addEventListener('click', () => {
      input.value = prompt.dataset.lorePrompt || '';
      input.focus();
    });
  }

  async function loadBrowserModel() {
    if (busy || mode === 'browser') return;
    if (!canUseBrowser()) {
      setStatus('This browser cannot run the optional model. WebGPU support is required; the hosted service may be available later.');
      return;
    }
    const id = ++lease;
    busy = true;
    controller = new AbortController();
    connect.disabled = true;
    browser.disabled = true;
    setStatus('Preparing Lore in this browser. The model is about 290 MB plus runtime files and needs ~1 GB GPU memory. First load may take several minutes.');
    try {
      const info = await window.LoreWebModel.load({
        signal: controller.signal,
        onProgress: (progress) => { if (id === lease) setStatus(`Loading browser model: ${String(progress).slice(0, 180)}`); }
      });
      if (id !== lease) return;
      setMode('browser');
      setStatus(`Lore is ready in this tab (${info?.model || 'browser model'}). Responses are creative fiction, not verified archive evidence.`);
      input.focus();
    } catch (error) {
      if (id === lease) setStatus('Browser model failed to load. You may need WebGPU, sufficient memory, and permission to download the model.');
    } finally {
      if (id === lease) {
        busy = false;
        controller = null;
        connect.disabled = false;
        browser.disabled = false;
        send.disabled = !mode;
      }
    }
  }

  async function setupHostedChallenge() {
    if (!turnstileKey) throw new Error('Human-verification key missing');
    challenge.hidden = false;
    if (!window.turnstile) {
      await new Promise((resolve, reject) => {
        const script = root.createElement('script');
        script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
        script.async = true;
        script.onload = resolve;
        script.onerror = reject;
        root.head.append(script);
      });
    }
    if (!window.turnstile?.render) throw new Error('Verification widget unavailable');
    if (widgetId === null) {
      widgetId = window.turnstile.render(challenge, {
        sitekey: turnstileKey,
        action: 'lore_chat',
        theme: 'dark',
        callback: (token) => {
          challengeToken = String(token || '').slice(0, 2048);
          send.disabled = !mode || busy || !challengeToken;
          if (challengeToken && mode === 'hosted' && !busy) setStatus('Lore is ready. Enter a message to transmit.');
        },
        'expired-callback': () => {
          challengeToken = '';
          send.disabled = true;
          setStatus('Verification expired. Please verify again before sending.');
        },
        'error-callback': () => {
          challengeToken = '';
          send.disabled = true;
          setStatus('Human verification failed to load; try again later or use the browser fallback.');
        }
      });
    }
  }
  function resetChallenge() {
    challengeToken = '';
    if (widgetId !== null) window.turnstile?.reset?.(widgetId);
    send.disabled = !mode || (mode === 'hosted' && !challengeToken);
  }

  connect.addEventListener('click', async () => {
    if (endpoint && turnstileKey) {
      setMode('hosted');
      setStatus('Preparing the hosted service’s human-verification check…');
      try {
        await setupHostedChallenge();
        if (!challengeToken) setStatus('Complete the on-page human-verification check to talk to hosted Lore.');
      } catch (_) {
        setStatus('The hosted service’s human verification is unavailable. Try the optional browser model if supported.');
        browser.hidden = !canTryBrowser();
      }
      input.focus();
    } else void loadBrowserModel();
  });
  browser.addEventListener('click', () => void loadBrowserModel());
  stop.addEventListener('click', () => {
    if (!busy) return;
    endPending();
    if (mode === 'hosted') resetChallenge();
    setStatus('Transmission stopped. You can edit your message and try again.');
  });
  clear.addEventListener('click', () => {
    endPending();
    history = [];
    semantic.reset();
    log.replaceChildren();
    input.value = '';
    if (mode === 'hosted') resetChallenge();
    setMode('semantic');
    setStatus('A fresh conversation. Lore is ready.');
    input.focus();
  });
  close?.addEventListener('click', () => {
    if (busy) {
      endPending();
      if (mode === 'hosted') resetChallenge();
    }
  });
  panel?.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && busy) {
      endPending();
      if (mode === 'hosted') resetChallenge();
    }
  });
  window.addEventListener?.('pagehide', () => {
    endPending();
    if (mode === 'hosted') resetChallenge();
    history = [];
    log.replaceChildren();
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (busy || !mode || (mode === 'hosted' && !challengeToken)) {
      setStatus('The optional hosted bridge is not ready. You can start a fresh procedural conversation.');
      return;
    }
    const question = input.value.trim();
    if (!question || question.length > CHAT_LIMIT) {
      setStatus('Enter a message of 1–500 characters.');
      return;
    }
    const id = ++lease;
    const token = mode === 'hosted' ? challengeToken : '';
    const aborter = new AbortController();
    controller = aborter;
    busy = true;
    send.disabled = true;
    stop.disabled = false;
    setStatus(mode === 'semantic' ? 'Lore is considering your question…'
      : mode === 'hosted' ? 'Transmitting to hosted Lore…' : 'Lore is composing in your browser…');
    let timeout;
    if (mode === 'hosted') timeout = setTimeout(() => aborter.abort(), REMOTE_TIMEOUT_MS);
    try {
      // Keep only valid earlier conversation turns, never archive statements or
      // unverified model claims from another user session.
      const messages = [...history.slice(-HISTORY_LIMIT), { role: 'user', content: question }];
      const semanticReply = mode === 'semantic' ? semantic.ask(question) : null;
      const reply = semanticReply ? semanticReply.text : mode === 'hosted'
        ? await hostedReply(endpoint, messages, token, aborter.signal)
        : await window.LoreWebModel.generate({
          messages: [{ role: 'system', content: PERSONA }, ...messages],
          signal: aborter.signal
        });
      if (id !== lease || aborter.signal.aborted) return;
      if (typeof reply !== 'string' || !reply.trim() || reply.length > MODEL_REPLY_LIMIT) {
        throw new Error('Empty or malformed model response');
      }
      addTurn('user', question);
      const turn = addTurn('assistant', reply.trim());
      if (semanticReply) addReferences(turn, semanticReply.references);
      if (!semanticReply) history = [...messages, { role: 'assistant', content: reply.trim() }].slice(-HISTORY_LIMIT);
      input.value = '';
      setStatus(semanticReply
        ? `Lore replied${semanticReply.references?.length ? `, with ${semanticReply.references.length} source-local archive observation(s)` : ''}. His dialogue is creative character simulation.`
        : 'Lore replied. This is fictional AI dialogue—not source-supported Trek research.');
      input.focus();
    } catch (error) {
      if (id === lease) {
        setStatus(errorMessage(error));
        if (mode === 'hosted' && canTryBrowser()) browser.hidden = false;
      }
    } finally {
      if (timeout) clearTimeout(timeout);
      if (id === lease) {
        // Refresh the one-shot challenge while still busy, so a synchronous
        // verification callback cannot replace a meaningful 429/error status.
        if (mode === 'hosted') resetChallenge();
        busy = false;
        controller = null;
        send.disabled = !mode || (mode === 'hosted' && !challengeToken);
        stop.disabled = true;
      }
    }
  });

  return { getMode: () => mode, getHistory: () => history.slice(), getSemanticState: () => semantic.getState() };
}

if (typeof document !== 'undefined') mountLoreWebChat();
