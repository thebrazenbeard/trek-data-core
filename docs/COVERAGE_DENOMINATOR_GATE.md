# Coverage denominator gate — accepted registry roster only

The coverage ledger deliberately separates **observed or proposed Work
records** from an **attested reporting denominator**. Counting candidate
episode titles, Wikidata links, or research files is not evidence that a Star
Trek Mission's episode inventory is complete.

## What a resolved denominator actually means

The `RESOLVED` status is currently available **only** for a census of the
accepted, non-fixture Work records already present under
`registry/authoritative/`. Its snapshot must be stored as exact bytes under
`coverage/denominators/`, and the scope is the following explicit descriptor:

```json
{
  "claim": "ACCEPTED_AUTHORITATIVE_WORK_REGISTRY_ROSTER",
  "work_type": "EPISODE",
  "parent_work_id": null
}
```

`work_type` and `parent_work_id` form an exact-match selection against the
authoritative Work registry; `null` means a literal null parent, **not** all
parents. For a series-specific roster, a non-null accepted parent Work ID may
be selected. The scope cannot claim an independently complete Mission or
franchise episode roster through arbitrary descriptive text.

Before showing a numeric denominator, the compiler independently verifies:

1. Every eligible Work is `ACCEPTED`, has `fixture_only: false`, satisfies
   the Librarian Work contract, and is backed by a real, non-symlinked file
   in the authoritative registry.
2. `unit_ids` exactly equals the **entire** accepted Work set matching the
   scope, not a caller-selected subset. All referenced Work contents must
   match the authoritative file bytes semantically.
3. `registry_head` equals the computed SHA-256 content digest of the entire
   accepted authoritative Work roster, not an arbitrary label or a hash
   copied from the untrusted snapshot itself.
4. The denominator snapshot has the exact recorded bytes and matching
   canonical `snapshot_hash`; duplicate JSON keys or symlinked authority
   inputs are rejected.
5. Accepted coverage events likewise reference accepted, non-fixture,
   file-backed authoritative Works before contributing to the numerator.

When these checks cannot be met, reports remain
`DENOMINATOR_UNRESOLVED` or refuse the invalid snapshot. The accepted roster
hash is a deterministic **consistency check**, not a third-party signature or
independent proof that every episode of a television series is present.

## Still required for complete Mission coverage

A genuine all-episodes denominator requires a separately reviewed,
source-versioned season/episode roster with a cutoff date, explicit work
identity reconciliation (including multipart installments and special
releases), and authorization to mark the resulting Work entries accepted.
Until that mechanism is reviewed and merged, **do not interpret a
registry-relative `RESOLVED` value as complete series coverage**.

The current repository has no admitted non-fixture episode roster. Its honest
state is `DENOMINATOR_UNRESOLVED`, and candidate discovery adds no coverage.

## Source-bound coverage is independently gated

An accepted coverage-event label is not itself evidence that a Work has a
verified Source. Before `SOURCE_BOUND` can contribute to coverage, the ledger
requires all of the following:

- The Source and Source↔Work binding are both non-fixture, accepted Librarian
  records with exact matching, non-symlinked origins under
  `registry/authoritative/` and valid respective Librarian schemas.
- The binding is `EVIDENCE_BEARING`, links the event's exact accepted Work and
  Source IDs, and its `BYTE_HASH` basis exactly matches the Source's declared
  lowercase SHA-256 content hash. Other methodological bases remain blocked
  from this coverage gate pending separate authoritative admission review.
- The event's `subject_type` and `subject_id` identify that same binding, and
  its governed scope identifies the same Work and Source.
- The accepted Work itself has already passed the independent authoritative
  Work-origin and lifecycle checks described above.

The same Source lifecycle/origin rule applies to later source-dependent
coverage states. These checks establish consistency with accepted registry
records; they do **not** independently verify remote source bytes or grant
permission to reproduce copyrighted episodes or transcripts. Nonempty
canonical admission and research rights review remain separate requirements.
