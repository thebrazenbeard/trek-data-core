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
    if (['episode', 'tv_episode', 'television_episode'].includes(kind)) return 'Briefing (episode)';
    return humanize(value);
  };
  const PAGE_SIZE = 72;
  const visibleLimits = { missions: PAGE_SIZE, briefings: PAGE_SIZE, records: PAGE_SIZE };
  const RESEARCH_PAGE_SIZE = 30;
  let visibleResearchLimit = RESEARCH_PAGE_SIZE;

  // Original, short interface signals. Audio is strictly user-opt-in: no
  // playback or AudioContext construction during startup, loading, or typing.
  let tonesEnabled = false;
  let tonePending = false;
  let toneGeneration = 0;
  let toneContext = null;
  const toneToggle = byId('tone-toggle');
  const updateToneToggle = () => {
    if (!toneToggle) return;
    toneToggle.setAttribute('aria-pressed', String(tonesEnabled));
    toneToggle.setAttribute('aria-label', tonePending ? 'Cancel enabling interface tones' : tonesEnabled ? 'Disable interface tones' : 'Enable interface tones');
    toneToggle.textContent = `Interface tones: ${tonePending ? 'Starting…' : tonesEnabled ? 'On' : 'Off'}`;
  };
  const discardToneContext = () => {
    const previous = toneContext;
    toneContext = null;
    if (!previous) return;
    try {
      if (typeof previous.close === 'function') Promise.resolve(previous.close()).catch(() => {});
    } catch (_) {
      // A failed close must never block archive navigation.
    }
  };
  const playTone = () => {
    if (!tonesEnabled || !toneContext || toneContext.state !== 'running') return;
    try {
      const start = toneContext.currentTime;
      [560, 830].forEach((frequency, index) => {
        const at = start + index * .045;
        const oscillator = toneContext.createOscillator();
        const volume = toneContext.createGain();
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(frequency, at);
        volume.gain.setValueAtTime(.0001, at);
        volume.gain.exponentialRampToValueAtTime(.018, at + .012);
        volume.gain.exponentialRampToValueAtTime(.0001, at + .088);
        oscillator.connect(volume);
        volume.connect(toneContext.destination);
        oscillator.start(at);
        oscillator.stop(at + .09);
      });
    } catch (_) {
      // Sound effects are cosmetic. Never interrupt navigation or research.
    }
  };
  if (toneToggle) {
    updateToneToggle();
    toneToggle.addEventListener('click', () => {
      if (tonesEnabled || tonePending) {
        toneGeneration++;
        tonesEnabled = false;
        tonePending = false;
        discardToneContext();
        updateToneToggle();
        return;
      }
      const Context = window.AudioContext || window.webkitAudioContext;
      if (typeof Context !== 'function') {
        toneToggle.disabled = true;
        toneToggle.textContent = 'Interface tones unavailable';
        toneToggle.setAttribute('aria-label', 'Interface tones unavailable in this browser');
        return;
      }
      try {
        if (!toneContext) toneContext = new Context();
        const requestedGeneration = ++toneGeneration;
        tonePending = true;
        updateToneToggle();
        const ready = toneContext.state === 'running' ? Promise.resolve() : toneContext.resume();
        Promise.resolve(ready).then(() => {
          if (requestedGeneration !== toneGeneration) return;
          tonePending = false;
          tonesEnabled = toneContext.state === 'running';
          updateToneToggle();
          playTone();
        }).catch(() => {
          if (requestedGeneration !== toneGeneration) return;
          tonePending = false;
          tonesEnabled = false;
          discardToneContext();
          updateToneToggle();
        });
      } catch (_) {
        tonePending = false;
        tonesEnabled = false;
        discardToneContext();
        updateToneToggle();
      }
    });
  }

  const controls = {
    search: byId('search-input'),
    scope: byId('scope-filter'),
    mission: byId('mission-filter'),
    kind: byId('kind-filter'),
    status: byId('status-filter')
  };
  const state = { missions: [], briefings: [], records: [], dataStatus: 'NOT_BUILT', projectionHash: null };
  const researchControls = {
    search: byId('research-query'),
    mission: byId('research-mission')
  };
  const researchState = { leads: [], available: false };

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
    appendDetail(detail, 'Indexed Briefings', count.toLocaleString());
    const leadCount = researchState.available ? researchState.leads.filter((lead) => lead.mission_id === row.id).length : 0;
    // Candidate counts are never combined with admitted Briefing counts.
    if (researchState.available) appendDetail(detail, 'Unverified research leads', leadCount.toLocaleString());
    card.append(detail);
    const button = el('button', null, 'Focus this Mission');
    button.type = 'button';
    button.setAttribute('aria-label', 'Filter Explorer to ' + row.title);
    button.addEventListener('click', () => {
      playTone();
      controls.mission.value = row.id;
      controls.scope.value = 'all';
      render();
      byId('search-heading').scrollIntoView({ block: 'start' });
      controls.search.focus();
    });
    card.append(button);
    if (leadCount > 0) {
      const researchButton = el('button', 'research-shortcut', `Inspect ${leadCount.toLocaleString()} unverified ${leadCount === 1 ? 'lead' : 'leads'}`);
      researchButton.type = 'button';
      researchButton.setAttribute('aria-label', `Inspect ${leadCount.toLocaleString()} unverified Research Leads for ${row.title}`);
      researchButton.addEventListener('click', () => {
        playTone();
        researchControls.search.value = '';
        researchControls.mission.value = row.id;
        visibleResearchLimit = RESEARCH_PAGE_SIZE;
        renderResearch();
        byId('research-heading').scrollIntoView({ block: 'start' });
        researchControls.search.focus();
      });
      card.append(researchButton);
    }
    return card;
  }

  function makeBriefingCard(row) {
    const card = el('article', 'card');
    const top = el('div', 'card-header');
    top.append(el('span', 'kicker', 'Briefing · episode'));
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
    appendDetail(detail, 'Briefing ID', row.briefing_id);
    card.append(detail);
    addSources(card, row);
    return card;
  }

  function makeResearchCard(row) {
    const card = el('article', 'card research-card');
    const top = el('div', 'card-header');
    const publisher = row.source_type === 'PUBLISHER_EPISODE_SLOT_METADATA';
    top.append(el('span', 'kicker', publisher ? 'Publisher-listed episode slot · unverified' : 'Wikidata episode metadata · unverified'));
    const badge = el('span', 'badge proposed', 'Candidate · not verified');
    badge.setAttribute('aria-label', 'Unverified candidate; not an admitted Briefing');
    top.append(badge);
    card.append(top, el('h3', null, row.episode_label));
    const mission = state.missions.find((item) => item.id === row.mission_id);
    card.append(el('p', null, mission?.title || row.mission_id));
    const detail = el('dl', 'detail-list');
    if (publisher) {
      appendDetail(detail, 'Publisher-listed slot', `Season ${row.season_number}, episode ${row.episode_number}`);
      appendDetail(detail, 'Observed on', row.observed_on);
    } else {
      appendDetail(detail, 'Wikidata item ID', row.episode_qid);
    }
    appendDetail(detail, 'Source independence group', row.independence_group);
    appendDetail(detail, 'Retrieval snapshot', row.snapshot_id);
    card.append(detail);
    const link = el('a', null, publisher ? 'Open publisher episode guide' : 'Open Wikidata item');
    // The source locator is exact-allowlisted; QIDs are bounded before URL assembly.
    link.href = publisher ? row.source_locator : 'https://www.wikidata.org/wiki/' + row.episode_qid;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    card.append(link);
    const provenance = el('details');
    provenance.append(el('summary', null, publisher ? 'View source limitations' : 'View recorded provenance hashes'));
    const hashes = el('dl', 'detail-list');
    if (publisher) {
      appendDetail(hashes, 'Scope', 'Publisher page title and episode slot only; not a verified season roster.');
      appendDetail(hashes, 'Page-response hash', 'Not captured — no publisher revision attested.');
      appendDetail(hashes, 'Independent corroboration', 'Not established; publisher pages share one independence group.');
    } else {
      appendDetail(hashes, 'Query SHA-256', row.query_sha256);
      appendDetail(hashes, 'Response SHA-256', row.response_sha256);
      appendDetail(hashes, 'Retrieval verification', 'Offline receipt; not remotely verified.');
    }
    provenance.append(hashes);
    card.append(provenance);
    return card;
  }

  function setResearchAvailability(available, message) {
    researchState.available = available;
    if (!available) researchState.leads = [];
    researchControls.search.disabled = !available;
    researchControls.mission.disabled = !available;
    byId('research-reset').disabled = !available;
    byId('research-count').textContent = available ? researchState.leads.length.toLocaleString() : '—';
    byId('research-state').textContent = message;
    renderResearch();
    // Mission cards must reflect the same validated candidate-only snapshot.
    render();
  }

  function renderResearch() {
    const container = byId('research-list');
    container.replaceChildren();
    const empty = byId('research-empty');
    if (!researchState.available) {
      empty.hidden = false;
      empty.textContent = 'Research Leads are not available in this Explorer. The Mission catalog above remains separate.';
      byId('research-summary').textContent = 'Research dataset unavailable.';
      return;
    }
    const search = normalize(researchControls.search.value.trim());
    const mission = researchControls.mission.value;
    const missionNames = new Map(state.missions.map((item) => [item.id, item.title]));
    const matching = researchState.leads.filter((row) => {
      if (mission !== 'all' && row.mission_id !== mission) return false;
      if (!search) return true;
      const slot = row.source_type === 'PUBLISHER_EPISODE_SLOT_METADATA' ? `s${row.season_number}e${row.episode_number} season ${row.season_number} episode ${row.episode_number}` : '';
      const haystack = normalize([row.episode_label, row.episode_qid || '', slot, row.mission_id, missionNames.get(row.mission_id)].join(' '));
      return search.split(/\s+/).every((term) => haystack.includes(term));
    });
    const count = Math.min(matching.length, visibleResearchLimit);
    const fragment = document.createDocumentFragment();
    for (const row of matching.slice(0, count)) fragment.append(makeResearchCard(row));
    container.append(fragment);
    if (count < matching.length) {
      const more = el('button', 'load-more', `Show next ${Math.min(RESEARCH_PAGE_SIZE, matching.length - count)} research leads`);
      more.type = 'button';
      more.addEventListener('click', () => {
        playTone();
        const firstNewCard = count;
        visibleResearchLimit += RESEARCH_PAGE_SIZE;
        renderResearch();
        focusNewPage(byId('research-list'), firstNewCard);
      });
      container.append(more);
    }
    empty.hidden = matching.length !== 0;
    empty.textContent = 'No unverified Research Leads match these filters. Clear lead filters to see all published candidates.';
    byId('research-summary').textContent = `${matching.length.toLocaleString()} matching unverified ${matching.length === 1 ? 'lead' : 'leads'}` +
      (count < matching.length ? ` · Showing ${count.toLocaleString()} (use Show next research leads to continue)` : '') + '.';
  }

  function acceptResearchIndex(data) {
    const rootKeys = ['coverage_effect', 'data_status', 'held_candidate_count', 'lead_count', 'leads', 'sampled_missions_count', 'schema_version', 'source_policy'];
    const wikidataKeys = ['episode_label', 'episode_qid', 'independence_group', 'mission_id', 'query_sha256', 'response_sha256', 'snapshot_id', 'source_type', 'verification_status'];
    const publisherKeys = ['episode_label', 'episode_number', 'independence_group', 'mission_id', 'observed_on', 'season_number', 'snapshot_id', 'source_locator', 'source_type', 'verification_status'];
    const exactKeys = (value, expected) => value && typeof value === 'object' && !Array.isArray(value) &&
      Object.keys(value).length === expected.length && expected.every((key) => Object.hasOwn(value, key));
    const isHash = (value) => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
    if (!exactKeys(data, rootKeys) || data.schema_version !== '2.0.0' ||
        data.data_status !== 'CANDIDATE_DISCOVERY_ONLY' ||
        data.source_policy !== 'EXTERNAL_METADATA_ONLY' || data.coverage_effect !== 'NONE' ||
        !Array.isArray(data.leads) || data.leads.length > 10000 ||
        !Number.isInteger(data.lead_count) || data.lead_count !== data.leads.length ||
        !Number.isInteger(data.sampled_missions_count) || data.held_candidate_count !== 2) {
      throw new Error('Research data does not have the candidate-only schema and boundaries.');
    }
    const missions = new Set(state.missions.map((row) => row.id));
    const sampled = new Set(), leadIds = new Set(), leads = [];
    for (const row of data.leads) {
      const publisher = row?.source_type === 'PUBLISHER_EPISODE_SLOT_METADATA';
      const wikidata = row?.source_type === 'WIKIDATA_METADATA';
      if ((!wikidata && !publisher) || !exactKeys(row, publisher ? publisherKeys : wikidataKeys) ||
          !missions.has(row.mission_id) || typeof row.episode_label !== 'string' ||
          row.episode_label !== row.episode_label.trim() ||
          !row.episode_label.length || row.episode_label.length > 160 ||
          /[\p{C}<>]/u.test(row.episode_label) ||
          typeof row.snapshot_id !== 'string' || !/^[A-Za-z0-9_-]{3,100}$/.test(row.snapshot_id) ||
          row.verification_status !== 'UNVERIFIED_METADATA') {
        throw new Error('Research data contains an invalid, duplicate, or unexpectedly admitted lead.');
      }
      let leadId;
      if (wikidata) {
        if (row.independence_group !== 'wikidata:wdqs' || !/^Q[1-9][0-9]{0,15}$/.test(row.episode_qid) ||
            !isHash(row.query_sha256) || !isHash(row.response_sha256) ||
            (row.mission_id === 'ent' && ['Q56247746', 'Q866375'].includes(row.episode_qid))) {
          throw new Error('Research data contains unreviewed Wikidata provenance or a held arc/umbrella.');
        }
        leadId = `wikidata:${row.episode_qid}`;
      } else {
        if (row.mission_id !== 'sfa' || row.independence_group !== 'publisher:paramount' ||
            row.source_locator !== 'https://www.paramountplus.com/shows/star-trek-starfleet-academy/episodes/1/' ||
            row.snapshot_id !== 'SFA-PUBLISHER-ROSTER-20261102-001' ||
            row.observed_on !== '2026-11-02' ||
            !Number.isInteger(row.season_number) || row.season_number !== 1 ||
            !Number.isInteger(row.episode_number) || row.episode_number < 1 || row.episode_number > 10) {
          throw new Error('Research data contains an unreviewed publisher source or season slot.');
        }
        leadId = `publisher:${row.mission_id}:${row.season_number}:${row.episode_number}`;
      }
      if (leadIds.has(leadId)) throw new Error('Research data contains duplicate candidate identities.');
      leadIds.add(leadId);
      sampled.add(row.mission_id);
      leads.push({ ...row });
    }
    if (sampled.size !== data.sampled_missions_count) {
      throw new Error('Research lead Mission totals do not match their declared count.');
    }
    researchState.leads = leads;
    visibleResearchLimit = RESEARCH_PAGE_SIZE;
    setSelectOptions(researchControls.mission,
      [...sampled].map((id) => [id, state.missions.find((item) => item.id === id).title]).sort((a, b) => a[1].localeCompare(b[1])),
      'All Missions');
    setResearchAvailability(true, 'External candidate metadata loaded. These leads have not been admitted as Briefings.');
  }

  async function loadResearchIndex() {
    try {
      const response = await fetch('./research-leads.json', { cache: 'no-store' });
      if (response.status === 404) {
        setResearchAvailability(false, 'The separate Research Leads index has not been published yet.');
        return;
      }
      if (!response.ok) throw new Error(`Research request returned HTTP ${response.status}.`);
      acceptResearchIndex(await response.json());
    } catch (error) {
      setResearchAvailability(false, `Could not load a valid Research Leads file. ${error.message || 'Check research-leads.json.'}`);
    }
  }

  // Pagination recreates its button on each render. Give keyboard and screen
  // reader users a stable next reading position instead of losing focus when
  // the formerly focused Show next button disappears from the document.
  function focusNewPage(container, firstNewCard) {
    const target = container.children[firstNewCard];
    if (!target) return;
    target.setAttribute('tabindex', '-1');
    target.focus();
  }

  function showList(sectionId, listId, emptyId, items, makeCard, enabled) {
    const section = byId(sectionId);
    section.hidden = !enabled;
    if (!enabled) return;
    const container = byId(listId);
    container.replaceChildren();
    const fragment = document.createDocumentFragment();
    const count = Math.min(items.length, visibleLimits[sectionId]);
    for (const item of items.slice(0, count)) fragment.append(makeCard(item));
    container.append(fragment);
    if (count < items.length) {
      const more = el('button', 'load-more', `Show next ${Math.min(PAGE_SIZE, items.length - count)} of ${items.length} ${sectionId}`);
      more.type = 'button';
      more.addEventListener('click', () => {
        playTone();
        const firstNewCard = count;
        visibleLimits[sectionId] += PAGE_SIZE;
        render();
        focusNewPage(byId(listId), firstNewCard);
      });
      container.append(more);
    }
    const empty = byId(emptyId);
    empty.hidden = items.length !== 0;
    if (!items.length && state.dataStatus === 'MISSION_CATALOG_ONLY' && sectionId !== 'missions') {
      empty.textContent = 'Catalog-only mode: no ' + (sectionId === 'briefings' ? 'Briefings' : 'continuity records') + ' have been admitted to this index.';
    } else {
      empty.textContent = sectionId === 'missions' ? 'No Missions match the current search.' :
        sectionId === 'briefings' ? 'No Briefings match the current filters.' :
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
    const renderedCount = (showMissions ? Math.min(missions.length, visibleLimits.missions) : 0) +
      (showBriefings ? Math.min(briefings.length, visibleLimits.briefings) : 0) + (showRecords ? Math.min(records.length, visibleLimits.records) : 0);
    byId('result-summary').textContent = `${visibleCount.toLocaleString()} matching ${visibleCount === 1 ? 'entry' : 'entries'}` +
      (renderedCount < visibleCount ? ` · Showing ${renderedCount.toLocaleString()} (use Show next to continue)` : '') + '.';
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
      if (!/^sha256:[a-f0-9]{64}$/.test(state.projectionHash)) {
        throw new Error('A governed index must provide a complete verified projection hash.');
      }
      state.briefings = unique(data.briefings);
      state.records = unique(data.records);
      const missions = new Set(state.missions.map((row) => row.id));
      const briefings = new Set(state.briefings.map((row) => row.id));
      if (state.briefings.some((row) => !missions.has(row.mission_id)) ||
          state.records.some((row) => row.mission_id != null && !missions.has(row.mission_id)) ||
          state.records.some((row) => row.briefing_id != null && !briefings.has(row.briefing_id))) {
        throw new Error('The governed index contains an unresolved Mission or Briefing reference.');
      }
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
      ? 'Catalog-only transmission. Mission names are available; no Briefings or continuity facts are admitted here.'
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
    setResearchAvailability(false, 'Research Leads require a valid Mission catalog.');
  }

  async function loadIndex() {
    try {
      const response = await fetch('./index.json', { cache: 'no-store' });
      if (response.status === 404) {
        showUnavailable('The index has not been built yet. This interface does not invent Missions, Briefings, or facts when index.json is absent.');
        return;
      }
      if (!response.ok) throw new Error(`Index request returned HTTP ${response.status}.`);
      acceptIndex(await response.json());
      await loadResearchIndex();
    } catch (error) {
      showUnavailable(`Could not load a valid local index. ${error.message || 'Check index.json.'} Serve the explorer over HTTP rather than opening the file directly.`);
    }
  }

  const resetPageCounts = () => {
    for (const section of Object.keys(visibleLimits)) visibleLimits[section] = PAGE_SIZE;
  };
  const filters = byId('filters');
  filters.addEventListener('input', () => { resetPageCounts(); render(); });
  filters.addEventListener('change', () => { playTone(); resetPageCounts(); render(); });
  filters.addEventListener('submit', (event) => { event.preventDefault(); playTone(); render(); });
  filters.addEventListener('reset', () => { playTone(); resetPageCounts(); window.requestAnimationFrame(render); });
  const researchFilters = byId('research-filters');
  researchFilters.addEventListener('input', () => { visibleResearchLimit = RESEARCH_PAGE_SIZE; renderResearch(); });
  researchFilters.addEventListener('change', () => { playTone(); visibleResearchLimit = RESEARCH_PAGE_SIZE; renderResearch(); });
  researchFilters.addEventListener('submit', (event) => { event.preventDefault(); playTone(); renderResearch(); });
  researchFilters.addEventListener('reset', () => { playTone(); visibleResearchLimit = RESEARCH_PAGE_SIZE; window.requestAnimationFrame(renderResearch); });
  setResearchAvailability(false, 'Checking for a separate research-leads index…');
  loadIndex();
})();
