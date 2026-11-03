# FILMS — six Paramount distributor film-page observations (2026-11-03 UTC)

**Status: candidate/source-local, no accepted identity, evidence, coverage, synopsis publication, or artwork release.** Baseline accepted `main@5d555279116a2f9152b76754cfcb7d6c522e04c5`. Read six different official Paramount movie pages using a rendered web reader. The page's year, rating, genre, runtime, selected cast/role pairs, selected director/writer labels, and publisher-linked `movie poster` asset locator are preserved in [`records.json`](records.json). The short synopses are **newly written paraphrases of these publisher descriptions**, not independent observation of the films and not re-publication of the publisher's original copy.

| Existing film discovery candidate | First-party film page read | As-listed year / rating / runtime |
| --- | --- | --- |
| `film-motion-picture` | [Paramount: The Motion Picture](https://www.paramount.com/movies/star-trek-the-motion-picture) | 1979 / G / 132 min |
| `film-wrath-of-khan` | [Paramount: The Wrath of Khan](https://www.paramount.com/movies/star-trek-ii-the-wrath-of-khan) | 1982 / PG / 113 min |
| `film-generations` | [Paramount: Generations](https://www.paramount.com/movies/star-trek-vii-generations) | 1994 / PG / 118 min |
| `film-first-contact` | [Paramount: First Contact](https://www.paramount.com/movies/star-trek-viii-first-contact) | 1996 / PG-13 / 112 min |
| `film-2009` | [Paramount: Star Trek (2009)](https://www.paramount.com/movies/star-trek-2009) | 2009 / PG-13 / 127 min |
| `film-into-darkness` | [Paramount: Into Darkness](https://www.paramount.com/movies/star-trek-into-darkness) | 2013 / PG-13 / 132 min |

## Source observation and custody

- The official page sections **About the Film**, **Synopsis**, **About the Cast**, **About the Crew**, and **Follow on Social Media → movie poster** were opened for each. The six page URLs differ from the fourteen already-proposed StarTrek.com synopsis URLs and the accepted separate [Paramount *Beyond* page](../beyond-paramount-metadata-20261103/records.json). This is extra publisher field observation; not six newly discovered movies or six independently corroborated film records.
- The reader's linked image previews led to six *different* `public-website-assets.paramountpictures.com` `poster_medium` URLs, preserved byte-for-byte as **held asset locators**. These current 800×1200 publisher-display derivatives are not represented as original-release theatrical poster editions, image hashes, cleared cover art, or rights licenses. **No image is copied, embedded, downloaded into the repository, or added to Explorer.** The image preview was rendered transiently by the web reader, but bytes were not saved or hashed here.
- Paramount and StarTrek.com are a related corporate publisher family. Two source URLs do **not** establish independent corroboration. No complete film, screenplay, scene, transcript, or immutable original HTML page snapshot was acquired. Accordingly `source_page_sha256=null`; the packet's own SHA-256 in `validate.py` is a local **record-integrity digest**, not a source-page digest.
- Each runtime is a distributor page number for an **unspecified version**. It must not be assigned automatically to theatrical, director's, remaster, international, streaming, or digital editions. The page's displayed year is not an exact premiere date.
- Cast and crew examples are verbatim **selected labels from the publisher page**, not complete credits, cast/character identity reconciliation, or proof of events inside the story. The original synopsis paraphrase for each film is a non-publication candidate for later editorial/source review.
- **Known source ambiguity:** The *First Contact* Paramount page places **Peter Lauritson** and **Jonathan Frakes** each under a **Director** label. Both labels are preserved exactly as the page reports them with `source_anomaly`; no resolution or independent film-credit conclusion is asserted. The other five pages' creative-credit selections likewise report the publisher's fields, not a formal film-credit audit.

## Integration and limitations

This tranche writes only `proposals/films/paramount-six-source-pages-20261103/` plus its test. It adds no global Work IDs, no canonical reconciliation decisions, no coverage ledger increments, no projection compiler, no displayed thumbnails, no Explorer data sidecar and no GitHub Pages deployment. A separate Consolidator/editorial decision is required before selected metadata or any synopsis enters a deterministic Explorer projection. The six poster locators **remain withheld** pending item-specific image permission and independent review.

> **Hostile falsifiers:** The publisher can alter a page or reissue the derivative-image token; a cached URL is not a stable binary identity. A rating/runtime without an edition binding can mislead. The `First Contact` dual-director labels can be inaccurate, and cast/crew credits can be incomplete or editorial. A selected publisher paraphrase can conflict with a complete primary film; these observations cannot settle that conflict.

## Validation

Run from the repository root:

```bash
python proposals/films/paramount-six-source-pages-20261103/validate.py
python -m unittest tests.test_films_paramount_six -v
python -m unittest discover -s tests -p 'test_*.py'
```

The validator checks source-local candidate IDs against the accepted film discovery inventory, ensures different publisher URLs than prior StarTrek.com synopses and the earlier *Beyond* record, fixes source URLs and poster asset paths against cross-film substitutions, rejects coverage/publication/reuse inflation, and pins the exact observation JSON record bytes. It is a deterministic packet integrity check, **not independent fact verification of the films**.

**Next frontier:** fresh primary source/edition binding for each film; independent verification of disputed credit labels; exact rights or non-image alternatives for Explorer; editorial admission/projection/rebuild only after source and permissions review.
