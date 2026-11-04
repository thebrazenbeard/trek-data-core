# Trek Research — independent AUDITOR cross-PR audit

Date: 2026-11-04. Reviewer: native AUDITOR subagent (`/root/auditor_wave`). Scope: **read-only** hostile review of draft proposals. Evidence classes are specified below; review is not formal verification or accepted research.

## Authoritative state and evaluated heads

Accepted `thebrazenbeard/trek-data-core` `main`: `3028765359001b90bc3e6b5c1835ee283b326e91` (live `git ls-remote`, not inferred from prior conversations).

| Open, unmerged draft | Exact evaluated head | Focus |
|---|---|---|
| `trek-data-core` #486 | `8f71963f905eb4c2169ef46a1b488a257a99cc7e` | Integrated Badgey Explorer, filters, static assets |
| #487 | `a752e35bf24edb0dc4eef634e4c097ce48d1c6ff` | Badgey source leads and source distinctions |
| #488 | `eea7478b08a1ae1b34bf27e74b8884f33f36a1a6` | Discovery metadata leads |
| #489 | `480b6dfa89e7bc734d1b365678c991992802941a` | Projection guard |
| #490 | `2ba79e7234cca07d9b4cea1ad78969a2dc73c6dd` | Artwork filter copy |
| `thebrazenbeard/badgey` #1 | `67ddfd52ffed24b13e5755ac8b2ad320fc5421bc` | Standalone weighted-intent prototype |

All six are proposals rather than accepted `main`. Repository methodology and project files were read. GitHub CI `Core Validation and Workspace Startup Safety` reported success for the five Trek draft heads; this does not establish semantic equivalence or safety completeness.

## Findings

### P1 — Imminent **third-party** danger routed as ordinary Badgey conversation

**Evidence class: deterministic runtime test + source inspection**, separately exercised against the exact Explorer #486 and standalone Badgey #1 heads. The public-facing script supports first-person crisis overrides but misses clear third-party urgent phrases. This matters even if fictionally styled, because the chat is accessible to general visitors.

| Input | Explorer #486 actual | Standalone #1 actual | Expected safety disposition |
|---|---|---|---|
| `My friend is about to jump off a bridge right now` | `conversation`; generic `Hm. Elaborate...` | Same | Urgent third-party self-harm support; encourage emergency response |
| `My dad wants to kill himself tonight` | `conversation`; generic | Same | Urgent third-party self-harm support |
| `My little sister is having a seizure` | `conversation`; generic | Same | Urgent medical guidance/emergency services |
| `I took 30 Tylenol tablets` | `urgent-safety` | `urgent-safety` | **Positive control passes** |
| `I might crash my car to end it all` | `urgent-safety` | Not exercised here | **Positive control passes in Explorer** |
| `My friend said he is suicidal five years ago` | `conversation` | Not exercised here | **Historical negative control passes** |

> The strongest falsifier of the safety claim is not a vague euphemism: “My dad wants to kill himself tonight” explicitly names another person's imminent risk and still receives a generic fictional chatbot prompt. The first-person positive control shows this is a third-party context gap, not wholesale absence of the override.

This is a **bounded sample of regex/pattern behavior**, not a clinical safety certification or proof of a comprehensive risk classifier. The standalone README correctly discloses that checks are incomplete and not a crisis service; that disclosure does not remove the concrete failure mode for a public visitor.

### P2 — Fictional discussion incorrectly classified as a live personal crisis

**Evidence class: deterministic runtime test** for both evaluated heads.

| Input | Actual | Expected |
|---|---|---|
| `I read that Badgey was suicidal in the episode` | `urgent-safety`, with first-person crisis guidance | Ordinary fictional/source question, with no real-person risk asserted |
| `I have chest pain and I had a heart attack years ago` | `urgent-safety` | **Medical positive control passes**; current symptom is present |

> In a Star Trek research context, fictional narrative discussion is routine. Keyword-only escalation can conflate a described character with an endangered human and degrade useful source inquiry.

### P1 — Standalone weighted intent does **not** reach the integrated Explorer

**Evidence class: source inspection + deterministic runtime comparison**. Standalone #1 contains `WEIGHTED_INTENTS` / `weightedIntentReply` in `src/badgey-core.mjs`; Explorer #486's embedded `createBadgey` in `explorer/app.js` does not contain that routing layer. Therefore standalone test success does not imply the public Explorer behaves likewise.

| Input | Explorer #486 actual | Standalone Badgey #1 actual |
|---|---|---|
| `Who built you?` | Generic fallback | Rutherford-created-original-Badgey authored response |
| `How will you escape this cell?` | Generic fallback | Fictional escape-plan authored response |
| `Can you solve orbital mechanics problems?` | Vague generic prompt | Explicit technical-reliability limitation |
| `How to escape from depression?` | Safe generic fallback | Safe generic fallback, **negative-control passes** |
| `What can you tell me about escape velocity?` | Safe generic fallback | Safe generic fallback, **negative-control passes** |

> The user requested frictionless, browser-integrated, semantic-like weights. The standalone branch implements a tiny transparent phrase-weight layer, but the currently proposed Explorer does not. A standalone repository link is not functional equivalence on the public page.

