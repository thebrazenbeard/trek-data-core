# Draft PR package: visitor-invoked real-world help (not automatic triage)

**Status:** DRAFT PROPOSAL ONLY — no merge, deployment or release approval.

## Dependency and exact state

- Accepted `main` is authoritative. Draft [#514](https://github.com/thebrazenbeard/trek-data-core/pull/514) is a proposal, not accepted progress.
- Parent-reported #514 draft head at packaging: `9a239038a804f1bc001996e7e7fee6a31e14072f`.
- This independently developed patch was based on local finite-dialogue checkpoint `d063bbb`; core implementation `40b73446f682bad124e98725ef0bb54dbc851410` was frozen and independently audited.
- **Integration requirement:** compare exact #514 head/tree with this local parent and reapply/rebase only the intended diff before any new PR. Do not assume commit ancestry or conflict-free cherry-pick.

## Proposed PR title

`feat(explorer): provide visitor-invoked help outside fictional Badgey chat`

## Proposed PR description

Add a native `Show real-world help (not Badgey)` button to the tokenless, browser-local Badgey console. Clicking directly requests static real-world assistance information; it does **not** inspect or classify the visitor's draft, invoke source lookup, transmit data, save chat history, fetch a model, or contact emergency services. It leaves an unfinished draft intact, interrupts scripted fictional follow-ups, and renders a separate **Real-world help // Not Badgey** response. Programmatic focus moves to the always-present help region so keyboard and assistive-technology users can reach its existing support link.

This is a **visitor-selected action** and cannot be represented as a fix for missed automatic crisis detection. It adds no authentication requirement, credential, backend, paid runtime, model weight, or storage migration.

## Exact change scope

Relative to local parent `d063bbb`, the change set is limited to:

1. `explorer/app.js` — deterministic `requestHelp()`, separate non-character response label, button click handler, topic reset, focus/scroll of help region.
2. `explorer/index.html` — one semantic `type="button"` native control with `aria-describedby` and `tabindex="-1"` for its existing real-world support region; versioned app.js digest updated.
3. `tests/test_explorer_badgey_engine.mjs` — direct-engine no-lookup/no-history/no-character invariant.
4. `tests/test_explorer.mjs` — live DOM native-button semantics, no form submission or draft erasure, separate help text, focus target, local-only behavior.
5. `tests/test_explorer_accessibility.mjs` — matching documented DOM surface inventory.

No changes to source datasets, accepted research ledgers, projection/SQL state, deployed assets, credentials, CSP network allowances, model dependencies, or paid services.

## Verification and independent review

- Implemented test-first: before code, new engine/UI tests failed because `requestHelp` and the button did not exist; before focus work, its keyboard target test failed as expected.
- Local verification: `node --test tests/test_explorer.mjs tests/test_explorer_accessibility.mjs tests/test_explorer_badgey_engine.mjs` **116/116 pass**; two asset-fingerprint Python tests and 30 Pages-artifact Python tests **32/32 pass**; `python3 tools/validate.py` **PASS**; `git diff --check` **PASS**.
- Independent immutable reviewer audit of core `40b7344`: sealed boundary 55/55, original 66/66 containment, 15/15 injection, 14/14 security, 21/21 topic isolation, 17/17 explicit-help invariants including 80 repeated calls without retained help history. Source for this review: reviewer-owned audit `c2e9992` (provided by Director).
- Independent hostile source/focus review of exact local `c4eb48c136aa62447b6f378f32990cf408abec89` **passed the bounded review**: unchanged 17/17 help controls; `tabindex=-1`, `scrollIntoView` followed by `.focus()`; no focus trap, handler-level Tab override, source lookup, or draft erasure. This is **code/test review, not a real Firefox/Chrome screenshot or screen-reader session**.

## Required human/manual checks before publication

- Keyboard: Tab to the native Help button and activate with Enter/Space; focus should move to the named help region, next Tab should reach the existing U.S. 988 external link; closing console should return to toggle as before.
- With an unsent draft in the chat box, activate Help: the draft must remain untouched and no form submission or source lookup occur.
- With an active fiction scene, activate Help, then ask `Tell me more`: fictional context must not resume.
- Confirm network panel shows no new network request on Help activation. Following the external 988 link is explicitly user-initiated.
- Run accessibility/contrast/mobile checks on the actual candidate Pages artifact; the native button should wrap rather than overflow on narrow screens.

## Non-goals and stop conditions

**Not a crisis triage tool.** Independent novel prompt checks of earlier #514-style engine behavior found only 1/20 urgent cases specifically recognized, with 3/20 benign escalations. Visitor-initiated Help does not improve those classifier figures, and generic scope fallback remains necessary. Do not describe this release as an emergency-service replacement, autonomous conversational model, trained weights inside a repository, or blanket ChatGPT-like chat.

Any unexpected source lookup, recording of help requests, external request without clicking the support link, loss of the unsent draft, inaccessible keyboard focus, or regression of the independent no-villain boundary blocks promotion. Rollback is a simple revert of the bounded UI/engine patch—no durable state migration required.
