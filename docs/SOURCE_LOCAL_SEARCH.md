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

## Separate ISBN-bound publisher-edition leads (three-row overlay)

The accepted research packet at
`proposals/research/lit-three-archive-discovered-publisher-editions-20261103/records.json`
supports **three** direct Simon & Schuster *edition candidate* metadata records.
Its separate deterministic projection is
[`lit-publisher-edition-leads.json`](../explorer/lit-publisher-edition-leads.json).
It is deliberately **not appended to the hard-pinned 1,214-row Explorer directory**
or the 37 separately reviewed public publisher paraphrases. Nor should these
three be counted as three already reconciled Works.

```sh
python3 tools/build_lit_publisher_leads.py --check
python3 tools/query_lit_publisher_leads.py --validate-sources --q "McCoy"
python3 tools/query_lit_publisher_leads.py --isbn 9780743419987
python3 tools/query_lit_publisher_leads.py --tag publisher-claim:topic:genesis-wave
```

The overlay is machine-queryable offline by title, creator, ISBN, format,
series label, and *source-relative publisher-copy candidate* tags. The
`publisher-claim:` prefix is substantive: a tag records a claim appearing in
the publisher's promotional description, not an admitted fact about Trek
continuity. The linked source packet contains original paraphrases, but none
are emitted in this overlay until a separate editorial publication receipt
exists. Its fields explicitly keep `synopsis_status` held, the owner-private
archive edition equivalence `UNVERIFIED`, and all coverage, denominator,
admission, and artwork release effects `NONE`.

The generator pins the accepted source file's SHA-256 and accepted commit;
the query program independently pins the **exact canonical overlay SHA-256**
even when `--validate-sources` is absent. Thus a downloaded index with
altered tags, dates, search text, or private-looking fields fails closed when
checked against the trusted program, while `--validate-sources` additionally
compares the whole overlay to a source reconstruction. The downloaded JSON
alone cannot authenticate itself without that trusted code pin. A future reviewed
Explorer-card adapter can expose the overlay alongside the base directory,
using separate counts and independent synopsis review; this batch does not
silently add the new records to the displayed directory.
