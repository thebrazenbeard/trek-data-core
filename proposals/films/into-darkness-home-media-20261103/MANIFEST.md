# FILMS — *Into Darkness*, five Paramount home-media source-local cards

**FILMS proposal-only discovery, 2026-11-03 UTC, accepted `main@1b4a91cda50f6f5b7c1d7d7ad424cdb58b951e8b`.** This is not a new Work, a watched-film source, a copyright license, a verified current offer, or a new public Explorer release.

## Producer/distributor source observations

1. Paramount's [current film listing](https://www.paramount.com/movies/star-trek-into-darkness), *About the Film*, shows **2013, PG-13, 132 MIN**, plus a synopsis/cast/crew section. The page does not name a cut or video medium for this length.
2. Paramount Home Media Distribution's [10 July 2013 release announcement, preserved at the studio's investor-relations PDF URL](https://ir.paramount.com/static-files/cf49d3ba-f408-4599-9180-d5141396e7e7), reports **131 minutes**, the historical digital and physical release dates, and concrete package contents. The named press-release issuer and host belong to the **same Paramount corporate publisher family** as the current page; their disagreement is not independently reconciled.

The press announcement's narrative describes the Enterprise investigating an attack within the Federation and pursuing the perpetrators. The packet's short synopsis sentence is an **original paraphrase of this producer marketing description**, not film evidence, and is not approved for publication. The accepted franchise publisher paraphrase for `film-into-darkness` is a separate, preexisting source-local record.

## Five *historically announced* format cards

| Source-local card | 2013 announced US date | Publisher format/content claim |
| --- | --- | --- |
| Digital debut | August 20 | Digital release, cut/encoding unspecified |
| Blu-ray/DVD combo | September 10 | 1080p Blu-ray and enhanced-widescreen SD DVD, with advertised digital access |
| Blu-ray 3D/Blu-ray/DVD combo | September 10 | Adds 1080p 3D disc to the above package |
| Single DVD | September 10 | Enhanced-widescreen 16:9 standard-definition disc |
| On Demand | September 10 | Availability channel named, no platform or encode specified |

These are **commercial release/package descriptions**, not five separate narrative Works. We did not identify packaging art versions from the announcement, download its media/cover/photo bytes, verify purchased SKU/barcode identity, or check contemporary service availability. `display_eligible=false` on every card. The 131-minute press figure remains **at the fact-sheet level**; the packet does not infer that every package and cut lasts 131 minutes. The two sources were inspected through a web reader, but original PDF/HTML bytes were **not** placed in custody and no `sha256` is invented.

## Hostile review

> **Runtime conflict:** The producer's live listing says 132 minutes, while its own home-media fact sheet says 131. Neither states identical source cut/rounding conventions. Do not overwrite one or claim a version-specific resolution.

> **Packaging identity collision:** Blu-ray/DVD and Blu-ray 3D/Blu-ray/DVD are separate publisher listings even though the latter includes the former's contents; collapsing them by movie title, artwork, format family, or an assumed disc hash creates unsupported identities.

> **Release timing:** The 2013 announced US date is historical evidence of an announcement, not proof that a given retailer, region, streaming service, or modern purchase remains available.

> **Rights/coverage inflation:** Studio distribution rights and published promotional text don't give the project a license to reproduce the cover, poster, still, video, audio, or full press release. No rights or cinematic analysis admission is granted.

> **Source custody:** The current Paramount page can change and the investor-relations PDF was read in rendered form. Neither immutable body digest nor exact page version is held; a future byte-custody receipt would require separately verified source bytes.

## Validation and next frontier

The validator locks exact reviewed source locators, film ID, issuer/lineage, five format/date/specification cards, the runtime disagreement and all release/coverage effects at `NONE`. The candidate-only proposal does **not** modify the public film catalog, synopsis compiler or artwork sidecar.

```bash
python3 proposals/films/into-darkness-home-media-20261103/validate.py
python3 -O -m unittest discover -s proposals/films/into-darkness-home-media-20261103 -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
```

**Next:** hostile review; authenticated edition/SKU and exact source-copy custody if independently obtained; an explicit version/rounding inquiry before resolving the one-minute runtime difference; and an independent artwork-rights grant before any thumbnail display.
