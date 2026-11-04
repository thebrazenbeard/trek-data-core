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
6. Each accepted event's governed scope names its exact Work; source-dependent
   states also name the exact Source, while discovery names its Work as the
   subject. Supersession cannot transfer attainment across Work, Source, or
   binding identifiers even when a forged scope and subject happen to match.

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

The [Original Series official roster scope comparison](../proposals/discovery/official-tos-roster-scope-20261102/RESEARCH_RECORD.md)
shows why even first-party catalogs need source-local numbering and explicit
edition rules: one service includes *The Cage* as S1E1 while another begins
with *The Man Trap*. These publisher observations remain proposal-only and
do not change the denominator.

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
coverage states. The **proposed extra mechanical gate** for disk-backed
`SOURCE_BOUND` is described in
[Source-bound custody review](SOURCE_BOUND_CUSTODY_REVIEW_GATE.md): an exact
content-addressed custody claim and separate Auditor-role review must also
match the accepted Work, Source, binding and producer. The claim pins a
privately retained byte-capture receipt checksum; it does not contain source
bytes. These checks establish consistency and a recorded review assertion,
not independently authenticated remote source bytes or permission to
reproduce copyrighted episodes or transcripts. Nonempty canonical admission
and external source/rights verification remain separate requirements.

## CLOSE_READ requires two independently reviewable custody records

An accepted `CLOSE_READ` event cannot advance the public coverage numerator
just by naming a producer and arbitrary basis strings. For disk-backed
validation, `basis_refs` must contain exactly one each of:

- `read-receipt:sha256:<64 lowercase hex>` — the SHA-256 of an exact JSON file
  at `coverage/read-receipts/<digest>.json`;
- `read-review:sha256:<64 lowercase hex>` — the SHA-256 of a separate JSON
  record at `coverage/read-reviews/<digest>.json`;
- `evidence:<id>` for every source-relative Evidence ID cited by the reading
  receipt.

Both files must be regular, single-link, non-symlinked in-repository files.
The reading receipt has `receipt_kind: CLOSE_READ_CONTENT_RECEIPT`, version
`1.0.0`, and **`verification_status: VERIFICATION_PENDING`**. It identifies
the exact accepted Work, Source, evidence-bearing binding, Source SHA-256,
research producer, full-declared-representation first/last locators, and
sorted Evidence IDs. Its `producer_ref` names
`research/<governed-lane>/batches/<batch-id>/manifest.json`; the receipt pins
that manifest's exact SHA-256. The manifest must satisfy the batch schema,
include the same Work, Source digest, and research lane, and carry the
repository's deterministic `batch_hash` over its own fields (excluding
`batch_hash`) and all sorted batch-local records. The declared required
`local_entities`/`evidence`/`assertions` counts must equal the actual batch
records. Every cited Evidence ID must exist as an exact record in the hashed
batch and in the loaded research corpus, with matching Work/Source IDs and
nonempty source-relative locators and observations. Merely listing an
Evidence ID outside the batch is insufficient.

The separate review record has `receipt_kind: CLOSE_READ_ADMISSION_REVIEW`,
version `1.0.0`, links the exact reading receipt digest and governed context,
and records an `AUDITOR`-role reviewer ID unequal to either the research role
or the exact producer manifest path, with
`decision: APPROVED_FOR_COVERAGE`. Every review-basis reference must be an
`evidence:<id>` cited in the verified batch; free-form self-declarations are
not accepted. Missing,
mis-scoped, altered, duplicate-key, hardlinked, symlinked, self-approved, or
unreviewed records fail closed. An Event's predecessor chain and the existing
Librarian Source/Work/binding gate are still required.

**Evidence ceiling:** SHA-256 and role labels prove only internal file
consistency and a recorded review decision; they do **not** authenticate an
external representation, prove a human actually read it, or cryptographically
establish that the reviewer is independent. A different `reviewer_id` string
is not a credential, and an actor with write access to both receipt files can
still impersonate a review. Those claims require genuine
external custody and human/independent audit before admission. The positive
unit test is a synthetic mechanical fixture, not accepted Star Trek coverage.
No existing accepted `CLOSE_READ` records were migrated or upgraded by this
gate. Coverage-event schema version `0.2.0` remains unchanged because the
receipt and review IDs reside in existing `basis_refs`; direct unit fixtures
without origin enforcement retain their original lightweight semantics.
Disk-backed accepted coverage remains blocked until real batch records and
independently reviewed receipts satisfy this gate.
