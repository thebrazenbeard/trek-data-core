# Held Draft-PR suitability — Explorer original reference cards

**Reviewer:** Explorer implementation author (INTERNAL_REVIEW). **Accepted repository baseline:** `main@3028765359001b90bc3e6b5c1835ee283b326e91`. **Dependency:** original local Librarian metadata/rights contract `d43c2f10a11758b2ec300c4c783a8f5f239c3944` copied without editing via local cherry-pick `02b3c92`. **Public effect:** none.

## Scoped draft assessment

**Technical draft suitability: YES, as a visibly HELD proposal only.** Six distinct same-origin original procedural SVG files, their deterministic manifest, and static preview can be code-reviewed without distributing copyrighted artwork. The exact six source-local row keys are included; every row remains `UNVERIFIED_METADATA`, `SOURCE_LOCAL`, no edition binding, and no coverage effect. The renderer only generates geometric vectors and metadata text. The gallery HTML loads its six *local generated SVGs*; publisher/Wikidata URLs are ordinary links triggered only by an explicit click. It does not read owner-private files or introduce external image requests.

**Protected public release: NO.** The Librarian contract itself says `public_release_eligible=false`. The public Pages Explorer must not begin loading these images or the new preview until separately reviewed and explicitly authorized. In particular, publisher URLs and book titles do not grant cover/still/poster image rights.

**Owner-private 347-entry OPF UI:** removed from this candidate's ancestry. The isolated art-only proposal branches from accepted `main`, importing only the six-row Librarian reference-card contract, generator, tests, and six original SVG gallery. No owner-private-derived 347-entry title preview, ebook file path, book body, OPF manifest, or member metadata appears in the diff. This does **not** certify the six source-local metadata titles as accepted Works.

## Verification classes

- **SOURCE_INSPECTION:** pinned 1,214-row source-local directory, accepted 347 OPF derivative, original SVG renderer, six-record held Librarian contract; no original ebook/episode/film-source close read.
- **TEST:** six SVGs byte-identical with deterministic generator; XML vocabulary excludes image/script/foreignObject/href/url; hostile title/locator/art-path mutation rejected; source IDs, statuses, no cover rights preserved. Full repo test suites and artwork release validators passed at local checkpoint.
- **VISUAL:** one generated SVG was rasterized with local Sharp at **640×360** and inspected as an original graphic, not a site screenshot. The visible title and `ABSTRACT PLACEHOLDER · NOT OFFICIAL ART` caption render; this does **not** validate the HTML layout or browser CSP.
- **REAL_BROWSER:** blocked: no local Playwright Chromium/Firefox/WebKit executable. No real 320/390/desktop screenshots, computed contrast or tab-order trace. An independent browser/accessibility and owner privacy review remain required.

> **Hostile challenge:** source-keyed graphics could be misconstrued as licensed artwork or verified catalog entries. Keep the explicit category-specific “NO EPISODE STILL / NO FILM POSTER / NO BOOK JACKET” notices and never convert `rechecked_exact` into a canonical `VERIFIED` badge.
