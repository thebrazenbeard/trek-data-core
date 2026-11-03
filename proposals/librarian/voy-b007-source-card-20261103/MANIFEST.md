# Voyager B007 — seven first-party episode guide-card rechecks

**LIBRARIAN** · source-local proposal only · baseline accepted `main@3c0b37564123166bf38bcfa66f018abc4d5c9996` · observed 2026-11-03 UTC.

Seven formerly unverified source-local Voyager entries `lead:0083`–`lead:0089` were individually checked against **rendered official Paramount+ U.S. episode-guide cards**. Each title, publisher season/episode slot and accompanying short-description field was actually inspected. These are one publisher family and seven metadata-card observations, **not seven full episode reads or seven admitted Works**. The originating rows are Wikidata-derived source-local leads; source IDs and official guide URLs stay distinct. No automatic global reconciliation is proposed.

| Source lead | Wikidata-derived local title | Official Paramount+ card | Resolution |
| --- | --- | --- | --- |
| `lead:0083` | *Juggernaut* | [S5E21, Juggernaut](https://www.paramountplus.com/shows/star_trek_voyager/episodes/5/) | Exact |
| `lead:0084` | *Infinite Regress* | [S5E7, Infinite Regress](https://www.paramountplus.com/shows/star_trek_voyager/episodes/5/) | Exact |
| `lead:0085` | *Natural Law* | [S7E22, Natural Law](https://www.paramountplus.com/shows/star_trek_voyager/episodes/7/) | Exact |
| `lead:0086` | *Human Error* | [S7E18, Human Error](https://www.paramountplus.com/shows/star_trek_voyager/episodes/7/) | Exact |
| `lead:0087` | *Basics, Part II* | [S3E1, Basics, Part 2](https://www.paramountplus.com/shows/star_trek_voyager/episodes/3/) | Roman-numeral variant unresolved |
| `lead:0088` | *Future's End, Part II* | [S3E9, Future's End, Part 2](https://www.paramountplus.com/shows/star_trek_voyager/episodes/3/) | Roman-numeral variant unresolved |
| `lead:0089` | *Year of Hell, Part II* | [S4E9, Year Of Hell, Part 2](https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/) | Numeral and capitalization variants unresolved |

### Read and authority boundaries

- Each official card was directly opened/read through the public web reader on the season-guide page. The body of the *episode* itself was **not** read, downloaded or hashed; no raw webpage response hash or stable revision ID was exposed. The record stores exact locators and source-specific guide titles but no publisher blurb text, original synopsis, transcript, image or clip.
- The publisher's `Part 2` card slot and the original lead's `Part II` are different representations. A roman numeral can often denote the same ordinal, but **that semantic interpretation is not silently elevated into an accepted Work mapping**. Preserve the title variance, especially in multipart franchises where episode cards and full story containers can differ.
- The Paramount+ source cards belong to one corporate publisher family. Wikidata, STAPI, Memory Alpha and mirrors might repeat related episode metadata; copied values do not become independent narrative witnesses. Only independently admitted primary source reads can justify higher research stages.
- The earlier B006 Voyager tranche covers `lead:0070`–`lead:0082`. This tranche is a **separate B007** with exactly seven subsequent IDs and no DS9, film or literary worker partition edits. It does not update the accepted Explorer recheck projection, publisher synopsis review queue, or coverage ledger.

> **Hostile challenge:** Both the Wikidata lead and Paramount guide may agree on an episode title while disagreeing about how an installment, part, or release is represented. A title/slot match alone cannot prove the source body, number of canonical Works, continuity or admission state. Publisher guide blurbs may also be misattached, so none is used as fictional fact here.

`validate.py` pins accepted directory SHA-256 `2326f8822c79ad4907b6937cfc133bed001301275e5bb831923322623fb6ebbc`, seven exact row IDs/QIDs and publisher title/slots, source lineage and all unresolved statuses. It rejects false exact matches, changed denominators, unreviewed fields, rights or body-custody claims, and coverage promotions. Run `python3 proposals/librarian/voy-b007-source-card-20261103/validate.py` plus `cd proposals/librarian/voy-b007-source-card-20261103 && python3 -O -m unittest -v test_validate`.

**Effects:** zero accepted Sources, Works, Source↔Work bindings, coverage events, official synopses, media files, thumbnails or deployed public changes.
