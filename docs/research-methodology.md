# Research Methodology

## Tiered processing

Coverage is tracked with distinct states and must never be collapsed into one `done` flag:

`DISCOVERED -> SOURCE_BOUND -> FULL_TEXT_AVAILABLE -> STRUCTURALLY_INDEXED -> CLOSE_READ -> SEMANTICALLY_ANALYZED -> ENTITY_LINKED -> CROSS_REFERENCED -> AUDITED`

Each state is reported independently. A later state must not be inferred merely because an earlier state is true, and file presence alone establishes none of the semantic states. Coverage denominators remain separable by medium and ledger.

## Evidence before interpretation

The narrowest safe primitive is source-relative evidence, not an assumed objective world-state fact.

Examples:
- a transcript depicts a character utterance;
- a ship computer reports a sensor result;
- a character recalls an event;
- an artifact depicts a visual state.

Those observations do not automatically establish the truth of the proposition reported by the character, computer, memory, or simulation.

## Epistemic context

Evidence may carry categorical context such as `BASELINE_DIEGESIS`, `DREAM`, `VISION`, `MEMORY`, `SIMULATION`, `HOLODECK`, `ALTERNATE_TIMELINE`, `MIRROR_UNIVERSE`, `POSSIBLE_HALLUCINATION`, `STORY_WITHIN_STORY`, or `UNKNOWN`. Uncertainty remains representable. Do not manufacture numeric precision where the source does not justify it.

## Assertions

Assertions are interpretations or propositions supported by one or more evidence records. New semantic predicates enter the predicate registry as `PROPOSED` or `EXPERIMENTAL`; workers may not silently redefine accepted predicates.

## Drift control

Use three complementary controls:

1. deterministic schema/graph validation;
2. a fixed regression suite of known difficult Trek situations;
3. synthetic/adversarial anomaly fixtures that verify graceful handling of previously unseen identity, timeline, testimony, and narrative-frame structures.

Regression fixtures test invariants rather than canon conclusions: contradiction must remain representable, unknown structures must not be discarded, local identities must not be silently merged, and source-relative reports must not become world-state truth automatically.

A small deliberate overlap between independent research passes may be used to estimate classification drift. Disagreement is data; it is not automatically averaged away.
