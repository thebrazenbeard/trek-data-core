# Voyager region-specific episode listing reconciliation — bounded VOY batch

**Status: PROPOSAL ONLY.** Base accepted `main`:
`d4ecd970bf28019696abd692011007d7d47f9ff8`.
Observed via full rendered publisher episode-guide pages and the BBFC classification
catalog on 2026-11-03. This is **not** an audiovisual viewing, authenticated
transcript reading, accepted Work binding, global identity resolution, or episode
denominator audit.

## Why this batch

The already-committed, *unadmitted* United States Paramount+ observations in
`publisher-season5-20261102` and `publisher-season7-20261102` correctly left
S5E16 and S7E10 unfilled. Their Season 7 snapshot also lacks E26. The
regional Australian Paramount+ pages expose the following **six publisher
display cards** (one source-relative local entity per card):

| Publisher location | Ordinal | Card title |
| --- | --- | --- |
| Australia, Season 5 | E15 | Dark Frontier, Part 1 |
| Australia, Season 5 | E16 | Dark Frontier, Part 2 |
| Australia, Season 7 | E9 | Flesh & Blood, Part 1 |
| Australia, Season 7 | E10 | Flesh & Blood, Part 2 |
| Australia, Season 7 | E25 | Endgame Part 1 |
| Australia, Season 7 | E26 | Endgame Part 2 |

These observations close **three source-discovery questions** about the US
listing gaps at the proposal level. They do **not** settle whether a combined
US 90-minute video, split regional streaming files, alternate edits, and
television broadcast installments should map to one or several global Works.
Nor do they authorize incrementing a canonical episode count.

## Source observations and lineage

- [Paramount+ Australia Voyager Season 5](https://www.intl.paramountplus.com/au/shows/star_trek_voyager/episodes/5/): displayed S5E15 and S5E16 as separate titled cards.
- [Paramount+ Australia Voyager Season 7](https://www.intl.paramountplus.com/au/shows/star_trek_voyager/episodes/7/): displayed S7E9/E10 and E25/E26 as separate titled cards.
- [Paramount+ US Voyager Season 5](https://www.paramountplus.com/shows/star_trek_voyager/episodes/5/): the already committed source-local `voy.csv` lacked 16, and the public catalog still displays a single `Dark Frontier` E15 card.
- [Paramount+ US Voyager Season 7](https://www.paramountplus.com/shows/star_trek_voyager/episodes/7/): the previously captured `voy.csv` lacks 10 and 26; the display uses `Flesh & Blood` E9 as one card. Source websites can change, so absence claims remain scoped to captured listings, not all publisher products.
- [British Board of Film Classification — Star Trek: Voyager](https://www.bbfc.co.uk/release/star-trek-voyager-q29sbgvjdglvbjpwwc00mtixnjm): the regulator separately lists `Dark Frontier` Parts 1 and 2 at episodes 15/16, and `Flesh And Blood` Parts 1 and 2 at episodes 9/10, with separately classified version lengths and dates. These classification records support edition/part distinctions, not a global Work count or semantic plot reading.

The four Paramount+ pages belong to **one corporate publisher independence
group**; geographic mirrors are not four independent witnesses. BBFC is a
separate classification-record lineage, but its classifications may derive
from submitted distributor materials. This is independent institutional
documentation, **not** independent audiovisual close reading.

The complete rendered listing content was inspected for these exact markers;
no streaming media, full episode transcript, or copyrighted narrative was
retrieved. This wave did **not** retain raw HTML source bytes or hash a new
publisher response. Existing US capture hashes remain in their earlier
proposal manifests. Do not promote the Australian observations to immutable
Source bindings until private raw-source captures, hashes, provenance and
edition-specific Work review are completed.

## Output contract

`records.json` contains five Source observations, six local publisher-card
entities, ten source-relative evidence entries, two proposed comparison
assertions, and explicit zero-effect coverage. The validator cross-checks
the retained US CSV ordinal gaps and rejects accidental admission, changed
source lineage, missing evidence links, and invalid local IDs.

```bash
python3 proposals/research/voy-region-split-20261103/validate.py
python3 -m unittest discover -s proposals/research/voy-region-split-20261103 -p 'test_*.py'
python3 tools/validate.py
```

**Unresolved next frontier:** capture Australian source bytes/hash privately;
bind publisher display cards to exact media editions, consult broadcast and
production custody sources, document any regional re-edits, seek independent
review, then permit Librarian/Consolidator acceptance work. No global
identity reconciliation is authorized by this batch.
