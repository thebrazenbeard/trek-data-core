# Private converted-derivative ZIP custody (proposal only)

This is a **separate, stricter-purpose** inventory for an ebook converter's
derivative output ZIP. It does not change `inventory_original_ebook_members.py`
or relax the original-source rule against zero-length `.lit`/`.txt` members.

The conversion ZIP may contain missing output files. A zero-byte `.htm`, `.jpg`
or `.css` is recorded as `CONVERSION_PLACEHOLDER`, with the SHA-256 digest of
the empty byte string (`e3b0c442...b855`), **not** as readable text, an image,
or a complete converted edition. A zero-byte `.opf` or any other empty file
type is rejected. For this exact archive, capture requires matching all three
empty-type counts; an extra empty `.htm`, `.jpg`, or `.css` fails closed.

## Private owner-host procedure

Use Python 3.10+ in an already-authorized POSIX/WSL2 runtime. Never run the
private receipt inside a repository or publicly synced directory. Prepare a
new **0700** owner-private directory; use a **new** output filename. The script
creates the file using mode **0600**, O_EXCL and O_NOFOLLOW. It reads ZIP
members in bounded chunks solely to compute hashes/verify ZIP CRC. It does
not write extracted books, OPF XML, images, HTML or covers.

```bash
python3 tools/inventory_converted_derivative_members.py capture \
  --converted-zip '/private/converted.zip' \
  --expect-archive-sha256 '<exact-64-character-lowercase-digest>' \
  --expect-files 3498 --expect-directories 348 --expect-opf 347 \
  --expect-empty-css 1 --expect-empty-htm 18 --expect-empty-jpg 8 \
  --out '/private/custody/converted-receipt.json'

python3 tools/inventory_converted_derivative_members.py verify \
  --converted-zip '/private/converted.zip' \
  --expect-archive-sha256 '<same-64-character-lowercase-digest>' \
  --expect-files 3498 --expect-directories 348 --expect-opf 347 \
  --expect-empty-css 1 --expect-empty-htm 18 --expect-empty-jpg 8 \
  --receipt '/private/custody/converted-receipt.json'
```

All per-member names, paths, sizes and SHA-256 values remain in the **private
receipt**. Console output contains only aggregate file and empty-placeholder
counts. Never commit or upload that receipt. Replay does not imply independent
semantic review; a separate verifier should check every stream hash, ZIP
identity and the 0700/0600 file protections.

The custody model retains `source_work_binding: UNRESOLVED`,
`content_completeness: NOT_ESTABLISHED`, rights `UNKNOWN`, and admission and
coverage effects `NONE`. Exact filename/stem matches between original `.lit`
and converted `.opf` entries, if any, are only candidates requiring a separate
recorded provenance link. No index-based/ordinal alignment is permitted.

Issue #23 remains a mandatory hold on new literary close reads and accepted
coverage; this proposal grants no merge, deploy, permission changes, or
source/work admission.
