# VOY S4 E10–E14 — five HELD source-local Paramount+ guide cards

**Role:** Voyager source worker. **Accepted-main base at selection:** `806c4502af8eb5306137c13eaacea54f8cd469ba`. **Source observation:** 2026-11-03. **State:** proposal only.

## Fresh source processing and disjointness

Directly read the rendered [Paramount+ *Star Trek: Voyager* Season 4 guide](https://www.paramountplus.com/shows/star_trek_voyager/episodes/4/), locating each of these five headings, numbered badges, and adjacent publisher blurbs:

| Guide ordinal | Publisher's source-relative title | Blurb text fingerprint |
|---|---|---|
| S4 E10 | Random Thoughts | SHA-256, 120 normalized characters |
| S4 E11 | Concerning Flight | SHA-256, 141 normalized characters |
| S4 E12 | Mortal Coil | SHA-256, 87 normalized characters |
| S4 E13 | Waking Moment's | SHA-256, 80 normalized characters |
| S4 E14 | Message In A Bottle | SHA-256, 163 normalized characters |

These were **already discovered** in the accepted `proposals/discovery/publisher-season4-20261102/voy.csv` 26-card season list; no new episode discovery is claimed. This tranche adds held, individually bounded source-local records, rendered-blurb fingerprints, and original one-sentence synopsis candidates. A separate accepted librarian batch already contains S4 E9 *Year Of Hell, Part 2*; it is deliberately excluded. The previous local worker tranche covered E1–E5; E10–E14 are distinct. No open PR identified at selection time had this exact five-card range.

**Literal source variant:** Paramount+'s heading and earlier accepted discovery CSV print **Waking Moment's** for E13. That apostrophe is preserved, marked `PUBLISHER_APOSTROPHE_VARIANT_HELD`, and is **not** an automatically reconciled title or a global Work identity decision.

## Evidence, fingerprints, and limitations

The source was read as a **rendered web page**, not a watched episode, transcript, script, or archived original HTML response. A separate direct HTTP request from Lappy returned **406 Not Acceptable**; `raw_page_sha256` is therefore null. Each recorded blurb SHA-256 was computed from the displayed one-sentence text after Unicode NFKC and whitespace collapse; no publisher blurb text is redistributed in the packet. The five SHA-256s and character lengths are *review pins* owned by `validate.py`, not claims of persisted source-byte custody. All five complete source-local rows, including original synopsis drafts and status labels, have separate code-owned SHA-256 pins. The earlier discovered CSV's exact byte SHA-256 is also checked to expose source drift.

The source lineage is one Paramount corporate publisher family, not five independent corroborating sources. The card display is evidence of a *publisher statement*, not confirmation that a fictional event occurred, that a canonical Work has been reconciled, or that an airdate is correct. No media image/video asset URLs could be source-bound from the inspected representation, so those candidate fields are explicitly null. No visual or audiovisual content was retrieved.

Synopsis candidates are **original paraphrases of the brief publisher blurbs**, not literary or audiovisual close readings. All remain `HELD_ORIGINAL_PARAPHRASE_REQUIRES_EDITORIAL_REVIEW`. Do not publish them to the Explorer as reviewed text without a separate editorial decision. No Work binding, Source binding, episode discovery, close-read, semantic-coverage, rights, image, or Explorer effect occurs in this proposal.

## Validation

```bash
python3 proposals/research/voy-s4-e10-e14-publisher-cards-20261103/validate.py
python3 proposals/research/voy-s4-e10-e14-publisher-cards-20261103/test_validate.py
python3 -O proposals/research/voy-s4-e10-e14-publisher-cards-20261103/test_validate.py
```

The validator rejects unexpected JSON keys, duplicate keys, wrong publisher/series/season, mutable source lineage, altered upstream CSV bytes, swapped blurbs, title/ordinal drift, unauthorized Work or coverage escalation, forged source reads, and invented artwork/video URLs. Tests demonstrate failure in ordinary and optimized Python. Passing means **this candidate is internally consistent with the observed guide and accepted discovery baseline**, not that independent full-source verification has happened.

**Next frontier:** independently inspect the complete episode content or authorized transcript, obtain raw source-byte custody for the exact guide and associated assets where feasible, resolve title/spelling and version/edition variants through accepted reconciliation records, and only then upgrade source-bound Work and synopsis/Explorer states through the appropriate gates.
