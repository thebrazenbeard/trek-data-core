# VOY “Living Witness”: genuine episode still, rights hold, original LCARS reference card

**SOURCE-LOCAL / NO PUBLIC EPISODE IMAGE.** This proposal records a publisher image-to-episode association and an independently authored visual fallback. It does not read the full episode, establish a broadcast frame, release a copyrighted still, reconcile a Work, change coverage, or edit Explorer.

## Source identity, edition and image variants

1. The accepted main `explorer/discovery-catalog.json` contains the Paramount+ source-local episode lead `publisher:s4:voy:022`: *Voyager* **S4E23**, **“Living Witness”**, `UNVERIFIED_METADATA`. The source-local state remains unchanged.
2. First-party [StarTrek.com, “The Best of The Doctor”](https://www.startrek.com/news/voyager-the-doctor-watchlist), published **31 October 2023**, presents the episode-specific heading **“Living Witness”** immediately alongside an image alt label **`Star Trek: Voyager "Living Witness"`**, credit **StarTrek.com**. The adjacent paragraph discusses The Doctor's appearance in a museum centuries later. It gives a publisher *image-to-episode editorial association*, not independent evidence from the original episode and not copyright permission.
3. The article links the [Prismic delivery variant](https://images.prismic.io/star-trek-untold/NjFiMDBmZGEtYjczNC00N2I4LThkMjAtNjRlNWY4NWE3NjQ5_th_livingwitness.jpg?auto=compress%2Cformat). Retrieved **3 November 2026**, exact **97,350-byte**, **1920×1080 JPEG**, SHA-256 `0190eb49039850fc0515375e754b14539354a835d25e9606a3efe641fa652358`. The [same object path without the query](https://images.prismic.io/star-trek-untold/NjFiMDBmZGEtYjczNC00N2I4LThkMjAtNjRlNWY4NWE3NjQ5_th_livingwitness.jpg) yielded a different **114,509-byte**, **1920×1080 JPEG**, SHA-256 `d9361b21961b0446def489d9c4b2b6ed845e1cc6410e3a9f8bf89c69bba6c2e9`. Both were fetched and visually inspected: The Doctor stands foreground against a blue-lit interior with another indistinct figure behind, and an official StarTrek.com watermark in the lower right. These are distinct *compressed delivery variants of one photo*, **not** independent witnesses.
4. The site does not name the individual photographer for this exact file. The pictured scene does not establish this photo's method of capture; no claim it is specifically a broadcast-frame extract rather than a production editorial still.

## Rights HOLD and safe fallback

- [CBS/Paramount Terms](https://www.viacomcbs.legal/us/en/cbsi/terms-of-use) §4/§4.1 reserve content rights; the publisher displaying a still or publishing it with a watermark is **not** a broad reuse license.
- [Paramount Press Express Terms](https://www.paramount.com/paramount-press-express-terms-of-use) §2–3 condition repost permission on authorized-user status and legitimate scoped editorial use, with substantial restrictions. The StarTrek.com article image is **not** demonstrated to have been obtained through an authorized Press Express grant to this project. No license is inferred from `Access-Control-Allow-Origin`, caching headers, public viewability, or the site's watermark. No categorical legal conclusion about fair use is made.
- `title-card.svg` is an ORIGINAL, self-contained abstract graphic with only colored bars and exact title/episode text; no Paramount visual pixels, Starfleet marks, cast portraits, stock assets, hotlinks, external requests, or executable behavior. Its visible legend is **“REFERENCE CARD — NOT A SCENE STILL”**. A future authorized Explorer integration could link this safe card to the first-party article while separately showing publisher-photo rights **HELD**.

## Falsifiers and boundary

`validate.py` pins the accepted source-local row/catalog hash, both Prismic URL byte identities, caption, rights status, original SVG SHA, manifest SHA and exact five-file tracked inventory. It rejects nested/hidden files, disguised JPEG/PNG, embedded image URLs, external SVG media/scripts, fabricated public-domain rights, false photographer/scene-frame claims, inflated coverage, and a public release flag. `test_validate.py` exercises those paths.

Run:

```bash
python3 proposals/librarian/voy-livingwitness-official-scene-safe-card-20261103/test_validate.py
python3 proposals/librarian/voy-livingwitness-official-scene-safe-card-20261103/validate.py
```

**No episode JPEG is checked in. Source packet only.** Independent hostile review and downstream visual release decisions remain separate.
