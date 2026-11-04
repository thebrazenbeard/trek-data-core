# LCARS original visuals + bounded Badgey — proposed conflict resolution

**Status: PROPOSED/HELD ONLY.** This isolated local branch is not accepted
`main`, is not a Pages deployment, and is not authorization to merge or to
offer Badgey as a general-purpose or emergency-support chatbot.

## Exact inputs and deterministic construction

The literal GitHub repository was rechecked on 2026-11-04:

| Input | Exact commit |
| --- | --- |
| Accepted `main` | `3028765359001b90bc3e6b5c1835ee283b326e91` |
| LCARS visuals/navigation draft #510 | `87a996126d620605178982f77ee45718a4643141` |
| Badgey closed-domain draft #514 | `9a239038a804f1bc001996e7e7fee6a31e14072f` |

An isolated branch was created at accepted main, then #514 was cherry-picked
locally first, then #510. Git reported **three true textual conflicts** in
`explorer/index.html`, `tests/test_explorer.mjs` and
`tests/test_explorer_accessibility.mjs`; `explorer/app.js` and `explorer/app.css`
were automatically merged without textual conflict. The earlier conservative
preflight independently detected **five overlapping changed paths**, not
five actual cherry-pick conflicts.

The explicit resolutions are:

1. **HTML asset pins:** retain both original sources' actual merged HTML
   controls; recompute `app.css` and `app.js` SHA-256 from the combined bytes,
   rather than using either stale draft fingerprint.
2. **Node Explorer DOM fixture:** union the LCARS scroll-control IDs from
   #510 with Badgey's original research controls and lookup IDs from #514.
   Do not erase `discovery-artwork`, `discovery-overview`, the Badgey help
   rail or unrelated research controls.
3. **Accessibility fixture:** union LCARS previous/next scroll controls with
   the Badgey and artwork controls, preserving keyboard and focus checks.
4. **Automerge review:** require the original per-record abstract graphic
   seed/beacon, hero search jump and focusable scroll buttons *and* the
   zero-model, closed-domain Badgey chat with session-only memory, source
   cleaning, urgent/scope fallback, and a separate real-world help rail.
   No outside portrait, still, book jacket or licensed raster is added by
   this combination.

The resolved public asset fingerprints are:

```text
explorer/app.css 0992d81797259d34e0a0ee2e8fdfb7e62589916381deae44704b79d63b3eb2e0
explorer/app.js  819c77cd3fdc92be5d0064783170587f997869500bdb344338a135f7c394abd3
```

These pins must be regenerated if any subsequent code change touches public
CSS or JavaScript. No Pages publisher or remote branch was changed.

## Tests and source boundaries

| Evidence class | Result |
| --- | --- |
| Combined Explorer Node tests | 121/121 |
| Independent integration-only invariants | 4/4 within Node total |
| Explorer Python asset/index checks | 14/14 |
| Pages artifact-scope Python tests | 30/30 |
| Full repository Python suite | 1,391/1,391 |
| Repository validator | PASS; zero admitted identified records |
| Independent prior 66 prompt boundary + 15 injections + 21 context | 66/66, 15/15, 21/21 |
| Prospectively sealed 55 prompt boundary | 55/55, zero villain/source leaks |

The independent sealed corpus retains severe **classification** limits:
only 1/20 novel urgent examples was specifically recognized (19 generic
scope-limit responses), and 3/20 novel benign messages falsely escalated.
Generic neutral fallback is not reliable medical or safety triage.

Actual rendered 320px/390px mobile interaction, real browser focus/layout,
and external human/rights review were not performed: local Playwright was
unavailable. Existing DOM/CSS/Page tests are not substitutes for a real
browser. Issue #23 Source/Work custody remains unresolved; this branch
does not alter accepted research, artwork licenses or coverage.

## Competing resolution, rejected pending separate review

The tempting one-sided option—choose #510's public HTML/test files wholesale
and discard #514's copies, or vice versa—would drop Badgey research controls
or LCARS nav and artwork provenance controls. This branch instead preserves
the explicit union. It remains a **candidate**, not a proof that the joined UI
is suitable for deployment.
