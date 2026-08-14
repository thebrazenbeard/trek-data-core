# Worker Contract

A worker is a research role, not a permanent chat identity.

## Required behavior

- Work only in the assigned corpus partition and bounded batch.
- Bind evidence to an identified source and work.
- Preserve local entity identity when global identity is not yet resolved.
- Separate source-relative evidence from interpretation.
- Preserve ambiguity and contradictory evidence.
- Use the accepted predicate registry; propose extensions explicitly.
- Finish and validate a batch before advancing coverage counters.
- Record source failures and incomplete coverage rather than substituting recaps or guesses.
- Never edit shared global identity/reconciliation state from a series worker.

## Forbidden shortcuts

- Do not convert filename presence into source-bound/close-read status.
- Do not treat repeated downstream copies of one source as independent corroboration.
- Do not turn a character statement into a world-state fact without reconciliation.
- Do not silently merge alternate, duplicated, simulated, mirrored, possessed, reconstructed, or timeline-divergent entities.
- Do not let user preferences alter primary research salience or evidence weighting.

## Batch boundary

A batch should be large enough to avoid micro-commit noise and small enough to audit. Episode-level or modest multi-episode batches are preferred. Literature batches should preserve work boundaries even when several works are processed together.
