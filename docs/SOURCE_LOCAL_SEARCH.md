# Source-local callable search (v1)

The Explorer publishes [`search-catalog.json`](../explorer/search-catalog.json), a
deterministic, downloadable JSON projection of the **accepted public discovery
directory** and its exact-key metadata/synopsis sidecars. The JSON URL is a
static document, **not a backend API**. Query parameters appended to the Pages
URL do not filter results. Run the standard-library CLI locally instead:

```sh
python3 tools/build_source_local_search.py --check
python3 tools/query_trek_index.py --validate-sources --q "The Doomsday Machine" --series TOS
python3 tools/query_trek_index.py --medium LITERATURE --synopsis reviewed_publisher_paraphrase
python3 tools/query_trek_index.py --tag source:publisher:paramount --limit 40 --offset 40
python3 tools/query_trek_index.py --source-input explorer/research-leads.json --verification rechecked_exact
```

To query a downloaded copy outside the checkout, use `--index /path/to/search-catalog.json`
and omit `--validate-sources`. For independent reconstruction, retain the four
named public JSON inputs and compare their full-file SHA-256 hashes against
`source_input_sha256`. `--validate-sources` checks their exact bytes in the
checkout **and compares the entire JSON to a deterministic rebuild**; `--check`
checks the committed index byte for byte. A downloaded JSON file with no
independent source copy is not cryptographically authenticated merely because
it includes hashes claiming provenance; verify against accepted Git provenance
for stronger assurance. Structural tag namespace and facet consistency are
still checked in downloaded/offline mode.

Supported filters: `--id`, `--q` (casefolded Unicode, AND of whitespace terms),
`--medium`, `--series`, `--kind`, `--source-group`, `--source-input`,
`--context` (source-supplied contextual text, including author/publisher when
present), `--verification`, `--synopsis`, repeatable `--tag` (AND), `--limit`
from 1 to 100, and nonnegative `--offset`. The JSON response has
`total_matches`, `offset`, `limit`, `next_offset`, and `rows` in stable ascending
**source-local row ID** order. A result includes exact source path, locator,
structural tags, publicly reviewed synopsis-receipt hash when applicable,
and metadata-recheck batch. No query executes server-side.

The two interfaces share structural facet semantics. They intentionally differ
in convenience free-text search: the Explorer additionally recognizes friendly
series labels; the downloadable index additionally searches `source_input`
provenance paths and published publisher-paraphrase synopsis text. Both preserve
original source-local row IDs and never infer global work identities.

Structural tags only: `medium:*`, `kind:*`, `series:*` for an explicit episode
context code, `source:*`, `metadata:*`, `synopsis:*`. There are **no derived
themes, canon labels, ethics, motifs, creator identity, or global Work IDs**.
Such semantic dimensions require independently sourced evidence and accepted
reconciliation records, not a search compiler's guesses. Source publisher
names/creator text may be searched as source context without parsing them into
globally identified entities.

The current index's 1,214 source-local rows can include multiple leads for the
same episode. They are not 1,214 distinct franchise works; they are not
admitted evidence or close reads. The 56 rendered metadata rechecks and 37
publisher-paraphrase synopses are display/search statuses only. In particular,
even a rechecked title remains `verification_status: UNVERIFIED_METADATA` in
the original discovery record. Later accepted research batches do **not**
silently alter this projection until their separately controlled public sidecar
is explicitly updated and the index rebuilt. The GitHub Pages release remains
an explicit manual action after complete validation.
