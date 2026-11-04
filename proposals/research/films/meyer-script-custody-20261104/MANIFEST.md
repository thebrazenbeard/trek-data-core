# FILMS — Nicholas Meyer archival script-access inventory (HELD)

**2026-11-04 · FILMS researcher · proposal only** against accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91`. This is a three-film **source-access tranche**, not film viewing or screenplay close reading. The exact source objects read are *institutional finding-aid pages*. They describe archival script artifacts but **do not contain the scripts**.

| Candidate film | Archival source lead actually observed | Access status |
| --- | --- | --- |
| `film-wrath-of-khan` | University of Iowa Nicholas Meyer Papers MsC425, old register **Box 48**: revised final draft (1982-01-18) and **release dialogue script** (1982-05-24) | `HELD`: metadata read, not manuscript |
| `film-voyage-home` | Same old register **Box 49**: incomplete revised first act (1985-10-18), revisions (1985-11-07–12), scripts/correspondence (Feb–Mar 1986) | `HELD`: metadata read, not manuscript |
| `film-undiscovered-country` | Same old register **Boxes 49–50**: color-coded screenplay revisions; a *complete script* entry dated 1991-01-21 | `HELD`: metadata read, not manuscript |

Primary finding aid: [University of Iowa Meyer Papers legacy register](https://www.lib.uiowa.edu/scua/msc/tomsc450/msc425/msc425.html), **2000 addendum**, line locators in `records.json`. The register itself says manuscript text is normally available only at Special Collections, and the collection is open for research subject to publication/copyright conditions. A separate [ArchivesSpace collection record](https://s-lib019.lib.uiowa.edu/repositories/2/resources/2996) confirms research access and the use restrictions. Neither grants us a digital copy or permission to republish a screenplay.

## Anomaly held, not reconciled

An [object-level ArchivesSpace listing](https://aspace.lib.uiowa.edu/repositories/2/archival_objects/496613) separately labels a revised final draft dated **1982-01-18** in **Box 56** with the literal title **“Star Trek II: The Undiscovered Country”**. The legacy finding aid places a same-dated revised final draft under *Wrath of Khan* in **Box 48**. These could be a reboxed copy, alternate catalog title, or separate objects; the two catalogs descend from one institutional collection and are **not independent corroboration**. The apparent film-title collision must not be mistaken for a *Star Trek VI* screenplay or silently reconciled as `SAME_AS` with the legacy draft. No archive registrar was contacted; provenance/identity remains `UNRESOLVED`.

> **Hostile challenge:** A screenplay, even a release dialogue script, need not match the final edited film, subtitle track, alternate cut or soundtrack. A finding-aid title cannot prove a line was spoken on screen. Reusing a 1991 script as 1982 film dialogue because of the shared “Undiscovered Country” wording would be a particularly destructive cross-film identity mistake.

## Source → local entity → evidence → assertion

`records.json` contains 3 linked institutional catalog sources (one provenance/independence group), 5 source-local archival item entities, 6 metadata-only evidence records with line/box locators, and 6 proposed source-attributed assertions. `BATCH_MANIFEST.json` binds the exact record-file SHA-256; **no upstream HTML, screenplay or film hash exists**, because those bytes were not acquired. `source_hashes` is therefore honestly empty. There is no global Work ID, reconciliation, accepted evidence, `SOURCE_BOUND` promotion, or projection effect.

**2026-11-04 hostile-validation successor:** An independent AUDITOR packet at commit `5486a48` found five semantic bypasses in the original validator: impossible Box 999, invented 2099 revision date, wrong-film entity/evidence relabeling and an assertion attached to unrelated access evidence. The source records themselves matched the finding aids. The successor validator now pins **every** reviewed archival locator and observation, every local entity→candidate film association, and each assertion→specific evidence join. The unchanged source-local record SHA still guards byte drift, but semantic checks separately reject even valid-looking wrong-fact mutations if a future author re-pins a changed file. All five original independent audit probes were rerun unchanged against the successor validator and passed. The ambiguous Box 48/Box 56 pair remains unreconciled.

All three candidates already have brief, original **publisher-description paraphrases** in the accepted `proposals/research/films/publisher-synopses-20261103/` batch. These new archival catalogs have no plot content, so creating fresh film synopses here would merely rewrite one promotional source family and falsely suggest screenplay reading. That duplication is intentionally held in `synopsis_handling`.

## Provenance and rights

- Evidence class: `INSTITUTIONAL_CATALOG_PAGE_DIRECT_READ`, **not** `MANUSCRIPT_CONTENT_READ`, `FILM_PLAYBACK` or `AUTHORIZED_SUBTITLE_COPY`.
- Institution: University of Iowa Libraries, Meyer Papers `MsC0425`; legacy and ArchivesSpace pages are **related**, not independent.
- Source retrieval: web reader on 2026-11-04; raw HTML bytes and revisions not captured. Catalog page hashes remain `null`.
- Actual script/digital subtitle/transcript custody: **none**. No complete dialogue, images, media, or script text was copied to this repository.
- Work admission, evidence promotion, coverage promotion and public Explorer use: `NONE`.

## Reproduction and next frontier

```bash
python3 proposals/research/films/meyer-script-custody-20261104/validate.py
python3 -m unittest discover -s proposals/research/films/meyer-script-custody-20261104 -p 'test_validate.py' -v
python3 tools/validate.py
```

**Next:** request or authenticate archive access to the May 24 *Wrath of Khan* dialogue-script item, preserving its current box/identity mapping and exact material/version receipt. Separately obtain authorized film-specific captions or authenticated playback editions before cinematic coding. Do not equate script draft text with final film dialogue, and do not ingest third-party PDFs marked restricted merely because web search indexed them.
