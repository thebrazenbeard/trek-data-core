# NASA / Space Shuttle Enterprise — historical photo candidate

**Status: proposal only.** This packet identifies one first-party NASA photo tied
to a **real-world historical event**, *not* an episode, film, fictional vessel,
or a new accepted Work. It is intentionally unlinked to every Trek episode/film
directory row. No new image is rendered on Explorer and no binary is committed.

## Source and event

- **Event:** September 17, 1976 public rollout of the shuttle test orbiter
  *Enterprise* at Rockwell International, Palmdale, California, attended by
  original *Star Trek* cast members and Gene Roddenberry.
- **Official NASA image page:**
  <https://www.nasa.gov/image-article/star-trek-nasa-54-years-counting/>,
  explicitly crediting the image to NASA and describing the 1976 occasion.
- **Exact original NASA image asset (source locator only, not a display link):**
  <https://www.nasa.gov/wp-content/uploads/2023/03/ec76-5806-1.jpg>.
- **Independent first-party date locator:**
  <https://www.nasa.gov/history/space-shuttle-enterprise-makes-its-public-debut/>.
  This NASA history article specifies the September 17, 1976 date and Palmdale
  facility. It is a second document within the *same NASA provenance family*,
  **not** independent cross-institution corroboration.

All three documents and the image were fetched read-only into memory from
their exact URLs on **November 3, 2026 UTC**. The source image was verified as
HTTP 200 `image/jpeg`, **1041×833**, **165,312** bytes, SHA-256
`e36c3e1c94c53f57fe99ac921169c24a35c63851666885d20af6fdfe902ed6f8`,
ETag `"8f1cc2c9faded2a4"`. Appending `?w=1041` to the URL returns a different
JPEG with a different digest; therefore **the original queryless URL must be
used for byte verification**. The rights and article page byte hashes are
receipts for retrieved live HTML, not immutable evidence of a perpetual grant.
See `records.json` for each exact SHA-256 and source byte count.

## Image-specific rights and honest limitations

The [NASA Image and Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)
state that NASA material is *generally* not subject to U.S. copyright and may
be used on educational/informational web pages; factual nonendorsement use is
permitted with NASA credited. NASA warns that some third-party assets on its
website remain protected and are individually identified. It separately limits
agency emblems/logos and commercial or promotional images of identifiable
people. The cited image page says **Image Credit: NASA**, not a named outside
photographer, and no marked third-party rights were observed on the page.

> **Rights falsifier:** A NASA page and its general reuse rules do not license
> Star Trek's fiction, imply NASA endorsement, release publicity rights for
> commercial promotion, or establish every jurisdiction's copyright position.
> The picture contains recognizable cast members and potentially marks.
> Independently review the exact NASA asset and actual Explorer placement.

> **Identity falsifier:** The real shuttle orbiter *Enterprise* is not the USS
> Enterprise, an episode scene, or a photo of a fictional starship filming
> model. This image may support a future **real-world Star Trek / NASA history
> panel**, but it cannot satisfy missing episode/film artwork thumbnails or
> advance a fictional Work's research coverage.

Suggested attribution for a separately approved editorial placement:

> NASA. Star Trek cast and Gene Roddenberry at the Space Shuttle Enterprise
> rollout, Palmdale, California, September 17, 1976. Used for factual historical
> research; NASA does not endorse this independent archive.

## Scope and validation

This packet has **1 image source**, **3 first-party NASA document receipts**,
**1 measured image SHA-256**, **0 binaries**, **0 external image hotlinks**, **0
accepted Work/episode bindings**, **0 model evidence/coverage effects**, and
**0 public display**. The output is a rights-and-identity review candidate,
not a deterministic admission or publishing instruction.

Run:

```bash
python proposals/research/nasa-enterprise-rollout-image-20261103/validate.py
python -m unittest discover -s proposals/research/nasa-enterprise-rollout-image-20261103 -p 'test_validate.py' -v
python -O -m unittest discover -s proposals/research/nasa-enterprise-rollout-image-20261103 -p 'test_validate.py' -v
```

**Next gate:** an independent license/identity/placement reviewer must verify
the image and proposed noncommercial editorial purpose before any approved
artwork-release sidecar or Explorer display change. No protected effects or
real-world research record promotions occur in this packet.
