# Architecture audit delta — SQLite query projection PR #68 at 2db7c1d

Role: AUDITOR  
Proposal audited: PR #68 `architecture/query-db-sqlite-v0.1` @ `2db7c1d9a87969a32cac22a0eb645f7af2def306`  
Base: semantic-diff proposal PR #64  
CI: `validate-core` run `31815227216` SUCCESS

## Disposition

**USEFUL DERIVED-QUERY PROTOTYPE / NOT YET TRUSTWORTHY AS A PINNED PROJECTION CACHE**

The implementation correctly treats SQLite bytes as non-canonical and tests deterministic query content. However, the builder currently trusts a manifest hash without verifying the logical files it imports, allowing database content to diverge from the projection identity it claims to represent.

## Positive controls confirmed

PR #68:
- deletes/rebuilds derived query state rather than incrementally accumulating stale rows;
- stores the upstream logical `projection_hash` in metadata;
- preserves assertion `projection_status` and partition rather than flattening uncertainty;
- preserves full canonical source rows in `record_json` columns alongside indexed convenience columns;
- retains provenance rows, reconciliation history, entities, assertions, and relation rows;
- enables SQLite foreign keys and links provenance to projected assertions;
- compares deterministic query snapshots rather than raw SQLite file hashes;
- explicitly verifies `STRUCTURAL_PARADOX` remains distinct in query state.

Those are sound derived-database design choices.

## Findings

### AUD-DB-001 — database pins an unverified projection_hash

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

`build_database()` reads `manifest.json`, extracts `projection_hash`, and stores it in SQLite metadata. It does not:
- require the canonical logical output set declared by the manifest;
- verify each JSONL file's hash and count against `manifest.outputs`;
- recompute/verify `projection_hash` from those output hashes;
- reject extra/stale files inconsistent with the manifest contract.

The current test fixture demonstrates the gap directly: it writes `outputs: {}` and arbitrary `projection_hash: sha256:projection-a`, then supplies independently created logical JSONL files. The builder accepts them and the test asserts the arbitrary hash was pinned.

Therefore a stale, mixed, or tampered projection directory can yield a database whose rows represent content Y while metadata claims canonical projection X.

That violates the central invariant that the database is a deterministic projection of the canonical logical state rather than an independent truth/cache identity.

**Required correction:** before touching the destination DB, verify the complete required canonical output contract, per-file hash/count metadata, and recomputed projection hash. Add negative fixtures for changed JSONL bytes, missing required output, incorrect count/hash, and mismatched projection hash.

---

### AUD-DB-002 — assertion partition/status consistency is not enforced

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

The importer derives `partition` solely from filename but stores `projection_status` solely from row content.

It does not enforce:
- `facts.jsonl` -> `STABLE`;
- `unresolved.jsonl` -> `UNRESOLVED`;
- `contested.jsonl` -> `CONTESTED` or `STRUCTURAL_PARADOX`.

A malformed or mixed logical directory can therefore create a row such as:

`partition = facts`, `projection_status = UNRESOLVED`

without rejection.

Query consumers could then obtain contradictory answers depending on whether they filter by partition or status.

**Required correction:** validate partition/status invariants during import and add adversarial fixtures for mismatches.

---

### AUD-DB-003 — query-projection build identity omits SQLite schema/builder identity

**Verdict:** CONFIRMED  
**Severity:** HIGH

Metadata copies the **logical projection compiler** `compiler_commit` from upstream manifest, but does not identify:
- SQLite query-schema version;
- SQLite projection-builder commit/version;
- query-projection migration/version contract.

Two versions of `build_sqlite.py` can produce different query schemas/indexes/semantics from the same canonical projection hash while the resulting databases expose identical upstream compiler metadata.

Raw DB bytes need not be canonical, but query-schema/build provenance must still be reproducible.

**Required correction:** add explicit query projection/schema version plus query-builder identity (or equivalent deterministic build manifest) independently of the upstream logical compiler identity.

---

### AUD-DB-004 — previous known-good database is destroyed before input validation succeeds

**Verdict:** CONFIRMED  
**Severity:** MEDIUM

`build_database()` unlinks an existing destination before creating/importing the replacement.

If the new logical input is malformed or insertion fails, the exception path removes the partially built replacement. The prior known-good derived DB is already gone.

Derived state is rebuildable, so this does not corrupt canonical truth, but it makes query availability unnecessarily fail-open operationally.

**Recommended correction:** validate inputs first and/or build to a temporary database, verify it, then atomically replace the prior derived DB after successful commit.

---

### AUD-DB-005 — canonical accepted-assertion history is silently omitted from query DB scope

**Verdict:** SUPPORTED WITH CAVEAT  
**Severity:** HIGH unless explicitly scoped

PR #59 canonical output includes `accepted_assertions.jsonl` and `accepted_reconciliation.jsonl` histories.

PR #68 imports accepted reconciliation history but does not import `accepted_assertions.jsonl` at all.

A query database may intentionally expose only current assertion partitions plus reconciliation history, but if so that is a deliberate query-surface scope and should be explicit/versioned. Today the DB pins the hash of the full logical projection while silently omitting one canonical output family.

**Required resolution:** either import accepted assertion history, or declare/store the query-surface contract and imported-output set so consumers do not mistake query availability for complete logical-projection preservation.

---

### AUD-DB-006 — canonical output identity is not retained beyond projection_hash

**Verdict:** CONFIRMED  
**Severity:** HIGH

The database metadata stores high-level manifest keys but not the canonical `outputs` hash/count map (or an equivalent verified import manifest).

Even after input verification is added, retaining the verified output identities in query metadata would allow deterministic audit of exactly which canonical logical files fed the DB.

This should not become a second truth source; it should be a receipt proving derivation from the first.

## Upstream dependency caveats

PR #68 inherits all semantic limitations of PR #59/#64. A query DB cannot repair provenance fields or reconciliation semantics absent from canonical logical outputs, and it must not invent them.

In particular:
- incomplete provenance upstream remains incomplete here;
- untyped reconciliation target semantics remain upstream;
- semantic diff gaps do not become SQLite responsibilities.

## CI interpretation

Green run 31815227216 validates the current four query-DB tests: projection-hash storage, state preservation, deterministic query snapshots, and stale-state replacement. It does not test that the stored projection hash actually matches imported JSONL bytes.

## Exact next frontier

Re-audit the first PR #68 successor that verifies manifest/output identity and partition/status invariants. Query-schema/build provenance should be resolved before this layer is considered reproducible enough for downstream consumers.
