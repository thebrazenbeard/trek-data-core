# Private OPF cover identification — no public image release

The Star Trek ebook collection includes OPF package manifests and embedded
JPEG/GIF/PNG resources. Some of those images are covers, others are illustrations,
publisher logos or internal page graphics. **Image presence is not a display
license, an accepted Work identity, or proof of a deep source read.**

`tools/index_private_opf_covers.py` is a bounded offline inventory utility.
It identifies source-relative image candidates using, in descending evidence
order:

1. OPF 3 manifest items marked `properties="cover-image"`;
2. OPF 2 `<meta name="cover" content="item-id">` plus the manifest `href`;
3. a direct image `href` in an OPF `<guide><reference type="cover">`;
4. **unverified filename hints** within the same OPF package directory.

The tool does not follow an OPF guide reference to a cover HTML page: doing
so would require reading rendered page content and another review gate. If
multiple explicit targets disagree, or multiple filename hints remain, it
keeps them all and marks the package **ambiguous**. A missing explicit target
is not silently replaced with another file named `cover.jpg`.

Only direct OPF-namespace children of the package's `manifest`, `metadata`,
and `guide` sections count as those declarations. Same-name elements hidden in
another section or namespace do not become cover evidence. The image candidate
must also match JPEG/PNG/GIF/WebP signature bytes, extension, and declared
media type. This is a conservative **format signature** check, not a complete
image decode or a guarantee that the picture is the publisher's book jacket.

## Run locally under private custody

On a POSIX environment with Python 3.10+ and the user's ZIP mounted read-only:

```bash
python3 tools/index_private_opf_covers.py \
  --opf-zip '/private/Star_Trek_OPF_Converted.zip' \
  --out '/private/new-trek-cover-candidates.json'
```

The output directory must already exist, must be outside **every Git checkout**,
and must not be replaced by a symlink. The target must be a new filename.
The tool uses `O_DIRECTORY`, `O_NOFOLLOW`, exclusive `dir_fd` creation and
mode `0600` on supported systems; it **fails closed on native Windows** rather
than substituting an insecure path-based output. No user book metadata, ZIP
member paths or titles are printed to the terminal. The output JSON is
private, not a source file to commit to Git.

The report preserves, privately:

- Whole-archive SHA-256 and exact OPF member/SHA-256 identifiers;
- selected Dublin Core metadata to aid later edition reconciliation;
- explicit OPF-reference and filename-hint bases for each possible cover;
- exact source-relative private image locators, sizes, and SHA-256 digests
  of *bounded candidate image bytes* (not a copy of the image itself);
- missing links, conflicting references, invalid XML and other review holds;
- `public_artwork_release_effect=NONE`, `accepted_work_effect=NONE`, and
  `coverage_effect=NONE`.

The script never opens ebook chapter HTML, `.txt`, `.lit`, or prose-body files.
It opens only OPF XML (at most 1 MiB per package, 32 MiB aggregate) and the
image candidates needed for hashes (at most 20 MiB each, 512 MiB aggregate).
It rejects unsafe ZIP traversal, symlinks, encrypted members, Unicode/case
name collisions, entity declarations, unknown DTDs, external cover URLs,
unsupported XML encodings, and oversized archives. It never extracts files.

## Result interpretation

`EXPLICIT_OPF_REFERENCE_UNVERIFIED` means an OPF package explicitly points
to a candidate image; it does **not** prove the file depicts the actual cover,
that its artwork matches the publisher edition, or that public display is
authorized. `FILENAME_HINT_UNVERIFIED` is strictly weaker. `AMBIGUOUS_*`,
`NO_DIRECT_IMAGE_COVER_REFERENCE`, and `REVIEW_REQUIRED` are legitimate
results, not ingestion failures to paper over.

The existing [public Explorer artwork contract](ARTWORK_THUMBNAIL_POLICY.md)
remains unchanged. Any future public book-cover preview must first match an
accepted source-local Work/edition (preferably ISBN), verify an appropriate
provider display route or explicit rights receipt, preserve attribution and
opt-in, then undergo an independent rights and exact-image review. User
possession or conversion of an ebook does not license its covers for public
redistribution.

## Validation

```bash
python3 -m unittest discover -s tests -p 'test_private_opf_cover_index.py' -v
```

The suite uses synthetic ZIPs, OPF XML and fake image bytes; no copyrighted
source files, account credentials or network connections are required.
