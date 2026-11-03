# First-party episodic still — SNW 201 “The Broken Circle”

**Status: SOURCE-LOCAL / RIGHTS HELD.** No public thumbnail, image binary, Explorer entry, Work identity promotion, or coverage effect.

## Evidence and identity

1. Accepted `explorer/discovery-catalog.json` contains source-local Paramount S2E1 discovery row `roster:modern-s2:snw:000`, title **“The Broken Circle”**, `UNVERIFIED_METADATA`. The row remains a lead; this proposal does not resolve it to an accepted global Work.
2. First-party [StarTrek.com episode recap](https://www.startrek.com/news/recap-201-the-broken-circle-strange-new-worlds) identifies its *Strange New Worlds* Season 2 premiere as episode 201 and names “The Broken Circle.”
3. First-party StarTrek.com [“Top 10 Moments from the Second Season”](https://www.startrek.com/news/top-moments-strange-new-worlds-season-2-guide) (published 15 July 2025) includes the section **“10. Spock Takes Command”** with image alt text **“Spock sits in the captain's chair on the bridge in 'The Broken Circle'.”** The adjacent display credit is **StarTrek.com**. This is direct editorial episode-image association, not merely a filename guess.
4. [Official promotional-stills gallery](https://www.startrek.com/gallery/first-look-strange-new-worlds-the-broken-circle) (15 June 2023) demonstrates that the publisher operates a named episode gallery, but the web-readable listing **does not establish that this exact article image belongs to that gallery**. Do not cross-join without evidence.
5. The exact article-embedded [Prismic CDN JPEG](https://images.prismic.io/star-trek-untold/MjNhNGQ0ZDktMmUyMi00NzBmLWExMTgtZDFmNzg0NzE0YTQx_snw_201_mg_0214_0773_rt.jpg) was fetched for private source verification and visually inspected: **849,914 bytes**, raw **3060×2041** JPEG, SHA-256 `96a88ec842d8a10329c09e66ee3442dbe4c8f21a2d04b1e8fce712d5d033e02d`. It visibly shows Spock seated in the captain's chair with bridge panels. Pixels alone cannot prove the episode; the publisher caption provides that identification.

## Why the public thumbnail stays held

- First-party webpage display **does not itself confer republication permission**.
- The publisher's [Terms of Use](https://www.viacomcbs.legal/us/en/cbsi/terms-of-use) (effective 27 May 2025), §4, expressly includes photographs among protected content and reserves rights; it describes restrictions on copying, database storage and redistribution except specified authorizations or §4.1's specifically designated distribution. Nothing observed identifies this exact image for unrestricted third-party display.
- The article footer identifies CBS Studios/Paramount companies and states **All Rights Reserved**. The article credit “StarTrek.com” does not identify an individual photographer; no name is inferred from `MG` in the image filename.
- The [Paramount Press Express photos portal](https://www.paramountpressexpress.com/paramount-plus/shows/star-trek-strange-new-worlds/photos/) is first-party but returned a **geographic access block** in the consulted environment; cached search descriptions were not treated as proof of full terms or license for this exact file. No access-control bypass attempted.
- Legal exceptions such as fair use are context-specific and are **not established** by this source packet. This packet makes **no definitive legal opinion**; it records an absence of affirmative broad display permission, so the project's display gate remains closed pending a separately supported authorization/usage decision.

## Hostile-review falsifiers

- Replace caption with “public domain screenshot,” “officially licensed for any fan site,” or assert an unverified named photographer → validation must fail.
- Promote image into Explorer, infer global Work identity, count episode coverage, or include `.jpg/.png` files (including nested/disguised) in this source packet → fail.
- The official 2023 promotional-stills gallery is **episode-specific**, but this distinct JPEG's membership in that gallery must remain `false` until directly proven.

Run `python3 proposals/librarian/snw-broken-circle-official-still-20261103/test_validate.py` and `python3 proposals/librarian/snw-broken-circle-official-still-20261103/validate.py`. No network required by validator; image bytes are not committed.
