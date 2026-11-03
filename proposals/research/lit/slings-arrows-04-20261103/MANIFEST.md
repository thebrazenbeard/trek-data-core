# Slings and Arrows #4 — private-source close-reading proposal

**Lane:** `LIT` · **Date:** 2026-11-03 UTC · **State:** proposal only, not admitted or independently audited.

This is the first bounded full-text *representation* read in this partition. It does not assert that the private file is an authenticated publisher edition, create globally reconciled Trek entities, or change the accepted literary denominator. The returned Source → Work relationship remains a local, unaccepted hypothesis.

## Source custody and content processing

The user-authorized Executor on Lappy located two private archives beneath OneDrive's Documents/Books directory. This batch opened **one member only** of `ST ebooks.zip` in memory, without extracting it to a public checkout or copying its prose to GitHub:

| Artifact | SHA-256 / observation |
| --- | --- |
| Private ZIP container `ST ebooks.zip` | `c30b66c73935b3bbf75fa288a85d406329b617fba3beaf9809291017913fbfac` |
| Private member `ST ebooks txt/Next Generation/Slings and Arrows - 004 - That Sleep of Death.txt` | `bf32d8dce8121a27bb4b013ff32067da3f26b1e7238e0fce5c1f615c85240ad1` |
| Member size | 64,375 bytes, UTF-8 with no replacement characters detected |
| Content checked | All eight numbered chapters read in order, plus terminal author biography; 10,993 whitespace-delimited tokens |
| Locator basis | Numbered chapter, one-based nonempty paragraph ordinal after CRLF-separated blank-line splitting, SHA-256 of each trimmed paragraph's UTF-8 bytes |

The complete-looking sequence does **not** prove no pages are missing or that the transcription exactly matches the publisher's eBook. Re-validation from the private source is required before any accepted Work binding. This private copy is a single source lineage even if a derived OPF conversion, ebook copy, or catalog lists the same Work.

## Publisher metadata, separately from the text

The independent **publisher listing** for [*That Sleep of Death*](https://www.simonandschuster.com/books/That-Sleep-of-Death/Terri-Osborne/Star-Trek-The-Next-Generation/9781416550242) identifies Terri Osborne, *Slings and Arrows* #4, Pocket Books/Star Trek, an eBook released January 14, 2008, 43 pages, ISBN-13 `9781416550242`. This supports metadata identity matching **only**. It is not a publisher text hash or a license.

## Output and research limitations

- `records.json`: eight source-local entity occurrences, fourteen separately located, paraphrased evidence observations, and six original typed assertions. The list distinguishes dialogue, medical reports, hologram reports, action, staged performance, narrator outcome and interpretive claims.
- Every assertion identifies source evidence and a substantive limit. In particular, Sellassars's account of Barth mutualism and Dream Riders does not become objective biological or metaphysical truth; Crusher's causal explanation is identified as a character inference.
- `validate.py`: deterministic local contract check with explicit `ValueError` failures under ordinary and optimized Python. It verifies allowed locators, paragraph hashes' format, internal references, draft-only effects, exact ISBN check digit and absence of source-text fields. It **does not** independently recompute paragraph hashes from the inaccessible private text.
- `tests/test_lit_slings_arrows04.py`: CI-discovered negative regression invoking both Python and `python3 -O` against deliberately corrupted admission, coverage, artwork, source-byte and copyright gates.
- All downstream statuses remain `NONE`: accepted Source/Work binding, global identity reconciliation, accepted coverage, public research-lead denominator, and artwork release.
- No book prose, publisher synopsis, scan, cover, image, audio, ZIP content, or large passage is committed. The text's copyright and permission to redistribute remain unresolved.

## Material falsifiers and next gates

1. Compare the private member against an authenticated/rights-accessible publisher edition; record variant, omission, conversion and editorial differences. Do not infer exact edition from matching title/author alone.
2. Have an independent reviewer recompute the member SHA and sampled paragraph fingerprints, then blind-check a representative spread of chapters and counterevidence.
3. Review local entity/predicate choices and reconcile only under accepted versioned decisions. In particular, preserve the distinction between a reported cultural experience and externally verified metaphysics.
4. Keep the existing *Picard: The Last Best Hope* Open Library ISBN/cover candidate apart from this Work. The cover has no source-local row or public release authorization and cannot be used here.

Run `python3 proposals/research/lit/slings-arrows-04-20261103/validate.py` and `python3 -m unittest discover -s tests -p 'test_lit_slings_arrows04.py'`. The source checksum proof requires private user-owned access to the ZIP and is not a public CI operation.
