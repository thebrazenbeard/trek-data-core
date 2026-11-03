# Librarian source custody — *Arena* Gorn museum exhibit photograph

Status: **SOURCE ONLY / HELD**. No image binary, Explorer thumbnail, database import, episode coverage, or accepted Work identity is added by this proposal.

## Exact visual and source identity

- **Work lead:** *Star Trek: The Original Series*, “Arena” (accepted discovery row `legacy:s1:tos:018`; its existing classification is `UNVERIFIED_METADATA`, not newly admitted).
- **Visual type:** Photographer Joe Ross/Joetography LLC's **22 August 2019 photograph of a Gorn costume display at the Henry Ford Museum's traveling *Star Trek: Exploring New Worlds* exhibit**. It is **not** a broadcast frame, screenshot, episode promotional still, or behind-the-scenes production photograph. The photographer links the display to “Arena.” The actual costume's status as an original filming artifact has **not** been independently authenticated.
- **Episode link:** [StarTrek.com's discussion of the Gorn introduction in “Arena”](https://www.startrek.com/news/strange-new-worlds-gorn-arenas-message-of-mercy) independently confirms the fictional character/episode association, **not** the museum costume's material provenance.
- **Photographer first publication:** [Flickr photo 49786531687](https://www.flickr.com/photos/joeross/49786531687/).
- **Commons photo + license record:** [Wikimedia Commons file](https://commons.wikimedia.org/wiki/File:The_Gorn!_Star_Trek-_Exploring_New_Worlds_exhibit_at_the_Henry_Ford_Museum,_Dearborn,_Michigan.jpg); [pinned 2026-02-17 revision](https://commons.wikimedia.org/w/index.php?title=File:The_Gorn!_Star_Trek-_Exploring_New_Worlds_exhibit_at_the_Henry_Ford_Museum,_Dearborn,_Michigan.jpg&oldid=1167442434). Commons records a 15 June 2023 Flickr license review confirming CC BY-SA 2.0.
- **License:** [Creative Commons Attribution-ShareAlike 2.0](https://creativecommons.org/licenses/by-sa/2.0/), covering the photographer's photo only. Attribution, source/license links, modification notice, ShareAlike duties if adapted, and no implied endorsement must accompany eligible reuse. This license does not purport to clear Paramount/CBS rights in costume design or exhibit content.
- **Original image fetched and visually inspected:** 7,753,903 bytes, MIME JPEG, metadata 5568×3712 with EXIF 90° clockwise rotation (displayed orientation 3712×5568); SHA-256 `c71f33e5d123e21dbefcfef41dc3f97f425c62470ef46d2f138cdf3baeaeb287`. Viewed pixels show a green reptilian costume/mannequin behind a glass display front; cannot prove the display's specific historical artifact lineage.
- **Pinned Commons page fetched:** 138,306 bytes, SHA-256 `5541a7251878e26d959455e30200395780986a998bdd4d471b0f749532c57b4c`.

## Rights / release gate

This proposal **does not** claim a fully cleared public episode thumbnail. Documentary museum imagery can be valuable alongside a properly labeled episode record, but bare use as an “Arena” screenshot would materially misrepresent the source. A future review needs to resolve or approve the depicted artifact's separate rights, exact context caption and attribution placement, transformation license effects, nonendorsement, and relationship to a work ID. Until then, `HELD_NO_PUBLIC_THUMBNAIL` means no merge/release/deploy effect.

Hostile falsifier: captions such as “frame from Arena,” “on-set production photograph,” or “original filming Gorn costume” must fail the validator; photographer/Commons association alone cannot substantiate those assertions.

## Reproducibility

Run `python3 proposals/librarian/arena-gorn-museum-20261103/test_validate.py` and `python3 proposals/librarian/arena-gorn-museum-20261103/validate.py`. These check the accepted discovery row, exact source/byte fields, pinned documentary label and held gates. Tests do not call the network, and the copyrighted image binary is **not** committed.

The validator recursively rejects nested image extensions, image-file magic disguised with another extension, and symlinks in this proposal partition; corresponding hostile regression tests exercise the first two bypasses.
