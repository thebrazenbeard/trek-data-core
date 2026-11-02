/* Trek Data Core Explorer. Local data only; no dependencies, telemetry, or HTML injection. */
(() => {
  'use strict';

  const byId = (id) => document.getElementById(id);
  const el = (tag, className, value) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined && value !== null) node.textContent = String(value);
    return node;
  };
  const asString = (value) => typeof value === 'string' ? value.trim() : '';
  const asItems = (value) => Array.isArray(value) ? value.filter((item) => item && typeof item === 'object' && !Array.isArray(item)) : [];
  const normalize = (value) => String(value ?? '').normalize('NFKD').toLocaleLowerCase();
  const humanize = (value) => asString(value).replaceAll('_', ' ').replace(/\b\w/g, (match) => match.toUpperCase());
  const kindLabel = (value) => {
    const kind = normalize(asString(value)).replace(/[\s-]+/g, '_');
    if (['series', 'tv_series', 'television_series'].includes(kind)) return 'Mission (series)';
    if (['episode', 'tv_episode', 'television_episode'].includes(kind)) return 'Mission Briefing (episode)';
    return humanize(value);
  };
  const MAX_RENDER = 72;

  const controls = {
    search: byId('search-input'),
    scope: byId('scope-filter'),
    mission: byId('mission-filter'),
    kind: byId('kind-filter'),
    status: byId('status-filter')
  };
  const state = { missions: [], briefings: [], records: [], dataStatus: 'NOT_BUILT', projectionHash: null };

  function safeHref(value) {
    if (typeof value !== 'string' || !value.trim()) return null;
    try {
      const url = new URL(value.trim(), document.baseURI);
      if (url.protocol === 'https:') return url.href;
      if (url.protocol === 'http:' && url.origin === location.origin) return url.href;
    } catch (_) {
      // Invalid or unsupported source reference is displayed as text, never as a link.
    }
    return null;
  }

  function termMatch(row, search) {
    if (!search) return true;
    const fields = [row.id, row.title, row.focus, row.summary, row.kind,
      row.mission_id, row.briefing_id, row.work_id, row.predicate,
      row.admission_status, row.projection_status,
      ...(Array.isArray(row.tags) ? row.tags : []),
      ...(Array.isArray(row.source_ids) ? row.source_ids : [])];
    const haystack = normalize(fields.filter((field) => typeof field === 'string' || typeof field === 'number').join(' '));
    return search.split(/\s+/).every((term) => haystack.includes(term));
  }

  function setSelectOptions(select, values, label) {
    select.replaceChildren(new Option(label, 'all'));
    for (const [value, text] of values) select.add(new Option(text, value));
  }

  function refreshOptions() {
    setSelectOptions(controls.mission,
      state.missions.map((mission) => [mission.id, mission.title]).sort((a, b) => a[1].localeCompare(b[1])),
      'All Missions');
    const kinds = [...new Set(state.records.map((r) => asString(r.kind)).filter(Boolean))].sort();
    setSelectOptions(controls.kind, kinds.map((kind) => [kind, kindLabel(kind)]), 'All kinds');
    const statuses = [...new Set([
      ...state.briefings.map((r) => asString(r.admission_status)),
      ...state.records.map((r) => asString(r.projection_status))
    ].filter(Boolean))].sort();
    setSelectOptions(controls.status, statuses.map((status) => [status, humanize(status)]), 'All statuses');
  }

  function makeBadge(value) {
    const status = asString(value) || 'UNSPECIFIED';
    const badge = el('span', 'badge ' + status.toLowerCase().replace(/[^a-z0-9_-]/g, ''), humanize(status));
    badge.setAttribute('aria-label', 'Record status: ' + humanize(status));
    return badge;
  }

  function appendDetail(dl, key, value) {
    if (value === undefined || value === null || value === '') return;
    dl.append(el('dt', null, key), el('dd', null, value));
  }

  function makeMissionCard(row) {
    const card = el('article', 'card');
    const top = el('div', 'card-header');
    top.append(el('span', 'kicker', 'Mission · television series'));
    card.append(top, el('h3', null, row.title));
    if (row.focus) card.append(el('p', null, row.focus));
    const detail = el('dl', 'detail-list');
    appendDetail(detail, 'Mission ID', row.id);
    const count = state.briefings.filter((b) => b.mission_id === row.id).length;
    appendDetail(detail, 'Indexed Mission Briefings', count.toLocaleString());
    card.append(detail);
    const button = el('button', null, 'Focus this Mission');
    button.type = 'button';
    button.setAttribute('aria-label', 'Filter Explorer to ' + row.title);
    button.addEventListener('click', () => {
      controls.mission.value = row.id;
      controls.scope.value = 'all';
      render();
      byId('search-heading').scrollIntoView({ block: 'start' });
      controls.search.focus();
    });
    card.append(button);
    return card;
  }

  function makeBriefingCard(row) {
    const card = el('article', 'card');
    const top = el('div', 'card-header');
    top.append(el('span', 'kicker', 'Mission Briefing · episode'));
    top.append(makeBadge(row.admission_status || 'UNSPECIFIED'));
    card.append(top, el('h3', null, row.title));
    const detail = el('dl', 'detail-list');
    const chapter = [row.season != null ? `Season ${row.season}` : '', row.episode != null ? `Episode ${row.episode}` : ''].filter(Boolean).join(' · ');
    appendDetail(detail, 'Sequence', chapter);
    appendDetail(detail, 'Work ID', row.work_id);
    appendDetail(detail, 'Mission ID', row.mission_id);
    card.append(detail);
    return card;
  }

  function addSources(card, row) {
    const ids = Array.isArray(row.source_ids) ? row.source_ids.filter((value) => typeof value === 'string' && value.trim()) : [];
    const refs = Array.isArray(row.source_refs) ? row.source_refs : [];
    if (!ids.length && !refs.length) {
      card.append(el('p', 'source-note', 'No source references included in this index entry.'));
      return;
    }
    card.append(el('p', 'kicker', 'Provenance / Source references'));
    const list = el('ul', 'source-links');
    for (const id of ids) list.append(el('li', null, id));
    for (const ref of refs) {
      if (!ref || typeof ref !== 'object') continue;
      const label = asString(ref.label) || asString(ref.id) || asString(ref.href);
      if (!label) continue;
      const item = el('li');
      const href = safeHref(ref.href);
      if (href) {
        const link = el('a', null, label);
        link.href = href;
        link.rel = 'noopener noreferrer';
        if (new URL(href).origin !== location.origin) link.target = '_blank';
        item.append(link);
      } else item.textContent = label;
      list.append(item);
    }
    card.append(list);
  }

  function makeRecordCard(row) {
    const card = el('article', 'record-card');
    const top = el('div', 'card-header');
    top.append(el('span', 'kicker', kindLabel(row.kind) || 'Continuity record'));
    top.append(makeBadge(row.projection_status || 'UNSPECIFIED'));
    card.append(top, el('h3', null, row.title));
    if (row.summary) card.append(el('p', null, row.summary));
    const detail = el('dl', 'detail-list');
    appendDetail(detail, 'Record ID', row.id);
    appendDetail(detail, 'Predicate', row.predicate);
    appendDetail(detail, 'Mission ID', row.mission_id);
    appendDetail(detail, 'Mission Briefing ID', row.briefing_id);
    card.append(detail);
    addSources(card, row);
    return card;
  }

  function showList(sectionId, listId, emptyId, items, makeCard, enabled) {
    const section = byId(sectionId);
    section.hidden = !enabled;
    if (!enabled) return;
    const container = byId(listId);
    container.replaceChildren();
    const fragment = document.createDocumentFragment();
    for (const item of items.slice(0, MAX_RENDER)) fragment.append(makeCard(item));
    container.append(fragment);
    const empty = byId(emptyId);
    empty.hidden = items.length !== 0;
    if (!items.length && state.dataStatus === 'MISSION_CATALOG_ONLY' && sectionId !== 'missions') {
      empty.textContent = 'Catalog-only mode: no ' + (sectionId === 'briefings' ? 'Mission Briefings' : 'continuity records') + ' have been admitted to this index.';
    } else {
      empty.textContent = sectionId === 'missions' ? 'No Missions match the current search.' :
        sectionId === 'briefings' ? 'No Mission Briefings match the current filters.' :
          'No continuity records match the current filters.';
    }
  }

  function render() {
    const search = normalize(controls.search.value.trim());
    const scope = controls.scope.value;
    const mission = controls.mission.value;
    const kind = controls.kind.value;
    const status = controls.status.value;
    const matchesMission = (row) => mission === 'all' || (row.mission_id || row.id) === mission;
    const showMissions = scope === 'all' || scope === 'missions';
    const showBriefings = scope === 'all' || scope === 'briefings';
    const showRecords = scope === 'all' || scope === 'records';
    const missions = (status === 'all' && kind === 'all') ? state.missions.filter((row) => matchesMission(row) && termMatch(row, search)) : [];
    const briefings = (kind === 'all') ? state.briefings.filter((row) => matchesMission(row) && (status === 'all' || row.admission_status === status) && termMatch(row, search)) : [];
    const records = state.records.filter((row) => matchesMission(row) && (status === 'all' || row.projection_status === status) && (kind === 'all' || row.kind === kind) && termMatch(row, search));

    showList('missions', 'mission-list', 'mission-empty', missions, makeMissionCard, showMissions);
    showList('briefings', 'briefing-list', 'briefing-empty', briefings, makeBriefingCard, showBriefings);
    showList('records', 'record-list', 'record-empty', records, makeRecordCard, showRecords);
    const visibleCount = (showMissions ? missions.length : 0) + (showBriefings ? briefings.length : 0) + (showRecords ? records.length : 0);
    const renderedCount = (showMissions ? Math.min(missions.length, MAX_RENDER) : 0) +
      (showBriefings ? Math.min(briefings.length, MAX_RENDER) : 0) + (showRecords ? Math.min(records.length, MAX_RENDER) : 0);
    byId('result-summary').textContent = `${visibleCount.toLocaleString()} matching ${visibleCount === 1 ? 'entry' : 'entries'}` +
      (renderedCount < visibleCount ? ` · Showing the first ${renderedCount.toLocaleString()} (refine filters to see more)` : '') + '.';
  }

  function acceptIndex(data) {
    if (!data || typeof data !== 'object' || data.schema_version !== '1.0.0' ||
        !data.build || !['MISSION_CATALOG_ONLY', 'GOVERNED_PROJECTION'].includes(data.build.data_status) ||
        !Array.isArray(data.missions) || !Array.isArray(data.briefings) || !Array.isArray(data.records)) {
      throw new Error('Local index has an incompatible schema or incomplete build metadata.');
    }
    const unique = (items) => {
      const used = new Set();
      return asItems(items).filter((item) => {
        const id = asString(item.id), title = asString(item.title);
        if (!id || !title || used.has(id)) return false;
        used.add(id);
        return true;
      });
    };
    state.missions = unique(data.missions);
    state.dataStatus = data.build.data_status;
    state.projectionHash = asString(data.build.projection_hash);
    if (state.dataStatus === 'GOVERNED_PROJECTION') {
      state.briefings = unique(data.briefings);
      state.records = unique(data.records);
    } else {
      // A mission catalog alone is not evidence of admitted episodes or facts.
      state.briefings = [];
      state.records = [];
    }
    refreshOptions();
    byId('mission-count').textContent = state.missions.length.toLocaleString();
    byId('briefing-count').textContent = state.briefings.length.toLocaleString();
    byId('record-count').textContent = state.records.length.toLocaleString();
    byId('data-state').textContent = state.dataStatus === 'MISSION_CATALOG_ONLY'
      ? 'Catalog-only transmission. Mission names are available; no Mission Briefings or continuity facts are admitted here.'
      : 'The index declares a governed projection' + (state.projectionHash ? ` (${state.projectionHash.slice(0, 24)}…)` : '') + '. Check its build receipt and each record’s status before relying on it.';
    byId('notice').hidden = true;
    render();
  }

  function showUnavailable(message) {
    state.missions = []; state.briefings = []; state.records = []; state.dataStatus = 'NOT_BUILT';
    byId('mission-count').textContent = '0';
    byId('briefing-count').textContent = '0';
    byId('record-count').textContent = '0';
    byId('data-state').textContent = 'No usable local index loaded.';
    const notice = byId('notice');
    notice.textContent = message;
    notice.hidden = false;
    refreshOptions();
    render();
  }

  async function loadIndex() {
    try {
      const response = await fetch('./index.json', { cache: 'no-store' });
      if (response.status === 404) {
        showUnavailable('The index has not been built yet. This interface does not invent Missions, Mission Briefings, or facts when index.json is absent.');
        return;
      }
      if (!response.ok) throw new Error(`Index request returned HTTP ${response.status}.`);
      acceptIndex(await response.json());
    } catch (error) {
      showUnavailable(`Could not load a valid local index. ${error.message || 'Check index.json.'} Serve the explorer over HTTP rather than opening the file directly.`);
    }
  }

  byId('filters').addEventListener('input', render);
  byId('filters').addEventListener('change', render);
  byId('filters').addEventListener('reset', () => { window.requestAnimationFrame(render); });
  loadIndex();
})();
