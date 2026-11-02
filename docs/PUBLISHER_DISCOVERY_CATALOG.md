# Publisher discovery catalog — candidate-only source-local roster

This optional sidecar index is built deterministically from locally accepted
**proposal bundles**, not from live transcripts or newly admitted episodes.
The path/SHA-256 pairs in
[`registry/public_discovery_sources.json`](../registry/public_discovery_sources.json)
are the **entire positive input allowlist**. No wildcard scanning, network
fetching, indirect files, or implicit acceptance of new sources takes place.

```sh
python3 tools/build_publisher_catalog.py
python3 tools/build_publisher_catalog.py --check
python3 -m unittest discover -s tests -p 'test_publisher_catalog.py' -v
```

The initial `proposals/discovery/publisher-catalog.json` contains **15 source-local
candidate metadata rows**, not 15 independently verified episode Works:

- **10 Starfleet Academy Season 1 publisher-listed slots**, from one
  Paramount+ group; a companion press site is not a second independent witness.
- **5 TNG publisher-page references**, all one StarTrek.com group. Only two
  source records have season/episode ordinals; a preview, editorial mention,
  and watch-guide mention retain `null` ordinals. Their Work titles are
  **proposed associations**, not confirmed audiovisual identities.

Every row preserves the exact input bundle path, source-local identity,
publisher independence group, bounded source locator, proposed title,
observation kind, observation date, and unresolved ordinal. The source hash
confirms local bytes but **not** that the publisher served those bytes. Page
responses/revisions and full episodes have not been captured or authenticated;
the current bundles are dated observations with known review limitations.

The output is **outside `explorer/`** and separate from the canonical
`explorer/index.json` and the currently published `explorer/research-leads.json`.
This keeps the existing GitHub Pages exact asset allowlist unchanged; the
candidate sidecar is not advertised or silently deployed. Inclusion is for
*discovery and research triage only*. It must not change accepted Works,
Source↔Work bindings, Mission Briefings, continuity assertions, denominators,
or coverage. It cannot establish a franchise-wide episode inventory. An
operator adding a publisher source must first review the source and its
licensing/provenance, preserve the proposal-only schema, pin its exact bytes,
and obtain project review before publishing the sidecar. The validator fails
closed on unallowlisted paths, symlinks, SHA mismatches, source identity
collisions and any attempt to make the existing proposal rows accepted.

See [the denominator gate](COVERAGE_DENOMINATOR_GATE.md),
[Explorer index contract](EXPLORER_INDEX.md), and the proposal manifests in
`proposals/librarian/` for source-specific review risk and scope limits.
