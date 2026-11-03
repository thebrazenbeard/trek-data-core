# Five TOS Research Leads: publisher metadata crosswalk (proposal, 2026-11-03)

**Role:** Librarian. **Scope:** five source-local candidate crosswalks. **Admission:** `NONE`.
**Original research baseline:** content-equivalent local integration `e016a8bc2b8d3c1b1053c8b933c015d1932d460f`. **Current integration base:** accepted `main@5902f70c2f5f31b02c705793106dfc71ee8e2360` after #211, including the *Scouts* short-form observations and the LCARS/artwork interface. Only this proposal's own five-file partition was replayed; no previously accepted discovery artifact was replaced.

## What was actually checked

1. The accepted `explorer/research-leads.json` contains 218 candidate rows, including archived user-supplied Wikidata QID/title labels. This archived WDQS response's integrity does **not** authenticate its original query provenance or bind a canonical episode Work.
2. The accepted Paramount+ legacy Season 1 publisher batch reports a separately captured 319,956-byte TOS HTML source with SHA-256 `4e1252ee0573d3fc12a771bc9f88a1840eaa5c05ea254b2ab85901b312e33fc1`. Its TOS observation CSV SHA-256 is `b0055cd053941bc0f822ebe2738286e44e40ddb301134c6c6bcf448f42fe7859`. Those are **prior accepted capture receipts**; their private source bytes are not in this public repository and were **not re-captured** in this batch.
3. On 2026-11-03 a public web reader displayed the **complete Paramount+ TOS Season 1 episode guide**, including the five exact headings and publisher ordinals in `selection.json`: *The Man Trap* S1E2, *The Corbomite Maneuver* S1E11, *The Devil in the Dark* S1E26, *The Conscience of the King* S1E14, and *The Naked Time* S1E5. See the [official publisher page](https://www.paramountplus.com/shows/star_trek/episodes/1/). The public reader returned rendered lines but did not furnish a new immutable raw HTML body or hash; those reader line numbers are not durable locators.
4. `tools/build_lead_source_crosswalk.py` regenerates `crosswalk.json` by **exactly** joining the five archived QID/title/mission candidates to these prior publisher Season 1 title/ordinal observations. It first validates the existing publisher CSV SHA; unknown QIDs, wrong ordinals, mismatched titles, or duplicated QIDs fail closed.

What this supports: the *same five title strings* appear as TOS episode leads in an archived Wikidata-derived list and as TOS Season 1 listing entries in a separately maintained Paramount+ guide. It does **not** authenticate the Wikidata QID as a canonical identifier for an audiovisual episode, establish an accepted Source↔Work binding, prove all dialogue or episode order across editions, or verify a franchise denominator. Publisher order includes *The Cage* as S1E1, so order and pilot identity remain edition-scoped and potentially contested.

All five crosswalks remain `PROPOSED_TITLE_AND_SERIES_CROSSWALK`; the 218 Research Leads and **1,206** discovery observations (1,155 episode-related / 35 short-form) stay unchanged; **zero Briefings** or coverage effects are added.

## Hostile challenges

> **Title collision:** Two different works, editions, alternate cuts, or umbrella slots can share a title. Same-title matching is a *candidate* link, never an LLM global identity reconciliation.

> **Dependence:** An archived WDQS result and an official publisher listing are separate named independence groups, but this batch does not prove how individual WDQS labels were sourced. Do not claim independent factual corroboration simply from different URLs.

> **Web-reader custody:** The live page rendered source data, but a web-reader transcript is not a newly captured HTML response with a verifiable hash. Current freshness is a qualified manual observation, not a new immutable source receipt.

> **Copyright:** No publisher page body, transcript, image, or audiovisual bytes are in this repository. The retained metadata, locators and digests do not confer content reuse rights.

## Repeatable lead verification queue

For each of the remaining leads, in bounded worker waves:

1. Confirm candidate QID/title/series and existing provenance from the frozen 218-row sample; retain held arc/umbrella entries outside ordinary episode counts.
2. Retrieve an actually readable primary publisher season guide or official episode page, capture allowed raw source bytes with a hash outside the repo where feasible, and record edition, retrieval date, locator, and lineage. A search snippet alone is insufficient.
3. Match title, series and source-specific ordinal; mark `AMBIGUOUS` on multipart titles, pilot differences, re-edits, alternate chronology, and collisions. Leave mismatches `UNRESOLVED`.
4. Independently audit a sample of the actual source receipts and crosswalk falsifiers; reject invented source identity or duplicate source-lineage corroboration.
5. Require a separately sourced full text or AV episode for evidence extraction and neutral coding before any `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, or Briefing claim. A Consolidator later proposes accepted Work bindings and versioned reconciliations; tests cannot auto-promote them.

This batch is the first **five-candidate crosswalk triage**, not five independently verified episodes or five completed close reads. Next: another 5–10 crosswalks from nonoverlapping official publisher pages and a source-custody audit.

Checks:

```bash
python tools/build_lead_source_crosswalk.py --check
python -m unittest tests.test_lead_source_crosswalk -v
python tools/validate.py
```
