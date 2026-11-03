# TAS Paramount+ Season 1–2 source-local roster observations

- **Worker role:** Source Librarian / TAS discovery, candidate metadata only
- **Source retriever/date:** Direct official Paramount+ episode guide HTML captures, 2026-11-02
- **Primary locators:**
  - `https://www.paramountplus.com/shows/star_trek_animated/episodes/1/`
  - `https://www.paramountplus.com/shows/star_trek_animated/episodes/2/`
- **Publisher family:** `publisher:paramount`; these are not two independent sources for canonical truth
- **External crosscheck:** `https://www.startrek.com/series/star-trek-the-animated-series` currently lists **2 seasons, 22 episodes**, but belongs to the Paramount family and does not establish independent corroboration
- **Raw source custody:** private temporary `/tmp` captures only; never committed to Git; each original response size and SHA-256 recorded in `index.json`
- **Raw HTML source receipt:** Season 1 `281559` bytes, SHA-256 `64576be49b260ad80473116a8d8826ab437f36de50cdec70db6edf8285880044`; Season 2 `256698` bytes, SHA-256 `aa055b83af70ee1fe4af340d216f696f17a4f5741d0e14cc6b1733d1ccc9fb4e`
- **Observed publisher slots:** Season 1 E1–16 (**16**), Season 2 E1–6 (**6**); total **22 source-local listing observations**. These are not 22 newly researched episodes.
- **Existing-source overlap:** five Season 1 E1–5 publisher observations already appear in `proposals/discovery/ds9-voy-episode-slots-20261102/tas-observed-slots.csv`. This batch intentionally preserves its different response/season snapshot as source-relative data; no global cross-source deduplication or Work identity decision is attempted.
- **Admitted effects:** NONE for canonical identity, Briefings, continuity assertions, completed research or denominators.
- **Reproducibility:** `python tools/build_tas_publisher_roster.py --ingest-dir PRIVATE_CAPTURE_DIRECTORY` reproduces the CSV/bundles from both full HTML source responses. `python tools/build_tas_publisher_roster.py --check` validates the committed deterministic source-local metadata and receipts without retrieving source HTML.
- **Source qualification:** A matching local SHA-256 authenticates neither the website operator nor an aired video. Publisher page metadata does not establish AV content, full-text analysis or scene-level evidence. Original script/HTML bodies are absent from the public repository.
- **Next frontier:** Independent source replay / hostile review, Librarian source binding, and Consolidator integration after explicit approval. Retain the separate discovery, reading and semantic coverage states.
