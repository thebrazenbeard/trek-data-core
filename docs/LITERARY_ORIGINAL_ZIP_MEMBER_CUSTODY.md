# Private original-ebook ZIP member custody (proposal-only)

`tools/inventory_ebook_zip_members.py` supplies the missing byte-level bridge
between the 347 privately inventoried converted OPF packages and the original
ebook ZIP's 347 LIT / 220 TXT member observations (owner-reported counts until
the exact local invocation succeeds). It does not read text as prose, extract
books, assign a canonical Work or Source identity, or advance accepted coverage.

## Owner-only offline use

Run locally under a user-controlled **Linux or WSL POSIX** account (on Windows,
invoke Python **inside WSL**, not native PowerShell Python), supplying the
actual file paths only as **local arguments**. Never paste source paths or
private JSON into a GitHub issue, Actions log, PR, Explorer page, or public
repository.

```bash
python tools/inventory_ebook_zip_members.py \
  --original-zip /private/location/original.zip \
  --expected-sha256 YOUR_PREVIOUSLY_VERIFIED_64_CHAR_SHA256 \
  --opf-zip /private/location/converted-opf.zip \
  --out /private/location/new-member-custody.json
```

The OPF ZIP is optional; when supplied, this tool reuses the existing
`inventory_opf_metadata.py` bounded OPF-only parsing. That older OPF helper
reopens its input by path and does not yet pin its file descriptor as strongly
as the *original-member* scanner; supply a separately custody-verified,
user-controlled immutable converted ZIP. Links are **source-local,
unverified filename-stem candidates**, not assertions that an OPF describes
the same textual edition as a LIT or TXT file. Ambiguous or absent LIT
matches remain unresolved. All 347 candidate OPF records are retained as
ordinal source-local hints, never accepted Work identities.

Output must be newly created outside the repository under a pre-existing,
non-symlinked parent. On POSIX, the output file is opened exclusively at mode
`0600` relative to a pinned directory. This mode alone does **not** establish
Windows ACL privacy when running from WSL on DrvFS: keep output in a privately
ACL-protected folder and verify its Windows effective permissions separately.

## Exact receipt scope

- Whole original ZIP SHA-256 is replayed after member scanning against the
  same opened regular-file descriptor, with before/after file stat comparison.
- Member receipt: ordinal local ID, SHA-256 of opaque member bytes, declared
  compressed and measured uncompressed size, CRC-32, extension type, SHA-256 of
  member name. The name itself and full contents are never serialized.
- Rejects symlinked original input, unsafe/traversal paths, casefold/NFKC name
  collisions, ZIP symlinks and special files, encrypted members, unsupported
  compression, unexpected extensions, CRC/size mismatch, and oversized or
  extreme-compression members before private output creation.
- Does not emit filenames or local source paths on stdout/stderr. An input
  filename hash is *not* anonymity against guessing; this private JSON must
  never be published.

The accepted Source/Work admission hold in issue #23 remains untouched.
Repeat this exact-byte inventory only after verifying the original archive
custody digest. Even a successful 567-file receipt proves *local byte possession*
and bounded processing, not title, edition, authorship, rights, canon, close
reading, or semantically analyzed coverage.

## Validation

```bash
python -m unittest discover -s tests -p 'test_private_ebook_member_intake.py' -v
```

All tests create disposable synthetic ZIPs. They must not use actual
copyrighted source contents, or write private member receipts into Git.
