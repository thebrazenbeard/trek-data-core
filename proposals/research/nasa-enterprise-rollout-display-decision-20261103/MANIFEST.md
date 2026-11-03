# Display eligibility decision proposal — NASA's 1976 *Enterprise* rollout photograph

**Decision: CONDITIONALLY SUPPORTABLE FOR FACTUAL, NONPROMOTIONAL NASA–TREK
HISTORY CONTEXT; PUBLIC RELEASE REMAINS HOLD.** This is a recommendation for
independent rights and presentation review, not permission issued by NASA,
not a public Explorer release, and not a canonical fictional Work change.

The [NASA photo page](https://www.nasa.gov/image-article/star-trek-nasa-54-years-counting/)
visibly says **Image Credit: NASA** and includes an `og:image` pointing to
exactly <https://www.nasa.gov/wp-content/uploads/2023/03/ec76-5806-1.jpg>.
The original JPEG was fetched read-only on November 3, 2026: HTTP 200,
**1041 × 833**, **165,312 bytes**, SHA-256
`e36c3e1c94c53f57fe99ac921169c24a35c63851666885d20af6fdfe902ed6f8`.
It has no alternate image URL, screenshot crop, visual modification, or site
thumbnail in this proposal. A URL with `?w=1041` returns different JPEG bytes
and must not be substituted without its own provenance receipt.

The source describes the *real* Space Shuttle *Enterprise* rollout attended
by cast members, Gene Roddenberry, and NASA Administrator James C. Fletcher.
The [NASA historical chronology](https://www.nasa.gov/history/space-shuttle-enterprise-makes-its-public-debut/)
places the public ceremony at Rockwell's Palmdale plant on **September 17,
1976**. That date applies to the event; the photo page does not independently
establish a camera exposure timestamp. Neither page depicts or proves a
fictional Trek episode, film, or the USS *Enterprise*.

## Source-specific rights reasoning

| Question | Source-grounded result | Decision constraint |
| --- | --- | --- |
| Who credits this exact picture? | Individual NASA photo page says **Image Credit: NASA**; no competing copyright line observed near the credited image | NASA institutional credit supported; individual photographer **unknown**, no universal clearance inferred |
| Is NASA content automatically a CC/PD license? | [NASA Brand Center](https://www.nasa.gov/nasa-brand-center/) says NASA does not license its material, but generally accepts public reproduction subject to conditions; [media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) describe factual educational/informational web uses | Call it **conditional NASA usage policy**, not CC0, blanket public-domain permission, or a license deed |
| If copyrighted by a third party? | NASA says a separately copyright-marked item needs permission from the named holder | The observed first-party page lacks a competing mark; reviewer must still verify exact image provenance |
| Cast likenesses? | NASA distinguishes informational/factual display from commercial/promotion involving recognizable former/non-NASA people | Caption stays factual, not marketing or endorsement; promotional reuse is **HOLD** |
| NASA identifiers in the photo? | NASA allows incidental agency identifiers in their factual context but restricts logos, seals, and marks as third-party branding | Do not add NASA seal/insignia as UI branding, falsely imply NASA approval, or crop an emblem into an endorsement device |
| Link versus image delivery? | NASA allows website links and images used as graphical links to NASA web pages within guidelines | The policy does **not conclusively specify** whether cross-origin `<img src>` against the NASA CDN is a durable third-party hosting service; prefer a source-page link until a reviewed sidecar decides local exact-binary distribution |

**Potential future editorial display**, only after independent approval:

> At the public rollout of NASA's Space Shuttle Enterprise in Palmdale,
> California, on September 17, 1976, original Star Trek cast members and
> creator Gene Roddenberry joined NASA Administrator James C. Fletcher. This
> is a photograph of a real NASA event, not a Star Trek episode scene.

Attribution immediately adjacent to any future image:

> Image: NASA. Historical event: Space Shuttle Enterprise rollout, September
> 17, 1976. Source: NASA. This independent Star Trek research archive is not
> affiliated with or endorsed by NASA.

## Hostile review and deployment boundary

> **Source falsifier:** A first-party photo page and NASA credit are strong
> evidence for the institutional attribution, but a hidden third-party
> submission, photographer credit, or original distribution restriction could
> still matter. The reviewer must verify the specific JPEG and publication
> context, not merely the NASA domain or broad policy.

> **UI falsifier:** Calling this an episode thumbnail, film promotional still,
> USS *Enterprise* model photo, or "official NASA-backed Trek Explorer" would
> contaminate both history and identity. The NASA shuttle is a physical
> vehicle. A future **separate REAL_WORLD_HISTORY panel** requires a new
> source/evidence and visual-release contract, not the fictional discovery
> directory's `episode`/`film` art mapping.

> **License / delivery falsifier:** NASA's graphic-link language does not
> establish a perpetual third-party CDN embedding guarantee. Even if a future
> authorized release locally mirrors the original 165,312-byte image under
> NASA's reproduction conditions, it must pin source bytes, license evidence,
> no-endorsement wording, and editorial context in a separately reviewed
> release manifest. Do not ship arbitrary transformations or strip source
> attribution.

HTTP HTML source pages are dynamic. `decision.json` records one image-page,
event-page, Brand Center, and media-guideline response-body SHA-256 receipt,
plus two previously observed media-page variants of the same byte length.
Those are **client-specific HTTP fetch representations**, not content-addressed
legal instruments. Tests pin the research packet; they cannot independently
prove a rights grant. NASA's original image SHA-256 is separately reproducible.

Prior research [PR #411](https://github.com/thebrazenbeard/trek-data-core/pull/411)
and distinct [Nichols/Doohan candidate PR #414](https://github.com/thebrazenbeard/trek-data-core/pull/414)
remain *unaccepted* proposal references; this decision does not promote them.
In particular, **all three #414 photos stay rights-HOLD**, regardless of
whether the 1976 NASA page eventually qualifies.

## Result and reproducibility

- **1** exact first-party NASA photo and **3** independent URL types
  (specific image page, historical date page, agency policy pages in one
  institutional provenance family).
- **0** images copied, **0** public images displayed, **0** site changes,
  **0** fictional episode/film bindings, **0** coverage/admission effects.
- **1** decision proposal: reviewable conditional factual reuse, **not**
  rights-approved publication.

```bash
python proposals/research/nasa-enterprise-rollout-display-decision-20261103/validate.py
python -m unittest discover -s proposals/research/nasa-enterprise-rollout-display-decision-20261103 -p 'test_validate.py' -v
python -O -m unittest discover -s proposals/research/nasa-enterprise-rollout-display-decision-20261103 -p 'test_validate.py' -v
```

**Next gate:** independent review of exact image credits, NASA restrictions,
photograph-specific third-party notices, caption/attribution, nonendorsement,
and proposed real-world panel placement; then a separate explicit visual
release PR and deployment authorization if the review is GO.
