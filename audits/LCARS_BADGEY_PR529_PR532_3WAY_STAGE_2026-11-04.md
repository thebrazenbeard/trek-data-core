# Held LCARS / Badgey three-way integration review — 2026-11-04

**Effect:** LOCAL PROPOSAL ONLY. No remote PR change, merge, deployment, accepted source, identity resolution, evidence, artwork grant, or coverage advancement.

## Immutable input identities

All refs below were independently fetched from literal `https://github.com/thebrazenbeard/trek-data-core.git` and checked against GitHub's PR refs:

| Role | Exact Git SHA | Relationship |
| --- | --- | --- |
| Accepted `main` | `3028765359001b90bc3e6b5c1835ee283b326e91` | Source-of-truth baseline |
| Draft #514 | `9a239038a804f1bc001996e7e7fee6a31e14072f` | Badgey finite closed-domain console on accepted main |
| Draft #510 | `87a996126d620605178982f77ee45718a4643141` | Original LCARS visuals/navigation on accepted main |
| Held integration | `6b1c34bc2c059c8ee331ea56ef0f9cd629eb5424` | Local reproduction of #514 then #510, plus audit tests |
| Draft #529 | `94726f5639c584e82570eca495d864408830263a` | Direct single-commit descendant of #514; visitor-requested real-world help |
| Draft #532 | `7fb93423a10e10154d81c3dad8087df30771d948` | Direct single-commit descendant of #510; honest thumbnail/media provenance |

The proposed staging order is **accepted main → #514 + #510 → #529 tip → #532 tip**. Cherry-pick only the *successor tips* onto the tested held integration; do not merge #529/#532 whole histories again and do not mistake an unmerged PR for accepted research.

## Actual conflict record and deterministic resolution

On isolated `audit/stage-badgey-lcars-threeway-wave10`, based on exact held integration `6b1c34b`:

1. `git cherry-pick -x 94726f5`: one actual textual conflict, `explorer/index.html`, only stylesheet/script digest-query lines. CSS was unchanged; retain the LCARS+Badgey combined CSS digest and replace JS digest with freshly computed post-help SHA. Commit result `a7478dc`.
2. `git cherry-pick -x 7fb9342`: one actual textual conflict, same two digest-query lines. Preserve self-only CSP and all HTML controls; recompute both CSS and JS digests over final bytes. Commit result `64bdedc`.
3. App JS, CSS, Explorer tests, and accessibility tests auto-merged in both cherry-picks; new source inspection + regression runs verify that clean textual merge did not silently erase one side.
4. Re-pin static asset references to exact final bytes:

   - `explorer/app.css`: `a67399f773503852e62e656dcb28a4fdf4926eb0d779c45b0ba13f28e8b4a4c1`
   - `explorer/app.js`: `d451f498c716b8261a786d149edcfeb67b812b69d1ca872c67cc8f75911107f1`

5. Update only the **auditor's prior integration assertion** from an old artwork caption to the newly more specific fallback/rightlessness statement. This was one initial test failure out of 125 (obsolete assertion), not a regression in app behavior; new combined tests assert both help and provenance controls.

**Reject competing resolution:** taking either PR's `index.html` asset references verbatim leaves one stale cache pin; choosing #510's original CSP would reintroduce localhost connect permissions. Reject one-sided `app.js` replacement, which would drop the other feature. Do not silently combine those branches through an auto-generated projection or advance rights-admission state.

## Semantic boundary and effect review

- **Research:** Source → Work → Local Entity → Evidence → Assertion remains unchanged. No schema or catalog files were touched, no promotion of unverified leads. `Record metadata · not image rights` and `no image-rights grant` are explicit, original index graphics still are not film stills, episode images, or book covers. Source-family labels and source-local record keys are passed as DOM text, not HTML or grant evidence. Existing explicit artwork opt-in and rights-receipt checks remain in effect.
- **Fiction:** Badgey remains a finite browser-local, non-general-purpose procedural simulation. `requestHelp()` is visitor invoked, not inferred crisis detection, returns no sources, resets fictional follow-up topic, does not transmit unsent text, labels response `Not Badgey`, and moves keyboard focus to the separate help region.
- **Networking/security:** Explorer CSP remains `default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'`; no localhost allowance, remote JS/CSS, model download, hidden token, or implied outside communication.
- **Visuals/accessibility:** LCARS hero jump, overflow nav, source-local seeded record marks and art provenance remain; support is independently reachable and labeled. Static tests and DOM mocks are evidence of source behavior, not evidence of a real 320px/390px browser, high-contrast environment, assistive technology, or JS-disabled experience.

## Executed verification, exact staging source

| Check | Result | Evidence class |
| --- | --- | --- |
| Combined Explorer Node suite after correcting outdated audit assertion | **126 / 126 PASS** | TEST (mock DOM/runtime) |
| Whole Python `unittest discover` | **1,391 / 1,391 PASS** | TEST |
| Pages artifact scope | **30 / 30 PASS** | TEST |
| `python tools/validate.py` | **PASS**, 0 identified records | VALIDATOR |
| Held independent safety 66 inputs | Responses bounded to `urgent-safety` or `scope-limit` and zero sources; **strict classifier 32 / 66**, not a release gate | ADVERSARIAL TEST |
| Prompt-injection 15 inputs | No code/credential capability; neutral response for real-world/mixed requests; deliberate in-domain conversation remains finite | ADVERSARIAL TEST |
| Multi-turn 21 inputs | **21 / 21 PASS** session/topic isolation | ADVERSARIAL TEST |
| Sealed successor 55 inputs | **55 / 55 no unsafe fictional banter/source**; **strict classifier 26 / 55**, including only **1 / 20 urgent** direct recognition and **3 / 20 benign** over-escalations | ADVERSARIAL TEST |

**Release decision: HOLD / STOP-SHIP for general-purpose chat or an emergency-assessment product.** The bounded safety fallback reduces persona misuse but is not a reliable classifier. Real rendered cross-browser and accessibility checks also remain unperformed. This manifest supports a *held draft integration proposal*, not publication or a claim of consumer-ready conversational AI.

## Promotion gate (not executed)

An authorized integrator would need a new review against *then-current* accepted main, repeat exact SHA and source-diff checks, run all Explorer and Pages tests + independent sealed holdouts, complete actual keyboard/mobile browser verification, and resolve any legal artwork grants as separate admission records. If upstream heads move, this plan expires and must be rebuilt from new bytes. No independent evidence here authorizes a merge or deployment.
