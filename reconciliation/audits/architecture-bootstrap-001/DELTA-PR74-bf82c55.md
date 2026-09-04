# Architecture audit delta — graph/search PR #74 at bf82c55

Role: AUDITOR  
Current head: `bf82c55eb764ccac2d4f253fe7f977df8a2f5b80`  
Previous audited head: `fb4a1947b8365d824aa8e7a4a35bc9e5201af51c`

## Delta

Comparison shows only:
- `.github/workflows/validate.yml` CI integration;
- `tools/test_graph_search_projection.py` test expansion.

`tools/build_graph_search.py` is unchanged.

The new test explicitly verifies that non-empty `relations.jsonl` fails closed until a governed relation-row schema exists. This converts a previously code-inspected positive control into an executable regression fixture.

## Disposition

**POSITIVE TEST HARDENING / PRIOR AUD-GRAPH FINDINGS UNCHANGED**

The following remain current because the implementation bytes did not change:
- AUD-GRAPH-001 unverified canonical projection input;
- AUD-GRAPH-002 Local-Entity-only subject edge mapping;
- AUD-GRAPH-003 partition/status invariant gap;
- AUD-GRAPH-004 stale-output directory/atomic replacement gap;
- AUD-GRAPH-005 generator/schema build identity gap;
- AUD-GRAPH-006 lossy convenience search-text distinction;
- AUD-GRAPH-007 explicitly incomplete graph/search history surface.

The domain-relation fail-closed behavior is now stronger evidence than at the prior audit head.

## Exact next frontier

Re-audit PR #74 only after builder bytes change for verified canonical input, typed subject handling, partition validation, output replacement, or adapter provenance.
