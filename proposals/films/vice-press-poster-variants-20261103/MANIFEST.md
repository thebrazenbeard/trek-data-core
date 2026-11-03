# FILMS — *The Voyage Home* poster-art variant provenance (2026-11-03 UTC)

**Candidate-only source metadata.** One film, three 2024 Vice Press lithograph editions. This tranche does not add an accepted Work, image, thumbnail, copyright clearance, source hash, film viewing, or semantic coverage.

## Actually examined

- [Vice Press' original producer announcement](https://vice-press.com/blogs/news/star-trek-iv-the-voyage-home-by-bob-peak), whose release description credits **Bob Peak** for the original art, **Thomas Peak** with providing the artwork and **Matt Ferguson** with remastering it. This is a claim by a product producer, not a fully documented rights-chain transfer.
- The same announcement distinguishes three 24×36-inch 2024 lithograph editions: a timed regular print (no edition cap supplied), a foil edition limited to 200, and a Japanese-title variant limited to 150.
- Direct [Vice Press foil-variant product page](https://vice-press.com/products/star-trek-iv-the-voyage-home-foil-variant-poster-bob-peak) and [Japanese-title product page](https://vice-press.com/products/star-trek-iv-the-voyage-home-japanese-title-variant-poster-bob-peak), whose headings independently identify each *variant within the same producer lineage*. No exact still-image bytes were inspected.
- The franchise publisher's [Star Trek Day 2024 product guide](https://www.startrek.com/gallery/star-trek-day-2024-gift-guide) lists the partner product through its search-indexed gallery description. It is a marketing relationship, **not an independent copyright grant**. The directly fetched editorial page did not expose the per-product text, so the Vice Press page is the stronger exact edition source.

The records map locally to the existing **discovery** candidate `film-voyage-home`, not a globally reconciled Work. A print of an artist's remastered marketing illustration is neither a film frame nor an original-theatrical-poster binary. The three variants share source lineage but differ in physical edition and are not three independent proof sources. The null timed-edition product locator is deliberate: the separately indexed `/products/star-trek-iv-the-voyage-home` page currently describes a generic Editions poster, not a verified exact match to the 2024 timed release.

## Explicitly withheld

- No `cdn.shopify.com` image URL, JPEG/PNG, hash of unseen bytes, artwork sidecar, Explorer image request, or Pages publication.
- No permission to use product images on the Trek Research public site. Even if Vice Press has the necessary rights to sell these prints, that would **not** be a sublicensing grant to unrelated sites. Bob Peak's art, Matt Ferguson's changes, and franchise marks raise distinct rights questions.
- No claim that English/Japanese versions or foil substrate represent distinct fictional Works; they are physical print variants of a candidate artwork family.
- No claim of `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, evidence-based episode/film continuity, or accepted research coverage.

## Hostile challenges

> **Source version trap:** A current retail product page can replace a 2024 limited-edition listing. Preserve the announcement's specific date and variant language; do not join a generic product URL to the timed print by title similarity.

> **Rights trap:** A producer's marketing credit may omit estate, franchise, derivative-artwork, or territorial license limitations. A product being officially licensed for sale does not authorize public thumbnail copying.

> **Independence trap:** Three product editions and a franchise partner guide can all inherit one promotional statement. More URLs do not mean more independent witnesses.

> **Visual edition trap:** A remaster and Japanese text version cannot silently replace an original 1986 one-sheet, an episode still, or a screenshot. There is no verified pixel-identity mapping.

## Deterministic validation

```bash
python3 proposals/films/vice-press-poster-variants-20261103/validate.py
python3 -O -m unittest discover -s proposals/films/vice-press-poster-variants-20261103 -p 'test_*.py' -v
```

The validator pins exact observed source statements/variant dimensions/limits, product locators, artist attribution, acceptance baseline and fail-closed rights. No retrieval is replayed by the compiler; no new license or canonical fact can be inferred from a green test. A later release must separately secure image-level rights, source snapshots, an exact accepted film-row match and a reviewed artwork sidecar before rendering.
