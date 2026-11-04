# Resume Integration Updates — historical migration triage, 2026-11-04

**Status:** migration **proposal**. Four historical assistant assertions are
`NOT_ADMITTED`. Accepted Source/Work/reconciliation, literary or audiovisual
coverage, denominator, publication, and deployment effects are **NONE**.

Baseline: accepted `main@3028765359001b90bc3e6b5c1835ee283b326e91`.
The accompanying `MANIFEST.json` identifies Patrick's saved-chat ZIP and its
single HTML member by SHA-256, with source-relative rendered line locators. The
ZIP, images, book texts, transcripts, and raw web-page bytes are **not** stored
in this proposal. The saved chat is evidence that a historical assistant
**claimed** operations, not proof that any source was read or that GitHub or
Explorer was correctly updated at that moment. The private OPF archive is not
replayed by this validator.

## Regressions anchored to accepted public artifacts

| Hazard | Exact accepted inputs | Deterministic check | What it does **not** prove |
| --- | --- | --- | --- |
| Aggregate-preserving ISBN verification permutation, historically discussed as PR #351 | `explorer/publisher-isbn-crosschecks.json`, 39 public publisher source-local entries | Check code-owned SHA-256 for sorted `(source_local_ref, publisher_isbn13, crosscheck_state)` membership, *plus* full projection bytes and 39/30/9 counts. A held/agreement exchange preserving totals fails. | It does not authenticate privately held book editions; publisher ISBN matches do not equal source custody, text equivalence, or full reading. |
| Duplicate literary navigation reference from overlapping proposal paths | `proposals/librarian/picard-companion-editions-20261103/records.json`, `proposals/librarian/simon-schuster-three-novels-20261103/records.json`, `explorer/discovery-catalog.json` | Check both proposed *Second Self* paperback edition records refer to the same publisher URL, ISBN `9781982194833`, publisher lineage, format and candidate Work ID; exactly **one** source-local Explorer navigation row, even if total directory count remains constant. | Matching metadata from the same publisher is **not** independent corroboration and does not admit or globally reconcile the Work. |

This validator pins an **accepted-public snapshot** at the recorded main head.
It intentionally fails if the accepted metadata changes; updating its pins
requires a new review of changed source rows and projection semantics, not a
blind digest refresh. The existing `tools/build_publisher_isbn_crosschecks.py`
and `tools/build_unified_discovery.py` remain the owning builders and source
validators. This proposal adds a separate historical-migration regression
receipt; it neither modifies nor replaces those builders.

## Reproduction

At the repository root:

```bash
python3 proposals/migration/resume-integration-export-triage-20261104/validate.py
python3 -m unittest discover -s proposals/migration/resume-integration-export-triage-20261104 -p 'test_*.py' -v
python3 tools/build_publisher_isbn_crosschecks.py --check
python3 tools/build_unified_discovery.py --check
```

The hostile tests modify isolated temporary copies, never accepted data. They
exercise a preserved 39/30/9 ISBN status swap, ISBN rebinding, source identity
conflicts, same-publisher independence spoofing, and a duplicated *Second Self*
row that replaces a different row to keep the overall catalog count unchanged.

## Unresolved source custody and admission gates

1. Privately replay the exact ZIP and ebook/source receipts under authenticated
   custody; reproduce the claimed 347 OPF, 332 parse and 326 spine counts, with
   exact member identities and OPF-to-text relationships. Historical counts
   alone cannot become research coverage.
2. Audit the underlying ISBN source rows and private edition equivalence rather
   than inferring validity from 39/30/9 or a matching publisher title. Current
   publisher input validators already protect reviewed source-local metadata.
3. Treat overlapping PR histories and candidate Work IDs as reconciliation
   leads, not accepted duplicate Works or an implicit `SAME_AS` decision. A
   genuine Work identity decision needs separately reviewed evidence and a
   versioned accepted reconciliation record.

> Hostile challenge: Could exact aggregate counts conceal changed membership?
> Yes; the mutation tests intentionally preserve the aggregate while proving
> the membership gate rejects reclassification or ISBN rebinding.

> Hostile challenge: Could two source files from one publisher establish two
> independently confirmed books? No. The metadata overlap check holds both
> as source-local proposals and fails on incompatible identity descriptors.
