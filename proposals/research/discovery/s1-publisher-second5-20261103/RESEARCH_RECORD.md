# Discovery S1E6–E10 first-party evidence record

## Method

The question, falsifiers and confirmatory methods were preregistered before
the direct raw HTML capture. A preliminary third-party page-text rendering
was exploratory and not treated as the canonical source receipt.

| Evidence ID | Artifact or operation | Observation | Limits |
|---|---|---|---|
| DIS6-01 | `curl` GET official Season 1 page, 2026-11-03 | HTTP 200; 289,669 bytes; SHA-256 `1c428f8c7e85197d50dcfe5c8b2c7546933dc2293874eabb321b1ab03343c77e` | Publisher-hosted unsigned snapshot; changes between retrievals possible |
| DIS6-02 | Private exact HTML, lines 1667–1806 | Five distinct source-card blocks, own-card title/slot/time/video/art image and descriptions | No full episode, footage, subtitle or script |
| DIS6-03 | Accepted `proposals/discovery/modern-paramount-season1-20261102/dis/bundle.json` | Five sequential title/slot crosswalk matches at SHA-256 `0d3db808c7319e32168be00e8756cf31e9686fe363419c6e671e1a7c0bc27418` | Same upstream publisher family; no independent witness |
| DIS6-04 | `records.json`, local entity/evidence/assertion and held art objects | Five bounded author-created paraphrases, five explicit source-relative assertions, all non-admitted | Editorial derivative: requires independent close reading and audit |

## Interpretation boundary

The evidence establishes five first-party **publisher statements**. It does
not independently verify Burnham's recollections, Lorca's motives, the
chronology of the Klingon war, or alternate realities implied by episode
titles or synopsis. These hypotheses remain untested until complete source
works can be legitimately examined.

## Hostile falsifiers for independent review

> An HTML card could have the correct title but a swapped video or image;
> only per-card binding, not a page-wide set match, can detect that.

> Five cards are five publications from one source, not five independent
> observations of fictional events.

> Short source-labeled paraphrases must not be promoted to canonical facts or
> publicly attributed episode synopses without a separate editorial release.
