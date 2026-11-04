# Owner-private LIT ↔ converted OPF manifest candidates

Status: **Librarian source-local proposal only**, held by Director issue #23.
This uses the two previously captured owner-private member receipts and the
converter's manifest **metadata** (one JSON and one CSV) within the converted
ZIP. It does not open original LIT books, OPF text, HTML, images or covers.

## Evidence and non-evidence

- `source_lit` from the converter CSV and `source` from JSON are explicit
  converter-provided original-file references. Each must match exactly one
  normalized basename in the independently byte-hashed private LIT inventory.
- `opf_files` is the converter's explicit claimed output filename. It must
  resolve to exactly one hashed OPF file in the converted ZIP. Matching happens
  by bounded NFKC/casefold/whitespace-normalized **full basename**, not titles,
  token similarity, file position, row order, or equal collection sizes.
- Converter JSON and CSV are **two exports of the same upstream conversion**.
  Their agreement is a consistency check, **not independent corroboration**.
- Ambiguous multiple manifest records/targets, conflicting exports, absent
  outputs, **multiple original LIT names claiming the same OPF**, and
  unreferenced OPF files remain visibly unresolved. A JSON/CSV target missing
  on only one side is contested in either direction; a target missing from
  both is unresolved. Converter-only source names absent from the original
  LIT custody receipt remain in an **opaque unbound manifest-source ledger**;
  they are never silently dropped or admitted as works. An output
  labeled `success` in a converter log still requires byte custody; it does
  not prove that a readable or complete literary work exists.
- Explicitly named `partial_with_opf` conversion results preserve that status;
  even other candidate rows carry `content_completeness: NOT_ESTABLISHED`.

## Private procedure

Use Python 3.10+ from a checkout of this **stacked draft** and an existing
POSIX/WSL owner-private 0700 directory. The three input paths below are
placeholders, not real private source paths. An output must be new and outside
the public repository; it is created 0600 without overwriting any receipt.

**Independent digest pin prerequisite:** before running, obtain both expected
`members_sha256` values from a separately verified, immutable or owner-custodied
checkpoint. Do **not** copy them from the same mutable receipt files being
checked in this invocation, nor recompute them from those files. The tool
requires an operator-attested provenance label but cannot itself independently
prove the label is truthful. If no genuinely separate trust anchor exists,
**stop**; do not use the tool or claim that its receipt has authenticated
member identity.

```bash
python3 -m tools.private_lit_opf_manifest_crosswalk capture \
  --original-receipt '/private/original-member-receipt.json' \
  --converted-receipt '/private/converted-member-receipt.json' \
  --converted-zip '/private/converted.zip' \
  --expect-original-sha256 '<original-archive-sha256>' \
  --expect-converted-sha256 '<converted-archive-sha256>' \
  --expect-original-members-sha256 '<independently-pinned-original-members-sha256>' \
  --expect-converted-members-sha256 '<independently-pinned-converted-members-sha256>' \
  --pin-provenance INDEPENDENT_OWNER_CUSTODY_CHECKPOINT \
  --expect-lit 347 --expect-opf 347 --expect-manifest-rows 347 \
  --out '/private/new-source-local-crosswalk.json'

python3 -m tools.private_lit_opf_manifest_crosswalk verify \
  --original-receipt '/private/original-member-receipt.json' \
  --converted-receipt '/private/converted-member-receipt.json' \
  --converted-zip '/private/converted.zip' \
  --expect-original-sha256 '<original-archive-sha256>' \
  --expect-converted-sha256 '<converted-archive-sha256>' \
  --expect-original-members-sha256 '<independently-pinned-original-members-sha256>' \
  --expect-converted-members-sha256 '<independently-pinned-converted-members-sha256>' \
  --pin-provenance INDEPENDENT_OWNER_CUSTODY_CHECKPOINT \
  --expect-lit 347 --expect-opf 347 --expect-manifest-rows 347 \
  --receipt '/private/new-source-local-crosswalk.json'
```

Only aggregate disposition counts are printed. The private JSON contains
opaque original/converted member IDs, evidence classes, converter-reported
status and unresolved/orphan/unbound lists, **not** filenames or book prose.
It records the supplied archive/member-list digest pins and their asserted
provenance. It must never be uploaded to GitHub or Pages.

The independent member-list pins detect a self-consistent rewrite of a
mutable custody receipt **only when** the trusted external pins remain fixed.
They are a *pinned-receipt consistency* test, **not** a fresh rehash of all
original LIT and converted OPF ZIP members. This step still rehashes the
converted ZIP as a whole and byte-checks its two converter manifests, but it
does not open original LIT, OPF, covers or prose. A new complete byte-custody
claim would require a separate guarded full-member replay.

The instrument does **not** create canonical Source/Work identity, literary
edition equivalence, independent publication verification, semantic assertions
or coverage events. All rights remain UNKNOWN. Any manifest discrepancy
requires owner-private source review; count parity never justifies pairing
unmatched leftovers.
