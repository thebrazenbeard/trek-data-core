# Source-bound custody claim and review gate (draft)

This draft adds a **mechanical evidence gate** for an accepted, disk-backed
`SOURCE_BOUND` event. Its purpose is to prevent an accepted Librarian Source,
Work, binding, and *declared* matching `BYTE_HASH` from becoming public research
coverage solely because those declarations are mutually consistent.

There are currently **zero accepted nonfixture** Source→Work bindings and zero
`SOURCE_BOUND` events on the accepted `main` used to prepare this proposal.
No existing accepted event is migrated, corrected, or promoted by this draft.

## Proposed required references

When the public coverage compiler runs with `enforce_origins=True`, each active,
accepted `SOURCE_BOUND` event must include exactly one of each in `basis_refs`:

- `bound-claim:sha256:<64 lowercase hex>` for the exact JSON file at
  `coverage/bound-claims/<digest>.json`;
- `bound-review:sha256:<64 lowercase hex>` for a distinct review JSON file at
  `coverage/bound-reviews/<digest>.json`.

The files are read by the existing no-follow, directory-descriptor-anchored
regular-file reader and must have exactly one hard link. Their UTF-8 bytes are
SHA-256 checked against their filenames; duplicate JSON keys are rejected.

The **claim** (`SOURCE_BOUND_CUSTODY_CLAIM`, v1.0.0) pins the accepted Work,
Source, binding, their canonical record hashes, the Source's *declared* content
SHA-256, the event's scope key and Librarian producer identity, and an SHA-256
of the owner-private capture receipt produced by the separately documented
`tools/source_custody_receipt.py` workflow. The claimed status must remain
`CLAIM_PENDING_SEPARATE_REVIEW`; a producer cannot approve their own claim.

The **review** (`SOURCE_BOUND_CUSTODY_REVIEW`, v1.0.0) pins the exact claim hash
and Work/Source/binding context, names a syntactically distinct Auditor-role
reviewer, cites the exact private capture receipt checksum, and records
`APPROVED_FOR_SOURCE_BOUND`. Review scope is restricted to
`PRIVATE_RESEARCH_ONLY_NO_PUBLICATION_GRANT` and `SOURCE_LOCAL_ONLY`. Altered,
missing, duplicate, mismatched, self-attributed, unapproved, or symlinked
records cause the report to fail.

## Critical evidence ceiling

> The public compiler does **not** have the owner's private source bytes or
> private receipt. A legitimate-looking claim/review pair with invented
> digests can still be written by an actor who controls both records. Even
> a syntactically distinct reviewer ID is not identity authentication.
> Hashes prove **in-repository consistency**, not that an authorized observer
> actually rehashed the source, checked its edition, or approved access.

This gate is an explicit, auditable record of a required independent review,
not a cryptographic replacement for that review. Before an actual Source is
accepted, the Librarian and Auditor must retain and independently replay the
private capture, verify exact source/representation identity, assess permitted
research access, and record their authenticated decision **outside the
compiler**. No claim establishes public reproduction, redistribution,
copyright ownership, independent corroboration, canonical Work identity, a
full-text read, or semantic coverage.

The existing progression stages remain separate: `SOURCE_BOUND` does **not**
infer `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED`, or `CLOSE_READ`. Later
accepted events need their own exact predecessor and method gates.

## Deterministic synthetic verification

The isolated unit fixture deliberately uses fake bytes and a fake private
receipt hash to test only the mechanical rule. It checks a passing two-record
chain and failures for absent review, invalid private digest, changed
Work/Source/binding fingerprints, event scope/producer swaps, self-review,
scope/publication escalation, and symlink/hardlink receipt aliases. It is
**not** a genuine Source admission or an actual external custody test.

```sh
python3 -m unittest tools.test_coverage_ledger -v
python3 -O -m unittest tools.test_coverage_ledger -q
python3 tools/coverage_ledger.py validate
```

The event schema version remains `0.2.0`: it already supports these opaque
source-relative refs in `basis_refs`. An independent methodology/rights review
and exact-head PR qualification are required before considering merge.
