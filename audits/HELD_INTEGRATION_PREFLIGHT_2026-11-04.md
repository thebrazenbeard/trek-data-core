# Held draft integration preflight — isolated auditor proposal

Status: **local-only, read-only proposal**. No merge, deployment, rights
clearance, registry admission, projection generation, or accepted coverage
change. The authoritative `main` checked through literal GitHub remote was
`3028765359001b90bc3e6b5c1835ee283b326e91`. Draft #508 remains proposed;
draft #517 is a Director checkpoint that *references* seven other draft PRs.
Its table is not proof that their commits have been integrated.

## Purpose

`tools/held_integration_preflight.py` accepts a JSON plan of **full
40-character Git commit IDs**, a pinned accepted base and a proposed candidate. It reads
local Git objects only. The caller must independently verify that those IDs
match current GitHub heads; the tool never treats a self-declared plan as
authorization. It checks:

- a candidate and every selected draft descend from the pinned base;
- a selected draft is actually present by ancestry or its exact changed tree
  paths and blob identities, so a Director document cannot stand in for code;
- declared draft dependencies are included or already in the accepted base,
  without cycles;
- independent selected drafts changing the same path to different blobs are
  flagged for manual resolution;
- prospective public image/asset additions require the existing independent
  artwork rights release gate, while root research/coverage/registry changes
  and any public `explorer/` machine-readable data require semantic review;
- public Explorer HTML/CSS/JS changes and projection compiler modifications
  cannot be mistaken for a publish authorization.

It does **not** prove any undeclared semantic dependency, copyright license,
source custody, successful reconstruction, visual browser behavior, or
production suitability. The result explicitly says
`NO_PREFLIGHT_BLOCKERS_NOT_AUTHORIZED` when this narrow screening finds no
blockers; manual approvals and lane validators still apply.

## Real immutable draft check

All heads below were fetched from the literal GitHub repository on
2026-11-04 (not inferred from local aliases). Two frozen sample plans:

| Plan | Result | Observation |
| --- | --- | --- |
| `held_integration_review_517_20261104.json` | No preflight blockers, **not authorized** | #517 changes one `proposals/director/.../MANIFEST.md`, not code or accepted evidence |
| `held_integration_hypothetical_prod_20261104.json` | **BLOCKED** | The seven other PRs are not in #517's tree, and #510/#514 independently change five overlapping Explorer/test paths to conflicting blobs |

The hypothetical production case reports exactly seven
`DRAFT_NOT_IN_CANDIDATE`, five `DRAFT_PATH_COLLISION`, and one
`PUBLIC_UI_RELEASE_REVIEW` blockers; the conflicting paths are
`explorer/app.css`, `explorer/app.js`, `explorer/index.html`,
`tests/test_explorer.mjs`, `tests/test_explorer_accessibility.mjs`.

No public artwork raster or accepted semantic-record change is in that
*candidate* #517 tree. This is not evidence that artwork rights or literature
and episode admission are resolved: #513's rights leads and #511/#512/#516's
source-local research remain HELD proposals, while their eventual public
promotion would require separate review. Synthetic regression cases check
that an attempted public raster or episode/literature JSON promotion is
blocked by the relevant gate.

## Reproduction

```bash
python -m unittest tools.test_held_integration_preflight -q
python tools/held_integration_preflight.py --plan audits/held_integration_review_517_20261104.json
python tools/held_integration_preflight.py --plan audits/held_integration_hypothetical_prod_20261104.json
```

The last command intentionally exits nonzero on the hypothetical release
attempt. Only read-only Git commands are invoked; it does not merge,
cherry-pick, publish, or update refs.

Validation: 13 targeted synthetic Git-tree tests pass with test-first red
cases for missing inclusion, stale dependencies, unrelated public JSON,
dependency cycles, and malformed dependency types. Full preexisting repository
Python regression suite: 1,391 tests passed. `python tools/validate.py` also
passed (zero identified admitted records).
