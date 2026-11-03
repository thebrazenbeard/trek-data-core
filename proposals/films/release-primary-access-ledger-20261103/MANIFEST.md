# First-party film release-source access remediation — 2026-11-03 UTC

**Source-access proposal only; corrected after independent audit.** This packet does not supersede or merge held film research PRs [#332](https://github.com/thebrazenbeard/trek-data-core/pull/332) (*Star Trek* 2009, reviewed head `2f74b0c6777d980314f9b4a0786df63e41f577a0`) and [#325](https://github.com/thebrazenbeard/trek-data-core/pull/325) (*Into Darkness*, reviewed head `d4315328935ed1079bd7543f423118be23e3982d`). It separates **the author's earlier HTML read** from **the latest independent direct-source recheck** and older search-index leads. Baseline accepted main `a3ca40e94ef4c0a4ba47455333a0c122ded38c9a`.

## Historical author observations versus independently rechecked access

1. [Paramount Digital Entertainment's 17 November 2009 iTunes Extras announcement](https://ir.paramount.com/news-releases/news-release-details/paramount-digital-entertainment-releases-never-seen-star-trek) — **author-reported directly read HTML on 2026-11-03, not presently reproducible**. The earlier author recorded the announced HD iTunes Extras product, more than forty visual extras, and previously unseen poster key art. An independent auditor checked the exact page at **2026-11-03 13:01:34 UTC**, reported web fetch **404** and Lappy HTTP **HEAD 403 Forbidden** (Blotter `3278`, reviewed draft head `7c7d5ab1025f75da28a474ff1dd91f2bbb406fff`). That does not falsify the earlier observation, but the row's *current reliably observed fields are now empty*; the 2009 date and content stay in historical author testimony, not current direct-source custody. Neither result proves a permanent global outage.
2. [StarTrek.com staff, 19 July 2013 *Into Darkness* Blu-ray/DVD cover announcement](https://www.startrek.com/news/first-look-star-trek-into-darkness-blu-ray-dvd-box-art) — **direct first-party HTML reverified** (the site redirects to its locale path). It reports **10 September 2013 US Blu-ray, Blu-ray 3D, DVD, On Demand** and **20 August digital** availability. It also says box art was unveiled but does not grant a license to reproduce it. This source does **not** establish the 131-minute fact-sheet figure, any edition-level codec, a frame/bitstream hash, or current service availability.

Both publishers belong to related Paramount/CBS corporate lineage and are **not independent film witnesses**. The two movie-page runtimes (2009 film page 127 minutes, 2013 film page 132 minutes) and prior publisher paraphrases are already in the **accepted six-film Paramount packet** [`#329`](../paramount-six-source-pages-20261103/records.json); they are not re-recorded as new support here.

## Direct primary-source retrieval blockers, not silently repaired

| Held candidate | Exact first-party locator attempted | Fresh retrieval result |
| --- | --- | --- |
| 2009 Paramount Home Entertainment release sheet (#332) | [Paramount static PDF](https://ir.paramount.com/static-files/21c8db87-fe44-48f0-be67-9fa3d6be0bc6) | Web reader reported 404; separate Lappy `curl -I` reported 403 Forbidden. Search engine indexed an older producer document; that is **not** current direct PDF read. |
| 2009 Paramount iTunes Extras publisher attachment (alternative lead; not independent corroboration) | [Paramount static PDF](https://ir.paramount.com/static-files/65c97927-b964-415f-801a-329ab6d2883e) | Older producer-owned search result indexed a PDF, but current direct fetch failed (404). **INDEXED ONLY**: exact body and marketing-artwork identity not retrieved. |
| 2013 Paramount Home Media Distribution sheet (#325) | [Paramount static PDF](https://ir.paramount.com/static-files/cf49d3ba-f408-4599-9180-d5141396e7e7) | Web reader reported 404; indexed producer text is not a current direct PDF read. |
| 2013 Paramount investor-relations HTML release (#325) | [Paramount HTML press release page](https://ir.paramount.com/news-releases/news-release-details/director-jj-abrams-worldwide-blockbuster-sets-course-star-trek/) | Current direct web reader reported 404; indexed Paramount text quotes technical specs and 131 minutes, but no direct page content was retrieved. |

The 2009 Home press document appears in search-index excerpts describing **three-disc Blu-ray/digital copy, two-disc DVD/digital copy, single-disc DVD** on **17 November 2009**, but those physical product fields remain **HELD from this access-remediation packet**, pending reproducible source custody. Likewise, the 2013 Home press index says **131 minutes** while the directly read Paramount movie page says **132 minutes**. Both are **publisher assertions at unspecified versions**; neither number resolves the film's cut, rounding method or media edition. The 131 field remains indexed-only here.

The 2009 iTunes Extras product is not the digital-copy disc bundled with either physical format; the 2013 Blu-ray/DVD, 3D combo, single DVD, digital and On Demand labels are **historical channel/package descriptions**, not separate narrative Works or authenticated distinct feature-film bitstreams.

## Rights, provenance, and tests

The six access-status observations in `records.json` distinguish **one currently reverified first-party HTML**, **one historically author-read but independently unreproducible HTML**, and **four never-directly-retrieved publisher leads**. All five currently held observations have **empty `reliably_source_observed_fields`** and named `withheld_fields`. The independent audit timestamp/status, original author fields, URL identities and exact row digests are validator-pinned. This is a candidate packet; it changes no accepted source–Work binding, film coverage, editorial synopsis, public image permission, source/projection compiler, artwork sidecar, or Explorer/Pages deployment. No press PDF, image, video, audio, or full copyrighted source passage was copied into the public repository.

> **Hostile challenge:** Search-cached producer text can be stale or a downstream copy. A primary-hosted title or search hit is a source-discovery lead, not proof of current body custody. A source access failure in this environment does not prove the URL is permanently unavailable to every browser or network.

> **Hostile challenge:** The earlier 2009 author-reported rendered HTML read is preserved, not erased; the latest independent 404/403 is separately documented. Promoting either the older author observation or the newly indexed Paramount PDF to **currently accessible direct publisher proof** would fail closed. `HEAD 403` is not a successful or complete `GET`, and web 404 cannot be silently overwritten with indexed snippets.

> **Hostile challenge:** Replacing #325/#332 original PDF citations with the short 2013 StarTrek.com cover announcement would overclaim precise codec/runtimes; that announcement supports the exact dates and format names only.

> **Hostile challenge:** The phrase “previously unseen poster key art” is a marketing statement, not a reusable image file or redistribution license.

Validation:

```bash
python proposals/films/release-primary-access-ledger-20261103/validate.py
python -m unittest tests.test_film_release_source_access -v
python -m unittest discover -s tests -p 'test_*.py'
```

**Next action for authors of #325 and #332:** use **only the 2013 StarTrek.com directly reverified HTML** as a currently accessible partial fallback. Do not present the 2009 IR page as currently retrievable; independently recover a first-party body before promoting its author-observed historical claims. Obtain reproducible primary full release-sheet source/edition receipts for the remaining fields or hold them as index-only. Independent review must be repeated at their new exact heads. No third-party reprint should be mislabeled as a new independent Paramount source.
