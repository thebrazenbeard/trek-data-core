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
  outputs, and unreferenced OPF files remain visibly unresolved. An output
  labeled `success` in a converter log still requires byte custody; it does
  not prove that a readable or complete literary work exists.
- Explicitly named `partial_with_opf` conversion results preserve that status;
  even other candidate rows carry `content_completeness: NOT_ESTABLISHED`.

## Private procedure

Use Python 3.10+ from a checkout of this **stacked draft** and an existing
POSIX/WSL owner-private 0700 directory. The three input paths below are
placeholders, not real private source paths. An output must be new and outside
the public repository; it is created 0600 without overwriting any receipt.

```bash
python3 -m tools.private_lit_opf_manifest_crosswalk capture \
  --original-receipt '/private/original-member-receipt.json' \
  --converted-receipt '/private/converted-member-receipt.json' \
  --converted-zip '/private/converted.zip' \
  --expect-original-sha256 '<original-archive-sha256>' \
  --expect-converted-sha256 '<converted-archive-sha256>' \
  --expect-lit 347 --expect-opf 347 --expect-manifest-rows 347 \
  --out '/private/new-source-local-crosswalk.json'

python3 -m tools.private_lit_opf_manifest_crosswalk verify \
  --original-receipt '/private/original-member-receipt.json' \
  --converted-receipt '/private/converted-member-receipt.json' \
  --converted-zip '/private/converted.zip' \
  --expect-original-sha256 '<original-archive-sha256>' \
  --expect-converted-sha256 '<converted-archive-sha256>' \
  --expect-lit 347 --expect-opf 347 --expect-manifest-rows 347 \
  --receipt '/private/new-source-local-crosswalk.json'
```

Only aggregate disposition counts are printed. The private JSON contains
opaque original/converted member IDs, evidence classes, converter-reported
status and unresolved/orphan lists, **not** filenames or book prose. It pins
both archive/member-list digests. It must never be uploaded to GitHub or Pages.

The instrument does **not** create canonical Source/Work identity, literary
edition equivalence, independent publication verification, semantic assertions
or coverage events. All rights remain UNKNOWN. Any manifest discrepancy
requires owner-private source review; count parity never justifies pairing
unmatched leftovers.
