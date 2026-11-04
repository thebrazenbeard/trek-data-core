# DS9 B009 typed-intake correction — November 4, 2026

**Role:** DS9. **Accepted comparison:** `main@3028765359001b90bc3e6b5c1835ee283b326e91`.
**Scope:** Proposal validator and hostile regressions only. No source records, Work
identity, Source↔Work binding, evidence, assertions, coverage events, or release
assets are changed.

The accepted Season 7 tail `observations.json` uses JSON booleans for held
source-capture and admission-relevant flags, and integer episode ordinals.
Python equality alone did not enforce these types: the original validator
accepted the substitutions `proposal_only: 1`, `current_raw_html_captured: 0`,
`actual_episode_or_script_read: 0`, `season: 7.0`, `episode: 17.0`, and
`additional_s7e26_inferred: 0` while returning nine held cards. These were
**synthetic mutation probes** on the validator, not observed source data.

The corrective validator now checks exact Python JSON-decoded types as well
as values, including the finale hold. Tests exercise each previously accepted
mutation and the unchanged accepted candidate snapshot in normal and
optimized Python mode. Type fidelity is a mechanical intake invariant; it
does not authenticate a publisher page, settle the finale's cut/part identity,
or justify new episode research while Director hold #23 remains open.

> **Hostile challenge:** A source-only metadata proposal that accepts numeric
> stand-ins for booleans can preserve a visible `NONE` status while corrupting
> the machine contract on which later admission checks may rely. Exact types
> must be enforced before any downstream consumer treats those fields as
> governed flags.

The existing batch manifest and observational records retain their historical
source-local provenance, unresolved finale presentation, and zero admission
effects. This is a correction proposal, not a new close-read batch.
