/**
 * Standalone opt-in LCARS preview of pinned, still-unmerged literary metadata.
 * No interaction with the governed Explorer index or its Mission/Work counts.
 */
const PREVIEW_SHA256 = 'dfbfd558114ddc7d0387df4c2d56e9b4b7707d405293e8be2a1dd22004b4f7f2';
const SOURCE_DETAILS = new Map([
  [494, Object.freeze({
    family: 'publisher:simonandschuster.com', head: '0ec895e17f70b505579b35c69e4af423e4b1dd6f',
    file: 'proposals/research/lit-five-publisher-bibliography-20261104/records.json',
    sha256: 'db04282ad717cb4f71932a5e2b7e8267c5e26b295dd7d02c1cf455b57be38c13',
    format: 'EBOOK', form: 'FICTION_PUBLISHER_EBOOK_METADATA',
  })],
  [497, Object.freeze({
    family: 'publisher:titanbooks.com', head: '785e4516d65b8a8e3769e7eaf69875966bf2e4bb',
    file: 'proposals/research/lit-titan-five-artbooks-20261104/records.json',
    sha256: 'c01c276712477b94565cd61ec275fa83c6f2130637022abf7cca1fd8a9bedc8d',
    format: 'HARDBACK', form: 'NONFICTION_ARTBOOK_PUBLISHER_METADATA',
  })],
]);
// Independent per-edition identity pins defend against a future accidental
// JSON digest re-pin that would otherwise relabel a *different* product page
// as the reviewed draft's title/ISBN. This is NOT global Work reconciliation.
const EDITION_IDENTITIES = new Map([
  ['9780743400817', ['The Lives Of Dax', 'https://www.simonandschuster.com/books/The-Lives-Of-Dax/Marco-Palmieri/Star-Trek-Deep-Space-Nine/9780743400817', 'Marco Palmieri|EDITOR', '1999-12-01', 384, null]],
  ['9780743419864', ['The Romulan Way', 'https://www.simonandschuster.com/books/The-Romulan-Way/Diane-Duane/Star-Trek-The-Original-Series/9780743419864', 'Diane Duane|AUTHOR,Peter Morwood|AUTHOR', '2000-09-22', 304, null]],
  ['9780743420730', ['Unification', 'https://www.simonandschuster.com/books/Unification/Jeri-Taylor/Star-Trek-The-Next-Generation/9780743420730', 'Jeri Taylor|AUTHOR', '2000-09-22', 256, 'AUTHOR_HEADER_JERI_VS_DESCRIPTION_TERI_UNRESOLVED']],
  ['9780743453851', ['Pathways', 'https://www.simonandschuster.com/books/Pathways/Jeri-Taylor/Star-Trek-Voyager/9780743453851', 'Jeri Taylor|AUTHOR', '2009-09-29', 528, null]],
  ['9780743453868', ['Mosaic', 'https://www.simonandschuster.com/books/Mosaic/Jeri-Taylor/Star-Trek-Voyager/9780743453868', 'Jeri Taylor|AUTHOR', '2002-10-04', 320, null]],
  ['9781781166703', ['Star Trek: The Art of Juan Ortiz', 'https://titanbooks.com/6933-star-trek-the-art-of-juan-ortiz/', 'Juan Ortiz|AUTHOR_ARTIST', '2013-09-03', 112, null]],
  ['9781785653872', ['Star Trek The Next Generation: The Art of Juan Ortiz', 'https://titanbooks.com/9032-star-trek-the-next-generation-the-art-of-juan-ortiz/', 'Juan Ortiz|AUTHOR_ARTIST', '2017-09-05', 208, null]],
  ['9781785659119', ['Star Trek: The Art of John Eaves', 'https://titanbooks.com/9614-star-trek-the-art-of-john-eaves/', 'Joe Nazzaro|AUTHOR', '2018-11-27', 208, null]],
  ['9781785659348', ['Star Trek: The Artistry of Dan Curry', 'https://titanbooks.com/9639-star-trek-the-artistry-of-dan-curry/', 'Dan Curry|AUTHOR,Ben Robinson|AUTHOR', '2020-12-01', 204, null]],
  ['9781789095159', ['Star Trek: The Art of Neville Page', 'https://titanbooks.com/70373-star-trek-the-art-of-neville-page/', 'Joe Nazzaro|AUTHOR', '2023-08-08', 192, null]],
]);
const EFFECTS = ['public_explorer_effect', 'coverage_effect', 'accepted_work_effect',
  'accepted_source_binding_effect', 'accepted_evidence_effect', 'public_synopsis_effect',
  'artwork_release_effect', 'main_commit_or_pages_release_effect'];
