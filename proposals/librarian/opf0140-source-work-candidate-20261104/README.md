# Held first nonfixture literary Source→Work candidate

Status: **PROPOSED / METADATA_ONLY / NOT ADMITTED**. This is a new bounded
Librarian candidacy, not accepted research, a claim of source-read coverage, or
a change to the public explorer. Follow issue #23's source-bound preflight hold.

## What was actually checked (2026-11-04)

- A source-local OPF metadata row already tracked in `main`'s *proposal* area
  (`opf-local:0140`) reports creator Gene Roddenberry, title
  `THE MOTION PICTURE™`, and valid ISBN10 `0743412087`.
- Using connected owner-private Lappy/WSL access, the Librarian checked that
  there was exactly one private converted OPF archive member with the pinned OPF
  member hash, and one explicit converter-declared candidate mapping to an
  original LIT member. The independently anchored archive/crosswalk receipt
  hashes are in `candidate.json`; they are **opaque fingerprints**, not public
  manifests of names or book content.
- The original LIT member was present as an ordinary owner-extracted file;
  streamed SHA-256 and byte count were checked live, and matched the private
  original archive member receipt: 314,662 bytes, SHA-256
  `910b2da59954827c2bd6311088e2de3d3934437cc20331e684ee7952ca870462`.
  No source text was read, copied or published.
- The official publisher's publicly viewed eBook listing is
  [Simon & Schuster, *Star Trek: The Motion Picture*](https://www.simonandschuster.com/books/Star-Trek/Gene-Roddenberry/Star-Trek/9780743412087),
  ISBN13 `9780743412087`. The OPF ISBN10 converts to that checksum-valid ISBN13.
  This metadata relationship **does not independently establish edition/text
  identity**.

## Exact limits

The original bytes are real, but this candidate is **not** a Source-bound
edition, an evidence-bearing Work binding, a verified complete novel, a read
book, a rights finding, or accepted coverage. The single converter-declared
link is part of the same derivative lineage, not independent corroboration.
The publisher's product page corroborates metadata, not the bytes in the
owner-held LIT. Public hashes are intentionally insufficient to retrieve or
reconstruct the private source; none of its original member names, paths,
prose, cover bytes, or directory listings are exported here.

The next qualified private work unit is to capture and reverify a standalone
source-custody receipt bound to the exact owner file; independently inspect
format integrity and content/edition correspondence *in private*, with a
documented lawful-use boundary and Librarian/Auditor review. If identity remains
uncertain, retain `METADATA_ONLY` and `UNVERIFIED`, and do not emit a
`SOURCE_BOUND` coverage event.

## Repeatable public consistency check

`python3 proposals/librarian/opf0140-source-work-candidate-20261104/validate.py`

This checker validates structure against accepted `main`'s Librarian contract,
the tracked OPF metadata proposal and pinned observation fields. The bounded
single-candidate packet is SHA-256 pinned over canonical typed JSON, with
exact source, Work, binding, evidence-class, and admission-blocker values.
This prevents unreviewed edits from silently changing provider/locator,
Work identity, claimed verification method, rights blockers, or witness claims;
it does **not** authenticate those claims independently. It **cannot**
replay the owner's private LIT byte hash, publisher page, or legal provenance;
those live observations require separate private and independent confirmation.
Seventeen mutation/contract tests include the independently reported seven
source and identity falsifiers. Run them with
`python3 -m unittest discover -s proposals/librarian/opf0140-source-work-candidate-20261104 -p 'test_*.py'`.
