# Held publisher bibliography: isolated Consolidator preview (2026-11-04)

**Status: LOCAL PROPOSAL ONLY — NOT MERGED, RELEASED, OR ACCEPTED.**

`tools/build_held_publisher_draft_preview.py` produces a deterministic,
reviewable JSON metadata preview **on stdout**, or into an explicitly scoped
proposal sidecar with `--write-preview`, from the two exact Git blobs
below. It does not edit the accepted Explorer or its indexes. Its emitted entries are
`HELD_DRAFT_METADATA_PREVIEW_NOT_ACCEPTED`, not admitted Works, completed
reads, independent corroboration, canon assertions, or artwork releases.

| Draft source | Exact head | Pinned `records.json` SHA-256 | Metadata editions | Independent upstream group |
| --- | --- | --- | ---: | --- |
| [PR #494](https://github.com/thebrazenbeard/trek-data-core/pull/494), `proposals/research/lit-five-publisher-bibliography-20261104/records.json` | `0ec895e17f70b505579b35c69e4af423e4b1dd6f` | `db04282ad717cb4f71932a5e2b7e8267c5e26b295dd7d02c1cf455b57be38c13` | 5 eBook product editions | `publisher:simonandschuster.com` |
| [PR #497](https://github.com/thebrazenbeard/trek-data-core/pull/497), `proposals/research/lit-titan-five-artbooks-20261104/records.json` | `785e4516d65b8a8e3769e7eaf69875966bf2e4bb` | `c01c276712477b94565cd61ec275fa83c6f2130637022abf7cca1fd8a9bedc8d` | 5 nonfiction hardback artbook product editions | `publisher:titanbooks.com` |

The two source families are different publishers; each individual publisher
is one upstream group, not five independent witnesses. The first-party page
reads are **reported by the draft workers**; this compiler checks pinned
proposal bytes and restricted metadata semantics but does not independently
re-fetch publisher pages. The *Unification* product record has an unresolved
publisher author-header-versus-description anomaly. It remains visibly held.

The opt-in [LCARS review preview](../proposals/consolidator/held-publisher-ui-preview-20261104/README.md)
is intentionally separate from the accepted-main Explorer and kept under
`proposals/consolidator/` so it cannot enter the strict Pages artifact allowlist:

| Main-branch display/data lane | Accepted-main scope |
| --- | --- |
| Missions | 12 television **series**, not 12 episodes |
| Briefings | 0 admitted episodes |
| Governed records | 0 accepted continuity records |
| Universe Directory | 1,214 source-local observations; **9** literary candidate rows, not admitted Works |
| Research Leads | 218 sampled unverified episode leads, not a verified episode denominator |
| Publisher edition shelf | 3 source-local edition leads |
| First-party publisher ISBN crosschecks | 39 accepted source-only metadata crosschecks; not 39 new Works |
| This new preview | 10 **additional held draft** publisher edition rows, independently counted from both unmerged PRs; **no addition** to any line above |

Run locally in a clone that has the two pinned PR heads fetched (does not
fetch from the network, write repository files, or publish):

```bash
python3 -m unittest tests/test_held_publisher_draft_preview.py
python3 tools/build_held_publisher_draft_preview.py > /tmp/trek-held-draft-preview.json
```

Strict checks reject changed proposal bytes, scope promotions, unsupported
publisher URLs, duplicated or invalid ISBN-13 values, identity assertions,
content/cover release claims and source-family drift. **This is a local-only UI
preview, not a production Explorer UI integration.** Before any public display, accept or
reject each draft research proposal, perform a separate source/provenance
review, authorize a separately reviewed HELD-only UI sidecar, run Pages
artifact and browser tests, and obtain explicit deployment authorization.

Related but distinct drafts: PR #498 reviews five artwork delivery routes
without releasing an unlicensed thumbnail; PR #499 is a Badgey interaction
change, stacked on #486, not literary source admission. Neither is merged into
this preview.
