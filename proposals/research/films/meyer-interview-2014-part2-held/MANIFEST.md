# HELD FILMS source-first batch — Nicholas Meyer, Part II interview (2014)

**Accepted-main anchor:** `3028765359001b90bc3e6b5c1835ee283b326e91`.
**Effect:** `PROPOSED` research only; no admitted Sources/Works, audiovisual CLOSE_READ, screenplay close-read, identity reconciliation, projection/database update, public source text or film-coverage increment.

## Exact source actually read

- Full first-party StarTrek.com Staff interview, published September 26, 2014: [Part II, Nicholas Meyer on Directing](https://www.startrek.com/en-un/news/exclusive-interview-part-ii-nicholas-meyer-on-directing).
- Complete rendered article inspected through line 89, including introduction, every interview question/answer and concluding note; source-relative testimony locators 47–87. Retrieval recorded in `records.json` on November 4, 2026.
- **No upstream HTTP response bytes archived or SHA-256 claimed.** Rendered line locators are dependent on this retrieval representation and must be rebound if page extraction changes.
- The three film catalog candidates are **already accepted discovery metadata with `UNVERIFIED_METADATA`**, not newly reconciled canonical Works. One source provides all three accounts; independent publisher-family count = **one**.
- Eight evidence records, eight source-attributed local assertions, three original interview-account summaries. No copyrighted interview dialogue or film scripts reproduced.

### Exact reviewed-text gate

Independent hostile review demonstrated that merely recomputing `BATCH_MANIFEST.packet_sha256` allowed arbitrary source-title, evidence, assertion and synopsis substitutions to pass the original length/keyword checks. The corrected packet validator now pins the canonical JSON SHA-256 of the reviewed source metadata and SHA-256 digests for **all eight original evidence paraphrases, eight assertion objects and three original summaries**, separately from the transport packet digest. Tests exercise forged records with recomputed matching manifest hashes. These are **editorial review-content fingerprints**, not hashes of the copyrighted upstream interview or proof that it is objectively true.

Source-relative corrections remain possible, but require a deliberate reviewed-text digest change and a fresh independent source audit; merely modifying a manifest SHA no longer authorizes a semantic rewrite.

## Source-relative observations and deliberate uncertainties

| Film candidate | Supporting lines | Qualifying / counterevidence in same source |
| --- | --- | --- |
| *The Wrath of Khan* | 47–57, 60–65: Meyer describes how his script staged Spock's mortality and remembers directing Montalban. | He explicitly cannot recall all earlier scripts. His own later judgment of return-facilitating changes is qualified, and no screenplay/daily footage was read. |
| *The Voyage Home* | 66–73: Meyer reports writing the Earth-set middle portion after an earlier script was discarded. | He says he was told **not to read** the earlier draft and does **not** recall this rewrite's exact duration. No derivative-source comparison is possible from this page. |
| *The Undiscovered Country* | 76–87: Meyer remembers Nimoy's post-Cold-War framing and later work with Flinn. | He guesses at the studio's motives for trying other writers; interviewer corrects a production-timeline recollection, Meyer accepts it. These are candid limits on retrospective precision. |

> Hostile challenge: creator testimony that a scene was written or planned is evidence of a creator's statement, not independently observed final-film content.

> Hostile challenge: Meyer's account and the StarTrek.com editorial framing share one interview lineage. Three film joins do **not** constitute three independent primary sources.

> Hostile challenge: the interviewer's chronology suggestion, even when accepted by Meyer, is still an interview exchange. Independent production-date corroboration would be separate evidence.

## Validation/release gates

Run:
```sh
python3 proposals/research/films/meyer-interview-2014-part2-held/validate.py
python3 -m unittest discover -s proposals/research/films/meyer-interview-2014-part2-held -p 'test_validate.py' -v
python3 -m unittest discover -s tests -q
python3 tools/validate.py
```

This proposal should remain HELD until an independent auditor reads the full source again, checks question/answer boundaries, verifies the citation spans and counters semantic overreach. Page-level raw custody, official script/dailies, film viewing and independent creator corroboration are **not** supplied by this batch. No merge/deployment rights were requested.
