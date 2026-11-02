# First nonfixture Mission Briefing — admission readiness

The repository now has a working *verification pipeline*, not an accepted
episode corpus. A **Mission** is the public display label for a series; a
**Mission Briefing** is an episode. A Wikidata episode QID, a publisher
heading, and a DVD/streaming link can aid discovery and identity research,
but none alone means that an episode was inspected or admitted.

Run the read-only diagnostic against the checked-out tree:

```sh
python3 tools/check_episode_pilot_readiness.py
python3 tools/check_episode_pilot_readiness.py --work-id <accepted-work-id>
python3 tools/check_episode_pilot_readiness.py --require-technical-prerequisites
```

The last command exits **2** until at least one accepted episode Work has
all five listed mechanical prerequisites; a malformed or invalid authoritative
input exits **3**. The ordinary command exits **0** for a valid diagnostic
even when its JSON correctly says `TECHNICAL_PREREQUISITES_BLOCKED`.
The diagnostic performs the existing global record and coverage validators
before counting any episode Work. It is strictly read-only and never edits
Source, Work, Evidence, projection approval or coverage state.

## Exact gates for a small pilot

| Gate | Required evidence | Who must decide |
| --- | --- | --- |
| 1. Work identity | An accepted, nonfixture **series** Work and an accepted `work_type: EPISODE` Work under `registry/authoritative/`, with a non-cyclic `parent_work_id` chain. An ancestor's title must match exactly one catalog series title for the Explorer. | Librarian independently resolves editions, multipart identities, episode ordinals and contradictory listings. |
| 2. Source identity and binding | A nonfixture, accepted Source describing a permitted and actually inspected representation; an accepted `EVIDENCE_BEARING` Source↔Work binding with an exact matching `BYTE_HASH` basis for `SOURCE_BOUND`. | Librarian verifies provenance and scope, obtains rights-valid access, and checks the actual source bytes independently. A matching *declared* hash is only a consistency test. |
| 3. Scoped observation | An Evidence record naming the exact Source and episode Work, a bounded locator and observation, and one eligible accepted binding. | Assigned researcher records what was observed, distinct from dialogue, character testimony and inferred events. Do not upload source scripts, subtitle streams, video, whole prose, or copied passages. |
| 4. Assertion and coverage | An accepted, source-attributable assertion referencing that Evidence, plus a separately accepted, exact Work/Source/binding `SOURCE_BOUND` coverage event. Later `CLOSE_READ`, `AUDITED`, etc. states require their own evidence and are not inferred. | Reconciler/Auditor independently evaluates uncertainty and contradictions. Green syntax does not certify a human watched a full episode. |
| 5. Public projection | Deterministic nonempty canonical output, independently reviewed projection manifest and exact hash in `registry/approved_projection_hashes.json`, then regenerated `explorer/index.json`. | Project authority approves the projection; Pages deployment stays separately manual-only. |

The diagnostic currently reports the first four gates only as **technical
prerequisites** (plus the catalog-ancestor requirement). It displays the
number of approved hash receipts as context, not as proof that a particular
Work was approved. Its status `HUMAN_REVIEW_REQUIRED` means the **mechanical
checks** are present; it is explicitly *not* an acceptance decision or a
license/rights determination. No command here can turn a proposal into canon.

## Current blocker, without invented completeness

As of the 2026-11-02 acceptance baseline, `main` has **no nonfixture accepted
episode Works**, no eligible Source-bound pilot Evidence/Assertion and **no
approved projection hash**. The coverage denominator remains
`DENOMINATOR_UNRESOLVED`. A later `RESOLVED` accepted registry roster would
only count *admitted* Works, not prove the total episodes in a series.

The five TNG publisher-page associations in
[`proposals/librarian/tng-official-metadata-20261102/`](../proposals/librarian/tng-official-metadata-20261102/)
are deliberately `PROPOSED / METADATA_ONLY`. Two publisher pages display
season/episode slot labels, while the other three are narrower preview or
editorial mentions. These are useful **research starting points**, but they
provide no accepted Source↔Work content binding, full episode witness, or
coverage event. Likewise the 190 Wikidata research leads remain candidates.

## Safe minimum first pass

1. Select one episode from a rights-valid representation and cross-check its
   identity against a dated, reviewable roster. Keep the exact source version,
   scope, acquisition date and checksum receipts; exclude third-party content
   bytes from the public repository.
2. Propose the parent series Work, episode Work, actual Source and binding
   separately. Have a Librarian independently check the records and their
   source authority before any `ACCEPTED` lifecycle change.
3. Propose a small **original** observation and one bounded assertion, with a
   precise locator and treatment of speaker reliability. Obtain separate
   Reconciler/Auditor review of factual claims and conflicts.
4. Record each coverage state as its own explicitly accepted event; do not
   promote `DISCOVERED` into `SOURCE_BOUND`, `CLOSE_READ`, or `AUDITED` by
   inference, and do not construct a full-Mission denominator from titles.
5. Regenerate and independently review a nonempty projection/Explorer index.
   Only after a reviewed projection hash lands on `main` can the public
   index show that first admitted Mission Briefing. Release remains an
   independent, guarded GitHub Pages action.

Test this diagnostic with:

```sh
python3 -m unittest discover -s tests -p 'test_first_episode_readiness.py' -v
```

The test records are deliberately synthetic and cannot count as real corpus
admission. For system contracts, see
[`COVERAGE_DENOMINATOR_GATE.md`](COVERAGE_DENOMINATOR_GATE.md),
[`CANONICAL_PROJECTION_INTEGRATION.md`](CANONICAL_PROJECTION_INTEGRATION.md)
and the [Librarian registry guide](../registry/README.md).
