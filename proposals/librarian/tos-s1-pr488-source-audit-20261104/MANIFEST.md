# Independent Librarian review — draft #488 TOS Season 1 source ordering

**Effect:** `REVIEW_ONLY_NO_ADMISSION`; issue [#23](https://github.com/thebrazenbeard/trek-data-core/issues/23)
remains OPEN, so this does **not** initiate new corpus batches or promote
metadata to Source↔Work acceptance.

**Accepted main:** `3028765359001b90bc3e6b5c1835ee283b326e91`.
**Reviewed draft PR #488 head:** `eea7478b08a1ae1b34bf27e74b8884f33f36a1a6`.
**Reviewed draft `selection.json` SHA-256:** `406452d366e74e93a38ad10826a69f193690a474517f5bf71c475735147a8368`.

## Primary publisher page actually rechecked

On 2026-11-04 the public web reader opened the **live official Paramount+**
TOS Season 1 guide at <https://www.paramountplus.com/shows/star_trek/episodes/1/>.
The text view was crawled that day and exposed episode headings/season-slot
labels at the line locators in [`review.json`](review.json). The following five
title/slot fields *all match* draft #488 and the previously accepted
`proposals/discovery/legacy-paramount-season1-20261102/tos.csv`:

| Candidate QID | Title | Paramount+ displayed slot | Wikidata item description/ordinal in fetched view |
| --- | --- | ---: | ---: |
| Q2664096 | Mudd's Women | S1 E7 | 6 |
| Q2984502 | The Enemy Within | S1 E6 | 5 |
| Q3107459 | Dagger of the Mind | S1 E10 | 9 |
| Q3178411 | Balance of Terror | S1 E15 | 14 |
| Q3487125 | A Taste of Armageddon | S1 E24 | 23 |

The live Paramount+ guide also displays **The Cage** as **S1 E1** (guide lines
102–104). The five Wikidata item pages consulted through the web reader use
an ordinal exactly one lower. This is **disconfirming evidence against treating
the archived QID's episode ordinal and Paramount+'s displayed slot as one
identical numbering field**, even though their title associations match.
It is not evidence that draft #488 *already made* such an ordinal identity
claim, nor an adjudication of which convention should be canonical.

### Exact source constraints

- Publisher fields: official Paramount+ guide, observed 2026-11-04. The web
  reader exposed text, not independently saved raw response bytes; therefore
  no new live `source_body_sha256` is claimed. The old 2026-11-02 publisher
  body receipt is not a hash of this live read.
- Wikidata item pages: <https://www.wikidata.org/wiki/Q2664096>,
  <https://www.wikidata.org/wiki/Q2984502>,
  <https://www.wikidata.org/wiki/Q3107459>,
  <https://www.wikidata.org/wiki/Q3178411>,
  <https://www.wikidata.org/wiki/Q3487125>. Web results had **mixed cached
  crawl ages**, despite the current retrieval. Item descriptions/ordinals
  are Wikidata assertions, often sourced through downstream listings; they
  are not independent primary audiovisual evidence or a verified QID↔Work
  reconciliation. Item-line locators appear in `review.json`.
- All five publisher rows share **one official guide / publisher family**.
  The five external QIDs came from **one historical WDQS snapshot and query
  digest**. Multiplying rows does not multiply independent source witnesses.
- No episode video, complete transcript, subtitle, source-rights grant,
  edition-specific Source byte witness, or large copyrighted text was read,
  retained, or published by this audit.

## Deterministic reproducibility

The audit tool checks the five stored field-level observations against the
exact hash-pinned accepted research-lead sample and Paramount+ Season 1 CSV;
it guards QID duplication, slot collisions, title mismatches, metadata-only
status, source lineage, and false admission claims. With the reviewed draft
Git object locally fetched, `--verify-pr-head` additionally checks the exact
PR `selection.json` bytes and all five title/QID/slot tuples. It does *not*
pretend to replay the network reader or independently rehash live HTML.

```sh
git fetch origin refs/heads/research/librarian-tos-s1-followon-20261104
python3 tools/audit_tos_s1_pr488.py --verify-pr-head
python3 -m unittest discover -s tests -p test_tos_s1_pr488_source_audit.py -v
python3 -O -m unittest discover -s tests -p test_tos_s1_pr488_source_audit.py -v
python3 tools/validate.py
```

> **Hostile finding:** Draft #488's field-level title/Paramount slot matches
> survive this fresh publisher check, but the QID ordinal differs by exactly
> one for all five candidates. A later reconciler that silently equates the
> two number fields would mislabel episodes. Keep the orderings source-local
> and versioned; do not resolve Work identity by arithmetic offset alone.

**Next frontier:** independent Librarian source custody / edition qualification
under issue #23; a future crosswalk review can retain both source-relative
orderings without promoting either to accepted global episode identity.
