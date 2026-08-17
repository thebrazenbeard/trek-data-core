# Librarian Source / Work / Binding proposal v1

Status: **proposal only**. These files exercise the Director contracts in issues #14 and #65. They do not create accepted Trek Source or Work identities and do not advance coverage.

The proposal keeps Source, Work, Source↔Work binding, external crosswalk, and analysis-pass provenance separate. Fixture IDs begin `FIX*`; an `ACCEPTED` lifecycle inside a fixture means “this record should satisfy validator rules for an evidence-bearing binding,” not “the project has accepted this Trek mapping.”

## Binding semantics

`source_work_binding` is independent of research Evidence. An `ACCEPTED` binding is SOURCE_BOUND-eligible only when `mapping_role=EVIDENCE_BEARING`, method and basis are present, and at least one basis item is content/hash/manifest grounded. Metadata-only or crosswalk-only association can never create SOURCE_BOUND.

The fixture set deliberately demonstrates:

- DS9 provider heading/index metadata disagreeing with audited transcript-body identity while both channels remain preserved (#41);
- one Prodigy combined Source mapping to two Work components, plus split Sources mapping to the same components (#45);
- SFA official-facing `Rubincon` versus provider `Rubicon`, with overlapping analysis passes sharing one Source witness (#47).

## Provenance and independence

A Source carries provider identity, locator, version/retrieval identity where known, optional content hash/fingerprint, variant, provenance family, independence group, and `derived_from`. Different analysis passes over one Source do not create additional Sources. A derivative representation cannot manufacture independent corroboration by assigning itself a fresh independence group.

## Validation

Run:

```bash
python tools/validate_librarian_registry.py registry/librarian_registry_fixtures.json
python tools/test_librarian_registry.py
```

The adversarial suite checks dangling Source/Work refs, metadata-only ACCEPTED bindings, missing evidence-bearing basis, supersession cycles/dangling predecessors, derivative pseudo-independence, source-derivation cycles, conflicting exclusive active bindings, dangling crosswalk targets, and authoritative registry objects placed under a research-worker partition.

## Deliberate boundary

No ebook ZIP bytes are available to this Librarian, so literary fixture bindings are not invented. The first byte-addressable archive remains the priority trigger for actual literary Source proposal work.
