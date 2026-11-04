# TOS derivative-source custody and admission audit — 2026-11-04

- **Admission:** `PROPOSAL_ONLY`
- **Kind:** `SOURCE_CUSTODY_AND_LINEAGE_AUDIT`
- **Scope:** Existing `main` manifests only. This audit did **not** fetch or independently close-read either underlying transcript page. It neither creates episode evidence nor advances accepted coverage.
- **Admission hold:** [#23](https://github.com/thebrazenbeard/trek-data-core/issues/23). Related proposals [#488](https://github.com/thebrazenbeard/trek-data-core/pull/488) and [#493](https://github.com/thebrazenbeard/trek-data-core/pull/493) must be considered without duplication.

## Inputs read

1. `proposals/research/tos-man-trap-derivative-close-read-20261102/MANIFEST.json` — Git blob `ad4d3d4501e01578d8b25c37d49dac947e8b917e`.
2. `proposals/research/tos-charlie-x-derivative-close-read-20261103/MANIFEST.json` — Git blob `f195efb96f1b704ab991d16980eec7f46dbb9458`.

Both manifests characterize their source as `THIRD_PARTY_DERIVATIVE_TRANSCRIPT_PAGE`, with lineage `SOURCE_SELF_REPORTED_UNVERIFIED_DERIVATION`, upstream episode matching `false`, authenticated primary AV/studio script `false`, copyright republication rights `UNVERIFIED`, and private source custody `TEMPORARY_LOCAL_ONLY_NO_DURABLE_AUTHENTICATED_ARTIFACT`.

| Work | Derivative discovery locator | Manifest-reported raw HTML bytes / SHA-256 | Manifest-reported rendered text bytes / SHA-256 | Proposed records | Accepted coverage events |
|---|---|---|---|---|---|
| The Man Trap | https://tvmeg.com/index.php/2023/08/07/trekmantraptrans/ | `148006` / `03d886c23410b26586c5ca46b2a06e3c014112aa8d78283c718e982c89674be6` | `32567` / `b33d541becf98606f809f44bdae0a710a75828f224135c2e0e4854d453c753ac` | 23 local entities; 17 source-relative evidence; 9 assertions | **0** |
| Charlie X | https://tvmeg.com/index.php/2023/08/07/charliextrans/ | `144687` / `4498f2ac33c4e1aa4c48123aab84254b890fb9dd8603f0540189d7abdcd3c616` | `27813` / `0e033f6883644602b7a941619f4f895e3780feffdc92e2a3a20f0e295721e849` | 20 local entities; 14 source-relative evidence; 7 assertions | **0** |

All byte sizes, hashes, and record counts above are **manifest-reported**, not independently recomputed in this audit. Combined proposals: 43 local entities, 31 evidence records, and 16 assertions; **no accepted coverage**. In both manifests, `accepted_briefings=0` and `global_identity_reconciliations=0`.

## Open discrepancies and falsifiers

- A recorded hash with unavailable retained source bytes is not a reproducible fresh verification. The prior manifests claim earlier full-page retrieval, but this audit had no retained authenticated source artifact to reprocess.
- A derivative page's own upstream attribution is not independent lineage verification, much less primary audiovisual or studio-script custody. Correlated derivatives may share one upstream source.
- `The Man Trap` official episode numbering remains `UNRESOLVED_BETWEEN_OFFICIAL_ROSTERS` in its manifest.
- For `Charlie X`, the manifest cites the official season listing at https://www.paramountplus.com/shows/star_trek/episodes/1/ and episode page at https://www.paramountplus.com/shows/video/804598975/ showing `S1 E3: Charlie "X"`, while the derivative caption says `Season 1, episode 2`. Preserve the ordinal conflict; don't silently select one.
- Copyright rights for republication are unverified. Do not commit full transcript text, large passages, or source media.

> **Hostile challenge:** Hashes without the underlying source bytes prove that claims were recorded, not that current readers can replay their extraction. Two self-attributed derivatives do not constitute two authenticated independent primary sources. Proposal-level coding is not accepted close-read coverage.

## Admission gates / next valid frontier

1. Honor #23's hold: no new TOS source admission or close-read coverage promotion until its gate is explicitly resolved.
2. Bind each work to a legally usable full primary source/edition and stable original locator, or explicitly retain derivative-only status; document rights, source lineage, and custody.
3. Independently retrieve and hash authorized source bytes in an appropriate private custody environment, then replay structural extraction and validate source-relative evidence. Do not imply this has happened here.
4. Review ordinal discrepancy against independent official edition/production/broadcast ordering definitions; represent different orderings separately if appropriate.
5. Only after source, evidence, rights and methodology review may the responsible authority accept reconciliation and deterministic projections. Keep series worker outputs local, append-only, and proposal-only meanwhile.

## Validation scope

Static comparison of the two existing proposal manifests: both were `PROPOSAL_ONLY`, derivative, non-primary, self-reported/unverified upstream, temporary-only source custody, and zero accepted coverage events. **No source read, new close read, content hash recomputation, semantic adjudication, CI run, or accepted-main mutation** occurred in this audit.
