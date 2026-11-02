# Mission Explorer index contract

The browser-facing `explorer/index.json` is a static **derivative**, not an
authoritative research store. Its labels are deliberately literal:

- **Mission** is a television series in the project's display catalog.
- **Mission Briefing** is an episode Work whose evidence is present in an
  accepted, source-bound canonical assertion projection.
- **Record** is a searchable assertion with its source IDs and projection
  status preserved. `STABLE`, `CONTESTED`, and `UNRESOLVED` must remain distinct.

The baseline catalog is sourced to the official franchise series list and is
explicitly marked `MISSION_CATALOG_ONLY`. This means **12 series cataloged,
zero episodes admitted**. The catalog cannot silently turn a historical
research branch's file list into episode coverage.

Generate deterministically from the repository root with Python 3:

```sh
python3 tools/build_explorer_index.py
python3 -m unittest discover -s tests -p 'test_explorer_index.py' -v
```

An optional admitted projection can later be supplied:

```sh
python3 tools/build_explorer_index.py --projection-dir path/to/verified-projection
```

All eight canonical projection output files must exist with matching
SHA-256/count receipts, and the aggregate projection hash must match. Each
indexed assertion must have accepted disposition, at least one attributable
evidence record, a matching Source and Work, and an **accepted
`EVIDENCE_BEARING` Source↔Work binding in each provenance row**. Missing
admission evidence fails the build. The proposal architecture must emit
`source_work_binding_record` before it can generate nonempty Explorer records.

Hash receipts alone establish bundle integrity, not independent signoff or
source licensing. The admission/review process remains governed by
`TREK_RESEARCH_METHOD.md` and `TREK_REPO_PROTOCOL.md`. The derivative exposes
only short scalar assertion metadata; it does not copy transcripts or dialogue.

The index is intentionally build-time JSON rather than a dynamic hosted API,
so GitHub Pages can serve the browser interface with no server, secrets, or
runtime access to research files. The Pages workflow should publish **only
`explorer/`** after tests pass.
