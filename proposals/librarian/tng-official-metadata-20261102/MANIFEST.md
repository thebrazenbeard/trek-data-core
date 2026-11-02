# TNG official-source identity pilot — five Mission Briefings

Batch: `TNG-OFFICIAL-METADATA-20261102-001`

Status: **PROPOSAL ONLY — not admitted**

Observation date: 2026-11-02
Scope: five metadata associations for the *Star Trek: The Next Generation*
Mission, corresponding to five external episode-discovery candidates.

The Librarian may review this proposal. It does not create accepted Work IDs,
source-bound Mission Briefings, copyrighted source extracts, continuity
assertions, coverage changes, or Explorer entries.

## Contents

- `bundle.json`: five proposed Source references, five proposed Work identities,
  five explicitly **PROPOSED / METADATA_ONLY** Source↔Work associations and five
  **CANDIDATE** Wikidata external-ID crosswalks. All IDs have a `proposal:`
  prefix so they cannot be mistaken for accepted canonical IDs.
- `EVIDENCE_SCOPE.md`: exact publisher locators, narrowly supported title and
  episode-position observations, contested assumptions and rights boundaries.
- `tests/test_tng_official_metadata_pilot.py` (repository root): schema and
  no-admission regression checks.

Each page is a distinct Source reference but all five share one
`publisher:startrek.com` independence group. They cannot be counted as five
independent primary audiovisual witnesses. Every Source has `content_hash`
and `content_fingerprint` set to `null`: no page body or video bytes were
retained or independently hashed. A web locator and an observed headline are
not equivalent to a verified full episode.

## Upstream candidate lineage

Wikidata Query Service discovery snapshot:
`WDQS-TNG-Q16290-20261102-10ROW-001` (proposed in the separate ten-candidate
research batch, draft PR #166). Response SHA-256:
`ea959ea993f21bb1de28ac955319a03f7024c37449a09c35129a795076d77499`.
The source response is retained off-public-Git under the repository's
source-byte policy. The five QIDs in this proposal were checked against that
candidate batch. StarTrek.com does **not** assert those Wikidata identifiers;
the crosswalks are independently checked *proposals awaiting human Librarian
review*, not accepted identity links.

## Admission blockers

1. A Librarian must independently verify each official locator and proposed
   Work identity, including the weaker preview, retrospective and watch-guide
   references.
2. Rights-valid access to the actual audiovisual episode or a licensed
   equivalent is needed before any `EVIDENCE_BEARING` Source↔Work binding can
   be considered. Automated Paramount+ source mining is not authorized.
3. An accepted parent Mission Work and explicit reconciliation are needed
   before canonical IDs, season roster denominators or episode coverage can
   be established.
4. Separate research-worker evidence and assertions would need source-relative
   review. This identity pilot deliberately contains **zero** narrative
   Evidence, Assertions, Local Entities or coverage events.

No merge, deployment, accepted-corpus mutation or protected effect is implied.
