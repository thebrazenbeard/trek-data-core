# LIT first-source admission checklist

Status: **proposal-only readiness artifact; no literary coverage effect**

This checklist belongs to the Star Trek Literary Corpus Research & Index (`LIT`) lane. It defines the minimum downstream checks LIT performs after the Librarian has admitted literary Source/Work bindings to accepted `main`.

It does not create or repair Source/Work identity. That remains Librarian work.

## 1. Accepted-state gate

Before selecting any literary work for deep reading, verify all of the following from accepted `main`:

- the Work record exists and is assigned to the LIT lane;
- at least one Source record is explicitly bound to that Work;
- the binding is accepted rather than legacy-only, proposal-only, discovery-only, or external-crosswalk-only;
- the selected Source has a stable identifier and reproducible hash/locator sufficient to distinguish the physical/source representation being read;
- source format/edition/release identity is explicit enough to avoid silently collapsing reprints, ebook releases, converted representations, or other source instances;
- container versus contained-work relationships are explicit where relevant;
- derivative lineage is represented where LIT/TXT/OPF/HTML or other transformed siblings exist;
- known unresolved source-family ambiguity is not being hidden by choosing whichever representation is easiest to parse;
- `SOURCE_BOUND` is actually supported and not inferred from filename presence, parse success, title match, or external metadata.

If any required condition fails, do not begin deep reading. Preserve the work as blocked or unresolved at the appropriate tier.

## 2. Full-source gate

A Source/Work binding alone does not establish `FULL_TEXT_AVAILABLE` or `CLOSE_READ`.

Before reading, verify:

- readable body text is available for the selected bound Source;
- beginning and ending are present;
- chapter/section structure is sufficiently intact to support stable locators;
- obvious truncation, corruption, decompression, conversion, or spine/body failure has been checked;
- if multiple source representations exist, the selected representation's provenance relationship to siblings is known enough that a derivative copy is not treated as independent corroboration;
- source completeness remains `UNKNOWN` if these checks cannot be performed.

## 3. Edge-case recheck triggers

Current Librarian migration/collision evidence is not accepted corpus state, but it identifies failure modes that must be rechecked if corresponding Works/Sources later appear in accepted `main`:

- **Ghost Ship**: recheck LZX/conversion warnings, beginning/end integrity, truncation, and original-versus-derived representation;
- **Millennium**: do not assume one physical representation equals one abstract Work; resolve component/container structure first;
- **A Time to...**: preserve component membership and series/container distinctions rather than treating a naming pattern as Work identity;
- **Worlds of Star Trek: Deep Space Nine, Volume Three**: preserve physical container versus contained-story distinctions; multiple abstract Works do not imply multiple independent physical witnesses;
- any reprint/ebook metadata such as those observed for legacy candidates **The Wounded Sky** or **Seven of Nine**: do not collapse edition/source-instance identity merely because title and story content correspond.

These names are test triggers only. They are not selected LIT works and do not become accepted Work IDs through this checklist.

## 4. Batch selection

After the accepted-state and full-source gates pass:

- select 1–3 substantial accepted Works by default;
- adjust batch size only when source structure makes another size more defensible;
- for anthologies/omnibuses, respect accepted container/contained-work modeling rather than treating the physical book as automatically one semantic Work;
- for multipart works, preserve accepted component relations and do not invent a combined identity;
- do not partition literature into new worker sub-lanes unless the accepted registry later demonstrates stable, useful empirical partitions.

Record the exact accepted `main` commit used to select the batch.

## 5. Deep-read execution

For every admitted Work:

1. retrieve/read the complete selected bound Source;
2. process the actual content, not metadata, snippets, filenames, recaps, or external summaries;
3. create Work-local entities only;
4. create source-relative Evidence with stable locators;
5. distinguish narration, dialogue/testimony, memory/recollection, dream/vision, simulation, story-within-story, altered reality, alternate timeline/universe, and uncertain frames when present;
6. create Assertions separately from Evidence and link interpretations to supporting/counterevidence;
7. apply preference-blind neutral coding;
8. preserve continuity/canon scope without forcing literary identities into screen-canon global identity structures;
9. actively record counterevidence and unresolved contradictions;
10. do not treat transformed sibling Sources as independent corroboration;
11. commit hashes, locators, metadata, structured evidence, and original analysis only, never complete copyrighted book text or large passages.

## 6. Coverage discipline

Advance only the states actually established:

`DISCOVERED → SOURCE_BOUND → FULL_TEXT_AVAILABLE → STRUCTURALLY_INDEXED → CLOSE_READ → SEMANTICALLY_ANALYZED → ENTITY_LINKED → CROSS_REFERENCED → AUDITED`

Do not infer one tier from another.

A completed LIT batch requires:

`SOURCE RETRIEVED → CONTENT ACTUALLY READ/PROCESSED → RECORDS GENERATED → VALIDATION PASSED → BATCH MANIFEST GENERATED`

## 7. Stop/fail-closed conditions

Stop or preserve uncertainty if:

- accepted Work identity is missing or changes underfoot;
- accepted Source binding is missing, superseded, or ambiguous;
- the selected source representation cannot be distinguished from a derivative sibling;
- source completeness cannot be established where completeness is required for the intended claim;
- container/contained-work structure is unresolved in a way that would change evidence attribution;
- continuity or identity ambiguity would require LIT to perform global reconciliation;
- the only support for a claim is external metadata rather than the bound literary Source;
- the source is available only as snippets/recaps rather than complete readable text.

The valid result in those cases is `UNKNOWN`, `AMBIGUOUS`, `CONTESTED`, `UNRESOLVED`, or a blocked coverage transition, not invented certainty.
