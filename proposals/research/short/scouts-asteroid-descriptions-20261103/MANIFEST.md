# Scouts Asteroid Blasters #1–#5 — publisher description source-local proposal

**Status:** source-local publisher-description **PROPOSAL ONLY**, based on
accepted `main@bce9cc158b9133a3a982ac0dc90e6b0c86482a20`. No episode
video watched, direct YouTube video page opened, script read, audiovisual
close-read evidence, admitted Work, consensus identity, coverage, public
Explorer description release, or artwork publication. The five candidate rows
remain `UNVERIFIED_METADATA` from the accepted discovery index; this proposal
does not create five more Works.

## Direct publisher metadata exposed by web search — 2026-11-03 UTC

I queried exact titles and watched the **search response**, not video streams.
The result provider returned the first episode-specific **Description**
paragraph in its first-party YouTube video results, including the attribution
to the publisher's *Blaze and the Monster Machines* Nickelodeon channel and a
video-page `Published` display date. That text was actually read and
paraphrased, but direct `youtube.com/watch` opening was throttled and
`youtu.be` URL opening was disabled. The query result is a mutable index view;
the whole video-page body was **not** downloaded, source bytes were not retained,
and this is not independent cryptographic proof of the publisher account.

| Existing candidate row | Official channel video result whose description was read | Search-result published date |
| --- | --- | --- |
| `short:scouts:asteroid_blasters:01` | [Soapy asteroid #1](https://www.youtube.com/watch?v=j-KvjtSgfJs) — first Description paragraph | 2025-09-08 |
| `short:scouts:asteroid_blasters:02` | [Meatball asteroid #2](https://www.youtube.com/watch?v=x1mIN62O00s) — first Description paragraph | 2025-09-08 |
| `short:scouts:asteroid_blasters:03` | [Chalk asteroid/fireworks #3](https://www.youtube.com/watch?v=PfaNbFeRCm4) — first Description paragraph | 2025-09-19 |
| `short:scouts:asteroid_blasters:04` | [Piñata asteroid #4](https://www.youtube.com/watch?v=j3asH2YbKz8) — first Description paragraph | 2025-10-04 |
| `short:scouts:asteroid_blasters:05` | [Booger asteroid #5](https://www.youtube.com/watch?v=60SkYJy-_2U) — first Description paragraph | 2025-10-11 |

The `source_locator` accepted in the discovery catalog is the equivalent
`https://youtu.be/<id>` URL, and its existing first-party oEmbed title/ID
receipts are described in the earlier
[Scouts discovery manifest](../../../discovery/scouts-firstparty-video-s1-20261103/MANIFEST.md).
This synopsis packet adds **publisher description content** over five of
those same source-local IDs, not another identity assignment. The corpus has
one Paramount/Nickelodeon corporate upstream family, not five independent
corroborating witnesses.

## Premise and date uncertainty

Each `synopsis` is an original ~20–30-word paraphrase of the first episode-
specific description paragraph. It captures a stated marketing premise, not
film-observed dialogue, actual successful rescue, production continuity, or
canon truth. All five are constrained to `PUBLISHER_DESCRIPTION_PARAPHRASE`.
The YouTube `Published` dates are **displayed metadata fields**, not a verified
distribution/first-airing audit. For #2, some derivative third-party episode
indexes report Sep 9 rather than the first-party search result's Sep 8; that
discordance is not silently reconciled, nor are third-party copies counted as
independent publisher description evidence.

> Search-result presentation may truncate, reformat, translate, or cache the
> first-party description. Because direct YouTube page access was throttled,
> this is a source-limited metadata packet. An auditor must independently
> retrieve the exact official video descriptions before admitting a display
> projection or upgrading evidence status.

> Five videos from one channel are not five independent story witnesses.
> Official marketing descriptions can establish **what the publisher says**;
> they cannot prove what a video actually depicts. The prior 20-video oEmbed
> receipts bind candidate IDs and titles, not plot content.

> No YouTube thumbnail, subtitle, video, script, caption passage, or artwork
> binary is copied. Copyright/publication, source admissibility, and the
> actual 3–4-minute episodes remain separate questions.

The SHA-256 of the committed UTF-8 `observations.json` proposal is
`6faa60b57c7435e40d4bbfe8f534665804ff61db039990940bff9a25dddd0ae2`.
This pins the **locally written observations**, not a raw official YouTube
response (which we did not capture).

## Offline checks

```bash
python3 proposals/research/short/scouts-asteroid-descriptions-20261103/validate.py
python3 -O proposals/research/short/scouts-asteroid-descriptions-20261103/validate.py
python3 -m unittest tests.test_scouts_asteroid_publisher_descriptions -v
python3 tools/validate.py
python3 -m unittest discover -s tests -p 'test_*.py'
node tests/test_explorer.mjs
```

Validation pins five existing source-local IDs, observed video IDs/URLs,
YouTube display dates, source access class, fixed proposal bytes, and explicit
no-admission/no-publication effects. The next bounded Scout tranche is
*Asteroid Blasters* #6–#10, then *Holodeck Rescues* #1–#10, contingent on
first-party description availability and separate independent review.
