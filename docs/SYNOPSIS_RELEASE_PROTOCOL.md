# Synopsis display release boundary (proposal)

The Explorer can show a synopsis status panel for each source-local episode,
film, literary, short-form, and audio row. **No plot summary is admitted by the discovery directory itself.**
Until a separately reviewed release is present, cards say **“Synopsis pending
source verification”**. The 218 sampled research leads carry the same pending
state. A placeholder does not assert that the Work has been read.

## Supported release type

A future optional `explorer/synopsis-catalog.json` can release publisher
description-based overviews for episode, film, or literary rows only. Short-form
and audio content remain pending until a separately qualified release mode is
defined. The release must use an exact `1.0.0` envelope with these keys:

| Envelope key | Required value |
| --- | --- |
| `schema_version` | `1.0.0` |
| `data_status` | `EDITORIALLY_REVIEWED_DISPLAY_ONLY` |
| `coverage_effect`, `admission_effect` | `NONE`, `NONE` |
| `synopsis_count` | Exact number of `synopses` |
| `synopses` | Array of approved source-relative entries |

Each entry is keyed by `row_id` (`directory:<source-local-id>` or
`film:<publisher-catalog-id>`), with exact title, medium, `source_group`,
`source_input`, `source_context` (edition/series context or film work type), source URL, original
`overview_text`, `overview_basis=PUBLISHER_DESCRIPTION_PARAPHRASE`,
`source_snapshot_date` (UTC calendar date of rendered-page observation),
`research_observation_path`, `research_observation_sha256` (the SHA-256 of the
*accepted local observation artifact*, not publisher HTML), `raw_webpage_sha256:null`,
`editorial_receipt_sha256`, and both effects `NONE`.

**Independent review gate:** the Explorer's `reviewedSynopsisReceipts` map is
deliberately empty. Metadata in a proposed sidecar cannot approve itself.
Every proposed release also requires a distinct, code-reviewed immutable tuple
pinning its source-group/input/context and URL/title, exact original text, rendered-page observation UTC date,
exact local observation path/digest and `raw_webpage_sha256:null`, and
editorial receipt SHA-256. A changed byte of purportedly reviewed text, wrong
source edition, or self-declared `CLOSE_READ` must fail closed. The public Pages
workflow currently disallows this optional sidecar: accepting a real release
requires its own explicit source/rights review, validator, allowlist update, and
authorized Pages dispatch. It must not sneak in through an unrelated PR.

An original paraphrase based solely on a verified publisher blurb is labeled
**“Publisher-description-based overview”**; it is *not* represented as a
full-work plot synopsis or `CLOSE_READ`. Future full-text-derived synopses need
an explicitly versioned schema extension with body/edition custody, location
references, validation, and independent human editorial review.

## Research / rights boundaries

- Do not mirror publisher/Fandom blurbs or reuse substantial copyrighted prose.
- Do not claim a ZIP filename, catalog match, or raw hash proves content was
  actually read or identity resolved.
- Preserve `SOURCE → WORK → LOCAL ENTITY → EVIDENCE → ASSERTION`, source family,
  duplicate rows, unresolved classifications, and separately governed coverage.
- The local hardcoded receipt pins are a *publication gate*, not a proof of
  independent source reading. Editorial reviewers must examine original source
  and the proposed prose before pinning a release.
