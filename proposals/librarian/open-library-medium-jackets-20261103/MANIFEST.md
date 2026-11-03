# Four medium Open Library jacket previews — source-relative candidate packet

**Status:** Source-local, proposal only. **No image-release, Source/Work identity, rights, or coverage effects.**

The current, separately reviewed Explorer artwork sidecar displays four opt-in
Open Library *small* jacket previews (`-S`, observed 38 px wide). For those exact
edition-cover pairs, a separate independent visual/source review documented
four matching *medium* JPEGs (`-M`, observed 180 px wide). This packet preserves
that observation as a candidate for a subsequent code-owned release decision.

## Evidence and limitations

- The **exact** source of the medium-byte SHA-256 values, all-four 200 JPEG
  responses, 180 px widths and jacket-visual assessments is Blotter event
  **#3466**, actor `chatgpt.trek.librarian.private_inventory`, dated
  2026-11-03. The author of this packet did not independently reproduce those
  bytes; the fingerprints are *reported observed receipts*, not current CDN
  verification.
- The existing publisher ISBN/edition/cover identity receipts are the accepted
  proposals at `proposals/librarian/open-library-nine-literature-20261103/records.json`
  and code-owned pins at `tools/validate_artwork_release.py`. This packet
  crosschecks every `(row_id, isbn, cover_id)` tuple against those pins.
- Open Library's [Covers API](https://openlibrary.org/dev/docs/api/covers)
  documents `-S`/`-M` size suffixes and `?default=false`. Its
  [licensing explanation](https://openlibrary.org/developers/licensing) does
  **not** grant blanket publisher jacket rights. All four remain
  `API_DISPLAY_DOCUMENTED_COPYRIGHT_UNRESOLVED`; no image bytes are mirrored.
- The rejected *Enterprise War* interior title page (`cover_id=12857937`) is
  explicitly held. The other four unresolved discovery titles are not inferred
  from any similar title, Work, author or alternative edition.

## Release requirements

The *medium* variant must undergo a separate, independently reviewed pin and
Explorer release/test change before browsers request any `-M` URL. A valid
candidate receipt **does not enable any remote image loading**. If enabled
later, retain the existing user opt-in, no-referrer, title/ISBN attribution,
error fallback, keyboard operation, rights-language and source link contract.

This packet can be tested without network access:

```sh
python3 proposals/librarian/open-library-medium-jackets-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/open-library-medium-jackets-20261103 -p 'test_validate.py' -v
```
