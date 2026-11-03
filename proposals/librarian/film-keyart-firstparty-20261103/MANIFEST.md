# Four first-party film poster links — Librarian source observations

**Proposal only; all rights held.** Accepted main at acquisition:
`50e20f8776abb5c78d04a89df7ed7c56c31af8ac` (2026-11-03).
The film catalog at `explorer/film-catalog.json` was byte-verified as
`6513e5f96aac845727b57bd2f967170d56b95367fa95075e6919a4530bb3d6de`.
These are four **source-local publisher image links**, not four film
close-reads, licensed thumbnails, independently authenticated posters or
globally reconciled Work records.

## Source-first findings

| Source-local film ID | Official film page inspected | Image description on the publisher's page | Display |
| --- | --- | --- | --- |
| `film-voyage-home` | [*Star Trek IV: The Voyage Home*](https://www.startrek.com/movies/star-trek-iv-the-voyage-home) | “Poster Art for Star Trek IV: The Voyage Home” | HELD |
| `film-first-contact` | [*Star Trek: First Contact*](https://www.startrek.com/movies/star-trek-viii-first-contact) | “Poster art for Star Trek: First Contact featuring Jean-Luc Picard, Data and the Borg Queen” | HELD |
| `film-into-darkness` | [*Star Trek Into Darkness*](https://www.startrek.com/movies/star-trek-into-darkness) | “Poster art for Star Trek: Into Darkness” | HELD |
| `film-beyond` | [*Star Trek Beyond*](https://www.startrek.com/movies/star-trek-beyond) | “Poster Art for Star Trek: Beyond” | HELD |

The first-party film pages' **actual image-link targets** point to four
distinct `images.prismic.io/star-trek-untold` key-art PNGs. The exact
per-film URLs, raw publisher-HTML response body SHA-256, body byte counts,
and publisher-page image alt text are in `records.json`. Unlike the earlier
three `og:image` header observations in
`artwork-primary-asset-locators-20261103`, these four links come from the
publisher page's explicitly labeled *poster-art image*, not the header
image. No claim about official theatrical release/poster edition, image-pixel
contents or page-specific third-party grant is inferred from a filename
or alt text.

Observation procedure on 2026-11-03:

1. Independently opened each of four first-party film pages through a
   read-only rendered web source and followed its poster-image link. The
   image fetch itself failed in that retrieval interface; the exposed
   exact URL was retained, **not a claim that bytes were read**.
2. On the authorized Lappy Windows machine, ordinary Python HTTPS GET
   read each film HTML document (all HTTP 200). Its raw response-body
   digest and byte length are recorded; HTML bytes were not committed.
3. A separate bounded raw-HTML fetch for each page confirmed that the
   poster asset UUID appeared **48 times** and page markup contained
   an alt string featuring “Poster Art” or “Poster art.” This was a
   distinct response observation; dynamic HTML may change between GETs.
4. Each title, source URL and film ID was checked against the **exact
   accepted 14-row source-local film catalog**. No secondary aggregator
   was treated as an independent rights or image witness.

## Rights and publication boundary

Each publisher page shows a Paramount/CBS copyright reservation. **A
publicly viewable poster URL is not permission for GitHub Pages to hotlink,
rehost, mirror or redistribute it.** These publisher CDN URLs are research
locators only. This packet contains no image files, pixels, local art paths,
licensing claims, unbounded CSP change, browser code or artwork sidecar entry.
All four remain `HELD_NO_PUBLIC_DISPLAY_LICENSE` pending a distinct,
image-specific rights decision and visual review. This distinction applies
even for a noncommercial, $0 site.

**Independent hostile rights finding (2026-11-03):** the separately assigned
Auditor inspected the publisher film-page footer `Terms of Use` link to
[CBS Interactive / Paramount Terms of Use](https://www.viacomcbs.legal/us/en/cbsi/terms-of-use).
The Auditor reports that section 4 limits ordinary viewing and reuse,
section 4.1 requires specifically identified redistribution permission, and
section 10 prohibits making publisher Content available through inline
links. This is a material counterexample to treating a publisher-controlled
CDN asset as authorized to embed. No permission specific to these four
images was identified. **All four are HOLD for both public hotlinking and
local redistribution**, even if image pixels were later verified.
I independently fetched that exact current linked Terms page via Lappy
HTTPS (HTTP 200, 55,007 raw bytes, raw-response SHA-256
`22cca1e7632f0f6809e718a46c5cd759683027aa1f1b3c3090a1cb9740792a35`);
the page text included the frame-services restriction. This byte receipt is
an observation of a volatile online policy page, not an archived immutable
legal record or permission. `records.json` and its validator pin the
actual terms URL, response digest and negative display gate.

> **Hostile falsifier:** An image tagged “poster art” by a publisher is a
> first-party description, not a legally sufficient reuse grant. The
> asset host may be a publisher-controlled CDN without granting public
> third-party embeds. Unread pixels and changing HTML also prevent
> asserting a stable graphical fingerprint or authentic theatrical key art.

## Validation

The standalone validator enforces closed fields, all four exact
film-ID/title/official-page/poster-URL/alt/response-receipt tuples in code,
the byte-authenticated accepted film catalog, and publication/coverage
effects `NONE`. This guards against an image swap even if source film IDs
and official page URLs are swapped together, as well as forged same-host
links, invented rights, and schema smuggling. It is **not** a rights validator.

```sh
python3 proposals/librarian/film-keyart-firstparty-20261103/validate.py
python3 -m unittest discover -s proposals/librarian/film-keyart-firstparty-20261103 -p 'test_validate.py' -v
python3 -O -m unittest discover -s proposals/librarian/film-keyart-firstparty-20261103 -p 'test_validate.py' -v
```

**Effects: zero accepted Source/Work bindings, close reads, coverage changes,
public thumbnails, Explorer changes or deployment.** Next frontier:
independent visual/content and rights review for each specific PNG, image
bytes/receipt if a legitimate display route is established, and a separate
code-owned release proposal. No rights promotion follows from this packet.
