# Independent publisher-family literary bibliography: Titan Books art/reference works

**Role:** LIT. **State:** Held candidate-inventory proposal only. **Accepted main inspected:** `3028765359001b90bc3e6b5c1835ee283b326e91` (2026-11-04 UTC). **Open hold:** [#23](https://github.com/thebrazenbeard/trek-data-core/issues/23). **Accepted research effects:** NONE.

## Why this is a separate literature tranche

The five official product pages below came from **Titan Books** (`titanbooks.com`), not the Simon & Schuster source family in [the earlier draft bibliography](https://github.com/thebrazenbeard/trek-data-core/pull/494). These are five ISBN-bearing **nonfiction illustrated art/production-reference books**, explicitly not prose-novel editions. They belong in broader literary/bibliographic inventory, **not** as fictional-story evidence, screen-episode coverage, or licensed public image releases. Titan is one publisher-family source for this batch. No cross-publisher corroboration of a shared manifestation is claimed.

Five different local Work candidates with directly retrieved official publisher catalog pages on 2026-11-04:

| Candidate literary Work | Titan display credit | Edition format, ISBN13, page extent | US / UK publication dates | First-party provenance |
| --- | --- | --- | --- | --- |
| *Star Trek: The Art of John Eaves* | Joe Nazzaro (credited author; John Eaves is the art subject) | Hardback, `9781785659119`, 208 pages | 2018-11-27 / 2018-11-20 | [Titan](https://titanbooks.com/9614-star-trek-the-art-of-john-eaves/) |
| *Star Trek: The Artistry of Dan Curry* | Dan Curry and Ben Robinson | Hardback, `9781785659348`, 204 pages | 2020-12-01 / 2020-12-01 | [Titan](https://titanbooks.com/9639-star-trek-the-artistry-of-dan-curry/) |
| *Star Trek: The Art of Juan Ortiz* | Juan Ortiz | Hardback, `9781781166703`, 112 pages | 2013-09-03 / 2013-09-06 | [Titan](https://titanbooks.com/6933-star-trek-the-art-of-juan-ortiz/) |
| *Star Trek The Next Generation: The Art of Juan Ortiz* | Juan Ortiz | Hardback, `9781785653872`, 208 pages | 2017-09-05 / 2017-09-05 | [Titan](https://titanbooks.com/9032-star-trek-the-next-generation-the-art-of-juan-ortiz/) |
| *Star Trek: The Art of Neville Page* | Joe Nazzaro (credited author; Neville Page is the art subject) | Hardback, `9781789095159`, 192 pages | 2023-08-08 / 2023-08-08 | [Titan](https://titanbooks.com/70373-star-trek-the-art-of-neville-page/) |

Publisher metadata for the Neville Page book includes an additional subtitle ("Inside the mind of the visionary designer"); the structured title records the core title only. The public pages' page counts are marketed edition metadata, **not** proof of source completeness, exact numbers of illustrations, or evidence for fictional Star Trek events.

## Source and research boundaries

The five page locators were opened/read as publisher product metadata in this worker wave. Their ISBNs were checked against all accepted-main JSON proposal records; **zero existing duplicate ISBN records** were found. That does not prove titles absent across all possible manifestations or pending PRs. No complete book, image set, publisher PDF, cover bytes, chapter contents, or private owner artifact was retrieved, structurally indexed, or close-read. The proposal provides `local_work_candidate_id` and a **publisher edition candidate**, not a global Work identity or accepted Source↔Work record.

> **Hostile challenge:** An illustrated production companion can contain staged art, discarded concepts, behind-the-scenes recollections, design drafts, or the artist's interpretations. The mere presence of artwork does not establish an in-universe fictional event, and promotional descriptions do not independently authenticate its reproduction. Treating a credit's named design subject (John Eaves or Neville Page) as the book's credited author would also corrupt bibliographic provenance. Regional publication dates differ for two editions; the catalog preserves both rather than fabricating a universal release date.

The two Juan Ortiz books are distinct Works/editions even though they share an artist. All five Titan pages come from one publisher lineage, so they are **five records but only one upstream family**. Distinct lineage from Simon & Schuster in #494 supplies new discovery breadth, not independent corroboration of that packet's unrelated novels.

`records.json` deliberately contains no copyrighted prose/image assets. The validator is deterministic and has tests that reject format, creator, ISBN, Work/edition, date, copyright, coverage, and source-boundary laundering. Coverage remains `NONE`; issue #23 still prevents new `CLOSE_READ`.

Run `python3 proposals/research/lit-titan-five-artbooks-20261104/validate.py`, `python3 -m unittest discover -s proposals/research/lit-titan-five-artbooks-20261104 -p test_validate.py -v`, and `python3 tools/validate.py`.
