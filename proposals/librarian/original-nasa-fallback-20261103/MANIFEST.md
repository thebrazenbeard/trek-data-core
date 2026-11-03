# Original abstract cards and real-science artwork routes — bounded Librarian proposal

**2026-11-03; accepted source baseline:** `main@3c0b37564123166bf38bcfa66f018abc4d5c9996`.

**Effect:** artwork publication `NONE`; Source/Work/Evidence/coverage `NONE`. No image bytes, external requests, image-rights grants, official series graphics, public thumbnails, or Explorer code are added by this proposal.

## Reproducible no-rights-dependency fallback

`tools/render_original_abstract_art.py` renders a simple, self-contained, original SVG placeholder with a deterministic abstract star field, a media-type palette and an XML-escaped source-local title. It takes only an explicit media enum, a bounded row ID, and a bounded title. It performs no networking or repository writes; there is no embedded logo, insignia, screenshot, book jacket, actor, franchise title design, or claim that an image depicts a fictional episode. The SVG is visibly labeled **ABSTRACT PLACEHOLDER · NOT OFFICIAL ART**.

Five palettes are supported: `EPISODE`, `FILM`, `LITERATURE`, `SHORT_FORM`, and `AUDIO`. For untrusted titles or row IDs, reject control characters and escape markup. This is a design/code candidate and **not an accepted artwork publication authorization**. The Consolidator must separately qualify actual CSS/Pages compatibility, accessibility, UI behavior, asset paths, SVG security and any public deployment; no directory row is prebound here.

## Two primary-source real-astronomy routes (not Star Trek stills)

1. NASA Science's [*The Blue Marble*](https://science.nasa.gov/resource/the-blue-marble/) describes Apollo 17 photograph `AS17-148-22727` and credits **NASA Johnson Space Center**. This is Earth photography, **not** a starship, fictional location, or canonical episode illustration.
2. NASA Science's [*Cosmic Cliffs* NIRCam/MIRI composite](https://science.nasa.gov/asset/webb/cosmic-cliffs-in-the-carina-nebula-nircam-and-miri-composite-image/) documents real NGC 3324, Webb's early-release observations, and explicit credit **NASA, ESA, CSA, STScI**. The multi-agency contribution requires a per-item display decision; NASA-only ownership must not be inferred.

NASA's [media use guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) generally allow educational/informational use of NASA-created imagery subject to third-party-rights, no-endorsement, identity and logo restrictions. That general policy is **not** a verified item-level public-use permission for the multi-agency Webb composite or a blanket approval for all derivatives. We retained both items as **decorative real-science candidates only**, with `asset_url:null` and `local_binary_sha256:null`, and did not download or hotlink images.

Earlier accepted [Commons and publisher artwork research](../commons-asset-review-20261103/MANIFEST.md) covers the Joe Ross museum photograph, official Simon & Schuster book jacket, StarTrek.com posters, Open Library route and TMDB caveats; this packet does not reclassify their holds. The current nine literary discovery rows have **zero** edition-cleared covers in the accepted [directory gap audit](../artwork-current-directory-gap-20261103/MANIFEST.md).

## Source retrieval limitation

Direct public `openlibrary.org/isbn/*.json` calls failed in the current retrieval paths, including a Lappy TLS connection reset. This is an **access failure**, not proof of absence of an edition or cover. The indexable Open Library HTML for ISBN `9781783297481` resolves to `OL28813033M`, but did not expose a verified cover ID. No guessed cover IDs were entered.

## Deterministic validation

```bash
python3 -m unittest discover -s proposals/librarian/original-nasa-fallback-20261103/tests -p 'test_*.py' -v
python3 -O -m unittest discover -s proposals/librarian/original-nasa-fallback-20261103/tests -p 'test_*.py' -v
python3 proposals/librarian/original-nasa-fallback-20261103/tools/render_original_abstract_art.py --row-id 'lead:0000' --medium EPISODE --title 'Example observation'
```

The third command prints a generic SVG to stdout for offline inspection; **it does not add it to Pages**. A future public renderer must maintain the source-relative label and never imply the abstract card is official art or a captured film/episode frame.
