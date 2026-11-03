# Proposed cross-proposal bibliography consistency: *Second Self*

Status: **PROPOSAL / VALIDATION ONLY**. Accepted source/work/reconciliation,
source-binding and coverage effects: **NONE**.

## Exact overlap being checked

Two already separately authored Librarian proposals cite the same publisher
product record for *Star Trek: Picard: Second Self* (Una McCormack):

- `proposals/librarian/picard-companion-editions-20261103/records.json`,
  present in accepted `main@5127598af7e7c9a1148b11bb15863643f2914dfc`
  as **unadmitted proposed metadata**.
- `proposals/librarian/simon-schuster-three-novels-20261103/records.json`,
  separately proposed with additional eBook and audiobook manifestations.

Both use proposed Work ID `proposed-lit-picard-second-self`, paperback ISBN
`9781982194833`, the same Simon & Schuster URL, publisher provenance group,
title, creator, date, format, and extent. Their agreement comes from the **same
upstream publisher**, so it is not independent corroboration. The distinct
source proposal files do not imply two distinct narrative Works.

`tools/build_unified_discovery.py` now validates this narrow overlap before
emitting a single *Second Self* source-local navigation row. Tests fail on
contradictory Work/ISBN relationships, different publisher group, false
admission, inconsistent title/creator/page extent and related tampering.
The emitted row remains `UNVERIFIED_METADATA`, with admission and coverage
effects `NONE`. It contains paperback/eBook/audio ISBN details, **not** book
text, audio, images, a cover license, or a completed reading.

The publisher-source gate additionally pins the three reviewed novel titles,
authors and series labels and requires each product URL path to match that
Work's title, creator, series and ISBN. This prevents a false new title being
projected merely because a publisher URL retains the correct ISBN suffix.

## Boundaries and unresolved questions

- This is a deterministic metadata agreement check, **not** an accepted
  `SAME_AS` decision or a global identity-map rewrite.
- No page-byte custody, complete edition authentication, independent edition
  corroboration, or cross-format content-equivalence evidence is asserted.
- A future genuine reconciliation decision requires separately reviewed,
  versioned evidence and explicit acceptance; this proposal does not invent it.
- Draft PR #212's five fictional memoirs are a separate, still-unintegrated
  source family. Their additive integration and generated-page regression are
  pending independently of this narrow publisher overlap.

The deterministic generator and accompanying tests provide the auditable
guard. This manifest documents scope and must not be used as evidence to
promote the fiction's or editions' coverage state.
