# NASA Enterprise rollout photograph — photo-specific institutional crosswalk

**Librarian source corroboration, not image release.** Accepted `main` already holds the NASA rollout display-decision packet from #418. The separate #426 real-world panel contract remains a proposal. This packet adds a concrete second NASA-controlled catalog route and independently rechecks actual JPEG bytes. It changes no website, fictional work, published image or coverage count.

## Identity and actual bytes

- NASA historical source page: <https://www.nasa.gov/image-article/star-trek-nasa-54-years-counting/>. Its image points at `ec76-5806-1.jpg` and carries `Image Credit: NASA`.
- Second NASA article: <https://www.nasa.gov/image-article/shuttle-enterprise/>. Its text identifies NASA Administrator James D. Fletcher, DeForest Kelley, George Takei, James Doohan, Nichelle Nichols, Leonard Nimoy, Gene Roddenberry, U.S. Rep. Don Fuqua and Walter Koenig in the archival photograph.
- Official NASA-operated Flickr Commons collection: <https://www.flickr.com/photos/nasacommons/9467279838/>. Its title is *The Shuttle Enterprise with Star Trek cast*; its item number is `S91-27436`, date label September 17, 1976, credit NASA, rights label **“No known copyright restrictions.”** It links NASA's media-use guidelines. This is a collection-status label, **not** a blanket public-domain or rights-of-publicity clearance.
- NASA history timeline: <https://www.nasa.gov/history/space-shuttle-enterprise-makes-its-public-debut/>. The dated public rollout was September 17, 1976 at Rockwell International's Palmdale plant. An event date is not independent EXIF or shutter timestamp proof.
- Direct NASA JPEG inspected visually on 2026-11-03: <https://www.nasa.gov/wp-content/uploads/2023/03/ec76-5806-1.jpg>. Actual HTTP bytes re-fetched on Lappy WSL: **165,312 bytes**, SHA-256 **`e36c3e1c94c53f57fe99ac921169c24a35c63851666885d20af6fdfe902ed6f8`**, JPEG SOI `ffd8`, file dimensions reported 1041×833 in accepted #418. The image is a real shuttle/event group photograph, not an episode/movie still. The exact NASA JPEG image was returned by the connected image-reader and visually inspected in this research turn.

The institutional Flickr photo depicts an evidently matching composition, but the JPEG filename and Flickr catalog number differ. **Do not assert bit-equivalence, original-negative identity, an individual photographer or independent rights-holder corroboration** based on the thumbnails. Both NASA articles and NASA Commons belong to the same institutional source family.

## Conditional policy and release HOLD

NASA's current <https://www.nasa.gov/nasa-brand-center/images-and-media/> permits NASA imagery for factual educational/informational websites, with NASA acknowledgment and without implying endorsement. NASA warns that some images are third-party copyrighted, and promotional uses with recognizable persons or NASA logos have additional restrictions. This packet is a *potential educational/editorial use*, not a universally licensed asset, endorsement or an authorization to mirror/hotlink.

For an actual public picture in the Explorer:

1. An **independent photo-specific rights reviewer** must resolve the institutional credit, any underlying third-party/individual-photographer status, placement, and NASA's contemporaneous policy. Record exact reasoning and the image hash; don't merely count another model agreeing.
2. An **independent context/design reviewer** must approve a separate, nonpromotional real-world historical panel, adjacent `NASA` credit + nonendorsement, accurate alt/caption, no NASA insignia as branding, and no fictional episode/film/book artwork mapping.
3. Accept a separate image-specific **release manifest** and exact pinned asset/hash for a gated same-origin rendition, with no automatic fetch at HOLD. Verify image bytes, contrast, small-screen/keyboard behavior and consent flow. Protect the three distinct #414 NASA photos from blanket promotion.
4. Obtain the project's required publication/deployment authorization. Acceptance of this source packet alone does not grant it.

Until then: `public_display_eligible=false`, `release_authorization=NOT_GRANTED`, `image_binaries_included=0`, `site_effect=NONE`. No photo was added to the repository. This is a source-bound readiness increment, not the visual outcome Patrick is still waiting for.

Run `python3 validate.py` and `python3 -m unittest -v test_validate.py`. `python3 validate.py --verify-download` separately re-fetches the exact photo bytes when network is explicitly available; it does not write an asset.
