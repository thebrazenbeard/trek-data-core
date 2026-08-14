# Architecture

## Canonical flow

`SOURCE -> WORK -> LOCAL ENTITY -> EVIDENCE -> ASSERTION -> ACCEPTED RECONCILIATION -> DETERMINISTIC PROJECTION -> QUERY DATABASE`

### 1. Sources
A source is a concrete transcript page, ebook file, edition, API response, external dataset snapshot, or other evidence-bearing artifact. Source identity must preserve provenance, retrieval/version information, and a stable hash where available.

### 2. Works
A work is the governed creative or reference unit to which one or more source instances are bound. Source identity and work identity are distinct: editions, releases, containers, conversions, and derivative representations must not be collapsed merely because they appear to contain the same material.

### 3. Local entities
Workers create source/work-relative entity occurrences inside their assigned partitions. Local entities preserve unresolved identity and continuity questions and must not be silently promoted into shared global identity state.

### 4. Research batches
Workers write bounded, immutable batches inside their assigned corpus partition. A batch contains local entities, evidence, assertions, and a manifest. Workers do not edit shared global entity registries.

### 5. Reconciliation
Identity links, scope resolutions, supersessions, and other semantic decisions are versioned records. LLMs may propose decisions. Accepted decisions become immutable inputs to compilation. A later correction appends a successor decision rather than rewriting history.

### 6. Deterministic compiler
The compiler contains no LLM calls and no semantic creativity. The same accepted inputs, schema version, predicate registry, methodology version, and compiler commit must produce the same canonical logical projection.

### 7. Projection
Projection outputs are canonical JSONL plus a manifest. They are content-addressed and immutable. SQLite/Postgres/graph/search systems are derived query engines built from that logical projection.

### 8. Audit
Programmatic audit is mandatory. Semantic audit is complementary and should be blind to prior conclusions where practical. A semantic auditor proposes findings; it does not mutate accepted research while auditing it.

## Consensus gravity

The system does not reason from scratch for every boring query. Accepted, scope-resolved, uncontested propositions may be materialized into a fast consensus layer. When contradictory evidence, identity ambiguity, timeline divergence, frame uncertainty, mind/memory manipulation, retcon, or source dependence appears, the proposition is demoted for deeper reconciliation.

Projection states are currently: `STABLE`, `CONTESTED`, `UNRESOLVED`, and `STRUCTURAL_PARADOX`.

`STRUCTURAL_PARADOX` means the accepted narrative evidence is mutually incompatible under the current continuity model. It must not be used merely because a worker is confused.

## Identity

Identity is not a universal `same_as` boolean. Workers emit local entities. The Consolidator may later link them to global entities or to identity relations such as counterpart, duplication, divergence, merge, or shared causal history. Continuity dimensions are lazy: they are activated only when evidence or an assertion actually challenges one.

## History

Three histories remain independently inspectable:

1. Evidence history: what sources supplied.
2. Reconciliation history: what semantic decisions were accepted and superseded.
3. Projection history: what the accepted corpus compiled to under a pinned methodology/compiler state.
