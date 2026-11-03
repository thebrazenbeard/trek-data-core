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

  // Keep the section rail native-scrollable. Its cue is informational, not a
  // fake navigation control, and only appears when real links are offscreen.
  const navigation = document.querySelector?.('.lcars-navigation');
  const navigationHint = document.querySelector?.('.navigation-scroll-hint');
  const updateNavigationHint = () => {
    if (!navigation || !navigationHint) return;
    const maxScroll = Math.max(0, navigation.scrollWidth - navigation.clientWidth);
    const overflowing = maxScroll > 2;
    navigationHint.hidden = !overflowing;
    if (!overflowing) {
      navigation.removeAttribute('aria-describedby');
      return;
    }
    const atStart = navigation.scrollLeft <= 2;
    const atEnd = navigation.scrollLeft >= maxScroll - 2;
    const message = atStart ? 'More sections → Swipe, scroll or Tab'
      : atEnd ? 'Earlier sections ← Swipe, scroll or Tab'
        : 'Sections both ways ↔ Swipe, scroll or Tab';
    if (navigationHint.textContent !== message) navigationHint.textContent = message;
    if (navigation.getAttribute('aria-describedby') !== 'navigation-scroll-hint') {
      navigation.setAttribute('aria-describedby', 'navigation-scroll-hint');
    }
  };
  if (navigation && navigationHint) {
    navigation.addEventListener('scroll', updateNavigationHint, { passive: true });
    window.addEventListener?.('resize', updateNavigationHint);
    // The nav links' count badges grow after asynchronous catalog loads.
    // Observe links as well as the outer rail because only scrollWidth may grow.
    if (typeof window.ResizeObserver === 'function') {
      const observer = new window.ResizeObserver(updateNavigationHint);
      observer.observe(navigation);
      for (const child of navigation.children) observer.observe(child);
    }
    window.requestAnimationFrame(updateNavigationHint);
  }

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
  const filmState = { films: [], available: false };
  const publisherEditionState = { rows: [], available: false };
  const publisherIsbnState = { rows: [], available: false, limit: 12 };
  const publisherIsbnSha256 = '1170e8cb56b4ff3c5beab8d412fa5613b6e3b9d0ab7b5a18f80fe403c5bde3e8';
  const paramountState = { rows: [], available: false };
  const paramountSha256 = '40d968f1faa11bd888f2af838c6cc4075c1c89ba4b269cf08a2e33878e87e26b';
  const episodeSourceState = { rows: [], available: false };
  const episodeSourceSha256 = '38dfde3c3a1cfe38e41bf6740327b070f7846e2dc7c6149b74f88db7b85186f6';
  const episodeSourceBatches = new Map([
    ['PIC-FIRST5', ['proposals/research/pic/picard-s1-first5-guide-cards-20261103/records.json',
      '070dccdbda3b7a777e6f12201d725bd906610f4e1c5ee26e8c37c3a218c6829f', 'PIC', [1, 2, 3, 4, 5]]],
    ['PIC-LAST5', ['proposals/research/pic/picard-s1-last5-guide-cards-20261103/records.json',
      'fe962cc235ffc84f5cff7a970a940419cf9a21dce72cd5844cae76ce89f9a9cc', 'PIC', [6, 7, 8, 9, 10]]],
    ['SNW-FIRST5', ['proposals/research/snw/s3-publisher-first5-20261103/records.json',
      '89e816d651996405dce608fa3509b437178b0dcd635f2d8635962d0bd7acfe1c', 'SNW', [1, 2, 3, 4, 5]]],
    ['SNW-LAST5', ['proposals/research/snw/s3-publisher-last5-20261103/records.json',
      'b1daa95e849c61beb1011aabaebc06343589f29d0ec786e6359c07cb81137b2e', 'SNW', [6, 7, 8, 9, 10]]]
  ]);
  const episodeSourceTitles = new Map([
    ['pic-s1-e01-pplus-guide', 'Remembrance'],
    ['pic-s1-e02-pplus-guide', 'Maps and Legends'],
    ['pic-s1-e03-pplus-guide', 'The End is the Beginning'],
    ['pic-s1-e04-pplus-guide', 'Absolute Candor'],
    ['pic-s1-e05-pplus-guide', 'Stardust City Rag'],
    ['pic-s1-e06-pplus-guide', 'The Impossible Box'],
    ['pic-s1-e07-pplus-guide', 'Nepenthe'],
    ['pic-s1-e08-pplus-guide', 'Broken Pieces'],
    ['pic-s1-e09-pplus-guide', 'Et in Arcadia Ego, Part 1'],
    ['pic-s1-e10-pplus-guide', 'Et in Arcadia Ego, Part 2'],
    ['snw-s3-e01-pplus', 'Hegemony, Part II'],
    ['snw-s3-e02-pplus', 'Wedding Bell Blues'],
    ['snw-s3-e03-pplus', 'Shuttle to Kenfori'],
    ['snw-s3-e04-pplus', 'A Space Adventure Hour'],
    ['snw-s3-e05-pplus', 'Through the Lens of Time'],
    ['snw-s3-e06-pplus', 'The Sehlat Who Ate Its Tail'],
    ['snw-s3-e07-pplus', 'What is Starfleet?'],
    ['snw-s3-e08-pplus', 'Four-and-a-Half Vulcans'],
    ['snw-s3-e09-pplus', 'Terrarium'],
    ['snw-s3-e10-pplus', 'New Life and New Civilizations']
  ]);
  // Separate from source_row_sha256 (which binds private source fragments),
  // these *code-owned* SHA-256 values bind the complete PUBLIC row, including
  // utterance labels and tags. A forged JSON + updated whole-artifact digest
  // cannot silently rewrite a label into a fabricated publisher statement.
  const episodePublicRowPins = new Map([
    ['episode-publisher-card:pic-s1-e01-pplus-guide', '4b99c107d44ee2f3200a369043b126f16c6fe5918cd4f190dd9481cdf39fdbab'],
    ['episode-publisher-card:pic-s1-e02-pplus-guide', 'd802a1fa8521ecf95ab5f9a173b0365e32b001c96aabc63d74e2cf9ac224093e'],
    ['episode-publisher-card:pic-s1-e03-pplus-guide', '208935c3d66d135e46399eab0c6195df283d76266e0eb508944c7753a874d19d'],
    ['episode-publisher-card:pic-s1-e04-pplus-guide', '4a31d3c04bccb597a49118ab05a5d18e42241a4d2245ed65800a0d97883bc406'],
    ['episode-publisher-card:pic-s1-e05-pplus-guide', 'b283254a83dd7d4b8235644b067cdbf09599474dfd89d19e9f544ac1bf166a7e'],
    ['episode-publisher-card:pic-s1-e06-pplus-guide', 'f9e4cea60d2c89f14e5bdc7b4d33fbc2ed854127e1d76dce788f293f44a9b50b'],
    ['episode-publisher-card:pic-s1-e07-pplus-guide', '122b8e67b1c8f0142f8df5d6537c715479491a600c41de489f6758cd78d9e125'],
    ['episode-publisher-card:pic-s1-e08-pplus-guide', '4a1d5be16a99e6c5269be35c0bb1e61c2f2de52f4a0c613693e12f99d94eab07'],
    ['episode-publisher-card:pic-s1-e09-pplus-guide', 'dba360c488a15acd70e7ef70d841d9d4a095727c4676fcc901e7dddf6c01b7be'],
    ['episode-publisher-card:pic-s1-e10-pplus-guide', '3b2afe59ffc068f89a941e32909e7d4444f8e80e2de09ffb7bf359d2186b07bc'],
    ['episode-publisher-card:snw-s3-e01-pplus', 'df7ad399aac6456fefbbeb471ca9c5ab96d62741b7b0e85b312930f73917ea79'],
    ['episode-publisher-card:snw-s3-e02-pplus', 'ea475fbce4070ef97ddf350a0736647e11204b06c18490d814045250a3bfc6e5'],
    ['episode-publisher-card:snw-s3-e03-pplus', '265d5fe7f0dfa31987997dda84f32a87032e40e9c5b5da0c4ca5d405e381df6a'],
    ['episode-publisher-card:snw-s3-e04-pplus', 'c21fca17e8eff220f45fa5e2649743055f802e88adc575563358bd8f1d21dc50'],
    ['episode-publisher-card:snw-s3-e05-pplus', '3dc463d1d9194f414d289e9b30f0fc7fb8d2901725297b3cc7512a31758049ef'],
    ['episode-publisher-card:snw-s3-e06-pplus', 'f605ad0422a1106491bd88a56a55bddf962ef66bed95cf816113c6d26a73a450'],
    ['episode-publisher-card:snw-s3-e07-pplus', 'c2709ed5194476cdd3bef68fe2e0914af451c1e42d0e8a7f98da0d23edd5416a'],
    ['episode-publisher-card:snw-s3-e08-pplus', 'c59b77cdd4f56113d2208aebded6926ffb9eef695b476e45e5ae993a12e1069e'],
    ['episode-publisher-card:snw-s3-e09-pplus', 'c8fd93614a034f62db440074d6f6199c09049e8bbe05e1aaa165ade627405e7e'],
    ['episode-publisher-card:snw-s3-e10-pplus', '9ceb38c8d5a62fa2b6959c8105ba1d4bc8cb7b9d999c6dd45ec9868a0fa0de0b']
  ]);
  // Independent from the 1,214 multimedia directory and governed Work index.
  // The code-owned digest binds EVERY publisher-edition field and tag, not a
  // self-declared source hash in an untrusted JSON response.
  const publisherEditionIndexSHA256 = '0568db4c7313f3a3da4b3cd4a5d9e56430fe09e64ed0687d8d9690d782df67d5';
  const publisherEditionIsbns = new Set(['9780743419987', '9780743546591', '9780743546744']);

  // Source-local discoveries are not plot reads. A separate reviewed display
  // artifact may eventually supply ORIGINAL publisher-description paraphrases.
  // It cannot self-attest approval: an independently reviewed immutable tuple
  // must also be pinned here in a separately reviewed code change.
  const reviewedSynopsisReceipts = new Map([
    ["directory:literature:prh-autobiography-janeway", Object.freeze({"title":"The Autobiography of Kathryn Janeway","source_locator":"https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/","overview_evidence_locator":"https://www.penguinrandomhouse.com/books/646637/the-autobiography-of-kathryn-janeway-by-una-mccormack/","source_group":"distributor:penguinrandomhouse.com:titan-books","source_input":"proposals/librarian/prh-star-trek-autobiographies-20261103/records.json","source_context":"Una McCormack · distributor listing","directory_alias_row_id":null,"directory_alias_context":null,"overview_text":"The distributor presents Janeway recounting her Starfleet command, Voyager's long journey through the Delta Quadrant, her mixed Starfleet–Maquis crew, and encounters with the Borg. The promotional outline also includes her later advancement to vice admiral.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/lit-ring-memoir-publisher-20261103/observations.json","research_observation_sha256":"9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["directory:literature:prh-autobiography-kirk", Object.freeze({"title":"The Autobiography of James T. Kirk","source_locator":"https://www.penguinrandomhouse.com/books/250795/the-autobiography-of-james-t-kirk-by-david-a-goodman/","overview_evidence_locator":"https://www.penguinrandomhouse.com/books/250795/the-autobiography-of-james-t-kirk-by-david-a-goodman/","source_group":"distributor:penguinrandomhouse.com:titan-books","source_input":"proposals/librarian/prh-star-trek-autobiographies-20261103/records.json","source_context":"David A. Goodman · distributor listing","directory_alias_row_id":null,"directory_alias_context":null,"overview_text":"Presented as a fictional first-person account, the book surveys James T. Kirk's life and Starfleet career. The distributor describes an illustrated, in-universe memoir of the Enterprise captain, framed as his own recollections.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/lit-ring-memoir-publisher-20261103/observations.json","research_observation_sha256":"9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["directory:literature:prh-autobiography-picard", Object.freeze({"title":"The Autobiography of Jean-Luc Picard","source_locator":"https://www.penguinrandomhouse.com/books/555327/the-autobiography-of-jean-luc-picard-by-david-a-goodman/","overview_evidence_locator":"https://www.penguinrandomhouse.com/books/555327/the-autobiography-of-jean-luc-picard-by-david-a-goodman/","source_group":"distributor:penguinrandomhouse.com:titan-books","source_input":"proposals/librarian/prh-star-trek-autobiographies-20261103/records.json","source_context":"David A. Goodman · distributor listing","directory_alias_row_id":null,"directory_alias_context":null,"overview_text":"The distributor frames this fictional memoir around Picard's Starfleet life, including personal setbacks, Cardassian captivity, Borg assimilation, and command of the Enterprise. These events are publisher-described subjects, not independently verified book scenes.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/lit-ring-memoir-publisher-20261103/observations.json","research_observation_sha256":"9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["directory:literature:prh-autobiography-sisko", Object.freeze({"title":"The Autobiography of Benjamin Sisko","source_locator":"https://www.penguinrandomhouse.com/books/737400/the-autobiography-of-benjamin-sisko-by-derek-tyler-attico/","overview_evidence_locator":"https://www.penguinrandomhouse.com/books/737400/the-autobiography-of-benjamin-sisko-by-derek-tyler-attico/","source_group":"distributor:penguinrandomhouse.com:titan-books","source_input":"proposals/librarian/prh-star-trek-autobiographies-20261103/records.json","source_context":"Derek Tyler Attico · distributor listing","directory_alias_row_id":null,"directory_alias_context":null,"overview_text":"The distributor presents Sisko's life as a Starfleet officer, father, Bajoran emissary, and wartime leader. Its description spans Defiant development, the Dominion War, and his relationships with allies and adversaries aboard Deep Space Nine.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/lit-ring-memoir-publisher-20261103/observations.json","research_observation_sha256":"9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["directory:literature:prh-autobiography-spock", Object.freeze({"title":"The Autobiography of Mr. Spock","source_locator":"https://www.penguinrandomhouse.com/books/577045/the-autobiography-of-mr-spock-by-una-mccormack/","overview_evidence_locator":"https://www.penguinrandomhouse.com/books/577045/the-autobiography-of-mr-spock-by-una-mccormack/","source_group":"distributor:penguinrandomhouse.com:titan-books","source_input":"proposals/librarian/prh-star-trek-autobiographies-20261103/records.json","source_context":"Una McCormack · distributor listing","directory_alias_row_id":null,"directory_alias_context":null,"overview_text":"The distributor outlines Spock's fictional memoir from Vulcan childhood with Michael Burnham through Starfleet Academy and Enterprise service under Pike and Kirk. It also describes later diplomatic work and a concealed mission to Romulus.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/lit-ring-memoir-publisher-20261103/observations.json","research_observation_sha256":"9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["directory:literature:proposed-lit-discovery-enterprise-war", Object.freeze({"title":"Star Trek: Discovery: The Enterprise War","source_locator":"https://www.simonandschuster.com/books/Star-Trek-Discovery-The-Enterprise-War/John-Jackson-Miller/Star-Trek-Discovery/9781982113315","overview_evidence_locator":"https://www.simonandschuster.com/books/Star-Trek-Discovery-The-Enterprise-War/John-Jackson-Miller/Star-Trek-Discovery/9781982113322","source_group":"publisher:simonandschuster.com","source_input":"proposals/librarian/simon-schuster-three-novels-20261103/records.json","source_context":"John Jackson Miller · three publisher-format observations","directory_alias_row_id":null,"directory_alias_context":null,"overview_text":"The publisher places Pike's Enterprise in a dangerous nebula during the Federation–Klingon conflict. With the crew separated and command strained, the ship's survival depends partly on a mystery confronting Spock.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/lit-three-publisher-editions-20261103/observations.json","research_observation_sha256":"908070be21a187c305b56f7aec880f30eb69cb2d12911f07663a4d2c3c616826","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["directory:literature:proposed-lit-picard-second-self", Object.freeze({"title":"Star Trek: Picard: Second Self","source_locator":"https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781982194833","overview_evidence_locator":"https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781982194840","source_group":"publisher:simonandschuster.com","source_input":"proposals/librarian/simon-schuster-three-novels-20261103/records.json","source_context":"Una McCormack · three publisher-format observations","directory_alias_row_id":null,"directory_alias_context":null,"overview_text":"The publisher describes Raffi Musiker being drawn away from a possible quieter career by a Romulan contact seeking help. Elnor and Picard become involved in an investigation entangled with unresolved choices from Raffi's past.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/lit-three-publisher-editions-20261103/observations.json","research_observation_sha256":"908070be21a187c305b56f7aec880f30eb69cb2d12911f07663a4d2c3c616826","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["directory:literature:proposed-lit-snw-high-country", Object.freeze({"title":"Star Trek: Strange New Worlds: The High Country","source_locator":"https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-The-High-Country/John-Jackson-Miller/Star-Trek-Strange-New-Worlds/9781668002391","overview_evidence_locator":"https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-The-High-Country/John-Jackson-Miller/Star-Trek-Strange-New-Worlds/9781668002407","source_group":"publisher:simonandschuster.com","source_input":"proposals/librarian/simon-schuster-three-novels-20261103/records.json","source_context":"John Jackson Miller · three publisher-format observations","directory_alias_row_id":null,"directory_alias_context":null,"overview_text":"The publisher describes a shuttle failure scattering Pike's team across a world where familiar Starfleet technology stops working. Crew members face separate survival problems while Pike tries to reunite them and prevent a broader disaster.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/lit-three-publisher-editions-20261103/observations.json","research_observation_sha256":"908070be21a187c305b56f7aec880f30eb69cb2d12911f07663a4d2c3c616826","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["directory:literature:proposed-lit-snw-ring-of-fire", Object.freeze({"title":"Star Trek: Strange New Worlds: Ring of Fire","source_locator":"https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/9781668095898","overview_evidence_locator":"https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-Ring-of-Fire/David-Mack/Star-Trek-Strange-New-Worlds/9781668095898","source_group":"publisher:simonandschuster.com","source_input":"proposals/librarian/ring-of-fire-editions-20261102/records.json","source_context":"David Mack · 4 publisher editions","directory_alias_row_id":null,"directory_alias_context":null,"overview_text":"The publisher sends Pike and the Enterprise to a research station near a black hole after sabotage threatens a secret mission. An earlier tragedy involving Pike and concealed information from the station director complicate the crew's effort to prevent another disaster.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/lit-ring-memoir-publisher-20261103/observations.json","research_observation_sha256":"9fb292b443ddaa2f332568981e4a6629f43bfa7b31fc7d58687be90d432a9514","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-2009", Object.freeze({"title":"Star Trek (2009)","source_locator":"https://www.startrek.com/movies/star-trek-2009","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-2009","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-2009","directory_alias_context":"Star Trek films","overview_text":"A young Kirk struggles with expectations tied to his father's legacy while a future-displaced Romulan directs his grief and anger against the Federation.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-beyond", Object.freeze({"title":"Star Trek Beyond","source_locator":"https://www.startrek.com/movies/star-trek-beyond","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-beyond","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-beyond","directory_alias_context":"Star Trek films","overview_text":"During an extended mission into unexplored space, the Enterprise encounters a new adversary who tests both the crew and the Federation principles they represent.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-final-frontier", Object.freeze({"title":"Star Trek V: The Final Frontier","source_locator":"https://www.startrek.com/movies/star-trek-v-the-final-frontier","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-v-the-final-frontier","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-final-frontier","directory_alias_context":"Star Trek films","overview_text":"Sybok, Spock's half-brother, takes control of the Enterprise and sets a course toward the galactic center in pursuit of a being he regards as divine.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-first-contact", Object.freeze({"title":"Star Trek: First Contact","source_locator":"https://www.startrek.com/movies/star-trek-viii-first-contact","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-viii-first-contact","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-first-contact","directory_alias_context":"Star Trek films","overview_text":"The Borg travel into Earth's past, and Picard sends the Enterprise after them to protect a historic first warp-spaceflight.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-generations", Object.freeze({"title":"Star Trek Generations","source_locator":"https://www.startrek.com/movies/star-trek-generations","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-generations","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-generations","directory_alias_context":"Star Trek films","overview_text":"The studio synopsis brings Captains Picard and Kirk together through a time-defying phenomenon and has them combine their efforts against a planetary threat.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-insurrection", Object.freeze({"title":"Star Trek: Insurrection","source_locator":"https://www.startrek.com/movies/star-trek-ix-insurrection","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-ix-insurrection","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-insurrection","directory_alias_context":"Star Trek films","overview_text":"Picard challenges a Starfleet plan to move a planet's inhabitants so others can exploit the world's unusual natural properties.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-into-darkness", Object.freeze({"title":"Star Trek Into Darkness","source_locator":"https://www.startrek.com/movies/star-trek-into-darkness","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-into-darkness","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-into-darkness","directory_alias_context":"Star Trek films","overview_text":"An attack deep inside Federation territory sends Kirk's crew across hostile space in pursuit of a dangerous opponent with extraordinary abilities.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-motion-picture", Object.freeze({"title":"Star Trek: The Motion Picture","source_locator":"https://www.startrek.com/movies/star-trek-i-the-motion-picture","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-i-the-motion-picture","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-motion-picture","directory_alias_context":"Star Trek films","overview_text":"The publisher describes a mysterious threat approaching Earth, bringing Kirk and a newly refitted Enterprise back into service for an urgent defense mission.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-nemesis", Object.freeze({"title":"Star Trek Nemesis","source_locator":"https://www.startrek.com/movies/star-trek-nemesis","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-nemesis","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-nemesis","directory_alias_context":"Star Trek films","overview_text":"An engineered duplicate of Picard pursues vengeance and endangers the Federation using a weapon capable of widespread destruction.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-search-for-spock", Object.freeze({"title":"Star Trek III: The Search for Spock","source_locator":"https://www.startrek.com/movies/star-trek-iii-the-search-for-spock","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-iii-the-search-for-spock","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-search-for-spock","directory_alias_context":"Star Trek films","overview_text":"After Spock's apparent death, the studio's description places evidence of his survival on the Genesis planet, where his body had been taken.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-section-31", Object.freeze({"title":"Star Trek: Section 31","source_locator":"https://www.startrek.com/news/star-trek-section-31-premieres-january-24","overview_evidence_locator":"https://www.startrek.com/news/star-trek-section-31-premieres-january-24","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"STREAMING_ORIGINAL_FILM","directory_alias_row_id":"directory:film:film-section-31","directory_alias_context":"Star Trek films","overview_text":"The studio announcement describes Philippa Georgiou joining a covert Starfleet organization tasked with defending the Federation while she confronts the consequences of her past.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-undiscovered-country", Object.freeze({"title":"Star Trek VI: The Undiscovered Country","source_locator":"https://www.startrek.com/movies/star-trek-vi-the-undiscovered-country","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-vi-the-undiscovered-country","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-undiscovered-country","directory_alias_context":"Star Trek films","overview_text":"A catastrophe at a key Klingon energy facility makes peace negotiations possible. Kirk's crew escorts the Klingon leader toward talks while factions on both sides try to prevent reconciliation.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-voyage-home", Object.freeze({"title":"Star Trek IV: The Voyage Home","source_locator":"https://www.startrek.com/movies/star-trek-iv-the-voyage-home","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-iv-the-voyage-home","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-voyage-home","directory_alias_context":"Star Trek films","overview_text":"With Earth imperiled in their own era, the Enterprise crew travels to the 1980s aboard a Klingon vessel to bring back whales that may avert disaster.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
    ["film:film-wrath-of-khan", Object.freeze({"title":"Star Trek II: The Wrath of Khan","source_locator":"https://www.startrek.com/movies/star-trek-ii-the-wrath-of-khan","overview_evidence_locator":"https://www.startrek.com/movies/star-trek-ii-the-wrath-of-khan","source_group":"publisher:startrek.com","source_input":"explorer/film-catalog.json","source_context":"FEATURE_FILM","directory_alias_row_id":"directory:film:film-wrath-of-khan","directory_alias_context":"Star Trek films","overview_text":"A former exile with extraordinary engineered abilities seeks revenge against Kirk, forcing the admiral to face the consequences of an earlier encounter.","source_snapshot_date":"2026-11-03","research_observation_path":"proposals/research/films/publisher-synopses-20261103/observations.json","research_observation_sha256":"e128e74c474bf696947e12c159c1bda32cc07ded98df82faf9d89c347d88b378","raw_webpage_sha256":null,"editorial_receipt_sha256":"564569c700cbb235250198c0abccf5e16f806525bb9fd22251236c97037345e0"})],
  ]);
  const synopsisState = { entries: new Map() };
  const synopsisMedia = new Set(['EPISODE', 'FILM', 'LITERATURE', 'SHORT_FORM', 'AUDIO']);
  const publisherOverviewMedia = new Set(['EPISODE', 'FILM', 'LITERATURE', 'SHORT_FORM']);
  // A separate immutable publication artifact reviewed against the exact
  // accepted Short/Very Short publisher descriptions. This SHA-256 pins all
  // fourteen tuples and excludes the fifth Very Short Trek's slogan-only row.
  const reviewedShortSynopsisSHA256 = '47bdfabdab57f7b2f8430b0402d9cc0b9b3a872a8f704095164484159f274996';
  const reviewedShortSynopsisIds = new Set([
    ...Array.from({ length: 10 }, (_, i) => `directory:short:short-treks-${String(i + 1).padStart(2, '0')}`),
    'directory:short:very-short-treks-01', 'directory:short:very-short-treks-02',
    'directory:short:very-short-treks-03', 'directory:short:very-short-treks-05'
  ]);

  function appendSynopsis(container, medium, key) {
    if (!synopsisMedia.has(medium)) return;
    const block = el('section', 'synopsis-panel');
    block.setAttribute('aria-label', 'Synopsis and verification status');
    const release = synopsisState.entries.get(key);
    if (release) {
      block.append(el('strong', 'synopsis-label', 'Publisher-description-based overview'));
      block.append(el('p', 'synopsis-copy', release.overview_text));
      block.append(el('small', 'synopsis-scope', `Original paraphrase of publisher description observed ${release.source_snapshot_date} (rendered-page notes; raw webpage not archived). Not a full-work close read.`));
      const publisherLink = el('a', 'synopsis-evidence-link', 'Read publisher description source');
      publisherLink.href = release.overview_evidence_locator;
      publisherLink.target = '_blank';
      publisherLink.rel = 'noopener noreferrer';
      block.append(publisherLink);
    } else {
      block.append(el('strong', 'synopsis-label', 'Synopsis'));
      block.append(el('p', 'synopsis-pending', 'Synopsis pending source verification'));
    }
    container.append(block);
  }

  function acceptSynopsisCatalog(data, shortAppendix = false) {
    const exactKeys = (item, keys) => item && typeof item === 'object' && !Array.isArray(item) &&
      Object.keys(item).length === keys.length && keys.every((key) => Object.hasOwn(item, key));
    const rootKeys = ['schema_version', 'data_status', 'coverage_effect', 'admission_effect', 'synopsis_count', 'synopses'];
    const entryKeys = ['row_id', 'title', 'medium', 'source_group', 'source_input', 'source_context',
      'source_locator', 'overview_evidence_locator', 'overview_text', 'overview_basis', 'source_snapshot_date',
      'research_observation_path', 'research_observation_sha256', 'raw_webpage_sha256',
      'editorial_receipt_sha256', 'directory_alias_row_id', 'directory_alias_context',
      'admission_effect', 'coverage_effect'];
    if (!exactKeys(data, rootKeys) || data.schema_version !== '1.0.0' ||
        data.data_status !== 'EDITORIALLY_REVIEWED_DISPLAY_ONLY' ||
        data.coverage_effect !== 'NONE' || data.admission_effect !== 'NONE' ||
        !Array.isArray(data.synopses) || !Number.isSafeInteger(data.synopsis_count) ||
        data.synopsis_count !== data.synopses.length || data.synopses.length < 1 ||
        data.synopses.length > 5000) {
      throw new Error('Synopsis release envelope is not an approved display artifact.');
    }
    const sources = new Map();
    for (const row of directoryState.rows) sources.set(artworkKey(row), row);
    for (const row of filmState.films) sources.set(artworkKey(row), {
      ...row, medium: 'FILM', source_input: 'explorer/film-catalog.json', context: row.work_type
    });
    const entries = shortAppendix ? new Map(synopsisState.entries) : new Map();
    for (const item of data.synopses) {
      const source = sources.get(item?.row_id);
      // Short appendix bytes are first cryptographically bound to the exact
      // separately reviewed 14-row sidecar below. They cannot self-assert a
      // new row or change prose by supplying their own review hash.
      const pin = shortAppendix
        ? (reviewedShortSynopsisIds.has(item?.row_id) ? item : null)
        : reviewedSynopsisReceipts.get(item?.row_id);
      const validDate = /^\d{4}-\d{2}-\d{2}$/.test(item?.source_snapshot_date || '') &&
        !Number.isNaN(Date.parse(`${item.source_snapshot_date}T00:00:00Z`)) &&
        new Date(`${item.source_snapshot_date}T00:00:00Z`).toISOString().slice(0, 10) === item.source_snapshot_date;
      const publisherSource = source && /^(?:publisher:|distributor:)/.test(source.source_group) &&
        typeof source.source_locator === 'string' &&
        /^https:\/\/www\.(?:startrek\.com|paramountplus\.com|simonandschuster\.com|penguinrandomhouse\.com)\//.test(source.source_locator);
      let evidenceSamePublisher = false;
      try {
        const sourceUrl = new URL(item.overview_evidence_locator);
        const rowUrl = new URL(source?.source_locator);
        const sameWorkEdition = rowUrl.hostname === 'www.simonandschuster.com' &&
          rowUrl.pathname.replace(/\/97[89]\d{10}$/, '') === sourceUrl.pathname.replace(/\/97[89]\d{10}$/, '') &&
          /\/97[89]\d{10}$/.test(rowUrl.pathname) && /\/97[89]\d{10}$/.test(sourceUrl.pathname);
        const reviewedVeryShortVideo = shortAppendix && item.medium === 'SHORT_FORM' &&
          rowUrl.hostname === 'www.startrek.com' && sourceUrl.hostname === 'www.startrek.com' &&
          rowUrl.pathname === '/en-un/news/star-trek-very-short-treks-announce' &&
          /^\/videos\/very-short-treks-[a-z0-9-]+$/.test(sourceUrl.pathname);
        evidenceSamePublisher = rowUrl.hostname === sourceUrl.hostname && rowUrl.protocol === 'https:' &&
          sourceUrl.protocol === 'https:' && !sourceUrl.search && !sourceUrl.hash &&
          !sourceUrl.username && !sourceUrl.password && !sourceUrl.port &&
          (item.overview_evidence_locator === source.source_locator || sameWorkEdition || reviewedVeryShortVideo);
      } catch (_) { /* invalid publisher evidence link fails closed */ }
      const alias = item.directory_alias_row_id === null ? null : sources.get(item.directory_alias_row_id);
      const validAlias = item.medium === 'FILM'
        ? (item.directory_alias_row_id === null && item.directory_alias_context === null) ||
          (alias && item.directory_alias_row_id === `directory:${alias.row_id}` &&
            alias.medium === 'FILM' && alias.title === item.title &&
            alias.source_group === item.source_group && alias.source_input === item.source_input &&
            alias.source_locator === item.source_locator &&
            alias.context === item.directory_alias_context && !entries.has(item.directory_alias_row_id))
        : item.directory_alias_row_id === null && item.directory_alias_context === null;
      if (!exactKeys(item, entryKeys) || !source || entries.has(item.row_id) ||
          !publisherOverviewMedia.has(item.medium) ||
          (shortAppendix ? item.medium !== 'SHORT_FORM' : item.medium === 'SHORT_FORM') ||
          !publisherSource || !evidenceSamePublisher ||
          !validAlias || source.medium !== item.medium ||
          item.title !== source.title || item.source_group !== source.source_group ||
          item.source_input !== source.source_input || item.source_context !== source.context ||
          typeof item.source_locator !== 'string' ||
          item.source_locator !== source.source_locator ||
          item.overview_basis !== 'PUBLISHER_DESCRIPTION_PARAPHRASE' ||
          typeof item.overview_text !== 'string' || item.overview_text !== item.overview_text.trim() ||
          item.overview_text.length < 40 || item.overview_text.length > 700 ||
          /[\p{C}<>]/u.test(item.overview_text) || !validDate ||
          !/^proposals\/research\/[a-z0-9/_-]+\/observations\.json$/.test(item.research_observation_path || '') ||
          !/^[a-f0-9]{64}$/.test(item.research_observation_sha256 || '') ||
          item.raw_webpage_sha256 !== null ||
          !/^[a-f0-9]{64}$/.test(item.editorial_receipt_sha256 || '') ||
          item.coverage_effect !== 'NONE' || item.admission_effect !== 'NONE' ||
          !pin || pin.title !== item.title || pin.source_locator !== item.source_locator ||
          pin.source_group !== item.source_group || pin.source_input !== item.source_input ||
          pin.source_context !== item.source_context ||
          pin.overview_evidence_locator !== item.overview_evidence_locator ||
          pin.directory_alias_row_id !== item.directory_alias_row_id ||
          pin.directory_alias_context !== item.directory_alias_context ||
          pin.overview_text !== item.overview_text ||
          pin.source_snapshot_date !== item.source_snapshot_date ||
          pin.research_observation_path !== item.research_observation_path ||
          pin.research_observation_sha256 !== item.research_observation_sha256 ||
          pin.raw_webpage_sha256 !== null ||
          pin.editorial_receipt_sha256 !== item.editorial_receipt_sha256) {
        throw new Error('Synopsis has no independently pinned source/edition/text/review receipt.');
      }
      entries.set(item.row_id, item);
      if (item.directory_alias_row_id !== null) entries.set(item.directory_alias_row_id, item);
    }
    if (shortAppendix && (data.synopsis_count !== 14 ||
        reviewedShortSynopsisIds.size !== 14 ||
        ![...reviewedShortSynopsisIds].every((id) => entries.has(id)) ||
        entries.has('directory:short:very-short-treks-04'))) {
      throw new Error('Short Trek synopsis appendix is missing reviewed rows or invents a premise.');
    }
    synopsisState.entries = entries;
    renderDirectory();
    renderFilms();
  }

  async function loadSynopsisCatalog() {
    try {
      const response = await fetch('./synopsis-catalog.json', { cache: 'no-store' });
      if (response.status === 404) return;
      if (!response.ok) throw new Error(`Synopsis display release returned HTTP ${response.status}.`);
      acceptSynopsisCatalog(await response.json());
    } catch (_) {
      // Malformed, unreviewed or unpublished synopsis content cannot influence
      // the visible source-local observations or silently invent plot claims.
      synopsisState.entries.clear();
      renderDirectory();
      renderFilms();
    }
  }

  async function loadShortSynopsisCatalog() {
    try {
      const response = await fetch('./short-synopsis-catalog.json', { cache: 'no-store' });
      if (!response.ok || !globalThis.crypto?.subtle || typeof TextDecoder !== 'function') return;
      const bytes = await response.arrayBuffer();
      if (bytes.byteLength < 1000 || bytes.byteLength > 75000) return;
      const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const hex = Array.from(new Uint8Array(digest), (x) => x.toString(16).padStart(2, '0')).join('');
      if (hex !== reviewedShortSynopsisSHA256) return;
      acceptSynopsisCatalog(JSON.parse(new TextDecoder().decode(bytes)), true);
    } catch (_) {
      // The separately reviewed 23 film/literary descriptions remain intact
      // even if an optional Short Trek synopsis appendix is rejected.
    }
  }

  // Artwork is a separate, explicitly rights-reviewed release artifact. The
  // episode/film/source-local JSON schemas must not grow unaudited image URLs.
  // No publisher image URL is inferred from metadata. Licensed local images
  // and the explicitly documented Open Library Covers API are separate,
  // reviewed display routes; remote API thumbnails are opt-in, never mirrored.
  const artworkState = { entries: new Map(), available: false, enabled: false };
  // No Open Library ISBN-to-cover crosswalk has yet been independently
  // admitted for a public directory row. A sidecar cannot self-certify one:
  // pin reviewed row/locator/ISBN/cover/hash tuples here only after a separate
  // source-relative custody and release review. Empty means fail closed.
  const reviewedOpenLibraryEditionReceipts = new Map();
  const artworkToggle = byId('artwork-toggle');
  const artworkKinds = { EPISODE: 'Episode', FILM: 'Film', LITERATURE: 'Book', SHORT_FORM: 'Short', AUDIO: 'Audio' };

  function artworkKey(row) {
    return row && row.row_id ? `directory:${row.row_id}` : `film:${row.id}`;
  }

  function makeArtworkSlot(medium, key) {
    const label = artworkKinds[medium] || 'Media';
    const frame = el('div', `artwork-slot artwork-${normalize(medium)}`);
    const title = el('span', 'artwork-kind', label);
    const missing = el('span', 'artwork-missing', 'Artwork not sourced · original abstract');
    frame.append(title, missing);
    const source = artworkState.enabled ? artworkState.entries.get(key) : null;
    if (source) {
      const img = el('img');
      const remoteLibrary = source.provider === 'OPEN_LIBRARY_COVERS_API';
      img.src = remoteLibrary
        ? `https://covers.openlibrary.org/b/id/${source.cover_id}-S.jpg?default=false`
        : source.image_path;
      img.alt = source.alt_text;
      img.width = 76;
      img.height = 105;
      img.loading = 'lazy';
      img.decoding = 'async';
      img.referrerPolicy = 'no-referrer';
      img.addEventListener('error', () => {
        frame.replaceChildren(title, el('span', 'artwork-missing', 'Image unavailable'));
      });
      frame.append(img);
      if (remoteLibrary) {
        const credit = el('a', 'artwork-credit', 'Open Library');
        credit.href = source.attribution_url;
        credit.target = '_blank';
        credit.rel = 'noopener noreferrer';
        frame.append(credit);
      }
    }
    return frame;
  }

  // ISBN-specific *edition* discovery, not another count of distinct Works or
  // a public release channel for held publisher-description paraphrases.
  function setPublisherEditionAvailability(available, message) {
    publisherEditionState.available = available;
    if (!available) publisherEditionState.rows = [];
    byId('publisher-edition-nav-count').textContent = available ? String(publisherEditionState.rows.length) : '—';
    byId('publisher-edition-state').textContent = message;
    renderPublisherEditionLeads();
  }

  function renderPublisherEditionLeads() {
    const holder = byId('publisher-edition-list');
    const empty = byId('publisher-edition-empty');
    holder.replaceChildren();
    empty.hidden = true;
    if (!publisherEditionState.available) {
      byId('publisher-edition-summary').textContent = 'Publisher-edition index unavailable; no candidate records are displayed.';
      return;
    }
    const query = normalize(byId('publisher-edition-query').value.trim());
    const tag = byId('publisher-edition-tag').value;
    const terms = query.length <= 240 ? query.split(/\s+/).filter(Boolean) : ['QUERY_TOO_LONG'];
    const rows = publisherEditionState.rows.filter((row) => {
      if (tag !== 'all' && !row.query_tags.includes(tag)) return false;
      const corpus = normalize(`${row.search_text} ${row.title} ${row.creator} ${row.isbn13} ${row.query_tags.join(' ')}`);
      return terms.every((term) => corpus.includes(term));
    });
    byId('publisher-edition-summary').textContent = `${rows.length} of ${publisherEditionState.rows.length} source-local publisher edition candidates match · Excluded from the 1,214-row universe directory and admitted Works.`;
    empty.hidden = rows.length !== 0;
    const fragment = document.createDocumentFragment();
    for (const row of rows) {
      const article = el('article', 'card publisher-edition-card');
      const art = el('div', 'artwork-slot artwork-literature');
      art.setAttribute('role', 'img');
      art.setAttribute('aria-label', 'Original abstract literature placeholder, not the book cover');
      art.append(el('span', 'artwork-kind', 'Literature'), el('span', 'artwork-missing', 'Original abstract · cover not sourced'));
      const copy = el('div', 'publisher-edition-copy');
      copy.append(el('span', 'kicker', 'Publisher edition candidate · not an admitted Work'));
      copy.append(el('h3', '', row.title));
      copy.append(el('p', '', `${row.creator} · ${humanize(row.edition_format)} · ISBN ${row.isbn13}`));
      copy.append(el('p', 'edition-scope', `${row.publisher_series} · ${row.publisher_imprint} · ${row.publisher_publication_date} · ${row.publisher_extent}`));
      copy.append(el('p', 'edition-status', 'Synopsis held · no full-book reading or identity reconciliation'));
      copy.append(el('p', 'edition-scope', 'Source-local publisher description tags are discovery hints, not verified plot facts. Private archive format equivalence is unresolved.'));
      const link = el('a', 'edition-source', 'Inspect publisher edition source');
      link.href = row.source_locator;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      copy.append(link);
      const disclosure = el('details', 'edition-tags');
      disclosure.append(el('summary', '', 'Inspect source-relative search tags'));
      const list = el('ul', 'edition-tag-list');
      for (const claim of row.query_tags) list.append(el('li', '', claim));
      disclosure.append(list);
      article.append(art, copy, disclosure);
      fragment.append(article);
    }
    holder.append(fragment);
  }

  function acceptPublisherEditionIndex(data) {
    const rootFields = ['admission_effect', 'artwork_release_effect', 'coverage_effect', 'data_status',
      'denominator_effect', 'identity_scope', 'public_synopsis_effect', 'row_count', 'rows',
      'schema_version', 'source_accepted_commit', 'source_input', 'source_input_sha256'];
    const fields = ['admission_effect', 'coverage_effect', 'creator', 'edition_format', 'identity_scope',
      'isbn13', 'private_edition_equivalence', 'promotional_claim_scope', 'publisher_extent',
      'publisher_imprint', 'publisher_publication_date', 'publisher_series', 'query_tags',
      'row_id', 'search_text', 'source_group', 'source_input', 'source_locator', 'synopsis_status', 'title'];
    const hasExactFields = (item, keys) => item && typeof item === 'object' && !Array.isArray(item) &&
      Object.keys(item).length === keys.length && keys.every((key) => Object.hasOwn(item, key));
    if (!hasExactFields(data, rootFields) || data.schema_version !== '1.0.0' ||
        data.data_status !== 'PUBLISHER_EDITION_LEADS_SEARCH_OVERLAY_ONLY' ||
        data.row_count !== 3 || !Array.isArray(data.rows) || data.rows.length !== 3 ||
        !/^[a-f0-9]{64}$/.test(data.source_input_sha256) ||
        !/^[a-f0-9]{40}$/.test(data.source_accepted_commit) ||
        ['admission_effect', 'coverage_effect', 'denominator_effect', 'public_synopsis_effect', 'artwork_release_effect']
          .some((key) => data[key] !== 'NONE') ||
        data.identity_scope !== 'SOURCE_LOCAL_EDITION_NOT_RECONCILED') {
      throw new Error('Publisher edition index envelope violates source-local boundaries.');
    }
    const ids = new Set();
    for (const row of data.rows) {
      let source;
      try { source = new URL(row?.source_locator); } catch (_) { throw new Error('Invalid edition source URL.'); }
      if (!hasExactFields(row, fields) || !publisherEditionIsbns.has(row.isbn13) ||
          row.row_id !== `publisher-edition:${row.isbn13}` || ids.has(row.row_id) ||
          row.identity_scope !== 'EDITION_CANDIDATE_SOURCE_LOCAL' ||
          row.coverage_effect !== 'NONE' || row.admission_effect !== 'NONE' ||
          row.private_edition_equivalence !== 'UNVERIFIED' ||
          row.synopsis_status !== 'UNREVIEWED_PARAPHRASE_HELD_NOT_PUBLIC' ||
          row.promotional_claim_scope !== 'PUBLISHER_COPY_TAGS_NOT_FICTIONAL_TRUTH' ||
          row.source_group !== 'publisher:simonandschuster.com' ||
          row.source_input !== data.source_input ||
          source.protocol !== 'https:' || source.hostname !== 'www.simonandschuster.com' ||
          source.username || source.password || source.search || source.hash ||
          !source.pathname.startsWith('/books/') || !source.pathname.endsWith('/' + row.isbn13) ||
          !Array.isArray(row.query_tags) || row.query_tags.length !== 8 ||
          row.query_tags.some((tag) => typeof tag !== 'string' || tag.length > 145) ||
          !['EBOOK', 'ADAPTED_AUDIO_DOWNLOAD', 'ABRIDGED_AUDIO_DOWNLOAD'].includes(row.edition_format)) {
        throw new Error('Publisher edition row failed source, scope or identity validation.');
      }
      ids.add(row.row_id);
    }
    publisherEditionState.rows = data.rows;
    const tagSelect = byId('publisher-edition-tag');
    tagSelect.replaceChildren(new Option('All tags', 'all'));
    for (const tag of [...new Set(data.rows.flatMap((row) => row.query_tags))].sort()) {
      tagSelect.add(new Option(tag, tag));
    }
    setPublisherEditionAvailability(true, 'Three ISBN-specific publisher edition leads loaded · metadata only; no edition equivalence, full-book analysis, or public synopsis release.');
  }

  async function loadPublisherEditionIndex() {
    try {
      const response = await fetch('./lit-publisher-edition-leads.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Publisher edition sidecar unavailable.');
      if (!globalThis.crypto?.subtle || typeof TextDecoder !== 'function') throw new Error('SHA-256 verification unavailable.');
      const bytes = await response.arrayBuffer();
      if (bytes.byteLength > 65_536) throw new Error('Publisher edition sidecar exceeds 64 KiB.');
      const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const hex = Array.from(new Uint8Array(digest), (n) => n.toString(16).padStart(2, '0')).join('');
      if (hex !== publisherEditionIndexSHA256) throw new Error('Publisher edition data differs from the accepted source-derived digest.');
      acceptPublisherEditionIndex(JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)));
    } catch (error) {
      setPublisherEditionAvailability(false, `Publisher edition leads withheld: ${error.message || 'Verify accepted source index.'}`);
    }
  }

  // Public first-party publisher product metadata only. These 39 source-local
  // ISBN records are disjoint from the 3 edition candidates and 1,214-row
  // multimedia directory; an OPF-local ref is NOT proof of a private ebook.
  const isbnCrosscheckLabels = Object.freeze({
    ISBN_IDENTIFIER_AGREEMENT_SOURCE_LOCAL: 'Publisher ISBN identifier agreement · private edition unverified',
    HELD_ISBN_FORMAT_DISCREPANCY: 'HELD: publisher ISBN / format discrepancy',
    HELD_CREATOR_RENDERING_DISCREPANCY: 'HELD: creator rendering discrepancy',
    HELD_TITLE_SPELLING_DISCREPANCY: 'HELD: title spelling discrepancy',
    HELD_PUBLISHER_DATE_DISCREPANCY: 'HELD: publisher/source-local date discrepancy'
  });

  function setPublisherIsbnAvailability(available, message) {
    publisherIsbnState.available = available;
    if (!available) publisherIsbnState.rows = [];
    byId('publisher-isbn-nav-count').textContent = available ? String(publisherIsbnState.rows.length) : '—';
    byId('publisher-isbn-state').textContent = message;
    byId('publisher-isbn-download').hidden = !available;
    renderPublisherIsbnCrosschecks();
    window.requestAnimationFrame(updateNavigationHint);
  }

  function renderPublisherIsbnCrosschecks() {
    const holder = byId('publisher-isbn-list');
    const empty = byId('publisher-isbn-empty');
    holder.replaceChildren();
    empty.hidden = true;
    if (!publisherIsbnState.available) {
      byId('publisher-isbn-summary').textContent = 'Public publisher ISBN crosscheck layer withheld or unavailable; its count is not zero.';
      return;
    }
    const rawQuery = byId('publisher-isbn-query').value.trim();
    const terms = rawQuery.length <= 200 ? normalize(rawQuery).split(/\s+/).filter(Boolean) : ['QUERY_TOO_LONG'];
    const status = byId('publisher-isbn-status').value;
    const tag = byId('publisher-isbn-tag').value;
    const rows = publisherIsbnState.rows.filter((row) => {
      const agreement = row.crosscheck_state === 'ISBN_IDENTIFIER_AGREEMENT_SOURCE_LOCAL';
      if (status !== 'all' && status !== (agreement ? 'agreement' : 'held')) return false;
      const tags = [`source-batch:${row.source_batch.toLowerCase()}`,
        `crosscheck:${row.crosscheck_state.toLowerCase()}`, 'publisher:simonandschuster.com'];
      if (tag !== 'all' && !tags.includes(tag)) return false;
      const text = normalize([row.publisher_title, ...row.publisher_creators, row.publisher_isbn13,
        row.source_local_ref, row.source_batch, row.crosscheck_state].join(' '));
      return terms.every((term) => text.includes(term));
    });
    const shown = rows.slice(0, publisherIsbnState.limit);
    byId('publisher-isbn-summary').textContent = `${rows.length} of 39 source-local publisher ISBN crosschecks match` +
      (shown.length < rows.length ? ` · displaying ${shown.length}` : '') +
      '. These do not authenticate private books or establish distinct Works.';
    if (!rows.length) { empty.hidden = false; return; }
    for (const row of shown) {
      const agreement = row.crosscheck_state === 'ISBN_IDENTIFIER_AGREEMENT_SOURCE_LOCAL';
      const card = el('article', `card publisher-isbn-card${agreement ? '' : ' isbn-held'}`);
      const kicker = el('span', 'kicker isbn-kicker', `Public publisher metadata · ${row.source_batch}`);
      card.append(kicker, el('h3', '', row.publisher_title));
      card.append(el('p', '', `${row.publisher_creators.join(' · ')} · eBook ISBN ${row.publisher_isbn13}`));
      card.append(el('p', 'isbn-status', isbnCrosscheckLabels[row.crosscheck_state]));
      card.append(el('p', 'isbn-custody', `Source-local reference ${row.source_local_ref}; no private ebook authentication, plot text, artwork, or Work admission.`));
      const link = el('a', 'isbn-source', 'Inspect first-party publisher product metadata');
      link.href = row.publisher_url;
      link.rel = 'noopener noreferrer';
      link.target = '_blank';
      card.append(link);
      card.append(el('small', 'isbn-custody', `Accepted public crosscheck: ${row.public_source_record}`));
      holder.append(card);
    }
    if (shown.length < rows.length) {
      const more = el('button', 'directory-more', `Show next ${Math.min(12, rows.length - shown.length)} ISBN source rows`);
      more.type = 'button';
      more.addEventListener('click', () => {
        playTone();
        const start = shown.length;
        publisherIsbnState.limit += 12;
        renderPublisherIsbnCrosschecks();
        focusNewPage(holder, start);
      });
      holder.append(more);
    }
  }

  function acceptPublisherIsbnCrosschecks(data) {
    const sourceBatches = new Map([
      ['OPF-FIRST-NINE', { path: 'proposals/librarian/opf-publisher-crosscheck-20261103/records.json', ids: [9, 10, 15, 28, 29, 31, 34, 50, 51] }],
      ['OPF-NEXT-TEN', { path: 'proposals/librarian/opf-publisher-crosscheck-next-ten-20261103/records.json', ids: [52, 53, 54, 55, 56, 57, 58, 59, 60, 61] }],
      ['OPF-THIRD-TEN', { path: 'proposals/librarian/opf-publisher-crosscheck-third-ten-20261103/records.json', ids: [62, 63, 64, 65, 67, 68, 69, 70, 74, 75] }],
      ['OPF-TNG-0076-0079', { path: 'proposals/librarian/tng-opf-0076-0079-publisher-crosswalk-20261103/records.json', ids: [76, 77, 78, 79] }],
      ['OPF-FOURTH-SIX', { path: 'proposals/librarian/opf-publisher-crosscheck-fourth-six-20261103/records.json', ids: [73, 82, 84, 85, 87, 88] }]
    ]);
    const exactKeys = (object, keys) => object && typeof object === 'object' && !Array.isArray(object) &&
      Object.keys(object).length === keys.length && keys.every((key) => Object.hasOwn(object, key));
    const rootKeys = ['schema_version', 'data_status', 'row_count', 'publisher_isbn_identifier_agreements',
      'held_discrepancy_count', 'existing_publisher_edition_leads_count_unchanged',
      'existing_directory_rows_count_unchanged', 'private_ebooks_authenticated', 'canonical_works_admitted',
      'synopses_published', 'artwork_published', 'publisher_independence_group_count',
      'admission_effect', 'coverage_effect', 'accepted_public_input_receipts', 'rows'];
    if (!exactKeys(data, rootKeys) || data.schema_version !== '1.0.0' ||
        data.data_status !== 'PUBLIC_PUBLISHER_ISBN_SOURCE_LOCAL_CROSSCHECKS_ONLY' ||
        data.row_count !== 39 || data.publisher_isbn_identifier_agreements !== 30 ||
        data.held_discrepancy_count !== 9 ||
        data.existing_publisher_edition_leads_count_unchanged !== 3 ||
        data.existing_directory_rows_count_unchanged !== 1214 ||
        data.private_ebooks_authenticated !== 0 || data.canonical_works_admitted !== 0 ||
        data.synopses_published !== 0 || data.artwork_published !== 0 ||
        data.publisher_independence_group_count !== 1 ||
        data.admission_effect !== 'NONE' || data.coverage_effect !== 'NONE' ||
        !Array.isArray(data.accepted_public_input_receipts) || data.accepted_public_input_receipts.length !== 5 ||
        !Array.isArray(data.rows) || data.rows.length !== 39) {
      throw new Error('Public publisher ISBN index envelope was changed or elevated.');
    }
    const receipts = new Map();
    for (const [i, [, spec]] of [...sourceBatches].entries()) {
      const receipt = data.accepted_public_input_receipts[i];
      if (!exactKeys(receipt, ['path', 'sha256']) || receipt.path !== spec.path ||
          !/^[0-9a-f]{64}$/.test(receipt.sha256)) {
        throw new Error('Public publisher source receipt mismatch.');
      }
      receipts.set(receipt.path, receipt.sha256);
    }
    const rowKeys = ['row_id', 'source_local_ref', 'publisher_title', 'publisher_creators',
      'publisher_isbn13', 'publisher_format', 'publisher_url', 'publisher_lineage',
      'crosscheck_state', 'source_batch', 'public_source_record', 'public_source_record_sha256',
      'private_edition_equivalence', 'work_identity', 'public_synopsis_effect',
      'artwork_effect', 'admission_effect', 'coverage_effect'];
    const sourceIds = new Set();
    const isbns = new Set();
    let agreement = 0;
    for (const row of data.rows) {
      const spec = sourceBatches.get(row?.source_batch);
      const number = /^publisher-isbn-crosscheck:\d{4}$/.test(row?.row_id || '') ? Number(row.row_id.slice(-4)) : -1;
      const sourceId = `opf-local:${String(number).padStart(4, '0')}`;
      let url;
      try { url = new URL(row.publisher_url); } catch (_) { throw new Error('Publisher ISBN product URL invalid.'); }
      if (!exactKeys(row, rowKeys) || !spec || !spec.ids.includes(number) ||
          row.source_local_ref !== sourceId || sourceIds.has(sourceId) ||
          row.public_source_record !== spec.path || row.public_source_record_sha256 !== receipts.get(spec.path) ||
          row.publisher_lineage !== 'publisher:simonandschuster.com' || row.publisher_format !== 'EBOOK' ||
          row.private_edition_equivalence !== 'UNVERIFIED' || row.work_identity !== 'NOT_RECONCILED' ||
          row.public_synopsis_effect !== 'NONE' || row.artwork_effect !== 'NONE' ||
          row.admission_effect !== 'NONE' || row.coverage_effect !== 'NONE' ||
          !Object.hasOwn(isbnCrosscheckLabels, row.crosscheck_state) ||
          typeof row.publisher_title !== 'string' || !row.publisher_title.trim() ||
          row.publisher_title.length > 180 || row.publisher_title.includes('<') || row.publisher_title.includes('>') ||
          !Array.isArray(row.publisher_creators) || !row.publisher_creators.length ||
          row.publisher_creators.length > 8 ||
          row.publisher_creators.some((name) => typeof name !== 'string' || !name.trim() ||
            name.length > 110 || name.includes('<') || name.includes('>')) ||
          typeof row.publisher_isbn13 !== 'string' || !/^97[89]\d{10}$/.test(row.publisher_isbn13) ||
          isbns.has(row.publisher_isbn13) ||
          url.protocol !== 'https:' || url.hostname !== 'www.simonandschuster.com' ||
          url.username || url.password || url.port || url.search || url.hash ||
          !/^\/books\/[A-Za-z0-9-]+\/[A-Za-z0-9-]+\/[A-Za-z0-9-]+\/97[89]\d{10}$/.test(url.pathname) ||
          !url.pathname.endsWith('/' + row.publisher_isbn13)) {
        throw new Error('Public publisher ISBN title, identity, status, source or rights boundary rejected.');
      }
      sourceIds.add(sourceId);
      isbns.add(row.publisher_isbn13);
      if (row.crosscheck_state === 'ISBN_IDENTIFIER_AGREEMENT_SOURCE_LOCAL') agreement++;
    }
    if (sourceIds.size !== 39 || isbns.size !== 39 || agreement !== 30) {
      throw new Error('Public publisher ISBN source-local denominator drift.');
    }
    publisherIsbnState.rows = data.rows;
    publisherIsbnState.limit = 12;
    const tagSelect = byId('publisher-isbn-tag');
    tagSelect.replaceChildren(new Option('All source-local tags', 'all'));
    const tags = [...new Set(data.rows.flatMap((row) => [
      `source-batch:${row.source_batch.toLowerCase()}`, `crosscheck:${row.crosscheck_state.toLowerCase()}`,
      'publisher:simonandschuster.com'
    ]))].sort();
    for (const tag of tags) tagSelect.add(new Option(tag.replaceAll('_', ' '), tag));
    tagSelect.value = 'all';
    setPublisherIsbnAvailability(true,
      '39 first-party publisher ISBN metadata crosschecks loaded: 30 source-local identifier agreements, 9 held discrepancies. One publisher lineage; no private book authentication, Work admission, plot text or cover release.');
  }

  async function loadPublisherIsbnCrosschecks() {
    try {
      const response = await fetch('./publisher-isbn-crosschecks.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Publisher ISBN sidecar unavailable.');
      if (!globalThis.crypto?.subtle || typeof TextDecoder !== 'function') throw new Error('SHA-256 unavailable.');
      const bytes = await response.arrayBuffer();
      if (bytes.byteLength < 1000 || bytes.byteLength > 100000) throw new Error('Publisher ISBN sidecar size outside accepted scope.');
      const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const hex = Array.from(new Uint8Array(digest), (n) => n.toString(16).padStart(2, '0')).join('');
      if (hex !== publisherIsbnSha256) throw new Error('Publisher ISBN sidecar differs from accepted source-derived digest.');
      acceptPublisherIsbnCrosschecks(JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)));
    } catch (error) {
      setPublisherIsbnAvailability(false,
        `Publisher ISBN crosschecks withheld: ${error.message || 'Source metadata not validated.'} This is unavailable, not a verified zero.`);
    }
  }

  // A distinct studio-page observation shelf, not the 14-film discovery
  // catalog, not a watched-film claim, and not image/synopsis authorization.
  const paramountBatches = new Map([
    ['PARAMOUNT-FIRST-SIX', { path: 'proposals/films/paramount-six-source-pages-20261103/records.json',
      sha: 'c41eeeab288dd01eff8c89e0f9749d749b16487f6b1630d84deca09badfd869e',
      ids: ['film-motion-picture', 'film-wrath-of-khan', 'film-generations', 'film-first-contact', 'film-2009', 'film-into-darkness'] }],
    ['PARAMOUNT-SECOND-SIX', { path: 'proposals/films/paramount-second-six-pages-20261103/records.json',
      sha: 'aa590b5f77f0d148595814cd8d74fa7186c49c45fb32f854c7568d720f3e0b41',
      ids: ['film-search-for-spock', 'film-voyage-home', 'film-final-frontier', 'film-undiscovered-country', 'film-insurrection', 'film-nemesis'] }],
    ['PARAMOUNT-BEYOND', { path: 'proposals/films/beyond-paramount-metadata-20261103/records.json',
      sha: 'cde05393657f16d7c846c77c6c87227948bd38a2d2a06a2946bcd727e44cf122',
      ids: ['film-beyond'] }]
  ]);
  const paramountAnomalies = new Set(['film-first-contact', 'film-search-for-spock', 'film-insurrection']);

  function setParamountAvailability(available, message) {
    paramountState.available = available;
    if (!available) paramountState.rows = [];
    byId('paramount-nav-count').textContent = available ? String(paramountState.rows.length) : '—';
    byId('paramount-state').textContent = message;
    byId('paramount-download').hidden = !available;
    renderParamountRechecks();
    window.requestAnimationFrame(updateNavigationHint);
  }

  function renderParamountRechecks() {
    const holder = byId('paramount-list');
    const empty = byId('paramount-empty');
    holder.replaceChildren();
    empty.hidden = true;
    if (!paramountState.available) {
      byId('paramount-summary').textContent = 'Paramount metadata source shelf unavailable; not a verified zero.';
      return;
    }
    const typed = byId('paramount-query').value.trim();
    const terms = typed.length <= 150 ? normalize(typed).split(/\s+/).filter(Boolean) : ['QUERY_TOO_LONG'];
    const status = byId('paramount-status').value;
    const tag = byId('paramount-tag').value;
    const matches = paramountState.rows.filter((row) => {
      if (status !== 'all' && status !== row.recheck_status) return false;
      if (tag !== 'all' && !row.tags.includes(tag)) return false;
      const searchable = normalize([row.source_page_slug, row.source_local_candidate_id,
        row.genre_as_listed, row.year_as_listed, row.rating_as_listed,
        ...row.selected_directors_as_listed, ...row.selected_cast_performers_as_listed].join(' '));
      return terms.every((term) => searchable.includes(term));
    });
    byId('paramount-summary').textContent = `${matches.length} of 13 separate source-local Paramount film-page observations match. No films viewed, Works admitted or artwork released.`;
    if (!matches.length) { empty.hidden = false; return; }
    for (const row of matches) {
      const held = row.recheck_status === 'HELD_UNRESOLVED_SOURCE_ANOMALY';
      const card = el('article', `card paramount-card${held ? ' paramount-held' : ''}`);
      card.append(el('span', 'kicker', `First-party studio page · ${row.source_batch}`));
      card.append(el('h3', 'paramount-slug', row.source_page_slug.replaceAll('-', ' ')));
      card.append(el('p', '', `Paramount-listed ${row.year_as_listed} · ${row.rating_as_listed} · ${row.runtime_as_listed_minutes} minutes · ${row.genre_as_listed}`));
      card.append(el('p', '', `Listed directors: ${row.selected_directors_as_listed.join(' · ')}`));
      card.append(el('p', 'paramount-status', held ? 'HELD: unresolved source-page discrepancy' : 'First-party listing observed; source-local only'));
      if (held) card.append(el('p', 'paramount-custody', row.source_anomaly));
      card.append(el('small', 'paramount-custody', `${row.source_local_candidate_id} · publisher listing only; not a film copy, global Work or source-independent witness.`));
      const source = el('a', 'paramount-link', 'Inspect first-party Paramount listing');
      source.href = row.source_locator;
      source.target = '_blank';
      source.rel = 'noopener noreferrer';
      card.append(source);
      holder.append(card);
    }
  }

  function acceptParamountRechecks(data) {
    const exactKeys = (value, keys) => value && typeof value === 'object' && !Array.isArray(value) &&
      Object.keys(value).length === keys.length && keys.every((key) => Object.hasOwn(value, key));
    const rootKeys = ['schema_version', 'data_status', 'row_count', 'source_anomaly_held_count',
      'publisher_independence_group_count', 'distinct_works_admitted', 'full_films_viewed',
      'synopses_released', 'artwork_released', 'coverage_effect', 'admission_effect',
      'accepted_source_input_receipts', 'rows'];
    if (!exactKeys(data, rootKeys) || data.schema_version !== '1.0.0' ||
        data.data_status !== 'SOURCE_LOCAL_PARAMOUNT_FILM_PAGE_METADATA_ONLY' ||
        data.row_count !== 13 || data.source_anomaly_held_count !== 3 ||
        data.publisher_independence_group_count !== 1 ||
        data.distinct_works_admitted !== 0 || data.full_films_viewed !== 0 ||
        data.synopses_released !== 0 || data.artwork_released !== 0 ||
        data.coverage_effect !== 'NONE' || data.admission_effect !== 'NONE' ||
        !Array.isArray(data.rows) || data.rows.length !== 13 ||
        !Array.isArray(data.accepted_source_input_receipts) || data.accepted_source_input_receipts.length !== 3) {
      throw new Error('Paramount source metadata envelope elevated or changed.');
    }
    const receipts = [...paramountBatches.values()];
    for (let i = 0; i < receipts.length; i++) {
      const receipt = data.accepted_source_input_receipts[i];
      if (!exactKeys(receipt, ['path', 'sha256']) ||
          receipt.path !== receipts[i].path || receipt.sha256 !== receipts[i].sha) {
        throw new Error('Paramount accepted upstream source digest mismatched.');
      }
    }
    const rowKeys = ['row_id', 'source_local_candidate_id', 'source_page_slug', 'source_locator',
      'source_batch', 'source_input', 'source_input_sha256', 'publisher_family', 'year_as_listed',
      'rating_as_listed', 'runtime_as_listed_minutes', 'genre_as_listed',
      'selected_directors_as_listed', 'selected_cast_performers_as_listed', 'source_anomaly',
      'recheck_status', 'tags', 'source_snapshot_class', 'film_viewed', 'source_identity_scope',
      'work_admission_effect', 'coverage_effect', 'synopsis_release_effect', 'artwork_release_effect'];
    const seen = new Set(); let heldCount = 0;
    for (const row of data.rows) {
      const batch = paramountBatches.get(row?.source_batch);
      let url;
      try { url = new URL(row.source_locator); } catch (_) { throw new Error('Invalid Paramount source URL'); }
      const expectedTags = [
        'medium:film', 'publisher:paramount.com', 'batch:' + String(row.source_batch).toLowerCase(),
        'year:' + String(row.year_as_listed), 'rating:' + String(row.rating_as_listed).toLowerCase(),
        'anomaly:' + (paramountAnomalies.has(row.source_local_candidate_id) ? 'held' : 'none_documented')
      ].sort();
      if (!exactKeys(row, rowKeys) || !batch || !batch.ids.includes(row.source_local_candidate_id) ||
          seen.has(row.source_local_candidate_id) ||
          row.row_id !== 'paramount-source-local:' + row.source_local_candidate_id ||
          row.source_input !== batch.path || row.source_input_sha256 !== batch.sha ||
          row.publisher_family !== 'publisher:paramount.com' ||
          url.protocol !== 'https:' || url.hostname !== 'www.paramount.com' || url.port ||
          url.username || url.password || url.search || url.hash ||
          !/^\/movies\/[a-z0-9-]+$/.test(url.pathname) ||
          row.source_page_slug !== url.pathname.slice('/movies/'.length) ||
          !Number.isInteger(row.year_as_listed) || row.year_as_listed < 1900 || row.year_as_listed > 2100 ||
          !Number.isInteger(row.runtime_as_listed_minutes) || row.runtime_as_listed_minutes < 30 ||
          row.runtime_as_listed_minutes > 300 ||
          !['G', 'PG', 'PG-13', 'R', 'NR'].includes(row.rating_as_listed) ||
          typeof row.genre_as_listed !== 'string' || row.genre_as_listed.length > 100 ||
          !Array.isArray(row.selected_directors_as_listed) || !row.selected_directors_as_listed.length ||
          !Array.isArray(row.selected_cast_performers_as_listed) || !row.selected_cast_performers_as_listed.length ||
          [...row.selected_directors_as_listed, ...row.selected_cast_performers_as_listed].some(
            (s) => typeof s !== 'string' || !s.trim() || s.length > 100 || s.includes('<') || s.includes('>')) ||
          !Array.isArray(row.tags) || JSON.stringify(row.tags) !== JSON.stringify(expectedTags) ||
          row.source_identity_scope !== 'SOURCE_LOCAL_CANDIDATE' ||
          row.source_snapshot_class !== 'RENDERED_PUBLISHER_PAGE_NO_RAW_HTML_OR_FILM_COPY' ||
          row.film_viewed !== false || row.work_admission_effect !== 'NONE' ||
          row.coverage_effect !== 'NONE' || row.synopsis_release_effect !== 'NONE' ||
          row.artwork_release_effect !== 'NONE' ||
          (paramountAnomalies.has(row.source_local_candidate_id)
            ? row.recheck_status !== 'HELD_UNRESOLVED_SOURCE_ANOMALY' ||
              typeof row.source_anomaly !== 'string' || !row.source_anomaly.endsWith('NOT_RECONCILED')
            : row.recheck_status !== 'SOURCE_LOCAL_PAGE_METADATA_OBSERVED' || row.source_anomaly !== null)) {
        throw new Error('Paramount source row rights, identity, provenance or status failed.');
      }
      if (paramountAnomalies.has(row.source_local_candidate_id)) heldCount++;
      seen.add(row.source_local_candidate_id);
    }
    if (seen.size !== 13 || heldCount !== 3) throw new Error('Paramount source-local denominator drift.');
    paramountState.rows = data.rows;
    const select = byId('paramount-tag');
    select.replaceChildren(new Option('All source-local tags', 'all'));
    const allTags = [...new Set(data.rows.flatMap((row) => row.tags))].sort();
    for (const tag of allTags) select.add(new Option(tag.replaceAll('_', ' '), tag));
    select.value = 'all';
    setParamountAvailability(true,
      '13 separate Paramount publisher-page metadata observations; 3 source discrepancies held. Source-local only; no film viewing, Work admission, synopsis or image release.');
  }

  async function loadParamountRechecks() {
    try {
      const response = await fetch('./paramount-film-rechecks.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Paramount metadata shelf unavailable.');
      if (!globalThis.crypto?.subtle || typeof TextDecoder !== 'function') throw new Error('SHA-256 unavailable.');
      const bytes = await response.arrayBuffer();
      if (bytes.byteLength < 2000 || bytes.byteLength > 100000) throw new Error('Paramount metadata shelf size outside pinned scope.');
      const hash = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const hex = Array.from(new Uint8Array(hash), (n) => n.toString(16).padStart(2, '0')).join('');
      if (hex !== paramountSha256) throw new Error('Paramount metadata shelf differs from code-pinned source snapshot.');
      acceptParamountRechecks(JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)));
    } catch (error) {
      setParamountAvailability(false,
        `Paramount source metadata withheld: ${error.message || 'Source validation failed.'} Unavailable is not verified zero.`);
    }
  }

  // A distinct *episode-guide source* shelf. Source-local utterance labels
  // are publisher-description terms, not character identity or plot truth.
  function setEpisodeSourceAvailability(available, message) {
    episodeSourceState.available = available;
    if (!available) episodeSourceState.rows = [];
    byId('episode-source-nav-count').textContent = available ? String(episodeSourceState.rows.length) : '—';
    byId('episode-source-state').textContent = message;
    byId('episode-source-download').hidden = !available;
    renderEpisodeSourceCards();
    window.requestAnimationFrame(updateNavigationHint);
  }

  function renderEpisodeSourceCards() {
    const holder = byId('episode-source-list');
    const empty = byId('episode-source-empty');
    holder.replaceChildren(); empty.hidden = true;
    if (!episodeSourceState.available) {
      byId('episode-source-summary').textContent = 'Episode guide observations unavailable; not a verified zero.';
      return;
    }
    const typed = byId('episode-source-query').value.trim();
    const terms = typed.length <= 160 ? normalize(typed).split(/\s+/).filter(Boolean) : ['QUERY_TOO_LONG'];
    const series = byId('episode-source-series').value;
    const status = byId('episode-source-status').value;
    const tag = byId('episode-source-tag').value;
    const found = episodeSourceState.rows.filter((row) => {
      if (series !== 'all' && series !== row.series_code) return false;
      if (status !== 'all' && status !== row.source_status) return false;
      if (tag !== 'all' && !row.tags.includes(tag)) return false;
      const termsIn = normalize([row.title, row.series_title, row.source_local_id,
        `S${row.season}E${String(row.episode).padStart(2, '0')}`, row.source_status,
        ...row.publisher_utterance_labels, ...row.tags].join(' '));
      return terms.every((term) => termsIn.includes(term));
    });
    byId('episode-source-summary').textContent = `${found.length} of 20 validated, held publisher-guide cards match. Not episode viewing, Work identities or new catalog coverage.`;
    if (!found.length) { empty.hidden = false; return; }
    for (const row of found) {
      const card = el('article', 'card episode-source-card');
      card.append(el('span', 'kicker', `${row.series_title} · S${row.season} E${row.episode}`));
      card.append(el('h3', '', row.title));
      const chips = el('div', 'episode-source-chips');
      chips.append(el('span', 'badge proposed', 'Publisher source card'));
      chips.append(el('span', 'badge', 'HELD · 0 coverage'));
      chips.append(el('span', 'badge', 'Artwork not released'));
      card.append(chips);
      card.append(el('p', 'episode-source-status', 'HELD · First-party publisher guide card; episode content not independently read'));
      if (row.publisher_utterance_labels.length) {
        card.append(el('p', 'episode-source-labels', `Publisher description terms (source-local, not identity): ${row.publisher_utterance_labels.join(' · ')}`));
      }
      card.append(el('small', 'paramount-custody', `${row.source_local_id} · ${row.source_batch}; no synopsis or artwork released`));
      const link = el('a', 'paramount-link', 'Inspect source publisher episode guide');
      link.href = row.publisher_guide_url;
      link.target = '_blank'; link.rel = 'noopener noreferrer';
      card.append(link); holder.append(card);
    }
  }

  async function acceptEpisodeSourceCards(data) {
    const exact = (obj, keys) => obj && typeof obj === 'object' && !Array.isArray(obj) &&
      Object.keys(obj).length === keys.length && keys.every((key) => Object.hasOwn(obj, key));
    const rootKeys = ['schema_version', 'data_status', 'row_count', 'series_count',
      'publisher_independence_group_count', 'full_episodes_viewed', 'works_admitted',
      'synopses_released', 'artwork_released', 'admission_effect', 'coverage_effect',
      'source_input_receipts', 'rows'];
    const rowKeys = ['row_id', 'source_local_id', 'series_code', 'series_title', 'season', 'episode',
      'title', 'publisher_utterance_labels', 'tags', 'publisher_guide_url', 'source_batch',
      'source_input', 'source_input_sha256', 'publisher_family', 'source_status',
      'source_identity_scope', 'full_episode_read', 'work_admission_effect', 'coverage_effect',
      'synopsis_release_effect', 'artwork_release_effect', 'source_row_sha256'];
    const canonical = (value) => {
      if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
      if (value !== null && typeof value === 'object') {
        return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`;
      }
      return JSON.stringify(value);
    };
    if (!exact(data, rootKeys) || data.schema_version !== '1.0.0' ||
        data.data_status !== 'HELD_SOURCE_LOCAL_PUBLISHER_EPISODE_CARDS' || data.row_count !== 20 ||
        data.series_count !== 2 || data.publisher_independence_group_count !== 1 ||
        data.full_episodes_viewed !== 0 || data.works_admitted !== 0 ||
        data.synopses_released !== 0 || data.artwork_released !== 0 ||
        data.admission_effect !== 'NONE' || data.coverage_effect !== 'NONE' ||
        !Array.isArray(data.source_input_receipts) || data.source_input_receipts.length !== 4 ||
        !Array.isArray(data.rows) || data.rows.length !== 20) {
      throw new Error('Publisher episode source-card envelope elevated or changed.');
    }
    const batches = [...episodeSourceBatches];
    for (let i = 0; i < batches.length; i++) {
      const [name, [path, sha]] = batches[i];
      const receipt = data.source_input_receipts[i];
      if (!exact(receipt, ['batch', 'path', 'sha256']) || receipt.batch !== name ||
          receipt.path !== path || receipt.sha256 !== sha) {
        throw new Error('Original episode-guide packet receipt drifted.');
      }
    }
    const seen = new Set(); const slots = new Map([['PIC', new Set()], ['SNW', new Set()]]);
    for (const row of data.rows) {
      const batch = episodeSourceBatches.get(row?.source_batch);
      if (!exact(row, rowKeys) || !batch || seen.has(row.row_id)) {
        throw new Error('Duplicate or unrecognized publisher card.');
      }
      const codePin = episodePublicRowPins.get(row.row_id);
      if (!codePin || typeof TextEncoder !== 'function') {
        throw new Error('Unpinned episode card or WebCrypto encoding unavailable.');
      }
      const bytes = new TextEncoder().encode(canonical(row));
      const digestBytes = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const actualRowHash = Array.from(new Uint8Array(digestBytes), (n) => n.toString(16).padStart(2, '0')).join('');
      if (actualRowHash !== codePin) {
        throw new Error('Episode card full public-row evidence pin differs from reviewed source.');
      }
      const [path, sha, series, expectedEpisodes] = batch;
      const season = series === 'PIC' ? 1 : 3;
      const expectedId = `${series.toLowerCase()}-s${season}-e${String(row.episode).padStart(2, '0')}-pplus${series === 'PIC' ? '-guide' : ''}`;
      const expectedUrl = `https://www.paramountplus.com/shows/star-trek-${series === 'PIC' ? 'picard/episodes/1/' : 'strange-new-worlds/episodes/3/'}`;
      const expectedTags = [
        `series:${series.toLowerCase()}`, `season:${season}`, `slot:s${season}e${String(row.episode).padStart(2, '0')}`,
        'publisher:paramountplus.com', 'source-status:held',
        ...row.publisher_utterance_labels.map((label) =>
          `publisher-utterance:${label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`)
      ].sort();
      if (!Number.isInteger(row.episode) || !expectedEpisodes.includes(row.episode) ||
          row.season !== season || row.series_code !== series ||
          row.series_title !== (series === 'PIC' ? 'Star Trek: Picard' : 'Star Trek: Strange New Worlds') ||
          row.source_local_id !== expectedId || row.row_id !== `episode-publisher-card:${expectedId}` ||
          row.source_input !== path || row.source_input_sha256 !== sha ||
          row.publisher_guide_url !== expectedUrl || row.publisher_family !== 'publisher:paramountplus.com' ||
          row.title !== episodeSourceTitles.get(expectedId) ||
          !Array.isArray(row.publisher_utterance_labels) || row.publisher_utterance_labels.length > 12 ||
          row.publisher_utterance_labels.some((v) => typeof v !== 'string' || !v.trim() || v.length > 80 || /[<>]/.test(v)) ||
          !Array.isArray(row.tags) || JSON.stringify(row.tags) !== JSON.stringify(expectedTags) ||
          !/^[a-f0-9]{64}$/.test(row.source_row_sha256) ||
          row.source_status !== 'HELD_PUBLISHER_GUIDE_ONLY' ||
          row.source_identity_scope !== 'SOURCE_LOCAL_CARD_NOT_ADMITTED_WORK' ||
          row.full_episode_read !== false || row.work_admission_effect !== 'NONE' ||
          row.coverage_effect !== 'NONE' || row.synopsis_release_effect !== 'NONE' ||
          row.artwork_release_effect !== 'NONE') {
        throw new Error('Publisher episode card source, rights, slot or held status changed.');
      }
      seen.add(row.row_id); slots.get(series).add(row.episode);
    }
    if (seen.size !== 20 || [...slots.values()].some((set) => set.size !== 10)) {
      throw new Error('Publisher episode-card source-local denominator changed.');
    }
    episodeSourceState.rows = data.rows;
    const select = byId('episode-source-tag');
    select.replaceChildren(new Option('All source-local tags', 'all'));
    for (const tag of [...new Set(data.rows.flatMap((row) => row.tags))].sort()) {
      select.add(new Option(tag.replaceAll('_', ' '), tag));
    }
    select.value = 'all';
    setEpisodeSourceAvailability(true, '20 first-party publisher guide cards passed accepted source validators; all HELD, no full episodes viewed or artwork/synopses released.');
  }

  async function loadEpisodeSourceCards() {
    try {
      const response = await fetch('./episode-source-cards.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Episode guide source card shelf unavailable.');
      if (!globalThis.crypto?.subtle || typeof TextDecoder !== 'function') throw new Error('SHA-256 unavailable.');
      const bytes = await response.arrayBuffer();
      if (bytes.byteLength < 8000 || bytes.byteLength > 100000) throw new Error('Episode shelf byte size unexpected.');
      const hash = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const hex = Array.from(new Uint8Array(hash), (n) => n.toString(16).padStart(2, '0')).join('');
      if (hex !== episodeSourceSha256) throw new Error('Episode guide shelf differs from code-pinned accepted source snapshot.');
      await acceptEpisodeSourceCards(JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes)));
    } catch (error) {
      setEpisodeSourceAvailability(false,
        `Episode publisher card shelf withheld: ${error.message || 'Source validation failed.'} Unavailable is not verified zero.`);
    }
  }

  function setArtworkAvailability(available, message) {
    artworkState.available = available;
    if (!available) { artworkState.entries.clear(); artworkState.enabled = false; }
    artworkToggle.disabled = !available;
    artworkToggle.setAttribute('aria-pressed', String(artworkState.enabled));
    artworkToggle.textContent = artworkState.enabled ? 'Hide sourced artwork' : 'Show sourced artwork';
    byId('artwork-state').textContent = message;
    renderDirectory();
    renderFilms();
  }

  function acceptArtworkCatalog(data) {
    const exactKeys = (item, keys) => item && typeof item === 'object' && !Array.isArray(item) &&
      Object.keys(item).length === keys.length && keys.every((key) => Object.hasOwn(item, key));
    const rootKeys = ['schema_version', 'data_status', 'coverage_effect', 'rights_policy', 'artwork_count', 'artwork'];
    const localKeys = ['row_id', 'image_path', 'image_sha256', 'alt_text', 'source_locator', 'rights_status', 'rights_receipt_sha256'];
    const openLibraryKeys = ['row_id', 'provider', 'cover_id', 'isbn', 'alt_text', 'source_locator', 'rights_status', 'edition_metadata_sha256', 'attribution_url'];
    if (!exactKeys(data, rootKeys) || data.schema_version !== '1.1.0' ||
        data.data_status !== 'PROVENANCE_REVIEWED_ARTWORK' || data.coverage_effect !== 'NONE' ||
        data.rights_policy !== 'PER_ENTRY_DISPLAY_GATE' ||
        !Array.isArray(data.artwork) || data.artwork.length < 1 || data.artwork.length > 5000 ||
        data.artwork_count !== data.artwork.length) {
      throw new Error('Artwork release manifest has an invalid or unreviewed envelope.');
    }
    const sourceRows = new Map();
    for (const row of directoryState.rows) sourceRows.set(artworkKey(row), row);
    for (const row of filmState.films) sourceRows.set(artworkKey(row), row);
    const entries = new Map();
    for (const item of data.artwork) {
      if (typeof item?.row_id !== 'string' || !sourceRows.has(item.row_id) || entries.has(item.row_id) ||
          typeof item.alt_text !== 'string' || !item.alt_text.trim() || item.alt_text.length > 180 ||
          item.source_locator !== sourceRows.get(item.row_id).source_locator) {
        throw new Error('Artwork references an unknown or mismatched source record.');
      }
      if (item.provider === 'OPEN_LIBRARY_COVERS_API') {
        const literaryRow = sourceRows.get(item.row_id);
        if (!exactKeys(item, openLibraryKeys) ||
            literaryRow.medium !== 'LITERATURE' ||
            !Number.isSafeInteger(item.cover_id) || item.cover_id < 1 || item.cover_id > 999999999 ||
            typeof item.isbn !== 'string' || !/^97[89][0-9]{10}$/.test(item.isbn) ||
            item.attribution_url !== `https://openlibrary.org/isbn/${item.isbn}` ||
            item.rights_status !== 'API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED' ||
            !/^[a-f0-9]{64}$/.test(item.edition_metadata_sha256 || '')) {
          throw new Error('External cover has no pinned Open Library edition or documented API display scope.');
        }
        const editionIsListed = Array.isArray(literaryRow.details) && literaryRow.details.some((detail) => {
          if (typeof detail !== 'string') return false;
          const publisher = /^[A-Za-z][A-Za-z -]{0,56} · ISBN (97[89][0-9]{10})$/.exec(detail);
          const memoir = /^(?:Paperback|Hardcover|Trade Paperback|Ebook) ISBN (97[89][0-9]{10})$/.exec(detail);
          return (publisher || memoir)?.[1] === item.isbn;
        });
        if (!editionIsListed) {
          throw new Error('External cover ISBN is not listed on the target source-local edition.');
        }
        // Simon & Schuster product locators identify a particular ISBN even
        // when their source-local row lists several additional formats.
        const publisherUrl = new URL(literaryRow.source_locator);
        if (publisherUrl.hostname === 'www.simonandschuster.com' &&
            !publisherUrl.pathname.endsWith(`/${item.isbn}`)) {
          throw new Error('External cover ISBN does not match the publisher source URL edition.');
        }
        const receipt = reviewedOpenLibraryEditionReceipts.get(item.row_id);
        if (!receipt || receipt.source_locator !== item.source_locator ||
            receipt.isbn !== item.isbn || receipt.cover_id !== item.cover_id ||
            receipt.edition_metadata_sha256 !== item.edition_metadata_sha256) {
          throw new Error('External cover lacks an independently reviewed row/edition/cover crosswalk receipt.');
        }
      } else if (!exactKeys(item, localKeys) ||
                 !/^\.\/licensed-artwork\/[a-z0-9][a-z0-9._-]{1,128}\.(?:png|jpe?g|webp)$/.test(item.image_path) ||
                 item.image_path.includes('..') ||
                 item.rights_status !== 'PUBLIC_DISPLAY_PERMISSION_VERIFIED' ||
                 !/^[a-f0-9]{64}$/.test(item.image_sha256 || '') ||
                 !/^[a-f0-9]{64}$/.test(item.rights_receipt_sha256 || '')) {
        throw new Error('Local artwork lacks immutable image hash or verified public-display permission.');
      }
      entries.set(item.row_id, item);
    }
    artworkState.entries = entries;
    const apiCount = [...entries.values()].filter((item) => item.provider === 'OPEN_LIBRARY_COVERS_API').length;
    setArtworkAvailability(true, `${entries.size.toLocaleString()} source-attributed image options (${apiCount} Open Library API previews; underlying copyright may remain unresolved). Off until you choose Show sourced artwork.`);
  }

  async function loadArtworkCatalog() {
    try {
      const response = await fetch('./artwork-catalog.json', { cache: 'no-store' });
      if (response.status === 404) {
        setArtworkAvailability(false, 'Artwork is not yet display-cleared. Cards show original LCARS placeholders; no off-site image requests are made.');
        return;
      }
      if (!response.ok) throw new Error(`Artwork manifest returned HTTP ${response.status}.`);
      acceptArtworkCatalog(await response.json());
    } catch (error) {
      setArtworkAvailability(false, `Artwork release was rejected: ${error.message || 'Check artwork rights receipts.'}`);
    }
  }

  artworkToggle.addEventListener('click', () => {
    if (!artworkState.available) return;
    artworkState.enabled = !artworkState.enabled;
    artworkToggle.setAttribute('aria-pressed', String(artworkState.enabled));
    artworkToggle.textContent = artworkState.enabled ? 'Hide sourced artwork' : 'Show sourced artwork';
    renderDirectory();
    renderFilms();
  });

  function setFilmAvailability(available, message) {
    filmState.available = available;
    if (!available) filmState.films = [];
    const count = available ? filmState.films.length.toLocaleString() : '—';
    byId('film-top-count').textContent = count;
    byId('film-nav-count').textContent = count;
    byId('film-state').textContent = message;
    renderFilms();
    window.requestAnimationFrame(updateNavigationHint);
  }

  function renderFilms() {
    const container = byId('film-list');
    container.replaceChildren();
    if (!filmState.available) {
      byId('film-summary').textContent = 'Film discovery catalog unavailable; count is unknown.';
      return;
    }
    const search = normalize(byId('film-query').value.trim());
    const matched = filmState.films.filter((row) => normalize(row.title).includes(search));
    byId('film-summary').textContent = `${matched.length.toLocaleString()} of ${filmState.films.length.toLocaleString()} publisher-listed film candidates shown · unverified metadata.`;
    for (const row of matched) {
      const card = el('article', 'card media-card');
      const copy = el('div', 'media-card-copy');
      card.append(makeArtworkSlot('FILM', artworkKey(row)), copy);
      copy.append(el('span', 'kicker', row.work_type === 'STREAMING_ORIGINAL_FILM' ? 'Streaming movie · discovery' : 'Feature film · discovery'));
      copy.append(el('h3', null, row.title));
      copy.append(el('p', null, 'Publisher-listed title · metadata only · not source-reviewed'));
      appendSynopsis(copy, 'FILM', artworkKey(row));
      const link = el('a', null, 'Open official source');
      link.href = row.source_locator;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      copy.append(link);
      container.append(card);
    }
  }

  function acceptFilmCatalog(data) {
    if (!data || typeof data !== 'object' || data.schema_version !== '1.0.0' ||
        data.data_status !== 'DISCOVERY_ONLY' || data.coverage_effect !== 'NONE' ||
        data.source_group !== 'publisher:startrek.com' || !Array.isArray(data.films) ||
        !Number.isSafeInteger(data.film_count) || data.film_count !== data.films.length ||
        data.films.length < 1 || data.films.length > 500) {
      throw new Error('Film discovery metadata has an invalid schema or count.');
    }
    const used = new Set();
    const usedLocators = new Set();
    for (const row of data.films) {
      if (!row || typeof row !== 'object' || !/^[a-z0-9][a-z0-9-]{1,80}$/.test(row.id) ||
          used.has(row.id) || typeof row.title !== 'string' || !row.title.trim() || row.title.length > 200 ||
          row.source_group !== 'publisher:startrek.com' || row.verification_status !== 'UNVERIFIED_METADATA' ||
          !['FEATURE_FILM', 'STREAMING_ORIGINAL_FILM'].includes(row.work_type) ||
          !['OFFICIAL_DIRECTORY', 'OFFICIAL_ANNOUNCEMENT'].includes(row.discovery_source) ||
          ['admission_status', 'canonical_work_id', 'evidence', 'coverage_status', 'accepted'].some((key) => key in row)) {
        throw new Error('Film discovery record contains invalid or admission-like metadata.');
      }
      let source;
      try { source = new URL(row.source_locator); } catch (_) { throw new Error('Invalid official film locator.'); }
      const filmPath = /^\/movies\/[a-z0-9]+(?:-[a-z0-9]+)*$/.test(source.pathname);
      const section31 = source.pathname === '/news/star-trek-section-31-premieres-january-24';
      if (usedLocators.has(row.source_locator) || source.protocol !== 'https:' || source.hostname !== 'www.startrek.com' || source.search || source.hash ||
          source.port || source.username || source.password || !(filmPath || section31) ||
          (row.discovery_source === 'OFFICIAL_ANNOUNCEMENT') !== section31 ||
          (section31 ? row.work_type !== 'STREAMING_ORIGINAL_FILM' : row.work_type !== 'FEATURE_FILM')) {
        throw new Error('Film discovery link is outside the accepted publisher locator scope.');
      }
      used.add(row.id);
      usedLocators.add(row.source_locator);
    }
    filmState.films = data.films;
    setFilmAvailability(true, 'Publisher film metadata loaded. These films are discovery candidates, not reviewed research.');
  }

  async function loadFilmCatalog() {
    try {
      const response = await fetch('./film-catalog.json', { cache: 'no-store' });
      if (response.status === 404) {
        setFilmAvailability(false, 'The separate film discovery catalog has not been published yet.');
        return;
      }
      if (!response.ok) throw new Error(`Film request returned HTTP ${response.status}.`);
      acceptFilmCatalog(await response.json());
    } catch (error) {
      setFilmAvailability(false, `Could not load valid film discovery metadata. ${error.message || 'Check film-catalog.json.'}`);
    }
  }

  const directoryState = { rows: [], available: false, limit: 40 };
  // This is a separate display-only source-read layer. Discovery status stays
  // UNVERIFIED_METADATA and no Work/evidence/coverage state is promoted.
  const metadataRechecks = { byId: new Map(), available: false };
  // Exact accepted deterministic bytes, generated from the reviewed B001–B004
  // observations. Refuse any modified sidecar before reading its badge claims.
  const metadataRecheckSha256 = '3d8b846bfa9728b02144490c00f03d79d6c1b517f04c86e3e1747f366f6e7be8';
  // Separate accepted B005–B009 + DIS publisher-card observations. Their 61
  // titles are NOT added to the historical 56 checks or to Work coverage.
  const publisherCardChecks = { byId: new Map(), available: false };
  const publisherCardSha256 = '4ff4246f772117d847ed939a40218679fe6d1621c2c422f539d9c177971804a6';
  const directoryMediums = ['EPISODE', 'FILM', 'LITERATURE', 'SHORT_FORM', 'AUDIO'];
  // Source-local episode rows use compact catalog codes (for example VOY),
  // while visitors search for the series name they actually recognize.
  // This is a display/search alias only, never a Work-identity reconciliation.
  const directorySeriesLabels = Object.freeze({
    TOS: 'Star Trek The Original Series', TAS: 'Star Trek The Animated Series',
    TNG: 'Star Trek The Next Generation', DS9: 'Star Trek Deep Space Nine',
    VOY: 'Star Trek Voyager', ENT: 'Star Trek Enterprise',
    DIS: 'Star Trek Discovery', PIC: 'Star Trek Picard',
    LD: 'Star Trek Lower Decks', SNW: 'Star Trek Strange New Worlds',
    PRO: 'Star Trek Prodigy', SFA: 'Star Trek Starfleet Academy'
  });
  const directoryKinds = ['WIKIDATA_EPISODE', 'PUBLISHER_EPISODE_SLOT', 'PUBLISHER_REFERENCE', 'FEATURE_FILM', 'STREAMING_FILM', 'NOVEL', 'FICTIONAL_MEMOIR', 'SCRIPTED_SHORT', 'PROMOTIONAL_ANIMATION', 'SCRIPTED_AUDIO_SERIES'];
  const directoryFields = ['row_id', 'medium', 'candidate_kind', 'title', 'context', 'source_group',
    'source_input', 'source_locator', 'details', 'verification_status', 'identity_scope', 'coverage_effect', 'admission_effect'];

  function setDirectoryAvailability(available, message) {
    directoryState.available = available;
    if (!available) directoryState.rows = [];
    byId('discovery-nav-count').textContent = available ? directoryState.rows.length.toLocaleString() : '—';
    byId('discovery-top-count').textContent = available ? directoryState.rows.length.toLocaleString() : '—';
    byId('discovery-episode-count').textContent = available
      ? directoryState.rows.filter((row) => row.medium === 'EPISODE').length.toLocaleString() : '—';
    byId('discovery-literature-count').textContent = available
      ? directoryState.rows.filter((row) => row.medium === 'LITERATURE').length.toLocaleString() : '—';
    byId('discovery-state').textContent = message;
    if (!available) byId('discovery-metrics').textContent = 'No verified discovery index loaded; row counts are unknown.';
    renderDirectory();
    window.requestAnimationFrame(updateNavigationHint);
  }

  function renderDirectory() {
    const holder = byId('discovery-list');
    holder.replaceChildren();
    const empty = byId('discovery-empty');
    empty.hidden = true;
    if (!directoryState.available) {
      byId('discovery-summary').textContent = 'Discovery count unknown; no source-local index is available.';
      return;
    }
    const query = normalize(byId('discovery-query').value.trim());
    const medium = byId('discovery-medium').value;
    const series = byId('discovery-series').value;
    const kind = byId('discovery-kind').value;
    const lineage = byId('discovery-lineage').value;
    const overview = byId('discovery-overview').value;
    const verification = byId('discovery-verification').value;
    const publisherCheck = byId('discovery-publisher-check').value;
    const synopsis = byId('discovery-synopsis').value;
    const tag = byId('discovery-tag').value;
    const terms = query.split(/\s+/).filter(Boolean);
    const rows = directoryState.rows.filter((item) => {
      if (medium !== 'all' && item.medium !== medium) return false;
      if (kind !== 'all' && item.candidate_kind !== kind) return false;
      if (lineage !== 'all' && item.source_group !== lineage) return false;
      // The facet reflects only currently loaded and validated display-sidecar
      // records. A missing/failed appendix cannot masquerade as a reviewed read.
      const reviewedOverview = synopsisState.entries.get(artworkKey(item));
      const hasReviewedOverview = Boolean(reviewedOverview);
      if (overview === 'reviewed' && !hasReviewedOverview) return false;
      if (overview === 'not-loaded' && hasReviewedOverview) return false;
      const seriesCode = item.context.split(/\s+/, 1)[0];
      if (series !== 'all' && (item.medium !== 'EPISODE' || seriesCode !== series)) return false;
      const check = metadataRechecks.byId.get(item.row_id);
      const checkStatus = !check ? 'not_rechecked' : check.title_check === 'EXACT' ? 'rechecked_exact' : 'rechecked_unresolved';
      const publisherCard = publisherCardChecks.byId.get(item.row_id);
      const publisherCardStatus = !publisherCardChecks.available ? 'not_loaded' : !publisherCard ? 'not_in_batch'
        : publisherCard.publisher_title_check === 'EXACT' ? 'title_exact' : 'held_unresolved';
      const reviewed = hasReviewedOverview;
      if (verification !== 'all' && checkStatus !== verification) return false;
      if (publisherCheck !== 'all' && publisherCardStatus !== publisherCheck) return false;
      if (synopsis !== 'all' && (reviewed ? 'reviewed_publisher_paraphrase' : 'pending') !== synopsis) return false;
      if (tag !== 'all' && ![
        `medium:${item.medium.toLowerCase()}`, `kind:${item.candidate_kind.toLowerCase()}`,
        `source:${item.source_group.toLowerCase()}`, `metadata:${checkStatus}`,
        `publisher-card:${publisherCardStatus}`,
        `synopsis:${reviewed ? 'reviewed_publisher_paraphrase' : 'pending'}`,
        ...(item.medium === 'EPISODE' && Object.hasOwn(directorySeriesLabels, seriesCode) ? [`series:${seriesCode.toLowerCase()}`] : [])
      ].includes(tag)) return false;
      const seriesLabel = item.medium === 'EPISODE' && Object.hasOwn(directorySeriesLabels, seriesCode)
        ? directorySeriesLabels[seriesCode] : '';
      const body = normalize([item.title, item.context, seriesLabel,
        item.candidate_kind, item.source_group, item.source_input,
        publisherCard?.publisher_card_title, publisherCard?.source_batch,
        publisherCard?.publisher_title_check,
        ...item.details, reviewedOverview?.overview_text || ''].join(' '));
      return terms.every((part) => body.includes(part));
    });
    const visible = rows.slice(0, directoryState.limit);
    byId('discovery-summary').textContent = `${rows.length.toLocaleString()} source-local metadata rows match` +
      (visible.length < rows.length ? ` · Displaying ${visible.length.toLocaleString()}` : '') +
      '. These are not distinct or admitted Works.';
    if (!rows.length) { empty.hidden = false; return; }
    for (const item of visible) {
      const card = el('article', 'directory-card media-card');
      const copy = el('div', 'media-card-copy');
      card.append(makeArtworkSlot(item.medium, artworkKey(item)), copy);
      copy.append(el('span', 'kicker', `${item.medium.replaceAll('_', ' ')} · ${item.candidate_kind.replaceAll('_', ' ')}`));
      copy.append(el('h3', null, item.title));
      copy.append(el('p', 'directory-context', item.context));
      copy.append(el('p', 'directory-source', `${item.source_group} · unadmitted discovery · source-local`));
      const check = metadataRechecks.byId.get(item.row_id);
      if (check) {
        const exact = check.title_check === 'EXACT';
        copy.append(el('p', 'directory-recheck', exact
          ? `Official rendered metadata rechecked · ${check.recheck_batch} · ${check.observed_utc_date}`
          : `Official metadata read · ${check.recheck_batch} · title/identity ${check.title_check.replaceAll('_', ' ').toLowerCase()} · unresolved`));
        const evidence = el('a', 'directory-recheck-source', 'Inspect official metadata evidence page');
        evidence.href = check.official_evidence_url;
        evidence.rel = 'noopener noreferrer';
        evidence.target = '_blank';
        copy.append(evidence);
        copy.append(el('small', 'directory-provenance', `Observed fields: ${check.fields_observed.join(', ')} · rendered page; no raw-page custody, full-work read or identity admission`));
      }
      const publisherCard = publisherCardChecks.byId.get(item.row_id);
      if (publisherCard) {
        const exact = publisherCard.publisher_title_check === 'EXACT';
        copy.append(el('p', `directory-publisher-card${exact ? '' : ' held'}`, exact
          ? `Publisher card title string match · ${publisherCard.source_batch} · source-local metadata only`
          : `HELD / UNRESOLVED publisher card title or split · ${publisherCard.source_batch} · ${publisherCard.publisher_title_check.replaceAll('_', ' ').toLowerCase()}`));
        copy.append(el('p', 'directory-publisher-detail',
          `Rendered card: ${publisherCard.publisher_card_title} · ${publisherCard.publisher_season_episode_slots.map((slot) => `S${slot.season} E${slot.episode}`).join(' / ')} · ${publisherCard.observed_utc_date}`));
        if (publisherCard.publisher_guide_url) {
          const evidence = el('a', 'directory-recheck-source', 'Inspect publisher-card source');
          evidence.href = publisherCard.publisher_guide_url;
          evidence.rel = 'noopener noreferrer';
          evidence.target = '_blank';
          copy.append(evidence);
        }
        copy.append(el('small', 'directory-provenance',
          `Accepted source record: ${publisherCard.accepted_observation_path} · No audiovisual close read, raw publisher page custody, Work identity admission, or approved synopsis`));
      }
      appendSynopsis(copy, item.medium, artworkKey(item));
      copy.append(el('small', 'directory-provenance', `Data receipt: ${item.source_input}`));
      if (item.details.length) copy.append(el('p', 'directory-context', item.details.join(' · ')));
      if (item.source_locator) {
        const link = el('a', null, 'Inspect attributed source');
        link.href = item.source_locator;
        link.rel = 'noopener noreferrer';
        link.target = '_blank';
        copy.append(link);
      }
      holder.append(card);
    }
    if (visible.length < rows.length) {
      const button = el('button', 'directory-more', `Show next ${Math.min(40, rows.length - visible.length)} source rows`);
      button.type = 'button';
      button.addEventListener('click', () => {
        playTone();
        const firstNewCard = visible.length;
        directoryState.limit += 40;
        renderDirectory();
        focusNewPage(holder, firstNewCard);
      });
      holder.append(button);
    }
  }

  function acceptDirectory(data) {
    if (!data || typeof data !== 'object' || data.schema_version !== '1.0.0' ||
        data.data_status !== 'DISCOVERY_ONLY' || data.admission_effect !== 'NONE' ||
        data.coverage_effect !== 'NONE' || data.denominator_status !== 'NOT_ESTABLISHED' ||
        data.identity_scope !== 'SOURCE_LOCAL_NOT_DEDUPLICATED' ||
        !Array.isArray(data.rows) || !Array.isArray(data.source_digests) ||
        !Number.isSafeInteger(data.row_count) || data.row_count !== data.rows.length ||
        data.rows.length < 1 || data.rows.length > 5000) {
      throw new Error('Invalid multimedia discovery envelope.');
    }
    const seen = new Set();
    const counts = Object.fromEntries(directoryMediums.map((item) => [item, 0]));
    const seriesCounts = new Map();
    const kindCounts = new Map();
    const allowedHosts = new Set(['www.startrek.com', 'www.paramountplus.com', 'www.wikidata.org', 'www.simonandschuster.com', 'www.mikrosanimation.com', 'youtu.be', 'www.penguinrandomhouse.com']);
    // A URL on the host allowlist cannot by itself justify an unrelated
    // provenance badge. Keep source-lineage and retrieval-host scopes paired.
    const lineageHosts = new Map([
      ['wikidata:wdqs', new Set(['www.wikidata.org'])],
      ['publisher:paramount', new Set(['www.paramountplus.com', 'www.startrek.com', 'www.mikrosanimation.com', 'youtu.be'])],
      ['publisher:paramountplus.com', new Set(['www.paramountplus.com'])],
      ['publisher:startrek.com', new Set(['www.startrek.com'])],
      ['publisher:simonandschuster.com', new Set(['www.simonandschuster.com'])],
      ['distributor:penguinrandomhouse.com:titan-books', new Set(['www.penguinrandomhouse.com'])]
    ]);
    for (const item of data.rows) {
      if (!item || typeof item !== 'object' || Object.keys(item).sort().join('|') !== directoryFields.slice().sort().join('|') ||
          typeof item.row_id !== 'string' || !/^[a-z0-9:_.-]{3,210}$/.test(item.row_id) || seen.has(item.row_id) ||
          !directoryMediums.includes(item.medium) || !directoryKinds.includes(item.candidate_kind) ||
          typeof item.title !== 'string' || !item.title.trim() || item.title.length > 200 ||
          typeof item.context !== 'string' || !item.context.trim() || item.context.length > 160 ||
          typeof item.source_group !== 'string' || !lineageHosts.has(item.source_group) ||
          typeof item.source_input !== 'string' || !/^(?:explorer\/|proposals\/)[a-z0-9\/_.-]+\.json$/.test(item.source_input) ||
          !Array.isArray(item.details) || item.details.length > 8 || item.details.some((x) => typeof x !== 'string' || x.length > 150) ||
          item.verification_status !== 'UNVERIFIED_METADATA' || item.identity_scope !== 'SOURCE_LOCAL' ||
          item.coverage_effect !== 'NONE' || item.admission_effect !== 'NONE') {
        throw new Error('Invalid or promoted multimedia discovery row.');
      }
      if (item.source_locator === null && item.source_group !== 'wikidata:wdqs') {
        throw new Error('Publisher/distributor source-group claim needs a checkable retrieval locator.');
      }
      if (item.source_locator !== null) {
        let url;
        try { url = new URL(item.source_locator); } catch (_) { throw new Error('Invalid discovery source URL.'); }
        if (url.protocol !== 'https:' || !allowedHosts.has(url.hostname) ||
            !lineageHosts.get(item.source_group).has(url.hostname) || url.port || url.search || url.hash ||
            url.username || url.password || !url.pathname.startsWith('/') ||
            (url.hostname === 'www.penguinrandomhouse.com' &&
              (item.medium !== 'LITERATURE' || item.candidate_kind !== 'FICTIONAL_MEMOIR' ||
               item.source_group !== 'distributor:penguinrandomhouse.com:titan-books' ||
               !/^\/books\/[1-9][0-9]*\/[a-z0-9-]+\/$/.test(url.pathname))) ||
            (url.hostname === 'youtu.be' &&
              !/^https:\/\/youtu\.be\/[A-Za-z0-9_-]{11}$/.test(item.source_locator))) {
          throw new Error('Source URL outside the explicit publisher/catalog allowlist.');
        }
      }
      seen.add(item.row_id); counts[item.medium]++;
      kindCounts.set(item.candidate_kind, (kindCounts.get(item.candidate_kind) || 0) + 1);
      if (item.medium === 'EPISODE') {
        const seriesCode = item.context.split(/\s+/, 1)[0];
        if (Object.hasOwn(directorySeriesLabels, seriesCode)) {
          seriesCounts.set(seriesCode, (seriesCounts.get(seriesCode) || 0) + 1);
        }
      }
    }
    if (!data.counts_by_medium || directoryMediums.some((key) => data.counts_by_medium[key] !== counts[key]) ||
        Object.keys(data.counts_by_medium).length !== directoryMediums.length || data.source_digests.length < 4 ||
        data.source_digests.some((x) => !x || !/^[0-9a-f]{64}$/.test(x.sha256 || '') ||
          typeof x.path !== 'string' || !/^(?:explorer\/|proposals\/)[a-z0-9\/_.-]+\.(?:json|csv)$/.test(x.path))) {
      throw new Error('Source digests or medium counts fail validation.');
    }
    directoryState.rows = data.rows;
    directoryState.limit = 40;
    for (const [selectId, values, label] of [
      ['discovery-medium', directoryMediums, 'All media'],
      ['discovery-series', [...seriesCounts.keys()].sort((a, b) => directorySeriesLabels[a].localeCompare(directorySeriesLabels[b])), 'All series'],
      ['discovery-kind', [...kindCounts.keys()].sort(), 'All candidate types'],
      ['discovery-lineage', [...new Set(data.rows.map((row) => row.source_group))].sort(), 'All sources']
    ]) {
      const select = byId(selectId);
      select.replaceChildren(new Option(label, 'all'));
      for (const value of values) {
        const label = selectId === 'discovery-series'
          ? `${directorySeriesLabels[value]} · ${seriesCounts.get(value)} source rows`
          : selectId === 'discovery-kind'
            ? `${value.replaceAll('_', ' ')} · ${kindCounts.get(value)} source rows`
          : value.replaceAll('_', ' ');
        select.add(new Option(label, value));
      }
      select.value = 'all';
    }
    const tagSelect = byId('discovery-tag');
    tagSelect.replaceChildren(new Option('All source-grounded tags', 'all'));
    const structuralTags = [
      ...directoryMediums.map((value) => `medium:${value.toLowerCase()}`),
      ...[...kindCounts.keys()].map((value) => `kind:${value.toLowerCase()}`),
      ...[...seriesCounts.keys()].map((value) => `series:${value.toLowerCase()}`),
      ...[...new Set(data.rows.map((row) => row.source_group))].map((value) => `source:${value.toLowerCase()}`),
      'metadata:not_rechecked', 'metadata:rechecked_exact', 'metadata:rechecked_unresolved',
      'publisher-card:not_in_batch', 'publisher-card:title_exact', 'publisher-card:held_unresolved',
      'synopsis:pending', 'synopsis:reviewed_publisher_paraphrase'
    ];
    for (const tag of structuralTags.sort()) tagSelect.add(new Option(tag.replaceAll('_', ' '), tag));
    tagSelect.value = 'all';
    const metrics = byId('discovery-metrics');
    metrics.replaceChildren();
    for (const label of directoryMediums) {
      const name = {
        EPISODE: 'Episode refs', FILM: 'Film rows', LITERATURE: 'Literary leads',
        SHORT_FORM: 'Short-form releases', AUDIO: 'Audio containers'
      }[label];
      metrics.append(el('span', null, `${name}: ${counts[label].toLocaleString()}`));
    }
    setDirectoryAvailability(true, `${data.rows.length.toLocaleString()} source-local discovery rows loaded; not a franchise total or admitted continuity record count.`);
  }

  async function loadDirectory() {
    try {
      const response = await fetch('./discovery-catalog.json', { cache: 'no-store' });
      if (response.status === 404) {
        setDirectoryAvailability(false, 'The optional multimedia directory has not been published yet.');
        return;
      }
      if (!response.ok) throw new Error(`Directory request returned HTTP ${response.status}.`);
      acceptDirectory(await response.json());
    } catch (error) {
      setDirectoryAvailability(false, `Multimedia discovery data rejected: ${error.message || 'Check discovery-catalog.json.'}`);
    }
  }

  function acceptMetadataRechecks(data) {
    if (!directoryState.available || !data || typeof data !== 'object' ||
        data.schema_version !== '1.0.0' || data.data_status !== 'SOURCE_LOCAL_RENDERED_METADATA_RECHECKS_DISPLAY_ONLY' ||
        data.coverage_effect !== 'NONE' || data.admission_effect !== 'NONE' ||
        data.source_local_row_count !== directoryState.rows.length || data.source_local_row_count !== 1214 ||
        data.embedded_research_lead_rows !== 218 || data.embedded_research_leads_rechecked !== 51 ||
        data.embedded_research_leads_not_rechecked !== 167 || data.literary_directory_rows_rechecked !== 5 ||
        data.rendered_metadata_rechecks !== 56 || data.unrechecked_source_local_rows !== 1158 ||
        data.exact_title_matches !== 52 || data.unresolved_title_or_multipart_cases !== 4 ||
        data.raw_webpage_bytes_custodied !== 0 || data.admitted_works_or_evidence !== 0 ||
        !Array.isArray(data.input_observation_receipts) || data.input_observation_receipts.length !== 5 ||
        !Array.isArray(data.rows) || data.rows.length !== 56) {
      throw new Error('Unreviewed or promoted metadata recheck envelope.');
    }
    const directoryRows = new Map(directoryState.rows.map((row) => [row.row_id, row]));
    const checkKeys = ['row_id', 'medium', 'source_local_title', 'source_local_context', 'source_local_group',
      'source_local_input', 'source_local_locator', 'recheck_batch', 'official_observed_title',
      'official_evidence_url', 'official_section_locator', 'observed_utc_date', 'title_check',
      'fields_observed', 'source_observation_path', 'source_observation_sha256',
      'source_representation', 'official_source_family', 'raw_webpage_sha256',
      'source_local_discovery_state', 'governed_research_coverage_state', 'synopsis_publication_effect',
      'admission_effect', 'coverage_effect'];
    const accepted = new Map();
    let exact = 0;
    let leadCount = 0;
    let literatureCount = 0;
    for (const item of data.rows) {
      const row = directoryRows.get(item?.row_id);
      if (!row || accepted.has(item.row_id) ||
          Object.keys(item).sort().join('|') !== checkKeys.slice().sort().join('|') ||
          item.source_local_title !== row.title || item.source_local_context !== row.context ||
          item.source_local_group !== row.source_group || item.source_local_input !== row.source_input ||
          item.source_local_locator !== row.source_locator || item.medium !== row.medium ||
          !['B001', 'B002', 'B003', 'B004'].includes(item.recheck_batch) ||
          !['EXACT', 'UNRESOLVED_PUNCTUATION', 'UNRESOLVED_CASE', 'UNRESOLVED_MULTIPART'].includes(item.title_check) ||
          (item.title_check === 'EXACT') !== (item.official_observed_title === row.title) ||
          !/^2026-11-03$/.test(item.observed_utc_date) ||
          !Array.isArray(item.fields_observed) || !item.fields_observed.length ||
          item.fields_observed.some((value) => typeof value !== 'string' || !/^[a-z_]+$/.test(value)) ||
          typeof item.official_section_locator !== 'string' || !item.official_section_locator ||
          !/^proposals\/verification\/[a-z0-9/_-]+\.json$/.test(item.source_observation_path) ||
          !/^[0-9a-f]{64}$/.test(item.source_observation_sha256) ||
          item.source_representation !== 'RENDERED_OFFICIAL_METADATA_NOT_RAW_PAGE_CUSTODY' ||
          item.raw_webpage_sha256 !== null ||
          item.source_local_discovery_state !== 'CATALOGUED_METADATA_ONLY' ||
          item.governed_research_coverage_state !== 'NOT_ADMITTED' ||
          item.synopsis_publication_effect !== 'NONE' || item.coverage_effect !== 'NONE' || item.admission_effect !== 'NONE') {
        throw new Error('Metadata badge would change source-local evidence or coverage status.');
      }
      let source;
      try { source = new URL(item.official_evidence_url); } catch (_) { throw new Error('Invalid official recheck URL.'); }
      if (source.protocol !== 'https:' || !['www.paramountplus.com', 'www.simonandschuster.com',
          'www.penguinrandomhouse.com'].includes(source.hostname) || source.port || source.search || source.hash ||
          source.username || source.password) {
        throw new Error('Metadata recheck source outside accepted official publisher domains.');
      }
      if (row.medium === 'EPISODE' && (source.hostname !== 'www.paramountplus.com' ||
          item.official_source_family !== 'paramount_corporate_publisher_family')) {
        throw new Error('Episode check lacks official Paramount lineage.');
      }
      accepted.set(item.row_id, item);
      if (item.title_check === 'EXACT') exact++;
      if (item.row_id.startsWith('lead:')) leadCount++;
      if (item.medium === 'LITERATURE') literatureCount++;
    }
    if (exact !== 52 || leadCount !== 51 || literatureCount !== 5) {
      throw new Error('Unexpected source-local metadata check breakdown.');
    }
    metadataRechecks.byId = accepted;
    metadataRechecks.available = true;
    byId('discovery-metrics').append(el('span', 'directory-recheck-count',
      'Official rendered metadata rechecked: 56 / 1,214 rows · 51 / 218 embedded research leads · 5 / 9 literary leads · 4 unresolved title/multipart cases'));
    renderDirectory();
  }

  async function loadMetadataRechecks() {
    try {
      const response = await fetch('./metadata-rechecks.json', { cache: 'no-store' });
      if (!response.ok) return; // Optional fail-closed projection: no badge on missing/stale Pages release.
      if (!globalThis.crypto?.subtle || typeof TextDecoder !== 'function') return;
      const bytes = await response.arrayBuffer();
      if (bytes.byteLength > 150000 || bytes.byteLength < 1000) return;
      const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const hex = Array.from(new Uint8Array(digest), (x) => x.toString(16).padStart(2, '0')).join('');
      if (hex !== metadataRecheckSha256) return;
      acceptMetadataRechecks(JSON.parse(new TextDecoder().decode(bytes)));
    } catch (_) {
      // A corrupt or unavailable projection cannot promote a discovery row.
      metadataRechecks.byId.clear();
      metadataRechecks.available = false;
    }
  }

  function acceptPublisherCardChecks(data) {
    if (!directoryState.available || !data || typeof data !== 'object' ||
        data.schema_version !== '1.0.0' ||
        data.data_status !== 'ACCEPTED_SOURCE_ONLY_RENDERED_PUBLISHER_CARDS_NOT_RESEARCH_COVERAGE' ||
        data.directory_row_count !== 1214 || directoryState.rows.length !== 1214 ||
        data.prior_metadata_recheck_count_unchanged !== 56 ||
        data.new_publisher_card_source_local_lead_count !== 61 ||
        data.new_exact_title_matches !== 46 || data.new_unresolved_title_or_split_cases !== 15 ||
        data.unmapped_snw_s3_cards_not_joined !== 10 ||
        data.publisher_source_family_count !== 1 ||
        data.upstream_wikidata_is_not_independent_corroboration !== true ||
        data.source_directory_sha256 !== '2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc' ||
        data.admitted_works !== 0 || data.approved_public_synopses !== 0 ||
        data.full_audiovisual_content_reads !== 0 || data.raw_publisher_pages_custodied !== 0 ||
        data.coverage_effect !== 'NONE' || data.admission_effect !== 'NONE' ||
        !Array.isArray(data.accepted_input_receipts) || data.accepted_input_receipts.length !== 9 ||
        !Array.isArray(data.rows) || data.rows.length !== 61) {
      throw new Error('Unapproved publisher-card metadata envelope.');
    }
    const batchSpecifications = new Map([
      ['B005-DS9', { series: 'DS9', begin: 51, end: 66, path: 'proposals/verification/episode-guide-rechecks-b005-20261103/observations.json', allowed: ['EXACT', 'CASE_VARIANT_UNRESOLVED'] }],
      ['B006-VOY', { series: 'VOY', begin: 70, end: 82, path: 'proposals/verification/episode-guide-rechecks-b006-voy-20261103/observations.json', allowed: ['EXACT', 'CASE_VARIANT_UNRESOLVED', 'MULTIPART_TITLE_SCOPE_UNRESOLVED'] }],
      ['B007-VOY', { series: 'VOY', begin: 83, end: 89, path: 'proposals/librarian/voy-b007-source-card-20261103/records.json', allowed: ['EXACT', 'ROMAN_NUMERAL_VARIANT_UNRESOLVED', 'NUMERAL_AND_CASE_VARIANT_UNRESOLVED'] }],
      ['B008-ENT', { series: 'ENT', begin: 90, end: 98, path: 'proposals/verification/episode-guide-rechecks-b008-ent-20261103/observations.json', allowed: ['EXACT_OFFICIAL_CARD_TITLE', 'ROMAN_NUMERAL_VARIANT_UNRESOLVED'] }],
      ['B009-ENT', { series: 'ENT', begin: 99, end: 107, path: 'proposals/verification/episode-guide-rechecks-b009-ent-20261103/observations.json', allowed: ['EXACT_OFFICIAL_CARD_TITLE', 'PART_NUMERAL_STYLE_UNRESOLVED', 'PUNCTUATION_STYLE_UNRESOLVED', 'COMBINED_CARD_SPLIT_UNRESOLVED'] }],
      ['DIS-S3-SEVEN', { series: 'DIS', begin: 108, end: 114, path: 'proposals/research/dis/s3-publisher-seven-20261103/records.json', allowed: ['EXACT', 'PART_NUMERAL_STYLE_UNRESOLVED'] }]
    ]);
    const receiptPaths = ['explorer/discovery-catalog.json', ...[...batchSpecifications.values()].map((spec) => spec.path),
      'proposals/research/snw/s3-publisher-first5-20261103/records.json',
      'proposals/research/snw/s3-publisher-last5-20261103/records.json'];
    const receipts = new Map();
    for (let i = 0; i < receiptPaths.length; i++) {
      const receipt = data.accepted_input_receipts[i];
      if (!receipt || receipt.path !== receiptPaths[i] || !/^[0-9a-f]{64}$/.test(receipt.sha256)) {
        throw new Error('Publisher-card accepted source receipt mismatch.');
      }
      receipts.set(receipt.path, receipt.sha256);
    }
    if (receipts.get('explorer/discovery-catalog.json') !== data.source_directory_sha256) {
      throw new Error('Publisher-card directory receipt mismatch.');
    }
    const sourceRows = new Map(directoryState.rows.map((item) => [item.row_id, item]));
    const itemKeys = ['accepted_observation_path', 'accepted_observation_sha256', 'admission_effect',
      'coverage_effect', 'full_episode_or_transcript_read', 'medium', 'observed_utc_date',
      'original_resolution', 'publisher_card_title', 'publisher_family', 'publisher_guide_url',
      'publisher_season_episode_slots', 'publisher_surface', 'publisher_title_check',
      'raw_publisher_page_sha256', 'row_id', 'source_batch', 'source_local_context',
      'source_local_discovery_state', 'source_local_locator', 'source_local_source_family',
      'source_local_title', 'synopsis_publication_effect'];
    const checked = new Map();
    let exact = 0;
    for (const item of data.rows) {
      const spec = batchSpecifications.get(item?.source_batch);
      const row = sourceRows.get(item?.row_id);
      const idNumber = /^lead:\d{4}$/.test(item?.row_id || '') ? Number(item.row_id.slice(5)) : -1;
      const exactTitle = item?.publisher_title_check === 'EXACT';
      if (!spec || !row || checked.has(item.row_id) ||
          Object.keys(item).sort().join('|') !== itemKeys.slice().sort().join('|') ||
          idNumber < spec.begin || idNumber > spec.end || row.medium !== 'EPISODE' ||
          item.medium !== 'EPISODE' || item.source_local_context !== spec.series ||
          item.source_local_context !== row.context || item.source_local_title !== row.title ||
          item.source_local_locator !== row.source_locator ||
          item.source_local_source_family !== 'wikidata:wdqs' || row.source_group !== 'wikidata:wdqs' ||
          item.publisher_family !== 'paramount_corporate_publisher_family' ||
          item.accepted_observation_path !== spec.path ||
          item.accepted_observation_sha256 !== receipts.get(spec.path) ||
          !spec.allowed.includes(item.original_resolution) ||
          item.publisher_title_check !== (item.original_resolution === 'EXACT' ||
            item.original_resolution === 'EXACT_OFFICIAL_CARD_TITLE' ? 'EXACT' : item.original_resolution) ||
          typeof item.publisher_card_title !== 'string' || !item.publisher_card_title.trim() ||
          item.publisher_card_title.length > 200 ||
          exactTitle !== (item.publisher_card_title === row.title) ||
          !/^2026-11-03$/.test(item.observed_utc_date) ||
          item.publisher_surface !== 'RENDERED_PUBLISHER_CARD_SOURCE_ONLY' ||
          item.raw_publisher_page_sha256 !== null || item.full_episode_or_transcript_read !== false ||
          item.source_local_discovery_state !== 'CATALOGUED_METADATA_ONLY' ||
          item.admission_effect !== 'NONE' || item.coverage_effect !== 'NONE' ||
          item.synopsis_publication_effect !== 'NONE' ||
          !Array.isArray(item.publisher_season_episode_slots) ||
          item.publisher_season_episode_slots.length < 1 || item.publisher_season_episode_slots.length > 2 ||
          item.publisher_season_episode_slots.some((slot) => !slot ||
            Object.keys(slot).sort().join('|') !== 'episode|season' ||
            !Number.isSafeInteger(slot.season) || !Number.isSafeInteger(slot.episode) ||
            slot.season < 1 || slot.episode < 1 || slot.season > 10 || slot.episode > 50)) {
        throw new Error('Publisher-card status, source ID, provenance, or coverage spoof rejected.');
      }
      const guide = item.publisher_guide_url;
      if (guide !== null) {
        let url;
        try { url = new URL(guide); } catch (_) { throw new Error('Invalid publisher-card guide URL.'); }
        if (url.protocol !== 'https:' || url.hostname !== 'www.paramountplus.com' ||
            url.username || url.password || url.port || url.search || url.hash) {
          throw new Error('Publisher-card guide URL outside accepted first-party host.');
        }
      }
      if ((item.source_batch === 'B007-VOY' || item.source_batch === 'DIS-S3-SEVEN') !== (guide !== null)) {
        throw new Error('Publisher-card URL custody changed from accepted source record.');
      }
      checked.set(item.row_id, item);
      if (exactTitle) exact++;
    }
    if (checked.size !== 61 || exact !== 46 ||
        (checked.get('lead:0106')?.publisher_title_check !== 'COMBINED_CARD_SPLIT_UNRESOLVED') ||
        (checked.get('lead:0107')?.publisher_title_check !== 'COMBINED_CARD_SPLIT_UNRESOLVED') ||
        checked.get('lead:0106')?.publisher_card_title !== checked.get('lead:0107')?.publisher_card_title) {
      throw new Error('Publisher-card accepted source-local scope or unresolved split changed.');
    }
    publisherCardChecks.byId = checked;
    publisherCardChecks.available = true;
    byId('publisher-card-state').textContent =
      '61 additional accepted publisher-card reads: 46 exact title-string matches, 15 held/unresolved. One Paramount publisher lineage; 10 SNW cards unjoined. No Work admission, audiovisual close read, or new approved synopsis.';
    byId('publisher-card-download').hidden = false;
    byId('discovery-metrics').append(el('span', 'publisher-card-count',
      'Additional source-local publisher cards: 61 (46 title matches · 15 held), separate from 56 checks'));
    renderDirectory();
  }

  async function loadPublisherCardChecks() {
    try {
      const response = await fetch('./accepted-source-card-rechecks.json', { cache: 'no-store' });
      if (!response.ok) throw new Error('Publisher-card sidecar unavailable.');
      if (!globalThis.crypto?.subtle || typeof TextDecoder !== 'function') throw new Error('Publisher-card digest unavailable.');
      const bytes = await response.arrayBuffer();
      if (bytes.byteLength < 1000 || bytes.byteLength > 130000) throw new Error('Publisher-card bytes outside accepted scope.');
      const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
      const hex = Array.from(new Uint8Array(digest), (x) => x.toString(16).padStart(2, '0')).join('');
      if (hex !== publisherCardSha256) throw new Error('Publisher-card bytes differ from accepted projection.');
      acceptPublisherCardChecks(JSON.parse(new TextDecoder().decode(bytes)));
    } catch (_) {
      // This is an optional source-only layer; don't disturb directory,
      // B001–B004 badges, reviewed synopses, or separate ISBN edition shelf.
      publisherCardChecks.byId.clear();
      publisherCardChecks.available = false;
    }
    if (!publisherCardChecks.available) {
      byId('publisher-card-state').textContent = 'Additional publisher-card checks unavailable or rejected; their state is not loaded, not zero. Directory and older metadata remain separate.';
      byId('publisher-card-download').hidden = true;
      renderDirectory();
    }
  }

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
    controls.kind.disabled = kinds.length === 0;
    controls.kind.title = kinds.length ? '' : 'No admitted continuity records to filter by kind.';
    const statuses = [...new Set([
      ...state.briefings.map((r) => asString(r.admission_status)),
      ...state.records.map((r) => asString(r.projection_status))
    ].filter(Boolean))].sort();
    setSelectOptions(controls.status, statuses.map((status) => [status, humanize(status)]), 'All statuses');
    controls.status.disabled = statuses.length === 0;
    controls.status.title = statuses.length ? '' : 'No admitted research statuses to filter.';
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
    appendSynopsis(card, 'EPISODE', `research:${row.episode_qid || `${row.mission_id}:${row.season_number}:${row.episode_number}`}`);
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
    byId('research-top-count').textContent = available ? researchState.leads.length.toLocaleString() : '—';
    byId('research-nav-count').textContent = available ? researchState.leads.length.toLocaleString() : '—';
    byId('research-state').textContent = message;
    renderResearch();
    // Mission cards must reflect the same validated candidate-only snapshot.
    render();
    window.requestAnimationFrame(updateNavigationHint);
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
    if (state.dataStatus === 'NOT_BUILT') {
      for (const section of ['missions', 'briefings', 'records']) byId(section).hidden = true;
      byId('result-summary').textContent = 'Catalog unavailable; the number of matching entries is unknown.';
      return;
    }
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
    byId('mission-count').textContent = '—';
    byId('briefing-count').textContent = '—';
    byId('record-count').textContent = '—';
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

  // This is a small, deterministic local-search *character interface*, not a
  // model or a semantic/canon engine. It consumes only the same validated
  // source-local shelves the Explorer has already admitted for display.
  const loreToggle = byId('lore-toggle');
  const lorePanel = byId('lore-console');
  const loreClose = byId('lore-close');
  const loreForm = byId('lore-form');
  const loreQuery = byId('lore-query');
  const loreAnswer = byId('lore-answer');
  const setLoreOpen = (open) => {
    lorePanel.hidden = !open;
    loreToggle.setAttribute('aria-expanded', String(open));
    loreToggle.textContent = open ? 'Close Lore console' : 'Open Lore console';
    if (open) loreQuery.focus();
    else loreToggle.focus();
  };
  loreToggle.addEventListener('click', () => { playTone(); setLoreOpen(lorePanel.hidden); });
  loreClose.addEventListener('click', () => setLoreOpen(false));
  lorePanel.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') { event.preventDefault(); setLoreOpen(false); }
  });

  const addLoreShortcut = (label, targetId, queryField, renderView, query) => {
    const button = el('button', '', label);
    button.type = 'button';
    button.addEventListener('click', () => {
      queryField.value = query;
      renderView();
      byId(targetId).scrollIntoView({ block: 'start' });
      queryField.focus();
    });
    loreAnswer.append(button);
  };
  loreForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const typed = loreQuery.value.trim();
    loreAnswer.replaceChildren();
    if (!typed || typed.length > 100) {
      loreAnswer.append(el('p', '', 'Enter a subject of 1–100 characters. I am a local index search, not a guessing machine.'));
      return;
    }
    if (/^(hello|hi|help|who are you|status)\??$/i.test(typed)) {
      loreAnswer.append(el('p', '', 'Fictional Lore interface online. My considerable talents are confined to searching validated local metadata. Try an episode title, a series, or a book title.'));
      return;
    }
    const terms = normalize(typed).split(/\s+/).filter(Boolean);
    const directoryMatches = directoryState.available ? directoryState.rows.filter((item) => {
      const seriesCode = item.medium === 'EPISODE' ? item.context.split(/\s+/, 1)[0] : '';
      const series = Object.hasOwn(directorySeriesLabels, seriesCode) ? directorySeriesLabels[seriesCode] : '';
      return terms.every((term) => normalize([item.title, item.context, series, item.medium, item.candidate_kind].join(' ')).includes(term));
    }) : [];
    const guideMatches = episodeSourceState.available ? episodeSourceState.rows.filter((row) =>
      terms.every((term) => normalize([row.title, row.series_title, `S${row.season}E${String(row.episode).padStart(2, '0')}`,
        ...row.publisher_utterance_labels, ...row.tags].join(' ')).includes(term))) : [];
    if (!directoryState.available && !episodeSourceState.available) {
      loreAnswer.append(el('p', '', 'Neither validated local shelf is available. No result count or factual answer can be established.'));
      return;
    }
    if (!directoryMatches.length && !guideMatches.length) {
      loreAnswer.append(el('p', '', `No matching source-local rows for “${typed}” in the loaded shelves. This is not evidence that a subject is absent from Star Trek.`));
      if (!directoryState.available || !episodeSourceState.available) {
        loreAnswer.append(el('p', 'lore-row-label', 'One or more shelves could not be checked.'));
      }
      return;
    }
    const directoryCount = directoryState.available ? `${directoryMatches.length} directory observations` : 'Directory shelf unavailable';
    const guideCount = episodeSourceState.available ? `${guideMatches.length} HELD publisher-guide cards` : 'Publisher-guide shelf unavailable';
    loreAnswer.append(el('p', '', `${directoryCount} / ${guideCount} match “${typed}”. These are source-local records, not unique Works, confirmed events, or canonical answers.`));
    const results = el('ul');
    const sample = [
      ...directoryMatches.slice(0, 3).map((row) => ({ title: row.title, detail: `${row.medium.replaceAll('_', ' ')} · ${row.context} · source group: ${row.source_group}` })),
      ...guideMatches.slice(0, 3).map((row) => ({ title: row.title, detail: `${row.series_title} · S${row.season}E${String(row.episode).padStart(2, '0')} · HELD: ${row.publisher_family}` }))
    ].slice(0, 5);
    for (const item of sample) {
      const row = el('li');
      row.append(el('strong', '', item.title), el('span', 'lore-row-label', ` — ${item.detail}`));
      results.append(row);
    }
    loreAnswer.append(results);
    if (directoryMatches.length) addLoreShortcut('Inspect directory matches', 'discovery-directory', byId('discovery-query'), renderDirectory, typed);
    if (guideMatches.length) addLoreShortcut('Inspect held guide cards', 'episode-source-cards', byId('episode-source-query'), renderEpisodeSourceCards, typed);
    if (!directoryState.available || !episodeSourceState.available) {
      loreAnswer.append(el('p', 'lore-row-label', 'Unavailable shelves were excluded; their result counts are unknown.'));
    }
  });

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
  const filmFilters = byId('film-filters');
  filmFilters.addEventListener('input', renderFilms);
  filmFilters.addEventListener('change', () => { playTone(); renderFilms(); });
  filmFilters.addEventListener('submit', (event) => { event.preventDefault(); renderFilms(); });
  filmFilters.addEventListener('reset', () => window.requestAnimationFrame(renderFilms));
  const directoryFilters = byId('discovery-filters');
  directoryFilters.addEventListener('input', () => { directoryState.limit = 40; renderDirectory(); });
  directoryFilters.addEventListener('change', () => { playTone(); directoryState.limit = 40; renderDirectory(); });
  directoryFilters.addEventListener('submit', (event) => { event.preventDefault(); renderDirectory(); });
  directoryFilters.addEventListener('reset', () => { directoryState.limit = 40; window.requestAnimationFrame(renderDirectory); });
  // Status-board counts are drilldowns, not merely links to an unfiltered list.
  // Reset stale facets first so a count always opens its complete source-local
  // category without implying any of these rows are admitted Works.
  for (const [linkId, medium] of [
    ['discovery-episode-count', 'EPISODE'],
    ['discovery-literature-count', 'LITERATURE']
  ]) {
    byId(linkId).addEventListener('click', () => {
      if (!directoryState.available) return;
      byId('discovery-query').value = '';
      for (const id of ['discovery-series', 'discovery-kind', 'discovery-lineage',
        'discovery-overview', 'discovery-verification', 'discovery-publisher-check',
        'discovery-synopsis', 'discovery-tag']) byId(id).value = 'all';
      byId('discovery-medium').value = medium;
      directoryState.limit = 40;
      renderDirectory();
      // Keep keyboard/screen-reader focus with the destination after the
      // category and results update, rather than stranded on the status link.
      byId('discovery-directory').focus();
    });
  }
  const publisherEditionFilters = byId('publisher-edition-filters');
  publisherEditionFilters.addEventListener('input', renderPublisherEditionLeads);
  publisherEditionFilters.addEventListener('change', () => { playTone(); renderPublisherEditionLeads(); });
  publisherEditionFilters.addEventListener('submit', (event) => { event.preventDefault(); renderPublisherEditionLeads(); });
  publisherEditionFilters.addEventListener('reset', () => window.requestAnimationFrame(renderPublisherEditionLeads));
  const publisherIsbnFilters = byId('publisher-isbn-filters');
  publisherIsbnFilters.addEventListener('input', () => { publisherIsbnState.limit = 12; renderPublisherIsbnCrosschecks(); });
  publisherIsbnFilters.addEventListener('change', () => { playTone(); publisherIsbnState.limit = 12; renderPublisherIsbnCrosschecks(); });
  publisherIsbnFilters.addEventListener('submit', (event) => { event.preventDefault(); renderPublisherIsbnCrosschecks(); });
  publisherIsbnFilters.addEventListener('reset', () => { publisherIsbnState.limit = 12; window.requestAnimationFrame(renderPublisherIsbnCrosschecks); });
  const paramountFilters = byId('paramount-filters');
  paramountFilters.addEventListener('input', renderParamountRechecks);
  paramountFilters.addEventListener('change', () => { playTone(); renderParamountRechecks(); });
  paramountFilters.addEventListener('submit', (event) => { event.preventDefault(); renderParamountRechecks(); });
  paramountFilters.addEventListener('reset', () => window.requestAnimationFrame(renderParamountRechecks));
  const episodeSourceFilters = byId('episode-source-filters');
  episodeSourceFilters.addEventListener('input', renderEpisodeSourceCards);
  episodeSourceFilters.addEventListener('change', () => { playTone(); renderEpisodeSourceCards(); });
  episodeSourceFilters.addEventListener('submit', (event) => { event.preventDefault(); renderEpisodeSourceCards(); });
  episodeSourceFilters.addEventListener('reset', () => window.requestAnimationFrame(renderEpisodeSourceCards));
  setResearchAvailability(false, 'Checking for a separate research-leads index…');
  setFilmAvailability(false, 'Checking the separate film catalog…');
  setDirectoryAvailability(false, 'Checking the optional multimedia discovery catalog…');
  setPublisherEditionAvailability(false, 'Checking the independently indexed publisher-edition sidecar…');
  setPublisherIsbnAvailability(false, 'Checking accepted public publisher ISBN source-local metadata…');
  setParamountAvailability(false, 'Checking accepted public Paramount film-page metadata…');
  setEpisodeSourceAvailability(false, 'Checking accepted HELD publisher episode-guide cards…');
  // Separate publisher discovery is not an admission lane and must not depend
  // on an unrelated governed Mission index being available.
  Promise.all([loadFilmCatalog(), loadDirectory(), loadPublisherEditionIndex(), loadPublisherIsbnCrosschecks(), loadParamountRechecks(), loadEpisodeSourceCards()]).then(() => Promise.all([
    loadArtworkCatalog(), loadSynopsisCatalog().then(loadShortSynopsisCatalog),
    loadMetadataRechecks(), loadPublisherCardChecks()
  ]));
  loadIndex();
})();
