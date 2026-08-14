# Architecture audit delta — graph/search projection PR #74 at fb4a194

Role: AUDITOR  
Proposal audited: PR #74 `architecture/graph-search-projections-v0.1` @ `fb4a1947b8365d824aa8e7a4a35bc9e5201af51c`  
Base: PostgreSQL bundle proposal PR #71  
CI: `validate-core` run `31815709309` SUCCESS

## Disposition

**STRONG FAIL-CLOSED STRUCTURAL START / DERIVATION IDENTITY AND TYPED-SUBJECT COVERAGE STILL OPEN**

The implementation commendably refuses to invent domain graph semantics. Its main defects are inherited canonical-input trust plus incomplete structural coverage of the typed subject model now defined by Director issue #52.

## Positive controls confirmed

- structural node IDs use explicit namespaces (`entity:`, `assertion:`, `evidence:`, `source:`, `work:`), reducing cross-class ID collision risk;
- graph edges are structural only (`ASSERTION_SUBJECT`, `ASSERTION_EVIDENCE`, `EVIDENCE_SOURCE`, `EVIDENCE_WORK`, `ENTITY_WORK`);
- assertion predicate `CLAIMS` is not promoted into a graph edge merely because it exists in source data;
- projection status and partition are retained on assertion graph/search records;
- canonical source records are preserved in embedded `record` payloads for assertion/entity search documents;
- repeated source/work/evidence structural metadata conflicts fail closed rather than last-write-wins;
- non-empty `relations.jsonl` fails closed until governed relation-row semantics exist;
- graph/search output bytes and output hashes are deterministic;
- no graph database/search service is contacted.

These are appropriate anti-semantic-creativity boundaries.

## Findings

### AUD-GRAPH-001 — graph/search bundle pins an unverified projection hash

**Verdict:** CONFIRMED  
**Severity:** CRITICAL

`build_bundle()` reads only `manifest.projection_hash` before consuming JSONL files. It does not verify `manifest.outputs`, per-file hashes/counts, or recompute projection identity.

The current test fixture again uses `outputs: {}` plus arbitrary `sha256:projection-fixture` and independent JSONL files; the bundle is considered valid and pins that hash.

Thus graph/search content Y can deterministically claim canonical projection X.

**Required correction:** consume the same centralized verified canonical-projection reader recommended for SQLite/PostgreSQL. Query/adapter backends must not each trust raw directories independently.

---

### AUD-GRAPH-002 — assertion subject edges silently support only Local Entity subjects

**Verdict:** CONFIRMED  
**Severity:** CRITICAL once issue #52 typed subjects are implemented

Current logic creates `ASSERTION_SUBJECT` only when:

```python
subject in local_entity_ids
```

Director issue #52 now defines governed assertion subject types including:
- source;
- work;
- local_entity;
- assertion.

A legitimate Work-, Source-, or Assertion-subject assertion would therefore retain its literal `subject` inside the assertion node but have **no structural subject edge**, silently losing graph connectivity.

**Required correction:** after typed subjects are available upstream, map structural subject edges by explicit `(subject_type, subject)` to the correct namespace. Fail closed on missing/wrong-type targets rather than omitting the edge.

Do not infer target class from raw ID prefixes.

---

### AUD-GRAPH-003 — assertion partition/status consistency is not validated

**Verdict:** CONFIRMED  
**Severity:** HIGH

As in SQLite/PostgreSQL, filename determines `partition` while row content supplies `projection_status`. No check ensures:
- facts -> STABLE;
- unresolved -> UNRESOLVED;
- contested -> CONTESTED or STRUCTURAL_PARADOX.

Malformed upstream bundles can therefore produce graph/search nodes with contradictory status/partition metadata.

**Required correction:** central verified projection reader should enforce this once for all adapters.

---

### AUD-GRAPH-004 — output directory is not cleaned/atomically replaced

**Verdict:** CONFIRMED  
**Severity:** HIGH

`build_bundle()` calls `output_root.mkdir(..., exist_ok=True)` and overwrites the three current files plus manifest. It does not clear or atomically replace an existing bundle directory.

If an older generator version produced additional files, rebuilding into the same directory can leave stale artifacts that are not listed in the new manifest.

A consumer scanning the directory rather than manifest may see mixed generations.

**Required correction:** generate into a fresh temporary directory, verify bundle, then atomically replace or otherwise guarantee no undeclared stale files survive. Consumers should be instructed to trust manifest-declared outputs only.

---

### AUD-GRAPH-005 — bundle build provenance omits generator/schema identity

**Verdict:** CONFIRMED  
**Severity:** HIGH

The graph/search bundle manifest includes:
- bundle version;
- upstream projection hash;
- output hash/count map;
- domain-relation mapping status.

It does not identify the exact graph/search generator commit/content hash or a graph/search schema version distinct from the generic bundle version.

Different adapter implementations can produce different graph/search semantics from the same projection hash without an exact tool identity receipt.

**Required correction:** carry generator identity plus explicit adapter schema/contract version, independently from upstream logical compiler identity.

---

### AUD-GRAPH-006 — search `text` is a lossy convenience projection, not canonical literal content

**Verdict:** CONFIRMED WITH CAVEAT  
**Severity:** MEDIUM

`string_values()` recursively extracts values and joins them with spaces. Dict keys/field names and structural boundaries are omitted from `text`.

The embedded `record` field preserves the richer structural JSON for assertion/entity documents, so this is not data loss in the bundle overall. But the PR wording that search documents contain `literal canonical projection content` should distinguish:
- `record`: preserved structured content;
- `text`: lossy deterministic search convenience text.

Search ranking/query logic must not treat token adjacency or omitted field boundaries in `text` as evidence semantics.

---

### AUD-GRAPH-007 — accepted reconciliation/assertion history is absent from graph/search surface

**Verdict:** SUPPORTED WITH CAVEAT  
**Severity:** MEDIUM

The adapter consumes current entities/assertion partitions/provenance and deliberately ignores accepted assertion/reconciliation history exports.

That may be an appropriate current-search surface. It should be explicitly versioned as a **current structural/search subset** of the canonical projection rather than implying complete graph/search materialization of every canonical output.

Historical/reconciliation queries must remain available through canonical outputs or a separately governed history projection.

## CI interpretation

Green run 31815709309 proves the current five tests: structural-only edges, status preservation, literal-content/search presence, deterministic bundle bytes, and conflicting repeated metadata failure.

It does not prove canonical input identity, typed non-local subjects, partition/status integrity, stale-output cleanup, or adapter build provenance.

## Exact next frontier

Re-audit after canonical projection input verification or typed subject handling changes. Do not authorize domain relation mapping until a governed relation-row/predicate typing contract exists.
