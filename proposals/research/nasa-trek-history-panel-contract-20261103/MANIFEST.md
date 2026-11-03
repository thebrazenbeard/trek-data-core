# NASA–Star Trek real-world history panel — proposal-only LCARS interface contract

**No site change and no image release.** This packet proposes one separate
historical information panel about the 1976 Space Shuttle *Enterprise* rollout,
using the exact first-party NASA source packet accepted from [PR #418](https://github.com/thebrazenbeard/trek-data-core/pull/418)
in main `4b99102` after independent decision-only review. That acceptance did
**not** approve public image distribution or the Explorer panel.
It must never enter the fictional episode/film artwork slot, discovery count,
or Lore's fictional source-local search corpus. The historical event is not an
episode, film, starship identity, or a count of Trek Works.

## Actual source and editorial record

- NASA [image-specific article](https://www.nasa.gov/image-article/star-trek-nasa-54-years-counting/) credits **NASA** for EC76-5806-1. Exact image URL in `contract.json`, JPEG SHA-256 `e36c3e1c94c53f57fe99ac921169c24a35c63851666885d20af6fdfe902ed6f8`, 165312 bytes, 1041×833. No JPEG copied into this packet.
- NASA [event chronology](https://www.nasa.gov/history/space-shuttle-enterprise-makes-its-public-debut/) dates the *public event* September 17, 1976, at Palmdale; this is **not proof of the shutter timestamp**.
- NASA [Images and Media](https://www.nasa.gov/nasa-brand-center/images-and-media/) and [Brand Center](https://www.nasa.gov/nasa-brand-center/) guide factual, credited, nonendorsing use but do not constitute an unconditional licence or clear every individual's publicity rights.
- NASA is one institutional provenance family, not four independent corroborators. The individual photographer/third-party rights status remains subject to independent review.

## Proposed LCARS panel

- Mount as a self-contained region with its own nav label: **NASA–Trek history**, distinct from `#discovery-directory`, `#artwork-gallery`, `#films`, and `#lore-console`. Use original LCARS scalloped framing/colors and typed heading; no NASA seal as interface branding.
- At HOLD, show heading, a short source-grounded context paragraph, NASA article link, and explicit **Image withheld pending review** placeholder. **No image bytes and no NASA image request**.
- If a *later independently approved* source-specific image-release sidecar is accepted and deployed, initially show the same text-only state with **Show historical NASA image** button. On explicit session-local click, create the `img` using only a code-pinned **same-origin** approved asset, never NASA CDN hotlinking. Hide destroys its source; errors return to placeholder. A second click must not persist consent across sessions.
- Show exact editorial caption, immediately adjacent **Image: NASA** attribution, and explicit independent/nonendorsement statement while image is visible. Label this as a **real NASA spacecraft** event, not an episode still or fictional USS *Enterprise*.
- Source article navigates only by user-activated external link (`https`, `rel="noopener noreferrer"`, `referrerpolicy="no-referrer"`). No third-party font, image, tracking pixel, preconnect, preload, prefetch, URL query, or remote media at page initialization.

## Responsive and accessibility contract

- Semantic `section[aria-labelledby]`, heading, `<figure>/<figcaption>`, native button, `aria-pressed`, and a concise live status. Keyboard Enter/Space and clearly visible focus.
- Start with 320px CSS viewport and test 375, 600, 760, 1440 px with wrap-safe caption/credit; never depend on horizontal scrolling or hover-only controls.
- Image has descriptive alt text independent of the adjacent credit; no broken-image icon as information, color-only status, unsolicited motion, or autoplay. Respect reduced-motion and high-contrast preferences.
- This packet does not alter accepted Explorer HTML/CSS/JS or Content Security Policy. A future same-origin released asset avoids adding a NASA CDN host to `img-src`.

## Fail-closed acceptance for future implementation

The proposed release gate is intentionally **disabled** today. A future
separate PR must show the exact image's independently approved rights/publicity
assessment, explicit caption and attribution review, immutable release manifest
SHA, separately approved same-origin byte-pin, user consent behavior, responsive
browser probes, and deployment authority. A mere JSON field changed to `GO`,
or the source packet's conditional NASA policy assessment, cannot authorize
the image. The three distinct NASA photos in [PR #414](https://github.com/thebrazenbeard/trek-data-core/pull/414)
remain separately rights-HOLD.

> **Hostile failure mode:** A forger appends “NASA approved this archive” to the caption or changes the event into a fictional scene while keeping NASA source references intact. The contract validator must reject the entire exact-text change, not merely look for previously honest substrings.

> **Browser failure mode:** `loading="lazy"` on an already populated remote `img.src`, CSS `background-image`, `srcset`, `link rel=prefetch`, or an eager `Image()` request is still a potential network disclosure before visitor consent; zero network before opt-in must be tested in an actual future browser, not inferred from markup review.

> **Rights failure mode:** A verified SHA establishes image byte identity, not third-party rights, person likeness consent, nonendorsement or a transferable NASA license. A test-only source/asset simulation cannot grant publication rights.

## Current validation

`validate.py` freezes the complete proposal to a code-owned canonical SHA and
proves the release gate is in HOLD regardless of visitor opt-in or forged
in-memory approval fields. `test_validate.py` mutates source IDs, event type,
copy, rights state, fake local asset release, remote network, consent
persistence, and fictional count claims. These are **design/proposal tests**,
not a deployed-browser qualification.

```bash
python proposals/research/nasa-trek-history-panel-contract-20261103/validate.py
python -m unittest discover -s proposals/research/nasa-trek-history-panel-contract-20261103 -p test_validate.py -q
python -O -m unittest discover -s proposals/research/nasa-trek-history-panel-contract-20261103 -p test_validate.py -q
```

**Next frontier:** independent review of this interface contract against the
now-accepted #418 conditional rights *decision*, followed by separate
image-specific release review and consented browser qualification before any
public release. The public Explorer remains unchanged by this work.
