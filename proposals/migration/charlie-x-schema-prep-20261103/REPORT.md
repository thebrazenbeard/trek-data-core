# Charlie X legacy migration — unadmitted schema preparation

**Lane:** Migration (legacy proposal only). **Status:** `HELD_NOT_ADMITTED` under Director Issue #23. This report and its read-only adapter do **not** admit a Source, Work, Source↔Work binding, evidence, assertion, coverage event, or reconciliation. They do not reclassify the source as `CLOSE_READ`.

## Input and provenance boundary

The existing packet at `proposals/research/tos-charlie-x-derivative-close-read-20261103` reports 20 source-local entities, 14 source-relative evidence windows, and 7 proposed assertions, bound to a third-party derivative transcript page. Its manifest records an observed 144,687-byte HTML retrieval with SHA-256 `4498f2ac33c4e1aa4c48123aab84254b890fb9dd8603f0540189d7abdcd3c616`, and a 27,813-byte / 833-line rendered derivative digest `0e033f6883644602b7a941619f4f895e3780feffdc92e2a3a20f0e295721e849`. These are **reported provenance checksums**, not independently retrievable current custody: the source bytes and derived text are **not preserved in an authenticated durable location**. No authenticated episode video or studio script is established. The original packet is not altered here.

## Mapping evaluated in memory

| Legacy field | Governed target shape | Deliberate restriction |
| --- | --- | --- |
| `entities[].id/label/kind/notes` | `local_entity_id/label/entity_kind/notes` | Keep source-local identity, no global node resolution. |
| Legacy `work_local_id` | `work_id` on all candidate records | Candidate only; no canonical Work binding. |
| Legacy `source_local_id` | `source_id` on evidence | Candidate only; no canonical Source binding. |
| `evidence[].id/start_line/end_line` | `evidence_id`, structured `locator` | Locator explicitly tied to rendered text checksum, **not primary audiovisual timecodes**. |
| `evidence[].kind` | `legacy_evidence_kind` extension | Governed `evidence_kind` conservatively `other`; the legacy tags do not map losslessly to `depiction`/`testimony`/etc. |
| `evidence[].observation/local_entity_ids` | `observed.source_relative_summary` and local reference IDs | No transcript summary becomes an objective plot fact; epistemic status `UNKNOWN`. |
| `assertions[].id/subject_type/subject/predicate/object/evidence` | `assertion_id` and governed assertion fields | All remain `PROPOSED`. Subject/evidence references must resolve inside this proposal. |
| `context_evidence_ids/counter_evidence_ids/counter_evidence_search/falsifier` | Same-named **proposal-only extensions** | Preserve original counterargument rather than flattening it into support. |
| `scope/proposed_projection_status` | Same governed fields | Interpretive contest remains scoped to derivative text. |

`prepare.py` first invokes the **original legacy `validate.py`**, then independently checks each original validator-pinned source/manifest identity field (including the rendered-text and raw-HTML SHA-256s) against the in-memory migration input. A mutable `MANIFEST.json` may not silently change the transcript hash while retaining valid referenced record-file hashes. The adapter builds a **memory-only schema-shaped preview** and prints only counts/custody status. No JSONL batch, authoritative registry mutation, or corpus staging output is written. `tests/test_tos_charlie_x_migration_preparation.py` checks required schema fields/enums, exact source-file SHA-256 identities, referential links, locators within 833 derivative lines, count invariants, and negative tampering cases that fail closed.

## Gaps blocking admission

1. **Source custody:** no durable authenticated source bytes behind reported derivative transcript hash; source-relative line positions are not reproducible from this repository alone.
2. **Source↔Work binding:** Issue #23 requires governed Librarian binding/admission decisions. Both IDs remain temporary candidate IDs.
3. **Primary-source independence:** derivative transcript source lineage is unverified; named upstream attribution is a self-report and not independent corroboration. Authenticated audiovisual/script observations remain unverified.
4. **Episode ordinal:** Paramount-publisher `S1 E3` and derivative caption `Season 1 episode 2` remain source-relative, not silently unified.
5. **Semantic taxonomy:** legacy evidence-kind categories are not isomorphic to governed enum. `other` and verbatim legacy tag avoid invented certainty; a later semantic reviewer may propose a reasoned mapping.
6. **Accepted reconciliation and coverage:** zero accepted assertions, briefings, identity decisions, or coverage events; only a Consolidator with appropriate accepted prerequisites can make deterministic projection candidates.

> **Hostile challenge:** A structurally valid object can be mistaken for an admitted evidentiary record if someone consumes preview output without its `NOT_ADMITTED` context. Therefore the script intentionally does not serialize the full preview to a corpus file, and any later export requires a separate, explicit admission check.

> **Hostile challenge:** Even if every claimed line was actually processed during the prior worker session, the absence of durable raw/derived source bytes makes a reproducible `CLOSE_READ` claim uncheckable. Hashes without authenticated custody are insufficient.

## Validation and next frontier

Run `python3 -m unittest tests.test_tos_charlie_x_migration_preparation tests.test_tos_charlie_x_proposal_identity -v` and `python3 proposals/migration/charlie-x-schema-prep-20261103/prepare.py` from the repository root. No network, model inference, or external service is required.

**Next frontier:** Librarian Source/Work and custody issue resolution; a separate source-authentication and independent full-text or audiovisual check; governed admission before compiling into accepted evidence. The fanfiction lane is independent and deferred.
