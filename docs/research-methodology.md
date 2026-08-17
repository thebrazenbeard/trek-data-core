# Research Methodology

## Tiered processing

Corpus scale requires progressive depth. A work may advance through distinct states:

`DISCOVERED -> SOURCE_BOUND -> FULL_TEXT_AVAILABLE -> STRUCTURALLY_INDEXED -> CLOSE_READ -> SEMANTICALLY_ANALYZED -> ENTITY_LINKED -> CROSS_REFERENCED -> AUDITED`

Do not collapse these states into one `done` flag, and do not infer a later state from an earlier one.

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
2. a fixed regression suite of known difficult narrative cases;
3. generated adversarial anomaly tests that verify graceful handling of previously unseen identity, timeline, testimony, and narrative-frame structures.

A small deliberate overlap between independent research passes may be used to estimate classification drift. Disagreement is data; it is not automatically averaged away.
