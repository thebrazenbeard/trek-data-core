# TOS Season 1 archived lead crosswalk follow-on — Librarian proposal

**Batch:** `lead-qualification-tos-s1-followon-20261104`

**Authoritative starting point:** accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91`
**Effect:** `NONE` on accepted Source/Work bindings, canonical identity, Briefings, and coverage.

## Bounded work actually performed

Five additional nonoverlapping candidate QID/title rows in the accepted 218-row `explorer/research-leads.json` were joined to five unique title/ordinal entries in the **previously accepted** Paramount+ TOS Season 1 observation CSV. No live primary webpage was retrieved or read for this tranche; the current primary page could not be rechecked reliably. This is a **replay of prior hash-pinned publisher discovery metadata**, not a new source retrieval, full-episode access, or verification of QID truth.

| Archived candidate QID | Title (exact match) | Prior Paramount+ S1 slot |
|---|---|---|
| Q2664096 | Mudd's Women | 7 |
| Q2984502 | The Enemy Within | 6 |
| Q3107459 | Dagger of the Mind | 10 |
| Q3178411 | Balance of Terror | 15 |
| Q3487125 | A Taste of Armageddon | 24 |

The publisher observation input is `proposals/discovery/legacy-paramount-season1-20261102/tos.csv` with SHA-256 `b0055cd053941bc0f822ebe2738286e44e40ddb301134c6c6bcf448f42fe7859`, checked against its accepted index receipt. The prior capture receipt records the Paramount+ page `https://www.paramountplus.com/shows/star_trek/episodes/1/`, a 319,956-byte source body with SHA-256 `4e1252ee0573d3fc12a771bc9f88a1840eaa5c05ea254b2ab85901b312e33fc1`. The original source body bytes were not re-fetched, are not in this repo, and the receipt is not independently reauthenticated by this batch. Archived candidate WDQS lineage is also not proven independent merely by differing provider names.

`tools/build_followon_tos_crosswalk.py` deterministically regenerates `crosswalk.json`; it checks the prior receipt hash, mission, title, ordinal, candidate provenance flags, duplicate QIDs/ordinals, and disjointness from the prior five-candidate tranche `lead-qualification-tos-s1-20261103`. It fails closed on mismatches. Output preserves `canonical_work_id: null` and `accepted_source_work_binding: null`. The prior five proposals and these five yield **10 proposed local metadata links**, still **zero accepted source–Work links**. The number 218 remains a discovery-lead count, not a validated audiovisual or semantic denominator.

Additional hostile-review guard: the generator pins SHA-256 of the complete archived candidate sample, publisher index, publisher TOS CSV, publisher TOS bundle, and preceding crosswalk to bytes from accepted `main@3028765`. It will reject coordinated tampering in which a modified publisher CSV and a modified publisher index rehash each other, or in which a different WDQS candidate snapshot is silently substituted. Those digest pins prove reproducibility against accepted repository bytes, **not** independent external authenticity of the original publisher or WDQS capture.

## Hostile challenges / limitations

> **No fresh publisher read:** the previously accepted hash receipt plus a CSV replay can demonstrate deterministic cross-referencing of accepted *metadata*, but not freshness or current publication of the official guide. A reader must not label these five `SOURCE_BOUND` or `CLOSE_READ`.

> **Title/ordinal aliasing:** a matching label and publisher slot do not resolve alternate versions, broadcast/production order, episode parts, or canonical Work identity. TOS publisher Season 1 places *The Cage* first; do not silently equate all franchise orderings.

> **Upstream dependence:** archived Wikidata titles could themselves derive from publisher or fandom listings. The two namespace labels are not established independent corroboration without lineage custody.

> **Self-attesting receipts:** a CSV whose hash is recorded only in an editable adjacent index could be replaced alongside that index. Accepted-main file-level digest anchors reduce that exact replay risk; they do not establish an independent third-party signature.

> **Copyright:** no episode text, page HTML, screenshots, artwork, audio, or video bytes have been committed; only source locators, digest receipts, and original structured triage.

## Validation

From repository root:

```bash
python3 -m tools.build_followon_tos_crosswalk --check
python3 -m unittest tests.test_followon_tos_crosswalk -v
python3 -m tools.build_lead_source_crosswalk --check
python3 tools/validate.py
```

**Next Librarian frontier:** obtain new independently retrievable primary episode/edition sources with source custody and lineage checks; keep proposed crosswalks separate from accepted Source↔Work admission pending Consolidator reconciliation and audit.
