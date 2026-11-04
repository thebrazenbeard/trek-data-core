# Accepted Explorer presentation numerators — 2026-11-04

**Role:** CONSOLIDATOR cross-lane audit. **Evidence class:** deterministic
artifact/source inspection + tests; **not** independent publisher source
reading or a new Work-identity decision. Accepted `main` inspected at
`3028765359001b90bc3e6b5c1835ee283b326e91`.

The Explorer simultaneously shows accepted Mission catalog records and
**proposed source-local discovery observations**. Its visible numerators must
not be added as if they share a Work denominator.

| Presentation channel | Historical accepted-base rows/options | Separately pinned optional Picard supplement | Visible when both are verified | Meaning |
| --- | ---: | ---: | ---: | --- |
| Universe Directory | 1,214 | 2 | **1,216** | Source-local metadata **observations**, overlapping candidates permitted; not distinct Works |
| Literary Directory filter | 9 | 2 | **11** | Nine historical literary candidate rows (4 novels, 5 fictional memoirs), plus two separately pinned Picard publisher metadata candidates; no book close-read implied |
| Source-linked jacket options | 4 | 2 | **6** | Four historical opt-in Open Library autobiography jackets plus two exact Picard paperback jackets; external image bytes load only after visitor consent, copyright unresolved |
| Governed Missions | 12 series | 0 | **12 series** | Display catalog of television series, **not** episode admission |
| Governed Briefings / continuity records | 0 / 0 | 0 / 0 | **0 / 0** | No admitted episode Briefings or accepted continuity records |

The base JSON itself remains **1,214**, even when a browser displays 1,216.
The fifth historical fictional memoir (*The Autobiography of Benjamin Sisko*)
has **no** approved jacket option in these source-local artwork manifests.
Six preview options therefore do **not** establish complete visual coverage
of eleven literary candidates, let alone the complete Trek book corpus.

The distinct publisher-edition shelf (**3**), ISBN crosschecks (**39**), and
newer draft five-plus-five bibliography preview (**10 HELD**, under
`proposals/consolidator/`) are **separate ledgers and not added** to the
eleven directory rows. Likewise, the **218** sampled Research Leads are not an
episode denominator. Historical directory records and publisher rechecks may
share source lineage; different downstream indexes are not automatically
independent corroboration.

## Pinned source paths and byte receipts

| Artifact | SHA-256 | Contract |
| --- | --- | --- |
| `explorer/discovery-catalog.json` | `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc` | Immutable historical 1,214 source rows |
| `explorer/picard-literature-overlay.json` | `ab8e5d15f7b33bf1311aec0afb2755322b41bca73978d3c7889f1272dbfe21c8` | Two optional unadmitted publisher metadata rows; base remains 1,214 |
| `explorer/artwork-catalog-v1.3.json` | `f4f51a71e9db95368d03d1db88d07137425c09f7918e4a491c98e0eb6e8cfa2f` | Four opt-in medium-size autobiography jacket options |
| `explorer/picard-jackets-v1.0.json` | `85bdc8ebbb348d713d604fb9486c2af091e36d40138587a761ddd93716cd9615` | Two opt-in Picard paperback jacket options; zero public local image binaries |

The Picard literary overlay is rebuilt and byte-checked by
`tools/build_picard_literature_overlay.py --check`. The jacket sidecar is
checked against pinned candidate source and separately reviewed edition
receipts by `tools/validate_picard_jacket_release.py --check`. The JS
view merges the two directory arrays in memory and resolves jacket row IDs
against current source-local rows, without modifying `explorer/index.json`
or `explorer/discovery-catalog.json`. It sequences the optional loads so
jacket checks follow the Picard directory supplement.

## Hostile challenges and resolution

> Does `1,216` mean 1,216 distinct episode/book Works, or does `11` mean
> eleven book texts were read?

Neither. The front-end status message labels `1,214 original + 2 Picard
metadata proposals`; `11` is a filter count on source-local *row* types.
The 12-series Mission catalog remains a different projection. Both
supplement records carry `coverage_effect: NONE` and `admission_effect: NONE`.

> Does six sourced artwork mean six copyright-cleared local images or a
> complete six-book reading/admission benchmark?

Neither. All six are Open Library remote API **options**, no bytes mirrored
to the public repository. Underlying image copyright is explicitly
unresolved, previews require consent, and Sisko's fifth memoir candidate is
not among the four historical jacket options. The six are individually
bound edition references, not a literary coverage numerator.

> Could one absent or corrupted optional Picard artifact alter accepted
> historical coverage or rewrite prior rows?

The source loader fails closed: directory overlay failure leaves 1,214/9;
the independent jacket sidecar failure leaves four base image options.
Existing browser tests assert these fallbacks. Newly added independent
cross-lane tests assert exact SHA-pinned source and artwork sets and the
unchanged 12/0/0 governed projection.

## Reproducibility checks

```bash
python3 tools/build_picard_literature_overlay.py --check
python3 tools/validate_picard_jacket_release.py --check
python3 -m unittest tests.test_explorer_presentation_counts
node --test tests/test_explorer.mjs
```

**Result:** No material numerator misclassification found in accepted
source code or current sidecars. The principal presentation risk is that a
visitor can see the composite `1,216`, `11`, or `6` without noticing the
underlying historical/supplement split. Existing status labels make the
split available but not equally prominent next to every counter. A future
UX change could make that distinction more immediate; it must be reviewed
alongside any Badgey/LCARS UI patch and must not change accepted counts.
