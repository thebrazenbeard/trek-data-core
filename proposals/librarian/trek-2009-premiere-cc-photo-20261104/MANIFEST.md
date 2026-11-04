# HELD — *Star Trek* (2009) Sydney premiere ensemble photograph

Librarian artwork proposal · 2026-11-04 · not a public image release.

Rechecked live GitHub `main` at
`3028765359001b90bc3e6b5c1835ee283b326e91`. [Draft PR #523](https://github.com/thebrazenbeard/trek-data-core/pull/523)
for *Into Darkness* photographs is **open** and not accepted; this proposal
contains a **different photograph for a different already accepted film row**.
The accepted `explorer/beyond-premiere-photo.json` also covers a different
film; no existing photograph is re-ingested here.

## Exact file-level candidate

| Question | Observed source-relative answer |
|---|---|
| Accepted film row | `film:film-2009` — *Star Trek* (2009), first-party film locator [`startrek.com/movies/star-trek-2009`](https://www.startrek.com/movies/star-trek-2009) |
| Stable accepted film-row receipt | `explorer/search-catalog.json` SHA-256 `a197138a9069fb67ac5307055588659dd74a9fb4e1caa9d5295d24bc0687d4e5` |
| Actual photograph | [Commons: StarTrekSydneyOperaHousePremiereApr09.jpg](https://commons.wikimedia.org/wiki/File:StarTrekSydneyOperaHousePremiereApr09.jpg), [exact page revision `1254161622`](https://commons.wikimedia.org/w/index.php?title=File:StarTrekSydneyOperaHousePremiereApr09.jpg&oldid=1254161622) |
| Photographer | **Penny B. Dreadful**, via [original Flickr photograph `3420160659`](https://www.flickr.com/photos/visible-woman/3420160659) |
| Date and event | 2009-04-07, *Star Trek* film premiere at Sydney Opera House, Australia |
| Source image dimensions | 1,886 × 934 pixels (Commons metadata, not an independent pixel inspection) |
| Explicit file-level license | **CC BY 2.0**, [Creative Commons license](https://creativecommons.org/licenses/by/2.0/) |
| Prior source license verification | Commons states trusted reviewer **High Contrast** confirmed the Flickr CC BY 2.0 status on **2009-05-02** |
| People named by file-description prose | Karl Urban; Chris Pine; Bryan Burk; Zachary Quinto; J. J. Abrams; Eric Bana; John Cho |
| Structural original digest | Commons structured data reports image SHA-1 `57f3913143347cdf32056a57aeb86e6b9086b33b`; **not independently recomputed** here |
| Honest type | Real-world film premiere documentary photograph — **not** a film frame, Paramount still, or theatrical poster |

This is a stronger *film-specific* candidate than a generic actor portrait:
the file description explicitly identifies the film premiere, cast and
filmmakers, and the still-picture aspect ratio can suit a landscape card. It
is not a substitute for official artwork, and no visual reviewer has yet
inspected the exact pixels or crop. The film row's `UNVERIFIED_METADATA` and
zero research coverage remain unchanged.

## Separate rights gates

The file page's Creative Commons license claim and its 2009 Flickr reviewer
record support a potential copyright reuse path. A finished attributed image
would need photographer and supplied filename credit, source link, precise
license link, and an adaptation/change notice when relevant. The [Commons
page itself expressly warns of depicted people's personality rights](https://commons.wikimedia.org/wiki/File:StarTrekSydneyOperaHousePremiereApr09.jpg).
Review publicity/privacy, visible logo/backdrop, contextual endorsement,
venue terms where relevant, accurate cropping and size-specific attribution
before deciding any real Explorer use.

> **HOSTILE REVIEW:** Licensed photography is not licensed Star Trek
> intellectual property wholesale. The photographer's reusable documentary
> photo does not confer studio poster rights, actor endorsement, or permission
> to claim that the depicted red-carpet event is a film scene. Even a valid
> Commons SHA-1 metadata claim is not a locally verified SHA-256 binary receipt.

The HELD packet explicitly records null image SHA-256, null crop/thumbnail
digest, null visual/rights reviewer and null exact release binding. The
Commons old-revision URL is a page identity, **not** a cached page-body digest.
No image was downloaded, mirrored, modified, published or shown on Explorer.
No release-sidecar, Work/Source admission or coverage effect occurs.

Next frontier: independent pixel/rights review; exact selected source and
derivative bytes with SHA-256; visible attribution and change notice; specific
rights receipt and source-row binding accepted by the code-owned artwork
release gate; browser-qualified opt-in display; explicit release authorization.

Deterministic local validator: `python3 tools/validate_trek_2009_premiere_photo.py --check`
and `tests/test_trek_2009_premiere_photo.py`. These tests reject forged
license, rights, image hashes, swapped film IDs, or acceptance claims.
