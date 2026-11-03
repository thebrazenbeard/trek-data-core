# Projection reference-custody contract (proposal, v0.3.0)

This is a **stacked draft** on the projection replay hardening in PR #223. It
does not admit research, approve semantic reconciliation, or authorize merging
or deployment. Accepted `main` remains the source of accepted state.

## Why this is needed

The v0.2 projection exported Source, Work, Evidence, and Source–Work binding
records only when reachable through an assertion's provenance. A valid
`SCOPE_RESOLUTION` for an accepted, otherwise unreferenced Work, or an accepted
reconciliation decision supported by standalone Evidence, could compile but
would be rejected by the independent verifier as an unknown reference.

## Contract

The compiler exports **twelve** canonical, sorted, canonical-JSONL outputs.
The four additional, complete research catalogs are:

| File | Identity key | Custody purpose |
| --- | --- | --- |
| `sources.jsonl` | `source_id` | Every governed Source, even without an assertion |
| `works.jsonl` | `work_id` | Every governed Work, even without an assertion |
| `source_work_bindings.jsonl` | `binding_id` | Every governed binding and supersession |
| `evidence.jsonl` | `evidence_id` | Every governed Evidence record, including standalone decision support |

The existing eight outputs are preserved. Their exact names, hash and count
receipts, alongside the new four, define the versioned bundle identity. Old
eight-output directories are rejected by a v0.3 verifier, not silently
interpreted under the newer contract.

The verifier:

1. Checks canonical serialization, unique identities, record types and
   referential closure across all four catalogs.
2. Checks Source and Work parent ancestry for dangling references and cycles.
   Every Evidence record, including standalone decision support, must resolve
   exactly one accepted evidence-bearing Source–Work binding under the same
   admission predicate used by the repository validator.
3. Checks full provenance snapshots against catalog records, including the
   exact derived-source/parent-Work ancestry and assertion subject/objects.
4. Uses the complete catalogs for decision reference membership, while retaining
   the prior fail-closed decision-schema, supersession, registry, and semantic
   replay checks.
5. Recomputes `input_hash` from the same canonical logical inputs consumed
   by the compiler: Sources, Works, bindings, Evidence, undecorated local
   entities, assertion history, version pins and reconciliation-history hash.

The SQLite and PostgreSQL derived query builders now materialize complete
Source/Work/Evidence catalogs and the Source–Work bindings. PostgreSQL uses
the new `trek_projection_v0_3` schema; SQLite's metadata announces derived
schema version `0.3.0`. Graph-search uses the common twelve-file verifier.
Explorer checks all twelve file receipts and still requires a separately
reviewed projection-hash allowlist entry; its search/admission semantics are
unchanged.

## Falsifiers and limits

- Test a valid accepted Work scope decision with no assertion referencing that
  Work. It must compile **and** verify.
- Test a valid reconciliation decision supported by accepted Evidence which
  no assertion cites. It must compile **and** verify.
- Fabricate schema-invalid catalog records, crossed or missing Evidence
  bindings, references without catalog records, scrambled provenance snapshots,
  or omitted catalog ancestry. Verification must reject them.
- Modify an otherwise unreferenced catalog record without updating the
  independently pinned logical-input identity. Verification must reject it.

> All hashes establish **internal deterministic integrity and consistency**.
> They do not independently authenticate that a particular Git head, Source
> file, reconciliation approval, or compiler binary is authoritative. An
> attacker able to fabricate *all* inputs and reissue a manifest can still
> make a self-consistent bundle. External acceptance, review, provenance,
> rights and custody must be established by separate governed processes.

Complete catalogs can contain descriptive copyrighted-work **metadata**, not
the underlying full source bytes. Before promotion, independently review the
versioned interface and run the complete tool, repository, adapter, Explorer,
and actual compiler→verifier suites on the exact proposed Git head.