const ROW_EFFECTS = ['admission_effect', 'coverage_effect'];
const textOK = (value, max = 250) => typeof value === 'string' && value.length > 0 && value.length <= max &&
  value.trim() === value && !/[\u0000-\u001f\u007f]/u.test(value);

function validPublisherLink(value, pr) {
  try {
    const url = new URL(value);
    if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash ||
      url.port || url.pathname.includes('..') || url.pathname.includes('%')) return false;
    return pr === 494
      ? url.hostname === 'www.simonandschuster.com' && url.pathname.startsWith('/books/')
      : url.hostname === 'titanbooks.com' && /^\/\d+-star-trek-[a-z0-9-]+\/$/u.test(url.pathname);
  } catch { return false; }
}

export function validateHeldPublisherPreview(data) {
  if (!data || Array.isArray(data) || typeof data !== 'object' ||
      data.schema_version !== 'trek-held-draft-publisher-metadata-preview-v1' ||
      data.status !== 'HELD_DRAFT_METADATA_PREVIEW_NOT_ACCEPTED' ||
      data.source_family_count !== 2 || data.row_count !== 10 ||
      JSON.stringify(data.source_pr_numbers) !== '[494,497]' ||
      EFFECTS.some(field => data[field] !== 'NONE') ||
      !Array.isArray(data.rows) || data.rows.length !== 10 || !textOK(data.count_warning)) {
    throw new Error('Held preview envelope does not preserve unadmitted scope');
  }
  const rows = new Set();
  const seenISBN = new Set();
  const groups = new Map([[494, 0], [497, 0]]);
  for (const row of data.rows) {
    const source = SOURCE_DETAILS.get(row?.source_pr);
    const identity = EDITION_IDENTITIES.get(row?.isbn13);
    if (!source || !textOK(row.title) ||
        !textOK(row.isbn13, 13) || !/^\d{13}$/u.test(row.isbn13) ||
        !identity || row.title !== identity[0] || row.source_url !== identity[1] ||
        row.creator_credits?.map(c => `${c.name}|${c.role}`).join(',') !== identity[2] ||
        typeof row.publisher_date_us !== 'string' || row.publisher_date_us !== identity[3] ||
        !Number.isSafeInteger(row.publisher_extent_pages) || row.publisher_extent_pages !== identity[4] ||
        row.source_anomaly !== identity[5] ||
        row.row_id !== `draft-publisher-edition:${row.source_pr}:${row.isbn13}` ||
        !validPublisherLink(row.source_url, row.source_pr) ||
        row.source_family !== source.family || row.source_head !== source.head ||
        row.source_file !== source.file || row.source_file_sha256 !== source.sha256 ||
        row.edition_format !== source.format || row.source_local_form !== source.form ||
        row.identity_scope !== 'SOURCE_LOCAL_EDITION_UNRECONCILED' ||
        row.full_text_status !== 'NOT_READ' ||
        row.publisher_claims_are_fictional_truth !== false ||
        ROW_EFFECTS.some(field => row[field] !== 'NONE') ||
        !Array.isArray(row.creator_credits) || row.creator_credits.length < 1 || row.creator_credits.length > 4 ||
        row.creator_credits.some(credit => !credit || !textOK(credit.name) ||
          !['AUTHOR', 'EDITOR', 'AUTHOR_ARTIST'].includes(credit.role)) ||
        (row.source_anomaly !== null && row.source_anomaly !== 'AUTHOR_HEADER_JERI_VS_DESCRIPTION_TERI_UNRESOLVED') ||
        (row.source_pr === 497 && row.source_anomaly !== null) ||
        rows.has(row.row_id) || seenISBN.has(row.isbn13)) {
      throw new Error('Held preview includes unreviewed/duplicated or promoted edition metadata');
    }
    groups.set(row.source_pr, groups.get(row.source_pr) + 1);
    rows.add(row.row_id);
    seenISBN.add(row.isbn13);
  }
  if ([...groups.values()].some(n => n !== 5)) throw new Error('Publisher source-family count drift');
  return data.rows;
}

