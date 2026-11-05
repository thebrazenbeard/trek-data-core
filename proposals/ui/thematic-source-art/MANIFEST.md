# Two source-tied original thematic illustrations (HELD proposal)

**Accepted main when prepared:** `3028765359001b90bc3e6b5c1835ee283b326e91`.
**Dependency:** additive held *art-only* branch `d9b6b67743a2182062e3af097f5aecd52478fe4b`, not the owner-private 347-OPF preview. No actual public Explorer deployment.

## Primary publisher descriptions used

| Source-local candidate | Direct first-party publisher listing | Source-supported visual tags | Interpretive geometry |
|---|---|---|---|
| `lead:0000`, TOS S2 E6, *The Doomsday Machine* | [Paramount+ S2E6](https://www.paramountplus.com/shows/video/1226106142/), its episode listing synopsis | `machine`; `destroys planets` | An original mechanical aperture approaching a fractured sphere. The aperture and fragments are **visual interpretation**, not asserted frames from the episode. |
| `lead:0001`, TOS S2 E15, *The Trouble with Tribbles* | [Paramount+ S2E15](https://www.paramountplus.com/shows/video/1226188697/), its episode listing synopsis | `overrun`; `furry creatures` | Original generic compartment outlines filling with many colored fuzzy circles. Shapes do not reproduce any official creature design or vessel. |

Publisher description texts and **their exact UTF-8 SHA-256 digests** are in `manifest.json` and pinned independently in the builder. The accepted metadata rechecks support only **title/series/season/air date**, not episode description claims; this new proposal distinctly identifies the first-party publisher episode-page descriptions as an additional externally retrieved source. **No raw publisher webpage HTML SHA has been claimed**; no full video, transcript, screenplay or novel was read for these illustrations. Publisher listing synopsis is *not* a full episode close-read.

## What is different from a title card?

Both illustrations have large, visually interpretable subject matter occupying the main canvas. The mechanical aperture/planet fracture motif is distinct from the large overflowing fuzzy-circle matrix. A visible disclaimer remains: `NOT AN EPISODE STILL · NOT OFFICIAL ART · NOT CLOSE-READ EVIDENCE`.

The SVGs are original authored geometry using no remote image requests, actor likeness, franchise insignia, copied prop silhouettes, source image bytes, official cover, or external scripts. Source-relative evidence terms must match the publisher description, official URL must match the pinned accepted metadata crosswalk, and visual art/manifest bytes must deterministically regenerate.

```sh
python3 tools/build_thematic_source_art.py --check
python3 -m unittest tests.test_thematic_source_art -q
python3 tools/validate.py
```

This remains a **HELD draft candidate**, not a licensed image, admitted Work, content coverage, or public Pages release. Separate independent semantic, visual/accessibility, and franchise rights review is required.
