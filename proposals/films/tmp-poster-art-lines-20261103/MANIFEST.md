# FILMS — *The Motion Picture* 2023 poster-art identities and print editions

**Source-local candidate-only artwork provenance, 2026-11-03 UTC.** Two distinct 2023 Vice Press art families and four physical print variants for the same film discovery candidate `film-motion-picture`. The only artwork observed was publisher page text/image labels; no actual poster pixels, source HTML snapshot, binary hash, film footage, or rights grant is held.

| Artwork family | Primary producer source | Print editions described |
| --- | --- | --- |
| Bob Peak original artwork, remastered | [Vice Press, 9 Oct 2023](https://vice-press.com/blogs/news/star-trek-the-motion-picture-by-bob-peak) | Timed regular edition (quantity based on orders, no fixed cap asserted); foil edition of 200; both 24×36 inches |
| New Matt Ferguson art | [Vice Press, 19 Sep 2023](https://vice-press.com/blogs/news/star-trek-the-motion-picture-by-matt-ferguson) | Numbered regular edition of 200; foil edition of 175; both 24×36 inches |

The first announcement attributes the original art to **Bob Peak**, says the producer worked with **Thomas Peak**, and credits **Matt Ferguson** in the remaster effort, supported by film Director's Edition producer David C. Fein. The second separately describes **newly made Matt Ferguson artwork**. That distinction is decisive: artist credit on a print of Bob Peak's restored art must not silently become “original art by Matt Ferguson,” nor may Ferguson's new composition be represented as a Bob Peak poster. The two source pages are same-producer marketing, **not independent licensing witnesses**.

### Media/edition scope

The franchise publisher's [2022 Director's Edition 4K announcement](https://www.startrek.com/news/fully-restored-directors-edition-of-star-trek-the-motion-picture-arrives-on-4k-ultra-hd) documents 4K disc packaging, a Director's Edition, the theatrical cut and a special longer cut as different film/video presentations. This is **context for excluding those cover/case images**, not a film-viewing or poster-rights source. The 2023 print families must not be equated to 2022 4K cover art, 1979 first-release printing stock, later 2026 27×40 one-sheet reissues, or film screenshots merely because the underlying film title matches.

All records are `proposal_only`, `accepted_coverage_effect=NONE`, `accepted_identity_effect=NONE`, `public_artwork_release_effect=NONE`, `media_bytes_fetched=false`, and `display_eligible=false` with no digital reuse permission verified. The `source_page_sha256` remains `null` because web-reader retrieval did not preserve immutable page bytes. The issuer's copyright footer and retail authorization do not grant this repository a public license.

### Hostile checks

> **Artist collision:** Both families mention Matt Ferguson, but in different roles. Collapsing them by film title or contributor name would create a false global artwork identity.

> **Print collision:** Both foil editions exist, yet their documented limits differ (200 versus 175), and their art families differ. A single “foil poster” thumbnail without exact source binding is ambiguous.

> **Version collision:** A 2022 Director's Edition 4K product image, a 2023 fine-art print, and a 2026 one-sheet may not depict identical art or format. Source labels cannot establish pixel identity.

> **Rights inflation:** Producer-hosted preview images, franchise marks, and a product sale are not a written grant to reproduce them in the Explorer; actual image use remains blocked.

> **Epistemic limit:** Publisher marketing may change, and the publisher's title/variant numbers have not been independently archived. The validator pins what was reviewed, not what could be found after future page edits.

### Validation

```bash
python3 proposals/films/tmp-poster-art-lines-20261103/validate.py
python3 -O -m unittest discover -s proposals/films/tmp-poster-art-lines-20261103 -p 'test_*.py' -v
```

Only a later rights-reviewed, version-specific asset receipt could qualify a thumbnail. No change to the accepted film catalog, Explorer art sidecar, Pages workflow or governed film evidence is proposed here.
