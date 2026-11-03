# Public publisher ISBN crosschecks — source-local Explorer shelf

This optional Explorer shelf projects **39 distinct accepted Librarian observations** of public Simon & Schuster product-page metadata (title, named creators, ISBN-13, format, and direct publisher URL). It is not a book corpus, a rights or edition authentication service, or a global Work register.

The source lineage is **one publisher family**, not 39 independent witnesses. Thirty rows record an identifier-level publisher agreement with a locally observed OPF ISBN; nine preserve a discrepancy: two ISBN format differences, two creator renderings, one title spelling and four publisher-date conflicts. Every row has `private_edition_equivalence=UNVERIFIED`, `work_identity=NOT_RECONCILED`, and zero synopsis, artwork, admission or literary coverage effects. Neither private OPF content nor private archive locations are projected.

These observations are disjoint from the already accepted **3** literary publisher-edition candidates, **1,214** multimedia directory rows, **56** historical metadata rechecks, and **61** additional first-party publisher-card checks. Do not add them together as a Work, episode or audited coverage denominator.

## Reproducible source boundary

The compiler reads exactly five accepted, public `proposals/librarian` `records.json` files and checks their source-family/custody/no-admission boundaries, unique local IDs, valid ISBN-13 checksums, publisher-host URLs and status allowlist. The JSON contains a SHA-256 receipt for every accepted public input and has deterministic sorted records. It fails closed on unknown source IDs, duplicates, new status labels, unexpected batch counts and stale bytes.

```sh
python3 tools/build_publisher_isbn_crosschecks.py --check
python3 tools/query_publisher_isbn_crosschecks.py --validate-sources --limit 10
python3 tools/query_publisher_isbn_crosschecks.py --state HELD_PUBLISHER_DATE_DISCREPANCY
python3 -m unittest tests.test_publisher_isbn_crosschecks -v
```

The downloadable machine-readable artifact is `explorer/publisher-isbn-crosschecks.json`. Explorer validates the **complete code-pinned SHA-256** of that artifact before rendering, and independently checks its public schema and identity-neutral statuses. On missing, modified or malformed bytes, this optional shelf reports **unavailable**; the existing directory and publisher-edition shelves remain accessible.

## Review and editorial boundaries

- A publisher-page title/ISBN rendering is a **source-local metadata observation**, not proof that the corresponding private ebook is authentic or textually equivalent.
- A discrepancy marked `HELD` remains unresolved until a separate, reproducible, accepted research decision; no reconciliation occurs in this projection.
- Do not copy publisher synopsis text, cover files, private OPF details or full books into this artifact.
- Any new accepted source batch must update the explicit compiler scope, output digest, schema guards and tests; it cannot silently increase the cardinality.
