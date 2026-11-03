# Prodigy S1 first-five publisher-slot leads — derivative episode-guide read

**Role:** PRO. **State:** `PROPOSAL_ONLY / DERIVATIVE_METADATA_READ`.
**Accepted base:** `main@e7730804741b50a94b8b515674392475afb510d7`.

This tranche covers four contiguous **source entries** occupying five printed
production-style slots (`101/102`, `103`, `104`, `105`). A combined 101/102
entry is **one source observation** with two labels, not proof of two
independently researched audiovisual Works. Neither the source entries nor the
printed slot labels are accepted episode Briefings or coverage events.

## Source actually retrieved and read

- **Derivative representation:** [TVMEG Prodigy episode guide](https://tvmeg.com/index.php/2023/06/29/stpepguide/), HTTP 200, retrieved 2026-11-03 UTC. Raw HTML: **121,944 bytes**, SHA-256
  `e01541968cce29eccba2792b52299e718a36cc4880e1535d0b319737aa4a06bc`.
  The first-series list was read at raw HTML lines **499–519**, including all
  printed `101/102` through `120` entries. This batch records only lines
  **500–503**; each evidence record includes an exact physical-line SHA-256.
  No raw HTML, press loglines, media, or images are committed.
- **Attribution within the derivative:** HTML physical line 532 states that
  the episode-guide descriptions came from the Paramount+ Press Site. This
  is the TVMEG author's attribution, **not an authenticated original-source
  identity**. The corresponding [Paramount Press Express season-one loglines](https://www.paramountpressexpress.com/paramount-plus/releases/?view=101514-star-trek-prodigy-season-one-loglines)
  returned a geographic access block during this work; no original HTML
  digest or direct primary press read is claimed.
- **Separate first-party boundary check:** [StarTrek.com volume-one release](https://www.startrek.com/news/star-trek-prodigy-season-1-volume-1-release),
  HTTP 200, 1,226,890 raw HTML bytes, SHA-256
  `cdfa762fd65814d83c864072e1807c5ba5493e8d049845dc321661354225bea9`.
  The publisher announces a first-ten-episode physical volume, but does not
  independently enumerate these production codes. Both this page and the
  claimed press upstream belong to the broad Paramount publisher family;
  they are **not counted as independent witnesses**.

## What was extracted

Four local Work candidates, four local source-entry entities, four line-bounded
evidence records and four typed, **utterance-scoped** assertions. The records
preserve the short displayed titles, printed production codes, month/day
labels, writer/director credits, source identity, and provenance. The year is
not silently derived from an unqualified parenthetical date. This is coding
of source **metadata** and promotional descriptions, not watching or reading
the complete audiovisual episodes.

The existing [Mikros studio first-volume proposal](../../../discovery/prodigy-mikros-volume1-20261102/MANIFEST.md)
has ten inferred ordering positions and an isolated `Ep#103` image caption;
this batch must **not** silently convert its entire inferred sequence into
publisher-certified ordinals. `101/102` is a combined source label and may
represent a premiere packaging convention. Reconciliation is unresolved.

## Acceptance and rights gates

`accepted_work_effect=NONE`, `accepted_source_binding_effect=NONE`,
`coverage_effect=NONE`, `artwork_release_effect=NONE`. No global identity,
series denominator, transcript, frame, poster, or attributed prose passage
has been admitted. The original press page, primary audiovisual installments,
and full source-edition identity still require independent verification.

Validation:

```bash
python3 proposals/research/pro/s1a-derivative-loglines-20261103/validate.py
python3 proposals/research/pro/s1a-derivative-loglines-20261103/test_validate.py
python3 tools/validate.py
```

**Next bounded PRO frontier:** derivative `106`–`110` source entries, then
first-party source access, edition/ordinal custody and content research;
review source-family dependence before any governed admission.
