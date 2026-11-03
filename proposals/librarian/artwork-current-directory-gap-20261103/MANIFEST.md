# Accepted-directory artwork binding audit — 2026-11-03

**Role:** LIBRARIAN
**Artifact:** source-local coverage and rights gap report; **not** an artwork-release manifest.
**Accepted source snapshot:** `main@a7b10ad10f318b47c21df17e79ed1b865c0c6d34`
**Directory:** `explorer/discovery-catalog.json` SHA-256 `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`
**Effects:** accepted Source/Work/Evidence/coverage `NONE`; artwork publication `NONE`; no binary assets copied.

## Exact current directory boundary

The accepted source-local discovery catalog has **1,214 observations**, including **nine literary leads**. The nine literary row IDs and publisher/distributor edition identifiers below were read from the exact accepted directory snapshot. They are **not** nine globally reconciled Works or nine authenticated source editions.

| Source-local row | Publisher/distributor edition identifier(s) | Edition-bound public thumbnail cleared for this row? |
| --- | --- | --- |
| `literature:proposed-lit-snw-ring-of-fire` | `9781668095898`, `9781668095904`, `9781668095911`, `9781668134559` | **No.** An earlier source-receipt checked four Open Library ISBN cover endpoints and recorded HTTP 404; this was not a fresh negative test. |
| `literature:proposed-lit-picard-second-self` | `9781982194833`, `9781982194840`, `9781797137278` | **No verified image/cover ID.** |
| `literature:proposed-lit-snw-high-country` | `9781668002391`, `9781668002407`, `9781797149226` | **No verified image/cover ID.** Open Library's author directory independently lists a *High Country* Work with three editions, but that is not a matched cover for one of these ISBNs. |
| `literature:proposed-lit-discovery-enterprise-war` | `9781982113315`, `9781982113322`, `9781508283195` | **No verified image/cover ID.** Open Library's author directory independently lists an *Enterprise War* Work with three editions, not a publisher-edition cover assignment. |
| `literature:prh-autobiography-kirk` | `9781783297481` | **No verified image/cover ID.** A distinct Open Library **edition metadata** record `OL28813033M` independently lists this exact ISBN and Titan Books; cover identification and rights remain unverified. |
| `literature:prh-autobiography-picard` | `9781785659409` | **No verified image/cover ID.** |
| `literature:prh-autobiography-janeway` | `9781789095333` | **No verified image/cover ID.** |
| `literature:prh-autobiography-spock` | `9781785659416` | **No verified image/cover ID.** |
| `literature:prh-autobiography-sisko` | `9781803366258` | **No verified image/cover ID.** |

**The no-cleared-thumbnail verdict is a state of verification, not proof that no image exists.** Publisher book pages do show covers, but availability of publisher imagery is not a public-display license. The direct Open Library JSON endpoints for three current publisher ISBNs and the exact-book JSON link for Kirk timed out or were inaccessible to the available public retrieval tool during this audit. No current HTTP-404 conclusion may be derived from those failures.

## Source lineage and rights

- Accepted prior source/rights receipts: [`artwork-source-candidates-20261103`](../artwork-source-candidates-20261103/MANIFEST.md) and [`artwork-sourcing-wave2-20261103`](../artwork-sourcing-wave2-20261103/MANIFEST.md). The latter documents provider routes and rights gates; it does not authorize display.
- The only earlier functioning Open Library cover ID in those receipts, `10157401`, refers to *Star Trek: Picard: The Last Best Hope* ISBN `9781982142186`. **That edition has no matching row in the accepted directory snapshot.** It must not be assigned to any of the nine rows above.
- New public crosswalk observation: [Open Library *Autobiography of James T. Kirk* edition OL28813033M](https://openlibrary.org/books/OL28813033M/Autobiography_of_James_T._Kirk) directly lists ISBN `9781783297481`, Titan Books Limited, and 2016. This corroborates an edition identifier only, not a cover-image claim.
- [Open Library's John Jackson Miller author listing](https://openlibrary.org/authors/OL1395171A/John_Jackson_Miller) lists *The High Country* and *The Enterprise War* as Works with three editions each; individual cover ISBN associations remain unverified.
- [Open Library's licensing statement](https://openlibrary.org/developers/licensing) says Internet Archive does not assert new rights in its contributed database material, while acknowledging possible existing third-party rights. It does **not** independently clear publisher cover art.
- Episode and film poster/still thumbnails from Paramount+ remain subject to the previously recorded publisher-rights gate. A public page containing a still is not by itself an image-use license. TMDB's noncommercial API route also requires attribution, a legitimate API key, exact source-row matching, and separate underlying-image rights review.

## Next reproducible gate

1. Query one ISBN-edition Open Library or licensed provider page using a reliable, permitted API path. Capture the exact edition record, cover ID, observation date, and an immutable metadata digest. Do not invent an ID from a similarly titled Work.
2. Compare the ISBN to the **same** accepted source-local row's edition details. A correct ISBN on a different Work must be rejected.
3. Independently review public-display terms and attribution for the specific image. Keep the image opt-in and remote; do not mirror proprietary bytes by default.
4. Only after a reviewed edition/right match, prepare `explorer/artwork-catalog.json` against the then-current Explorer sidecar schema and test wrong-book/forged-rights negatives. This report itself must not enable the artwork toggle.

**Outcome:** zero newly display-cleared artwork assets; zero off-site image requests enabled; exact nine-row image provenance frontier recorded. This is not an assertion of image scarcity or a copyright conclusion.
