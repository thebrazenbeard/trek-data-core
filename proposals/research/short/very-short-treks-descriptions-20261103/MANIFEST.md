# Five very Short Treks publisher landing-page descriptions — bounded proposal

**Scope:** Four qualified official **publisher premise paraphrases** plus one
explicit `PENDING_PLOT_SYNOPSIS` gap. This is a SOURCE_LOCAL, proposal-only
layer over the five existing `PROMOTIONAL_ANIMATION` directory rows, based on
accepted `main@5663932d868a3b0bc2e14a67953eb60db23f5059`. Not a viewed
animation, Work/Source admission, plot assertion, release event verification,
Explorer publication, artwork license, or added coverage denominator.

## Actually read publisher sources — 2026-11-03 UTC

| Short / local row | First-party publisher video page body locator | Publisher page date |
| --- | --- | --- |
| `short:very-short-treks-01` *Skin a Cat* | [Video title *Skin A Cat*](https://www.startrek.com/videos/very-short-treks-skin-a-cat): narrative description line 36 | 2023-09-08 |
| `short:very-short-treks-02` *Holiday Party* | [Video page](https://www.startrek.com/videos/very-short-treks-holiday-party): description line 36 | 2023-09-13 |
| `short:very-short-treks-03` *Worst Contact* | [Video page](https://www.startrek.com/videos/very-short-treks-worst-contact): description line 36 | 2023-09-20 |
| `short:very-short-treks-04` *Holograms, All the Way Down* | [Video title *Holograms All the Way Down*](https://www.startrek.com/videos/very-short-treks-holograms-all-the-way-down): promotional tagline line 36, cast lines 47–57; **no plot supplied** | 2023-09-27 |
| `short:very-short-treks-05` *Walk, Don't Run* | [Video page](https://www.startrek.com/videos/very-short-treks-walk-dont-run): description line 36 | 2023-10-04 |

Also actually read StarTrek.com's [original five-title launch announcement](https://www.startrek.com/news/star-trek-very-short-treks-announce)
(Sep 5, 2023; title sequence and **announced** date list, rendered lines
43–60), which is the existing candidate discovery locator under an `/en-un/`
path in `explorer/discovery-catalog.json`. The five video pages and launch
announcement all belong to **one publisher corporate family**; they do not
independently corroborate the story or release events. No video/media/player
stream, full source, transcript, or raw webpage response was consumed or
archived. Page dates and publisher's scheduled dates are observations, not
independent historical release verification.

## Observed aliases and precisely bounded descriptions

The announcement writes *Skin a Cat* while its video page uses *Skin A Cat*
(capitalization). The announcement writes *Holograms, All the Way Down* while
its video page omits the comma. `publisher_title_variation` preserves each as
a source-local alias difference, **without** deciding global Work identity.

The four synopsis strings are original short paraphrases of modest
publisher-supplied premises. Crucially the *Holograms All the Way Down* landing
page gives only a holodeck-themed exclamation and cast list. It supplies no
event sequence or character motivation for a plot synopsis, so that record has
`synopsis: null` and `PUBLISHER_TOPIC_ONLY_PENDING_PLOT_SYNOPSIS`. The title
alone does not establish recursive holographic simulations or any specific
fictional event. This gap must remain visible in any downstream presentation;
otherwise the Explorer would turn a marketing headline into a fabricated plot.

> A website video-page description is not the same evidence type as a full
> animation close read. Seeing an embedded player or a still image does not
> establish that its video was watched or its story extracted.

> The recurring cast and the *Animated Series* visual homage in launch
> material cannot, on their own, establish scene appearances, continuity,
> psychological states, or fictional canon. Very Short Treks are publisher-
> labeled promotional animation, not automatically the same kind of canonical
> television episodes as the scripted *Short Treks*.

> The five first-party pages are one upstream corporate provenance family.
> Their shared publisher voice is not multiple independent witnesses.

The exact observation JSON SHA-256 is
`612485b687116757a8f0dcc5f9d971e27f53522bc3e2e73365000e87811d7d5a`.
This pins only locally authored proposal bytes for review; no raw source
representation digest is asserted.

## Verification

```bash
python3 proposals/research/short/very-short-treks-descriptions-20261103/validate.py
python3 -O proposals/research/short/very-short-treks-descriptions-20261103/validate.py
python3 -m unittest tests.test_very_short_publisher_descriptions -v
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_explorer.mjs
```

The validator fixes the five candidate identifiers, publisher page locators,
announcement dates, alias distinctions, premise classes, null gap, file digest,
and no-admission/no-publication invariants. It cannot prove media plot accuracy
without the media being processed. After independent hostile source review,
propose any approved projected descriptions with explicit source attribution
and retain one honest missing synopsis; the next 20 Scouts source-local video
candidates require their own direct source reconnaissance.
