# Short Treks: ten first-party writer / story / director credit cards

**SHORT worker, bounded proposal; observed 2026-11-03 UTC.** Starting accepted
`main@1ef3e4ef9cefa0e3ccd90caa4530a84c167a8ca6`. This does **not** create
ten more episode candidates or publish their previously held descriptions.
The same ten local directory references `short:short-treks-01`–`10` already have
source-local publisher synopsis proposals in
[`../publisher-synopses-20261103/observations.json`](../publisher-synopses-20261103/observations.json).
That accepted input's SHA-256 is
`91862225de0740c18b545de84efb4c9c84b0538d00888a55c4af1f78e3f2fd96`.
The older six-title 2019 announcement packet is pinned too. No proposed
synopsis is duplicated here.

## Sources actually read

| Publisher source | Directly read content | Distinct added facet |
| --- | --- | --- |
| [StarTrek.com, *Short Treks Schedule Revealed*](https://www.startrek.com/news/short-treks-schedule-revealed), published Sep 20, 2018 | article paragraphs and four adjacent credited writing/story/teleplay/directing lines (rendered lines 47–66) | Source-local credits for Runaway, Calypso, The Brightest Star, The Escape Artist |
| [StarTrek.com, *Short Treks Now Streaming on YouTube*](https://www.startrek.com/news/star-trek-short-treks-now-streaming-on-youtube), published Aug 17, 2020 | six individually titled bullets with credited writers and directors (rendered lines 46–52); current canonical redirect `/en-un/` | Source-local credits for Q&A, The Trouble with Edward, Ask Not, The Girl Who Made the Stars, Ephraim and Dot, Children of Mars |
| [StarTrek.com, home-video release announcement](https://www.startrek.com/news/announcing-star-trek-short-treks-release-on-blu-ray-and-dvd), published Mar 15, 2020 | announcement of two formats, nine named shorts, US June 2 release date and extras (rendered lines 40–54) | A distinct *edition container lead*, not a tenth independent Work or a verified disc inspection |

All three official publisher article bodies were directly retrieved/rendered by
the web research tool on 2026-11-03 and independently returned HTTP 200 from
Lappy's WSL curl (approximate transient sizes: 1,181,263; 1,165,224;
1,164,805 bytes). **Raw HTML was not archived or hashed**; do not describe
these as frozen custody witnesses. The line numbers are retrieval-local.
All three are in **one upstream Paramount/CBS/StarTrek.com publisher family**;
multiple announcements do not provide independent plot corroboration.
No audiovisual stream, transcript, book or disc was viewed or processed.

`observations.json` (SHA-256
`a2c3a8b13aa67991dd6c890f3570d6bf03b8d355c3fc278775fdfa6e4cd8f1f8`)
contains ten unique source-local credit records. `written_by`, `teleplay_by`
and `story_by` are **distinct publisher-labelled fields**, not normalized
global authorship assertions; in particular *Calypso* uses a teleplay and
story split. Names are preserved as actually printed by these source pages.

## Art provenance, but no artwork release

The article markup exposes three `images.prismic.io/star-trek-untold/...` image
locators. Their exact links, associated source article and **page-level scope**
are in `page_level_artwork_leads`. These are *article banners* or a home-video
article illustration, **not independently checked episode posters or stills**.
Following the image links did not retrieve image bytes. Permission to display,
copy, or serve each remains `UNKNOWN_HELD`. No asset was downloaded or committed.

No per-episode image has been authenticated here: every credit row says
`NO_EPISODE_IMAGE_CONFIRMED`. This is an unresolved artwork frontier, not a
claim that no official image exists.

## Source / chronology and edition cautions

- The accepted current Paramount+ guide compresses the original four plus the
  later six into one displayed S1E1–S1E10 sequence. Preserve its **guide
  slot** distinct from release-cohort labels and on-air chronology.
- A search index currently displays individual Paramount+ Short Treks video
  details, including nominal minute lengths and dates that sometimes differ
  by one day from official scheduled announcements. However **direct page
  requests freshly produced HTTP 500 or a redirect to the international
  splash page**, including Lappy HTTP 500 for Runaway. We do **not** certify
  indexed video runtimes, episode air dates, page stills, or player bytes.
- The March 2020 home-video *announcement* names nine short titles and a
  June 2 US release plan. `Children of Mars` is **not in the quoted nine-title
  list**; do not infer all subsequent editions, disc inventories or omitted
  items. The differing `Ephraim & Dot` and `The Trouble With Edward` spellings
  belong to the *article's own list*, not silent title normalization.
- The existing `PUBLISHER_DESCRIPTION_PARAPHRASE` strings are original worker
  synopses, but remain held proposals. This packet references them without
  declaring a full short read or public Explorer synopsis release.

## Hostile falsifiers

> An invalid alternative would count the ten credit records as ten newly
> verified Works or semantic episode close reads. The source only supplies
> publisher article credit claims and the guide's separate slot mapping.

> Another invalid alternative would label the three article banners as
> licensed episode thumbnails. Their image URLs, identity and publication
> rights do not establish that.

> A third would collapse *Calypso*'s credited teleplay/story fields or treat
> the nine-item home-video product as a ten-episode source container. Both
> errors are rejected by exact source-local validation.

## Bounded validation / effects

```bash
python -B proposals/research/short/short-treks-credits-20261103/validate.py
python -B -m unittest discover -s proposals/research/short/short-treks-credits-20261103 -p 'test_validate.py'
python -O -B -m unittest discover -s proposals/research/short/short-treks-credits-20261103 -p 'test_validate.py'
python -B -m unittest discover -s tests -p 'test_*.py'
python -B tools/validate.py
```

No Work/Source admission, global identity reconciliation, collection admission,
copyrighted source text/binaries, audiovisual coverage promotion, public
Explorer change, or synopsis/artwork publication. An independent source-access
and credit-transcription audit is needed before accepting this proposal to
`main`.