function addText(document, holder, tag, text, className = '') {
  const child = document.createElement(tag);
  if (className) child.className = className;
  child.textContent = text;
  holder.append(child);
  return child;
}

function renderCard(document, row) {
  const card = document.createElement('article');
  card.className = 'card publisher-edition-card';
  const body = document.createElement('div');
  body.className = 'publisher-edition-copy';
  addText(document, body, 'p', `HELD DRAFT · PR #${row.source_pr} · ${row.edition_format}`, 'eyebrow');
  addText(document, body, 'h3', row.title);
  addText(document, body, 'p', `${row.creator_credits.map(c => `${c.name} (${c.role})`).join(', ')} · ISBN ${row.isbn13}`);
  addText(document, body, 'p', `Publisher metadata only · ${row.source_family} · ${row.publisher_date_us}`);
  addText(document, body, 'p', 'No Work admission from this edition · No full-text read · No edition reconciliation');
  if (row.source_anomaly) addText(document, body, 'p', `HELD source anomaly: ${row.source_anomaly.replaceAll('_', ' ').toLowerCase()}`);
  const link = document.createElement('a');
  link.href = row.source_url;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  link.textContent = 'Inspect first-party publisher source';
  body.append(link);
  card.append(body);
  return card;
}

export function initHeldPublisherPreview({ document, fetchImpl = globalThis.fetch.bind(globalThis),
  cryptoSubtle = globalThis.crypto?.subtle, expectedSha256 = PREVIEW_SHA256 }) {
  const open = document.getElementById('held-preview-open');
  const reset = document.getElementById('held-preview-reset');
  const state = document.getElementById('held-preview-state');
  const count = document.getElementById('held-preview-count');
  const list = document.getElementById('held-preview-list');
  let epoch = 0;
  count.textContent = '—';
  list.replaceChildren();
  state.textContent = 'Preview closed. No draft metadata requests sent.';
  reset.disabled = true;

  reset.addEventListener('click', () => {
    ++epoch;
    list.replaceChildren();
    count.textContent = '—';
    state.textContent = 'Preview closed. No draft metadata retained in this display.';
    reset.disabled = true;
    open.disabled = false;
  });
  open.addEventListener('click', async () => {
    const active = ++epoch;
    list.replaceChildren();
    count.textContent = '—';
    state.textContent = 'Validating pinned local draft metadata…';
    open.disabled = true;
    reset.disabled = false;
    try {
      if (!cryptoSubtle) throw new Error('Browser digest verification unavailable');
      const response = await fetchImpl('./held-publisher-preview.json', { cache: 'no-store', credentials: 'omit' });
      if (!response.ok) throw new Error('Preview JSON unavailable');
      const bytes = await response.arrayBuffer();
      if (bytes.byteLength > 32_768) throw new Error('Preview JSON exceeds scoped size');
      const digest = await cryptoSubtle.digest('SHA-256', bytes);
      const actual = Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2, '0')).join('');
      if (actual !== expectedSha256) throw new Error('Preview data changed from reviewed digest');
      const raw = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
      const rows = validateHeldPublisherPreview(JSON.parse(raw));
      if (active !== epoch) return;
      for (const row of rows) list.append(renderCard(document, row));
      count.textContent = '10 HELD publisher edition metadata leads (2 publisher source families; 0 Work admissions from this preview)';
      state.textContent = 'HELD DRAFT preview loaded. Neither accepted research nor main Explorer counts changed.';
    } catch (_) {
      if (active !== epoch) return;
      list.replaceChildren();
      count.textContent = '—';
      state.textContent = 'Preview withheld: missing, changed, or invalid local draft metadata.';
    } finally {
      if (active === epoch) open.disabled = false;
    }
  });
}

if (typeof document !== 'undefined') initHeldPublisherPreview({ document });
