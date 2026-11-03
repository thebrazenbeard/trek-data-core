# FILMS — six additional Paramount first-party film pages (2026-11-03 UTC)

**Status: source-local research proposal only.** Accepted baseline `main@5b59deec9cf832ed030f25bd09c6fd7c318efb90`. Six distinct official Paramount film pages were read through a rendered web reader, including their **About the Film**, **Synopsis**, **About the Cast**, **About the Crew**, and **movie poster** link sections. No film audiovisual content or screenplay was read; none of this changes Work identity, accepted evidence, coverage, public synopsis, artwork release, or the Explorer.

| Existing discovery ID | First-party page (directly read) | Publisher year / rating / runtime |
| --- | --- | --- |
| `film-search-for-spock` | [*The Search for Spock*](https://www.paramount.com/movies/star-trek-iii-the-search-for-spock) | 1984 / PG / 105 min |
| `film-voyage-home` | [*The Voyage Home*](https://www.paramount.com/movies/star-trek-iv-the-voyage-home) | 1986 / PG / 119 min |
| `film-final-frontier` | [*The Final Frontier*](https://www.paramount.com/movies/star-trek-v-the-final-frontier) | 1989 / PG / 106 min |
| `film-undiscovered-country` | [*The Undiscovered Country*](https://www.paramount.com/movies/star-trek-vi-the-undiscovered-country) | 1991 / PG / 109 min |
| `film-insurrection` | [*Insurrection*](https://www.paramount.com/movies/star-trek-ix-insurrection) | 1998 / PG / 104 min |
| `film-nemesis` | [*Nemesis*](https://www.paramount.com/movies/star-trek-x-nemesis) | 2002 / PG-13 / 117 min |

The records preserve these source-relative metadata fields, three selected cast/role labels and two creative-role labels per page, and a short **original paraphrase of the page's marketing synopsis**. Publisher credits are not exhaustive film credits or globally reconciled cast/character identities. Page years are not exact theatrical premiere dates; published runtime fields do not bind a unique theatrical cut, home-media edition, digital transfer or streaming presentation.

## Original publisher-linked artwork leads — all HELD

Each page exposed a `movie poster` image link. All six current `poster_medium` image URLs were followed to confirm the **specific asset locator** and are recorded verbatim in `records.json`; the web reader displayed previews, but no image bytes/hash were saved or published. These are website-display derivatives whose filenames include some `refresh` or `noquote` qualifiers; they cannot automatically stand for an original theatrical one-sheet, print edition, or licensed reusable thumbnail.

**All six are `HELD_NO_PUBLIC_REUSE_PERMISSION_VERIFIED`.** No image embedding, GitHub binary addition, hotlink, CSP change, Pages publication or rights grant was made. Paramount's corporate ownership and public movie marketing do not establish a public reuse permission for these exact images.

## Source-dependent conflicts and limitations

- **The Search for Spock:** The Paramount page lists **1984**, while the previously accepted [StarTrek.com publisher movie description](../../research/films/publisher-synopses-20261103/observations.json) recorded **1982** for the same discovery candidate; the [AFI Catalog source-local proposal](../afi-theatrical-release-20261103/MANIFEST.md) lists a 1984-06-01 theatrical release. This batch preserves the contradiction. Agreement between a Paramount page and AFI metadata does **not** retroactively make the StarTrek.com field correct or authorize automatic reconciliation.
- **Insurrection:** Paramount's literal cast/role and crew labels include `Ru'afro`, `Anji`, and `Michael Pillar`. Those spellings are held as *source text*, explicitly unverified against on-screen credits, not silently normalized to common character or creator identities.
- All six pages and StarTrek.com originate in a related Paramount/CBS publisher lineage; multiple URLs within the same corporate family are **not independent film witnesses**. Any downstream dataset repetition would carry the same dependence risk.
- No raw source HTML, page revision digest, film-copy hash, image bytes, SKU/edition receipt, or exact rights-chain license is held. The SHA-256 in `validate.py` pins only the newly written *record file*, not upstream publisher content. Source changes require a newly reviewed packet.

> **Hostile falsifier:** A current site can silently replace an image token or marketing description; the present records are time-scoped link observations, not frozen snapshots.

> **Hostile falsifier:** A displayed runtime might describe a version other than the historically initial theatrical print; no cut binding or film reading is claimed.

> **Hostile falsifier:** Publisher credits can contain typographical errors. In particular, the *Insurrection* labels cannot be reconciled from a search result or a character assumption alone.

## Validation and integration boundary

The validator locks the exact reviewed source URL, film ID, poster path, metadata, source-lineage, contradictions and held effects; it cross-checks the accepted discovery roster, the earlier fourteen StarTrek.com paraphrases, and the [accepted six-film Paramount metadata packet](../paramount-six-source-pages-20261103/records.json) to prevent overlap. This remains a **separate proposed packet**; no automatic Explorer projection or data-release operation is included.

```bash
python proposals/films/paramount-second-six-pages-20261103/validate.py
python -m unittest tests.test_films_paramount_second_six -v
python -m unittest discover -s tests -p 'test_*.py'
```

**Next frontier:** independently resolve source-year and credit discrepancies by edition-specific primary receipts; obtain film-viewing custody for semantic research; decide synopsis/metadata editorial release through the Consolidator; verify item-specific image rights before any public thumbnails.
