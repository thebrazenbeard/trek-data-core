# Synopsis display release boundary

The Explorer can show a synopsis status panel for each source-local episode,
film, literary, short-form, and audio row. **No plot summary is admitted by the discovery directory itself.**
Without a source-grounded publisher overview, cards say **“Synopsis pending
source verification”**. The 218 sampled research leads carry the same pending
state. A placeholder does not assert that the Work has been read.

## Supported release type

This separate release proposal contains exactly **23 original publisher-description
paraphrases** from accepted research observations: nine source-local literary
rows and fourteen film candidates. Short-form, audio and episodes remain pending;
full-text/film source reads have not been performed. The optional release is a
strict `explorer/synopsis-catalog.json` `1.0.0` envelope with these keys:

| Envelope key | Required value |
| --- | --- |
| `schema_version` | `1.0.0` |
| `data_status` | `EDITORIALLY_REVIEWED_DISPLAY_ONLY` |
| `coverage_effect`, `admission_effect` | `NONE`, `NONE` |
| `synopsis_count` | Exact number of `synopses` |
| `synopses` | Array of approved source-relative entries |

Each entry is keyed by `row_id` (`directory:<source-local-id>` or
`film:<publisher-catalog-id>`), with exact title, medium, `source_group`,
`source_input`, `source_context` (edition/series context or film work type), exact
directory source URL, separate `overview_evidence_locator` for the edition whose
publisher description was paraphrased, original
`overview_text`, `overview_basis=PUBLISHER_DESCRIPTION_PARAPHRASE`,
`source_snapshot_date` (UTC calendar date of rendered-page observation),
`research_observation_path`, `research_observation_sha256` (the SHA-256 of the
*accepted local observation artifact*, not publisher HTML), `raw_webpage_sha256:null`,
`editorial_receipt_sha256`, explicit optional film-directory display alias
and its exact source context, and both effects `NONE`.

**Review gate:** the accepted source observations were checked by a separate
OpenAI model agent. Its exact 23/23 promotional-paraphrase review receipt was
*authored in a separate worktree*, with source SHA-256, row/text hashes,
reviewer role, provider/runtime, exact accepted Git revision, and material
qualifications. That is **internal model review, not a cryptographic signature,
independent human review, external provider confirmation, or rights clearance**.
The source-relative release payload and separately authored reviewer receipt
are checked together by `tools/build_publisher_synopsis_release.py --check`.
The Explorer also code-pins 23 immutable source-group/input/context/title,
row URL, description evidence URL, original text, observation date/path/digest,
review digest, and `raw_webpage_sha256:null` tuples. A mutated field must
fail closed. The Pages workflow now has an explicit, fail-closed optional
release allowlist and build check. Merging code does **not** itself deploy:
public Pages dispatch remains a separate authorized act.

**Edition identity:** the Simon & Schuster overviews for *Second Self*, *The
High Country*, and *The Enterprise War* came from their eBook ISBN pages;
the directory displays separately verified paperback ISBN pages. The release
records both exact locators, their separate ISBNs, and a same-candidate
publisher-edition crosswalk. That crosswalk is for publication provenance
only, not global Work-identity reconciliation. All fourteen dedicated Film
cards and their directory cards use an explicit, exact-source display alias
requiring title, source group, source input, context, and URL equality; it does
not collapse distinct research records or create admitted Works.

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
  full-work reading or external signatory authority. A separate technical
  hostile review must qualify the exact final Git head before any merge.
