# TNG “Darmok”: first-party scene-still identity + safe original text card

**SOURCE-LOCAL PROPOSAL / NO REPRODUCTION OF EPISODE PIXELS.** This is an inventory and visual-reference proposal, not an accepted Work identity, official still license, or public Explorer release.

## Work and publisher source

1. Accepted `explorer/discovery-catalog.json` source-local row `publisher:s5:tng:001` lists TNG S5E2 **“Darmok”** from the official Paramount+ season-5 discovery feed; its existing verification status is `UNVERIFIED_METADATA` and remains unchanged.
2. The first-party [StarTrek.com article “Striving to Create Our Own 'Picard and Dathon at El-Adrel'”](https://www.startrek.com/news/lessons-of-next-generation-darmok), published **13 August 2024** by Brooke Knisley, editorially associates the actual picture with this episode. The image's directly adjacent publisher caption describes Dathon offering a dagger to Picard in **“Darmok.”** This constitutes **publisher image↔episode association**, not a claim of full-source viewing or a licensed frame extraction.
3. Exact original article [Prismic JPEG](https://images.prismic.io/star-trek-untold/ZrrC_EaF0TcGI4Q-_darmok-hd-236.jpg), retrieved 3 November 2026 for private pixel inspection: **321,843 bytes**, **1436×1080**, SHA-256 `a7a8ac3ef4ad18d4dcd003b53ac3f0ff73a7c0b49c2c3730f1fffd07bce8ab8c`. The pixels show two recognizable scene characters on an outdoor set, with Dathon holding out a dagger as Picard looks away. This is an **episode-related editorial scene still**. The pixel inspection does not establish whether it is literally a broadcast-frame extraction or a separately posed production still.
4. The source article credits its image to **StarTrek.com**, not an individually named photographer. Filename and nearby image credits do not establish this photograph's creator. No duplicate or alternate-license image is presumed.

## Why the actual scene still is held

- [CBS/Paramount Terms of Use](https://www.viacomcbs.legal/us/en/cbsi/terms-of-use), §4/§4.1, reserve publisher content rights; the website's original display is **not** general third-party republication permission.
- [Paramount Press Express Terms](https://www.paramount.com/paramount-press-express-terms-of-use), effective **14 February 2024**, §2 allow certain news/editorial/promotional reposting **only for authorized users**, while §3 restricts archiving, mirroring, modifications, and other uses. This image was sourced from a **StarTrek.com article**, not verified as an asset licensed to this project through a Press Express account; no authorized-user status or image-specific agreement has been established. §2 is a **conditional pathway to investigate**, not a proven current grant.
- Technical HTTP headers such as `Access-Control-Allow-Origin: *` and `Cache-Control: public` affect delivery/caching, **not** copyright or publicity rights. A normal hyperlink to the official article can be catalogued; the official JPEG remains withheld from public display, GitHub and the Explorer.
- Fair use may be assessed for a particular purpose and presentation, but this packet does not establish that assessment or assert categorical permission.

## Original fallback visual

`title-card.svg` is original text-and-geometry only: **DARMOK**, **TNG / SEASON 05 / EPISODE 02**, and the prominent truth label **REFERENCE CARD — NOT A SCENE STILL**. There is no official insignia, portrait, screen frame, book cover, publisher photo, embedded image, remote network request, or linked byte dependency inside the SVG.

The *proposed* Explorer card would show this original placeholder with a visible source link to the official article and keep actual-still rights marked **HELD**. This draft itself does not modify Explorer or publish the SVG. The librarian records binding and custody; the Consolidator/UX owners would independently integrate a reviewed presentation if authorized.

## Adversarial checks

`validate.py` pins the accepted source-local row and catalog hash, official URL/image digest/size/classification, rights hold, original SVG exact hash, and a flat inventory. It denies hidden JPEG/PNG/PDF/ZIP data, unreviewed files, remote/embedded SVG media, script/event handlers, false "public-domain screenshot" captions, license inflation, misleading broadcast-frame claims, source-work promotion, and Explorer/coverage effects. `test_validate.py` includes mutation and nested-payload regressions.

Run:

```bash
python3 proposals/librarian/tng-darmok-official-scene-safe-card-20261103/test_validate.py
python3 proposals/librarian/tng-darmok-official-scene-safe-card-20261103/validate.py
```

**No copyrighted episode image is checked into this packet.** No merge or deployment is requested.
