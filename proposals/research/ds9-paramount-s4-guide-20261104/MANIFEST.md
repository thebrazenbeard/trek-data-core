# DS9 Season 4: held Paramount+ publisher-guide source cards

**Role:** DS9 research worker. **Batch:** `ds9-paramount-s4-guide-20261104`. **Status:** unaccepted, draft, source-local. Accepted Work/source bindings, episode research coverage, published Explorer briefings, and global identity state are **unchanged**.

## Source and extraction receipt

- Official [Paramount+ DS9 Season 4 Episode Guide](https://www.paramountplus.com/shows/star_trek_deep_space_nine/episodes/4/); source family `publisher:paramount`, one corporate publisher, not independent cross-source corroboration.
- Retrieved 2026-11-04 by `TinyFish fetch_content` as rendered Markdown and parsed the visible `Season 4 > Episode Guide` title, ordinal and short-description rows.
- **24 visible publisher cards**, ordinal S4 E1 and S4 E3–E25. **E2 and E26 are absent** from this rendering. No assumption is made about their titles or episode completeness.
- Each visible card stores exact source heading/ordinal locator; SHA-256 of its rendered UTF-8 **one-line short description without trailing newline**; and an original short, attributed paraphrase. No copyrighted vendor descriptions are reproduced in the repo.
- Raw webpage digest, verified HTTP status, source HTML byte count, media viewing, script reading and complete season census are **not** claimed.

## Source-relative anomaly requiring a separate verification

The publisher listing pairs **S4 E3 “The Visitor”** with a description about Bashir and O'Brien being held by Jem'Hadar, and **S4 E4 “Hippocratic Oath”** with a description about Sisko vanishing before Jake. This may be a title-description cross-assignment, but **that conclusion has not been independently source-verified**. The records preserve the publisher's displayed pairings verbatim as title/ordinal fields, store their description fingerprints, set `SUSPECTED_MISMATCH_UNRESOLVED`, and prohibit auto-correction. No episode-level plot assertion or canonical title reconciliation follows from this presentation.

Other cards include attributed accusations or uncertain subjective experiences (such as the Worf allegation in E18, the implanted memories in E19, and the Kasidy allegation in E22). Their held paraphrases retain that scope.

## Typed evidence model

`SOURCE → [WORK NULL/UNRESOLVED] → LOCAL ENTITY → EVIDENCE → ASSERTION`

The 24 publisher source slots link one-to-one with 24 local entities, 24 source-locator/fingerprint evidence records, and 24 `PUBLISHER_GUIDE_DESCRIBES` assertions. `fictional_truth_scope=NOT_OBJECTIVELY_ASSERTED`; no global reconciliation is attempted.

## Tests

```bash
python proposals/research/ds9-paramount-s4-guide-20261104/validate.py
python -m unittest discover -s proposals/research/ds9-paramount-s4-guide-20261104 -p 'test_*.py' -v
```

The validator pins all 24 exact title/ordinal/hash tuples, guards source provenance and admission effects, and checks every cross-reference. Eight adversarial test groups reject fabricated media/source proof, unsupported Work/coverage effects, tampered source description hashes, lost/misindexed cards, unjustified global identity, canonicalized allegations, and **premature resolution** of the E3/E4 anomaly.

**Next frontier:** Independently verify S4 E3/E4 guide title-description alignment, investigate the absent E2/E26 publisher cards, and only then perform authorised primary audiovisual/script review and separate admission decisions.
