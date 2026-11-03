# OPF metadata sample — held Consolidator review proposal

This is a deterministic **39-card cross-group illustrative sample of source-local OPF XML metadata**, drawn from the already-accepted 347-row librarian derivative. The selection is curated, not statistically representative. It is **not** 39 newly discovered literary Works, verified book editions, source-bound research, completed book reads, plot synopses, or public cover approvals. The 347 OPF entries may include conversions, constituent works, multipart works, collections and omnibus contents. In particular, a converted OPF and its original LIT file are not independent witnesses.

## What exists

- `cards.json`: exact original title and creator strings, source-local OPF row IDs, JSON pointers, exact original per-entry XML SHA-256, and explicit zero-effect provenance fields for 39 representative entries across source title groups.
- `tools/build_opf_sample_cards.py`: deterministic projection from `proposals/librarian/private-opf-metadata-20261103/observations.json`, pinned SHA-256 `5acb0f5af0f7c557214bcde07e60fe7e12cc9cb781c928a790341478013fd4a7`.
- `tools/query_opf_sample_cards.py`: source-local ID/title/creator search and stable pagination over the sample, validating both source and projection before any result; it cannot admit or publish Works.
- Historical `explorer/discovery-catalog.json`: byte-checked against `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`; stays **1,214** rows.
- `tests/test_opf_sample_cards.py`: deterministic and hostile checks against identity changes, parse-state changes, missing/ambiguous title or creator, entry digest changes, historical catalog changes and private-content leakage.

No copyrighted ebook text, thumbnails, covers, private member paths, GUIDs or archive downloads are included. A local OPF metadata observation does not provide a public publisher/product URL or verified creator/edition attribution; this proposal therefore does not invent either.

## Explicit holds

1. **No automatic public Explorer ingestion.** The accepted `docs/EXPLORER_LOCAL_OPF_SHELF.md` requires the 347-record owner-private metadata derivative to remain opt-in and browser-local. These held cards are not an alternative auto-loaded endpoint and do not change the existing public 11 literary leads (9 historical plus 2 Picard publisher leads).
2. **No Work identity or containment conclusion.** The sample preserves source-local IDs. It neither deduplicates nor claims an exhaustive Work census. Known archive features include omnibus/constituent overlaps and a source-filename encoding anomaly, as separately documented by the Librarian/Auditor.
3. **No source-text processing claim.** Reading OPF XML package metadata is not reading ebook prose. The source-to-Work and private-edition bindings remain unresolved; `FULL_TEXT_AVAILABLE`, `CLOSE_READ` and semantic coverage are not earned.
4. **No artwork reuse.** ISBN candidates and metadata do not grant image rights. Genuine cover candidates require edition-specific source matching and independent display-rights review.

## Verification and next frontier

```bash
python3 tools/build_opf_sample_cards.py --check
python3 -m unittest tests.test_opf_sample_cards -v
python3 tools/query_opf_sample_cards.py --q "Spock" --limit 5
```

The Librarian may subsequently link each source-local OPF to independently verified publisher/book metadata, record omnibus containment and archive edition identity, and forward reviewed source-bound proposal records. Only that reviewed lineage can justify any separate **public** literary lead overlay. No merge/deploy is requested by this proposal.
