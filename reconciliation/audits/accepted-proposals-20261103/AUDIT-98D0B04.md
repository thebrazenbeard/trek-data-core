# Accepted-main proposal boundary audit — 2026-11-03

**Role:** AUDITOR

**Exact accepted head inspected:** `98d0b043491a1b553d01fa1df44080f68ee6c154`
**Disposition:** `READ_ONLY_AUDIT / PROPOSAL_BOUNDARY_PRESERVED / FOLLOWUP_REQUIRED`

## Evidence classes and checks

This is a source-tree, deterministic-test and GitHub-check audit of the
named commit. It is **not** an independent viewing/reading of the franchise
source works, a formal verification, or a human editorial review.

| Check at exact head | Observed outcome | Evidence class |
| --- | --- | --- |
| `python3 tools/validate.py` | `VALIDATION PASSED: 0 identified records` | Local validation |
| `python3 tools/coverage_ledger.py report` | Zero governed events at every tier; denominator unresolved | Deterministic ledger report |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 475 passed | Local tests |
| `node tests/test_explorer.mjs` | 27 passed | Local tests |
| Eight manually selected `proposals/research/**/validate.py` programs | Eight passed, zero admission effects | Local proposal validation |
| Five local proposal-specific `test_validate.py` suites | 53 passed | Local negative tests |
| GitHub commit checks | Five checks successful, including Core Python and CodeQL | Remote CI status |

The manually checked proposal validators cover TOS *Charlie X*, TNG *The
Measure of a Man*, LIT *Slings and Arrows* #4, DS9 publisher S1, Voyager
regional splitting, SFA Press Express, SNW Season 2 last five, and the
2019 *Short Treks* cohort. The 53 local tests cover TNG, Voyager, SFA,
SNW, and Short Treks. The published Core CI workflow **does not run each
of these proposal-local checks**. Their success above is an independent
manual execution, not a claim about GitHub CI's test selection.

## Accepted proposal files are not admitted research

Recently merged proposals on `main` contain source-relative metadata,
derivative text analyses, publisher guide observations and private-library
research receipts. Their manifests preserve proposal-only status. They
have **not** been promoted into governed Source↔Work bindings, accepted
continuity Briefings, consensus projection records or the coverage ledger.

The deterministic universe directory remains **1,206 source-local
observations**, with overlap among observations and no verified global
Work denominator. This number is not 1,206 distinct verified Works.

Notable independently inspectable limitations:

- TOS *Charlie X* was read as a complete available **derivative webpage
  transcript**, not an authenticated audiovisual cut or studio script.
- TNG *The Measure of a Man* explicitly declares a purposive,
  identity-topic sample. This is not a preference-blind, representative
  episode sample, and cannot estimate corpus-wide motif prevalence.
- LIT *Slings and Arrows* #4 describes one privately read text
  representation, whose publisher-edition completeness and paragraph
  hashes cannot be authenticated by public CI alone.
- DS9 publisher date disagreements rely in part on indexed-page excerpts,
  not pinned direct page responses; the proposal preserves unresolved
  field/timezone explanations.
- Voyager regional cards and BBFC classifications concern presentation
  variants. They do not determine global episode Work identity.
- SFA `Ep. 200` and `Ep. Multiple` are media buckets in publisher
  publicity metadata, not automatically episodes or denominators.

> **Hostile challenge:** A green GitHub check or passing proposal validator
> can establish schema/internal consistency, but it cannot authenticate
> unaudited private source bytes, reconstruct missing audiovisual staging,
> establish independent upstream lineage, or license corpus-wide inference
> from purposively selected research.

## CI qualification gap and safe next gate

The reviewed-candidate step in `.github/workflows/ci.yml` intentionally
allowlists **three** already-reviewed candidate validators. It does not
automatically execute every newly merged `proposals/**/validate.py`:
untrusted proposal scripts should not gain CI execution authority merely
by appearing in the tree. This separation is a valuable control, but
maintainers must not infer that Core CI has tested all proposal-specific
validation logic.

Next: independently code-review each candidate validator, add explicitly
reviewed allowlist entries or safe data-only/schema checks by bounded PR,
then prove that the new checks fail on a falsified record. Do **not** add a
blind recursive proposal-script executor. Separately, source custodians
and the Librarian must authenticate editions/representations before any
governed coverage update.

**Effects:** No accepted source binding, Work, Evidence, Assertion,
reconciliation decision, coverage event, global identity resolution,
artwork release, Pages deployment or merge is proposed by this audit.

## Latest-main addendum: `afe25c0` (same session)

During this audit, other workers merged two further proposal-only research
batches. I refreshed GitHub and independently checked accepted
`main@afe25c07400ff14534e79b635c7551c5bed18c57`, which is five
commits after the pinned audit head in the ancestry shown by `git log`.

- New PRO batch: four derivative publisher-guide source entries spanning
  five printed slots. The combined `101/102` label is **not** promoted
  into two authenticated audiovisual Works. The inaccessible primary
  Press Express page is not falsely claimed as read.
- New TAS batch: 263 fragments from a third-party transcript of *Beyond
  the Farthest Star*, with explicit unknown upstream lineage and no
  claim of a primary audiovisual or studio-script examination.
- Both proposal validators passed independently. Their local negative
  tests passed **10** (PRO) and **8** (TAS), respectively.
- At this exact latest head, `tools/validate.py` still identifies **0**
  governed records; every coverage tier still has zero events with an
  unresolved denominator. The full repository Python suite still has
  **475 passing tests**, and the Explorer suite has **27 passing tests**.
  The generated public discovery directory remains **1,206 source-local
  observations**, not distinct accepted Works.

The additional derivative batches do not alter the original audit
conclusion or establish independent source custody. All counts in this
addendum are pinned to `afe25c0`, and later heads require fresh checks.
