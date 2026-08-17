# Trek Data Core

A provenance-aware research core for indexing, reconciling, and querying the Star Trek universe across screen and literary sources.

## Design principles

- Git stores immutable accepted research batches, schemas, methodology, reconciliation decisions, and projection history.
- Research workers extract local evidence; they do not silently mint global truth.
- LLMs may propose semantic or identity reconciliations, but projection builds are deterministic.
- The query database is a generated projection, never the only source of truth.
- Ambiguity, contradiction, and unresolved identity are preserved rather than forced into false certainty.
- Routine, uncontested facts can enter a fast consensus projection; difficult cases remain attached to the deeper evidence graph.
- Raw copyrighted transcripts, ebooks, video, and audio are not stored in this public repository.

See `docs/architecture.md`, `docs/research-methodology.md`, `docs/registry-and-coverage.md`, and `docs/worker-contract.md` before adding corpus data.
