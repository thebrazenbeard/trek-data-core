# Offline original ebook ZIP member custody

Status: **owner-private Librarian intake tool, proposal only**. This is a
reproducible mechanism for issue #404, not a report that the original archive
was available in this workspace. Director issue #23 continues to prohibit new
unbound literary close reads or coverage promotion.

## Owner-host procedure (Python 3.10+, POSIX/WSL2)

Run from a checkout of this proposal on the owner's machine, with the original
ZIP mounted read-only and a **new** output path outside all public repositories:

```bash
python3 tools/inventory_original_ebook_members.py capture \
  --original-zip '/private/original-ebooks.zip' \
  --expect-archive-sha256 c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac \
  --expect-lit 347 --expect-txt 220 \
  --out '/private/new-original-member-custody.json'
```

The paths above are placeholders. Do **not** commit the resulting JSON or send
it to the public Explorer. It contains exact private ZIP member paths alongside
stable opaque `original-local:lit:NNNN` / `original-local:txt:NNNN` IDs,
uncompressed and compressed sizes, CRC32, member SHA-256, whole-ZIP SHA-256,
and a canonical member-list digest. File payloads, book prose, images and
covers are not copied into the receipt.

Replay independently against the exact original ZIP:

```bash
python3 tools/inventory_original_ebook_members.py verify \
  --original-zip '/private/original-ebooks.zip' \
  --expect-archive-sha256 c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac \
  --expect-lit 347 --expect-txt 220 \
  --receipt '/private/new-original-member-custody.json'
```

Only a file count and `PRIVATE_CUSTODY_CAPTURED` or
`PRIVATE_CUSTODY_VERIFIED` appear on stdout. On POSIX hosts, a newly created
receipt is owner-only mode `0600` and existing outputs are not overwritten.
The implementation refuses symlinked source paths, symlink ZIP entries,
duplicate/case-ambiguous member paths, traversal, unknown file extensions,
encrypted/unsupported members, excessive compression, oversized archives and
unstable files. CRC verification occurs during bounded decompression.

The known archive hash and member counts come from earlier accepted aggregate
custody receipts. They are **operator-provided checks**, not freshly verified
against Patrick's host here. The digest of a file does not authenticate a
publisher edition, establish its rights, prove source-text completeness, or
resolve whether an anthology/omnibus contains multiple Works.

## What remains after successful owner-host execution

1. Independently replay exact source and receipt bytes on a second authorized
   custody session; check file hash/size and ZIP metadata consistency.
2. Build a **source-local candidate** LIT↔OPF↔TXT relationship ledger with
   explicit one-to-many, ambiguous, unmatched and derivative-conversion states.
   Preserve the 15 recovered OPF XML namespace cases and reported partial
   conversion; never turn title/stem similarity into canonical identity.
3. Publish only a minimal aggregate/hash evidence packet after a private-path
   leak review. Keep the full receipt off GitHub and off Pages.
4. Verify rights/editions and accepted Source↔Work bindings separately; #23
   must clear before actual literary close-reading or coverage advancement.

## Synthetic validation

```bash
python3 -m unittest discover -s tests -p 'test_original_ebook_custody.py' -v
python3 -O -m unittest discover -s tests -p 'test_original_ebook_custody.py' -v
```

These tests exercise a fabricated two-file ZIP and hostile ZIP structures. No
real Star Trek book contents or owner-private source bytes are in the tests.
