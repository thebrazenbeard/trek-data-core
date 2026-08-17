# Registry and Coverage Contracts

## Source to Work binding

The Librarian owns Source/Work inventory and binding proposals. A `source_work_binding` record binds one concrete source instance to one governed Work identity without requiring evidence records to exist first. This keeps source discovery, editions, conversions, duplicate representations, and source lineage separate from semantic research.

Bindings carry their own status. `PROPOSED` means discovered but not accepted; `ACCEPTED` is usable by governed research; `REJECTED` preserves a disproven candidate; `SUPERSEDED` preserves history when a later binding replaces an earlier one. External IDs remain crosswalk metadata and never become Trek IDs merely by appearing in a binding.

## Coverage state

Coverage is represented by `coverage_state` records keyed to a Work and a named ledger/medium. The governed states are `DISCOVERED`, `SOURCE_BOUND`, `FULL_TEXT_AVAILABLE`, `STRUCTURALLY_INDEXED`, `CLOSE_READ`, `SEMANTICALLY_ANALYZED`, `ENTITY_LINKED`, `CROSS_REFERENCED`, and `AUDITED`.

The states are explicit booleans rather than a single ordinal. No state is inferred solely from another. Denominators are ledger-specific, so audiovisual, literature, structural indexing, semantic research, reconciliation, and audit totals are not silently combined.

Coverage records must identify the evidence of transition, such as accepted binding IDs or accepted batch IDs. A filename, planned batch, snippet, or chat claim is not transition evidence.

## Batch integrity

For a governed batch, `batch_hash` is computed from every JSON/JSONL payload file under that batch directory except the manifest itself. For each file, compute SHA-256 of its exact bytes, sort by path relative to the batch directory, serialize each entry as `<relative-path>\0sha256:<hex>\n`, concatenate, and SHA-256 that UTF-8 byte sequence. This avoids a self-referential manifest hash while making the batch payload reproducibly checkable.

`record_counts` must match the record types actually present in those payload files. `source_hashes` must correspond to the content hashes of Source records used by the batch where those hashes are available.
