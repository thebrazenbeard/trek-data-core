# FILMS — fourteen official publisher-description synopsis observations

**2026-11-03 UTC · FILMS lane · PROPOSAL ONLY.** Starting accepted film discovery: `explorer/film-catalog.json` on `main@792e01284c914fde10ca3f5a43ef3ae39675d91b`. This is not a claim that fourteen films have been watched or that fourteen Works have been admitted.

I opened the **thirteen existing official StarTrek.com movie detail pages** used by the source-local film discovery index. Each displayed an explicit `Synopsis` heading and short descriptive text. I also read the [official *Section 31* announcement](https://www.startrek.com/news/star-trek-section-31-premieres-january-24), including its paragraph describing Philippa Georgiou and the clandestine Starfleet division. For each of those fourteen candidate film references, `observations.json` records the exact publisher URL, source section, source-page year where printed, and a newly authored concise synopsis based on that publisher description.

**Evidence scope:** A publisher synopsis proves what the publisher says about a film, **not** what actually occurs in audiovisual source content. The status `PUBLISHER_DESCRIPTION_PARAPHRASE` explicitly separates these fourteen metadata-derived summaries from full-film viewing, screenplay research, close reading, semantic plot assertions, or independent canonical narrative truth. All fourteen descriptions come from **one franchise publisher family** (`publisher:startrek.com`), not fourteen independent upstream witnesses. The source pages were read through a rendered web reader on 2026-11-03, not preserved as authenticated raw HTML. No page-body hash, film-text digest, or article revision has been invented.

## Exact source set

| Candidate | Publisher source | Observed synopsis field |
| --- | --- | --- |
| `film-motion-picture` | [*The Motion Picture*](https://www.startrek.com/movies/star-trek-i-the-motion-picture) | Movie page `Synopsis` |
| `film-wrath-of-khan` | [*The Wrath of Khan*](https://www.startrek.com/movies/star-trek-ii-the-wrath-of-khan) | Movie page `Synopsis` |
| `film-search-for-spock` | [*The Search for Spock*](https://www.startrek.com/movies/star-trek-iii-the-search-for-spock) | Movie page `Synopsis`, year conflict below |
| `film-voyage-home` | [*The Voyage Home*](https://www.startrek.com/movies/star-trek-iv-the-voyage-home) | Movie page `Synopsis` |
| `film-final-frontier` | [*The Final Frontier*](https://www.startrek.com/movies/star-trek-v-the-final-frontier) | Movie page `Synopsis` |
| `film-undiscovered-country` | [*The Undiscovered Country*](https://www.startrek.com/movies/star-trek-vi-the-undiscovered-country) | Movie page `Synopsis` |
| `film-generations` | [*Generations*](https://www.startrek.com/movies/star-trek-generations) | Movie page `Synopsis` |
| `film-first-contact` | [*First Contact*](https://www.startrek.com/movies/star-trek-viii-first-contact) | Movie page `Synopsis` |
| `film-insurrection` | [*Insurrection*](https://www.startrek.com/movies/star-trek-ix-insurrection) | Movie page `Synopsis` |
| `film-nemesis` | [*Nemesis*](https://www.startrek.com/movies/star-trek-nemesis) | Movie page `Synopsis` |
| `film-2009` | [*Star Trek* (2009)](https://www.startrek.com/movies/star-trek-2009) | Movie page `Synopsis` |
| `film-into-darkness` | [*Into Darkness*](https://www.startrek.com/movies/star-trek-into-darkness) | Movie page `Synopsis` |
| `film-beyond` | [*Beyond*](https://www.startrek.com/movies/star-trek-beyond) | Movie page `Synopsis` |
| `film-section-31` | [*Section 31* announcement](https://www.startrek.com/news/star-trek-section-31-premieres-january-24) | Article paragraph beginning “In the movie” |

The records use `film:<catalog-id>` as a **source-local discovery row reference**, never a reconciled global Work ID. The `publisher_display_year` field is a transcription of what a page labels, not accepted release-date verification. Section 31's announcement is not a movie-detail synopsis block and has no comparable year field; it remains null.

## Independent falsifier: The Search for Spock

The [franchise detail page](https://www.startrek.com/movies/star-trek-iii-the-search-for-spock) currently prints `1982 • PG` for *The Search for Spock*. But the [AFI Catalog listing](https://catalog.afi.com/Film/57202-STAR-TREK-III-THE-SEARCH-FOR-SPOCK) reports theatrical release on **1 June 1984**. The repository's accepted `proposals/films/afi-theatrical-release-20261103/` independently documents the same contradiction. This film research packet keeps the two source-relative assertions distinct and marks the year **UNRESOLVED_SOURCE_YEAR_CONTRADICTION_NOT_RECONCILED**; it does not silently overwrite either or use the studio's year as a proven release date.

> **Hostile challenge:** The studio's brief promotional text may omit major plot points, misstate dates, or change without archival notice. Its own third-film year discrepancy demonstrates that even a primary publisher page can contain a factual error. The synopsis paraphrases are useful display leads only, not a substitute for audiovisual source reading and independently versioned editorial acceptance.

## Rights, coverage and next frontier

- No movie, screenplay, transcript, dialogue, poster, still, cover, image URL or large publisher passage is copied into the public repository. The brief summaries are original paraphrases with direct source locators.
- All accepted Source–Work bindings, evidence, coverage and public synopsis release effects are `NONE`. No full-film view or close read is claimed. All public display needs separate Consolidator/editorial admission of these source-labeled synopsis records; the Explorer compiler is not modified here.
- Next: independent hostile review of each source-to-summary mapping, validate the exact candidate IDs/URLs against accepted film catalog, preserve source page versions or authenticated snapshots when possible, and route an approved source-labeled synopsis sidecar through the existing guarded Explorer publication workflow. Full-film source access and neutral coding are separate later research tiers.

## Reproduction

```bash
python3 proposals/research/films/publisher-synopses-20261103/validate.py
python3 -O proposals/research/films/publisher-synopses-20261103/validate.py
python3 -m unittest tests.test_films_publisher_synopses -v
python3 -m unittest discover -s tests -p 'test_*.py' -q
```

The validator locks the reviewed proposal bytes, exact accepted discovery row/URL associations, source-family host constraints, fourteen status labels and the unreconciled AFI contradiction. Mutation tests reject forged sources, swapped films, false cinematic coverage, rights release and synopsis changes.
