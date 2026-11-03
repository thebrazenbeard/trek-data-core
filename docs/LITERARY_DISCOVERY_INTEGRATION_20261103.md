# Literary discovery integration — proposal only

This bounded integration combines two **unaccepted** metadata-discovery
proposals without resolving global Work identity or admitting research:

- Three Simon & Schuster novel candidates and nine publisher format/ISBN
  observations, with the existing accepted-main *Second Self* publisher
  proposal cross-checked as **one source-local directory row**. Both related
  records share the same publisher lineage, not independent corroboration.
- Five Penguin Random House/Titan-distributed **fictional in-universe memoir**
  candidates, with one listed ISBN per title. The three-title boxed set is
  recorded as a collection **container**, not a tenth literary Work.

The resulting deterministic directory has **1,214 source-local rows**:
1,155 episode-related observations, 14 films, 35 short-form releases, one
audio-series container, and nine literary candidate rows (four novels, five
memoirs). These are neither 1,214 canonical Works nor a defensible franchise
denominator. All source rows retain `admission_effect=NONE` and
`coverage_effect=NONE`; there are zero accepted research records.

## Sources and controls

- Imported proposal: `#212`, source commit
  `8c3c5656588f963fd6147779be73772fa517ecb3`.
- Imported three-novel main-targeted proposal: `#233`, local reviewed commit
  `f873e420529f3888e328719156ef1548322ef5d1`.
- Original observed source groups remain `publisher:simonandschuster.com`
  and `distributor:penguinrandomhouse.com:titan-books` respectively. Both
  families are represented as metadata-discovery observations, without any
  new independent verification claim.
- The distributor's five product locators are pinned to their individual
  reviewed title/creator/ISBN and raw-page receipt hash. A valid URL for a
  *different* title on the same trusted host is rejected.
- The accepted Explorer series facet remains operational; its source URL
  allowlist extends narrowly to the distributor host. No remote cover loads
  are enabled by this integration.

Publisher-page receipt hashes do not authenticate literary text, authorize
copyright reuse, settle chronology/canon, or establish full-text custody.
The optional directory is a generated proposal artifact; Pages deployment
remains a separate protected effect.

## Rebuild and audit

Regenerate with `python3 tools/build_unified_discovery.py`, then verify with
`python3 tools/build_unified_discovery.py --check`. The owning source builders,
source digest array, corpus validator, Python and Explorer tests must remain
green. This is a draft integration proposal, not an accepted reconciliation
decision; accepted `main` remains authoritative until separately reviewed.
