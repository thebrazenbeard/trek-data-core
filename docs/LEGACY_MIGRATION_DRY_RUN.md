# Legacy research migration: pinned dry-run

This is a **Consolidator structural adapter**, not a source reader, semantic
reconciler, or coverage publisher. It takes an already-recovered, untrusted
legacy batch directory and emits a deterministic **unadmitted proposal** to
stdout. It neither downloads historical data nor writes to any registry.

## Why

The current `main` research ledger may show zero admitted installment Briefings
while older PR heads contain substantial authored analysis. One concrete lead
is TNG PR #3, `research/tng/batches/tng-s01-b001/`, whose manifest declares
five Works, 58 evidence observations, 31 assertions, and 69 local entities.
Those declarations and the surviving Git blobs are worth checking. They **do
not prove** that the old transcript pages were completely read, that the
transcript editions are authentic, or that any evidence is accepted today.

## Local preparation

1. Separately retrieve the exact historical batch as inert **data** from a
   pinned Git PR-head object; do not execute old tools, hooks, task scripts,
   or checkout automation. Keep the files outside the public repo until
   source provenance and rights have been reviewed.
2. Independently pin the raw `manifest.json` SHA-256, historical head commit
   and exact PR ref. The historical Git blob object ID is **not** an external
   transcript's content digest.
3. Run from the current repository with an existing private batch directory:

   ```sh
   python3 -B tools/plan_legacy_research_migration.py \
     --batch-dir /private/trek/tng-s01-b001 \
     --expected-manifest-sha256 a5e3270cc5d367739f227b799fd1e50ca808d9840643c4ef4462505ede62dea0 \
     --source-pr 3 \
     --source-head-sha 0695fb2d36870e9c156ce7acd16f00f70103b19e
   ```

   This command illustrates the recorded PR #3 manifest pin. The directory is
   an example; the script cannot conjure an archive that was not retrieved.

## What the output proves—and does not

The adapter requires an exact manifest-byte SHA, validates each named file's
SHA-256 and historical Git SHA-1 blob ID, reads only bounded regular files
without following symlinks, rejects duplicate JSON keys or local IDs, checks
counts against parsed records, and verifies assertion support references and
evidence source aliases. It retains source-relative locators and exact file
hashes **without emitting old observation text**.

Its output says `STRUCTURAL_MIGRATION_CANDIDATE_NOT_ADMITTED`. That is the
maximum conclusion: these authored records are internally recoverable and
structurally compatible with further migration review. It cannot attest the
past author's actual reading, legal access or source edition; it cannot
authenticate third-party transcript bytes, establish external-source
independence, resolve Work or character identity, prove neutrality, or
promote a coverage milestone. Even cryptographically correct old bytes can
contain incorrect or fabricated observations.

**Next gate:** the MIGRATION worker must examine original source editions,
compare source-relative observations to their locators and counterevidence,
and propose a neutral re-code; LIBRARIAN must bind source/edition provenance;
the AUDITOR and independent authority must review. Only accepted versions
may feed the Consolidator's deterministic projection. The dry-run is not that
acceptance path.

## Validations

On 2026-11-02, an isolated copy of PR #3's 12 regular Git blobs (manifest
plus 11 manifest-listed artifacts) was fetched into a private temporary
directory; no historical code was executed. Against the pinned manifest SHA
above, the dry-run **passed** and independently recounted **58 evidence
locators, 31 evidence-linked assertions, and 69 local entities**. All 11
artifact SHA-256 and Git blob IDs matched the archived manifest. The
deterministic dry-run report hash was
`e35859bfbdf43c507b18a9a98feefd056b648eeb54e58d00e9e572ccb0885cd7`.
This validates the archived *record structure and internal links*, **not**
the third-party transcript lines or actual historical full-text reading.

```sh
python3 -B -m unittest discover -s tests -p 'test_plan_legacy_research_migration.py' -v
python3 -B tools/validate.py
```

No past copyrighted transcript bodies, credentials, media bytes, or private
source snapshots belong in this public repository.
