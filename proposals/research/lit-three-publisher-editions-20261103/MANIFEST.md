# Literary publisher-edition verification — three existing novel leads

**Role:** LIT. **State:** PROPOSAL_ONLY. **Observation date:** 2026-11-03 UTC. **Accepted baseline:** `main@f387126c60942ff90952cd6e9251a67c8f5c26fa`.

I reopened all **nine individual official Simon & Schuster product pages** backing the three current novel leads—*Star Trek: Picard: Second Self*, *Star Trek: Strange New Worlds: The High Country*, and *Star Trek: Discovery: The Enterprise War*. For each paperback, eBook, and audio edition, I directly checked the displayed title, creator, format, publisher imprint, publisher release date, ISBN13, page count or audio runtime, and named audio reader where applicable.

**Result:** Nine of nine pages matched the specific edition fields already recorded by the Librarian in `proposals/librarian/simon-schuster-three-novels-20261103/records.json`. These are **bibliographically verified edition-page observations**, not just unchecked copied database rows. The validator cross-checks all nine against the accepted Librarian candidate source bundle. All records share **one publisher lineage** (`publisher:simonandschuster.com`); they are not nine independent source witnesses or nine independent Works.

I also read the **official publisher promotional descriptions** for each of the three titles and wrote one concise, original synopsis per candidate Work. These are explicitly `PUBLISHER_DESCRIPTION_PARAPHRASE` records, not a neutral close reading of the novel, an eyewitness depiction of its story events, or an accepted global plot assertion. Each synopsis links to its exact publisher edition page. The nine edition references reuse those **three** Work-level descriptions; they do not create nine different plots.

Primary page locators are specified per ISBN in `observations.json`. Representative direct links:

- [Second Self — publisher paperback ISBN 9781982194833](https://www.simonandschuster.com/books/Star-Trek-Picard-Second-Self/Una-McCormack/Star-Trek-Picard/9781982194833)
- [The High Country — publisher audio ISBN 9781797149226](https://www.simonandschuster.com/books/Star-Trek-Strange-New-Worlds-The-High-Country/John-Jackson-Miller/Star-Trek-Strange-New-Worlds/9781797149226)
- [The Enterprise War — publisher eBook ISBN 9781982113322](https://www.simonandschuster.com/books/Star-Trek-Discovery-The-Enterprise-War/John-Jackson-Miller/Star-Trek-Discovery/9781982113322)

All pages were read through a web reader, **not** preserved as authenticated raw HTML bytes. No fabricated content hash, independent upstream corroboration, or source-text custody is claimed. These sites could change; re-verification must refresh the observation date and recorded fields.

I also rechecked the owner's private 347-package OPF inventory on Lappy: none of these three novel titles or the five fictional memoir titles appears as a metadata title match. Therefore I have **not** bound these editions to any full-text book artifact. The original LIT and converted OPF holdings provide no basis for promoting these nine leads into `FULL_TEXT_AVAILABLE`, `CLOSE_READ`, or `SOURCE_BOUND` tiers.

**Effects:** No accepted Source↔Work bindings, Works, evidence assertions, global identities, coverage events, public book text, or artwork rights are changed. The public directory may display a separately labeled `PUBLISHER_METADATA_VERIFIED` editorial annotation only if the Consolidator subsequently adopts this record under the repo's acceptance process; the canonical research tier remains unchanged.