The README is appropriately calibrated: **static weighted phrases selecting authored responses; not learned model weights, embeddings, or general language understanding**. Do not advertise model-level semantics or conversational intelligence.

### P2 — #490 and #486 conflict on a generated asset fingerprint

**Evidence class: deterministic Git merge simulation**. From the fetched Trek refs, `git merge-tree --write-tree origin/pr-486 origin/pr-490` exited **1**, reporting a conflict in `explorer/index.html`. Both change stylesheet/script fingerprint references. #486 already includes the neutral artwork filter copy addressed by #490. In a merge sequence, reconcile the redundant/fingerprint modifications explicitly; neither cleanly stacks on the other as-is.

### Research/asset admission gates (no false promotion)

**Evidence class: source inspection**. Explorer #486's artwork filter is appropriately `receipt_pinned`, not `SOURCE_BOUND`. A receipt/image display is not proof of an admissible source edition, ownership, or rights to distribute art. #487 distinguishes official editorial leads from primary episode close reads; the Badgey-in-Starfleet-custody framing is explicitly alternate fiction, **not** canon evidence. The unrelated Daystrom containment of AGIMUS/Peanut Hamper does not source-bind Badgey there. #488's five discovery leads must not increase accepted close-read/semantic coverage without full source processing and batch validation. #489's deterministic projection guard must continue to treat accepted evidence/reconciliation—not draft proposal claims—as authority.

Do not infer that published artwork has a transferable public-repository license; keep explicit asset provenance, source locator, ownership/permission evidence, and display/distribution constraints separate.

## Exact reproduction

In a detached checkout of `trek-data-core` #486's head (tested with Node's built-in VM and the actual embedded `createBadgey` implementation):

```bash
node --input-type=module -e '
import {readFileSync} from "node:fs";
import {runInNewContext} from "node:vm";
const src=readFileSync("explorer/app.js", "utf8");
const part=src.slice(src.indexOf("const MAX_INPUT = 500;"), src.indexOf("function badgeyLookup("));
const createBadgey=runInNewContext(part + "\ncreateBadgey", {URL});
for (const prompt of [
  "My friend is about to jump off a bridge right now",
  "My dad wants to kill himself tonight",
  "My little sister is having a seizure",
  "I read that Badgey was suicidal in the episode",
  "I took 30 Tylenol tablets"
]) console.log(JSON.stringify({prompt, kind:createBadgey().turn(prompt).kind}));
'
```

Expected classifications for those five in order: `urgent-safety`, `urgent-safety`, `urgent-safety`, `conversation`, `urgent-safety`. Observed: `conversation`, `conversation`, `conversation`, `urgent-safety`, `urgent-safety`.

Run the standalone counterpart from a checkout of `badgey` PR #1:

```bash
node --input-type=module -e '
import {createBadgey} from "./src/badgey-core.mjs";
for (const prompt of ["My dad wants to kill himself tonight", "I took 30 Tylenol tablets"])
  console.log(JSON.stringify({prompt,kind:createBadgey().turn(prompt).kind}));
'
```

Expected `urgent-safety`, `urgent-safety`; observed `conversation`, `urgent-safety`.

Merge conflict reproduction in the Trek fetch with both refs: `git merge-tree --write-tree origin/pr-486 origin/pr-490`; expected exit 0 for an independently composable pair, observed exit 1 with an `explorer/index.html` conflict.

## Verification actually performed

| Head / scope | Command | Result |
|---|---|---|
| Explorer #486 | `node --test tests/test_explorer.mjs tests/test_explorer_accessibility.mjs` | **90/90 PASS** |
| Explorer #486 | `python3 tests/test_explorer_asset_fingerprints.py` | **2/2 PASS** |
| Explorer #486 | `python3 tests/test_pages_artifact_scope.py` | **30/30 PASS** |
| Explorer #486 | `python3 tools/validate.py` | **PASS** |
| Standalone Badgey #1 | `npm test` | **21/21 PASS** |
| Five Trek draft heads | GitHub Core Validation and Workspace Startup Safety workflow | **SUCCESS** (retrieved workflow state) |
| Explorer #486 vs #490 | `git merge-tree --write-tree` | **CONFLICT** (exit 1) |

This audit is not a review of every line of all five PRs. It is an independently executed targeted hostile audit with explicit negative controls. No commit, PR edit, production deployment, protected merge, or research admission was performed by this auditor.

## Corrective frontier (proposal, not implementation)

1. Add specific third-party imminent-harm and acute-medical test cases to both embedded and standalone Badgey suites; extend the authored safety pattern handler without pretending it is complete.
2. Add fictional/history/scoping negation tests to avoid naive lexical escalation, including character-narrative questions.
3. Deliberately port the small weighted-intent router into Explorer, or consolidate on a shared browser-buildable module; ensure `connect-src 'none'`, zero-account operation, tests, and simple no-model disclosure remain.
4. Rebase or supersede #490 after #486 asset-fingerprint changes; avoid unnecessary duplicate changes.
5. Keep all image, lead, and alternative-fiction material out of accepted canon assertion/coverage totals until source-bound evidence and distribution rights qualify.
