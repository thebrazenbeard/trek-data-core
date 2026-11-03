# Source-local unresolved proposal query (non-admitting)

`tools/query_source_local_unresolved.py` reports a bounded **proposal-review
frontier**, not canonical franchise contradictions, reconciled Works, or
completed audiovisual coverage. Its inputs are six already-committed research
proposal folders on accepted `main` (two TOS derivative-text analyses and four
DS9 publisher/source-access studies). Merely merging a proposed source-relative
assertion file into `main` does **not** accept its assertion as fictional truth.

The compiler uses explicit path and SHA-256 pins for twelve files: six
`assertions.json` files and their six associated evidence/observation files.
It refuses unreviewed path additions, changed source bytes, foreign evidence
IDs, duplicate records, unsupported schema fields, admission-like statuses,
and symlinked source paths. A legitimate append or correction requires
updating the reviewed input manifest and tests; no silent promotion occurs.

Current source-local proposal counts:

| Record class | Count | Meaning |
| --- | ---: | --- |
| `PROPOSED_UNRESOLVED` | 6 | Research worker explicitly left an observation/route question open |
| `PROPOSED_PROJECTED_UNRESOLVED` | 15 | TOS derivative-text worker suggested an unresolved later projection state |
| `PROPOSED_PROJECTED_CONTESTED` | 1 | TOS derivative-text worker suggested a contested later projection state |
| Other plain proposals excluded | 5 | Source-relative proposals without an unresolved projection request |

This is **22 visible query rows out of 27 proposal assertions**, not 22
verified contradictions or 27 admitted facts. A source family appearing twice
is not independent corroboration; all identity references remain source-local.
No episode audiovisual cut, full primary transcript, or licensed literary work
is certified by this query.

Read-only examples from the repository root:

```powershell
python tools/query_source_local_unresolved.py --limit 10
python tools/query_source_local_unresolved.py --kind PROPOSED_PROJECTED_CONTESTED
python tools/query_source_local_unresolved.py --predicate SOURCE_VERSION_RECONCILIATION_REQUIRED
python tools/query_source_local_unresolved.py --batch ds9-source-custody-gap-20261103 --q authenticated
```

Every result includes a unique `source_path:assertion_id` key, the exact
source-local subject, predicate, cited evidence IDs, source-relative scope,
worker-authored falsifier, and explicit `PROPOSED_NOT_ADMITTED` status.
Machine-readable results retain `admission_effect: NONE`,
`coverage_effect: NONE`, and `identity_resolution_effect: NONE`. The tool
does not write a database or public Explorer artifact.
