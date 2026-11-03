# Private literary metadata intake (OPF)

Star Trek books, novellas, omnibus editions and short-story collections are
**literary Works**, not television Missions or Mission Briefings. A file on a
reader's computer may be one edition, a collection of multiple Works, a
conversion, or an incomplete/altered file. Never mint canonical identity from
a filename or an OPF title alone.

`tools/inventory_opf_metadata.py` is a local, offline **candidate inventory**
for user-supplied ZIPs containing Open eBook/OPF descriptions. It never
extracts archives onto disk, decompresses or interprets prose chapters/HTML/TXT
content, copies covers, calls a network service, or writes accepted research
state. Whole-ZIP SHA-256 receipts do stream opaque archive bytes (including
compressed member payloads), without extracting their text. It parses
only small OPF package XML files and reads the ZIP member directory for
optional `.lit`-filename matching. It exports selected Dublin Core *title,
creator, identifier, publisher, date and language* fields, not descriptions,
rights paragraphs or passages. Legacy ReaderWorks namespace variants are
recognized; invalid, unbound or unsafe XML is flagged for review. XML encodings
whose markup cannot be safely scanned as bytes (including UTF-16/UTF-32) are
held for review, not silently admitted.

ZIP member names are checked before path normalization: dot/empty components,
drive-like paths, Unicode normalization that creates separators, and
casefold/NFKC-colliding names are refused. This guards ambiguous source-file
selection; it does not establish that an otherwise valid ZIP is a genuine
edition or independently sourced literary Work.

## Run privately

With Python 3.10+ and the two user-held ZIPs at their own local paths:

```bash
python3 tools/inventory_opf_metadata.py \
  --opf-zip /private/path/to/Star_Trek_OPF_Converted.zip \
  --original-zip '/private/path/to/ST ebooks.zip' \
  --out /private/path/to/new-trek-literary-inventory.json
```

The output path **must be outside this public repository** and must not exist.
The utility will not overwrite, creates an owner-only file (mode 0600), and
requires OS support for secure directory-relative creation (POSIX `dir_fd`,
`O_DIRECTORY` and `O_NOFOLLOW`); unsupported platforms fail closed. The output
is a private file-level inventory,
not a bibliographic truth source or a catalog safe to publish automatically.
It records input ZIP hashes, member paths and per-OPF SHA-256 digests; local
filenames, edition identifiers and possession metadata may themselves be
privacy-sensitive.

The accompanying tests use synthetic XML and bytes only:

```bash
python3 -m unittest discover -s tests -p 'test_opf_metadata_intake.py' -v
```

## Review and reconciliation gates

1. Verify each OPF's descriptive fields against suitable independent
   bibliographic sources and resolve title/creator variants. An OPF conversion
   is **not independent evidence** of the source ebook; identical metadata
   from both files is one lineage.
2. Distinguish Work, edition, manifestation/file, and omnibus contents. A
   multi-Work collection cannot silently become a single novel, and a
   conversion cannot count as a second literary witness.
3. Resolve malformed and ambiguous OPF metadata through a human-reviewed
   correction record, not an automatic title guess. A matched LIT basename
   is only a local pairing hint.
4. Determine rights and source-access authority separately. User possession
   or conversion does **not** establish copyright ownership or republication
   rights. No book text, covers, images or large excerpts enter public Git.
5. Only after review may **new proposal-only** Source/Work crosswalk records be
   curated. Source-bound evidence, statements, coverage and canonical
   acceptance require the ordinary Librarian/Consolidator/Auditor gates.

The inventory sets `accepted_work_effect`,
`accepted_source_binding_effect`, and `coverage_effect` to `NONE`, and every
candidate has a `null` canonical Work ID. A passing ingestion test proves
format and safety behavior; it does not prove Trek canon or a complete literary
bibliography.
